from __future__ import annotations

import ast
import operator
from pathlib import Path
from typing import Any

import yaml

from veph.ir import ControlRuleIR, ExpressionIR, FunctionIR, HarnessDeviceIR, MbdModelIR
from veph.markup_parser import parse_markup_file
from veph.scenario_types import ScenarioResult


class PreviewScenarioError(ValueError):
    """Raised when a preview scenario is malformed or fails expectations."""


def run_preview_file(
    model_path: str | Path,
    scenario_path: str | Path,
    report_path: str | Path | None = None,
) -> ScenarioResult:
    model = parse_markup_file(model_path)
    data = yaml.safe_load(Path(scenario_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise PreviewScenarioError("preview scenario file must contain a YAML mapping")
    result = run_preview(model, data)
    if report_path is not None:
        from veph.report import render_report

        output = Path(report_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_report(result), encoding="utf-8")
    if not result.passed:
        raise PreviewScenarioError(f"preview scenario {result.name} failed expectations")
    return result


def run_preview(model: MbdModelIR, scenario: dict[str, Any]) -> ScenarioResult:
    if scenario.get("model") != model.component.name:
        raise PreviewScenarioError(
            f"scenario model {scenario.get('model')!r} does not match {model.component.name!r}"
        )

    state = _initial_state(model)
    inputs = _initial_inputs(model)
    outputs = _initial_outputs(model)
    parameters = {name: _coerce_value(parameter.default) for name, parameter in model.component.parameters.items()}
    trace: list[str] = ["preview-only runtime started"]
    applied_rules: list[str] = []
    step_evidence: list[dict[str, Any]] = []

    scenario_steps = sorted(scenario.get("steps", []), key=lambda item: item.get("atMs", 0))
    for index, step in enumerate(scenario_steps):
        if "setInput" not in step:
            raise PreviewScenarioError(f"unsupported preview scenario step: {step}")
        signal = step["setInput"]
        name = str(signal["name"])
        if name not in inputs:
            raise PreviewScenarioError(f"unknown input: {name}")
        before = _state_snapshot(state, inputs, outputs)
        inputs[name] = _coerce_value(signal["value"])
        trace.append(f"input {name}={inputs[name]}")
        state, applied, evaluations = _evaluate_controls(model.controls, state, inputs, outputs, parameters)
        if applied is not None:
            applied_rules.append(applied.name)
            trace.append(f"rule {applied.name} applied")
        after = _state_snapshot(state, inputs, outputs)
        step_evidence.append(
            {
                "stepIndex": index,
                "atMs": step.get("atMs", 0),
                "scenarioInput": dict(signal),
                "before": before,
                "virtualIcObservation": _virtual_ic_observation(model, inputs),
                "controlRuleEvaluations": evaluations,
                "selectionPolicy": "lowest numeric priority wins after state scope and guard match",
                "appliedRule": applied.name if applied else None,
                "appliedOwner": applied.owner if applied else None,
                "generatedEcuCommandOutputs": _generated_outputs(model, outputs),
                "after": after,
                "requirementRefs": sorted(_step_requirement_refs(applied)),
            }
        )

    expected_behavior = dict(scenario.get("expect", {}))
    observed_behavior = {
        "finalState": state,
        "inputs": dict(inputs),
        "outputs": dict(outputs),
        "appliedRules": list(applied_rules),
        "harnessDevices": [
            {"name": device.name, "role": device.role, "boundary": device.boundary}
            for device in model.harness_devices
        ],
        "stepEvidence": step_evidence,
    }
    generated_outputs = _generated_outputs(model, outputs)
    checks = _evaluate_expectations(state, outputs, expected_behavior)
    passed = all(check.startswith("PASS") for check in checks)
    return ScenarioResult(
        name=str(scenario.get("name", "unnamed")),
        passed=passed,
        final_state=state,
        model_inputs=_model_inputs(model),
        scenario_steps=list(scenario_steps),
        observed_behavior=observed_behavior,
        expected_behavior=expected_behavior,
        reads=[],
        trace=trace,
        checks=checks,
        generated_ecu_command_outputs=generated_outputs,
    )


def _evaluate_controls(
    controls: list[ControlRuleIR],
    state: str,
    inputs: dict[str, Any],
    outputs: dict[str, Any],
    parameters: dict[str, Any],
) -> tuple[str, ControlRuleIR | None, list[dict[str, Any]]]:
    context = {**parameters, **inputs, **outputs, "state": state}
    evaluations: list[dict[str, Any]] = []
    selected: ControlRuleIR | None = None
    for control in sorted(controls, key=lambda item: (item.priority, item.name)):
        state_scope_matched = _state_scope_matches(control.state_scope, state)
        matched = _expression_is_true(control.condition_expr, context)
        evaluations.append(
            {
                "rule": control.name,
                "owner": control.owner,
                "priority": control.priority,
                "stateScope": control.state_scope,
                "stateScopeMatched": state_scope_matched,
                "condition": control.condition,
                "matched": matched,
                "selectable": state_scope_matched and matched,
                "actionsIfMatched": dict(control.actions),
                "trace": list(control.trace),
                "scenarios": list(control.scenarios),
            }
        )
        if state_scope_matched and matched and selected is None:
            selected = control
    if selected is None:
        return state, None, evaluations
    for key, value in selected.actions.items():
        resolved = _resolve_value(value, context)
        if key == "state":
            state = str(resolved)
            context["state"] = state
        else:
            outputs[key] = resolved
            context[key] = resolved
    return state, selected, evaluations


def _state_scope_matches(state_scope: str, state: str) -> bool:
    return state_scope in {"*", state}


def _expression_is_true(expression: ExpressionIR, context: dict[str, Any]) -> bool:
    return bool(_expression_value(expression, context))


def _expression_value(expression: ExpressionIR, context: dict[str, Any]) -> Any:
    if expression.kind == "always":
        return True
    if expression.kind == "variable":
        return _resolve_value(expression.name, context)
    if expression.kind in {"number", "boolean"}:
        return expression.value
    if expression.kind == "comparison":
        if expression.left is None or expression.right is None:
            raise PreviewScenarioError(f"unsupported condition: {expression.source}")
        return _compare_values(
            _expression_value(expression.left, context),
            expression.operator,
            _expression_value(expression.right, context),
        )
    if expression.kind == "logical":
        if expression.operator == "and":
            return all(_expression_is_true(operand, context) for operand in expression.operands)
        if expression.operator == "or":
            return any(_expression_is_true(operand, context) for operand in expression.operands)
        if expression.operator == "not":
            if len(expression.operands) != 1:
                raise PreviewScenarioError(f"unsupported condition: {expression.source}")
            return not _expression_is_true(expression.operands[0], context)
    raise PreviewScenarioError(
        f"unsupported condition: {expression.source or expression.diagnostic or expression.kind}"
    )


def _compare_values(left_value: Any, op_text: str, right_value: Any) -> bool:
    ops = {
        "<": operator.lt,
        "<=": operator.le,
        ">": operator.gt,
        ">=": operator.ge,
        "==": operator.eq,
        "!=": operator.ne,
    }
    if op_text not in ops:
        raise PreviewScenarioError(f"unsupported operator: {op_text}")
    return bool(ops[op_text](left_value, right_value))


def _evaluate_expectations(state: str, outputs: dict[str, Any], expect: dict[str, Any]) -> list[str]:
    checks: list[str] = []
    if "finalState" in expect:
        checks.append(_check("finalState", state, expect["finalState"]))
    for name, expected in expect.get("outputs", {}).items():
        checks.append(_check(f"outputs.{name}", outputs.get(name), expected))
    return checks


def _check(name: str, actual: Any, expected: Any) -> str:
    prefix = "PASS" if actual == expected else "FAIL"
    return f"{prefix} {name}: actual {actual}, expected {expected}"


def _model_inputs(model: MbdModelIR) -> dict[str, object]:
    return {
        "source": str(model.source_path),
        "sourceFormat": "mbd-markdown",
        "component": model.component.name,
        "parameters": {
            name: parameter.default for name, parameter in model.component.parameters.items()
        },
        "ports": {
            name: {"direction": port.direction, "type": port.type, "default": port.default}
            for name, port in model.ports.items()
        },
        "controlRules": [
            _control_rule_input(control)
            for control in model.controls
        ],
        "functionalDecomposition": [
            _function_input(function)
            for function in model.functions
        ],
        "controlSelectionPolicy": "lowest numeric priority wins after state scope and guard match",
        "harnessBoundary": [
            _harness_boundary_input(device)
            for device in model.harness_devices
        ],
        "traceabilityMatrix": _traceability_matrix(model),
        "requirementRefs": sorted(model.requirement_refs()),
        "previewSubsetAssumption": (
            "Preview subset assumption: discrete scenario steps represent the "
            "Simulink-compatible subset. Timing behavior such as sensor invalid "
            "debounce is represented by explicit scenario inputs and must be "
            "verified by external MBD/product-test infrastructure."
        ),
    }


def _control_rule_input(control: ControlRuleIR) -> dict[str, object]:
    return {
        "name": control.name,
        "owner": control.owner,
        "priority": control.priority,
        "stateScope": control.state_scope,
        "condition": control.condition,
        "actions": dict(control.actions),
        "trace": list(control.trace),
        "scenarios": list(control.scenarios),
    }


def _function_input(function: FunctionIR) -> dict[str, object]:
    return {
        "name": function.name,
        "responsibility": function.responsibility,
        "owns": list(function.owns),
        "inputs": list(function.inputs),
        "outputs": list(function.outputs),
        "trace": list(function.trace),
        "scenarios": list(function.scenarios),
    }


def _harness_boundary_input(device: HarnessDeviceIR) -> dict[str, object]:
    return {
        "name": device.name,
        "role": device.role,
        "boundary": device.boundary,
        "trace": list(device.trace),
    }


def _traceability_matrix(model: MbdModelIR) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for ref in sorted(model.requirement_refs()):
        rows.append(
            {
                "requirement": ref,
                "modelElements": _elements_for_ref(model, ref),
                "evidence": _artifact_evidence(model),
            }
        )
    return rows


def _artifact_evidence(model: MbdModelIR) -> list[str]:
    stem = model.source_path.name.removesuffix(".mbd.md").removesuffix(".md")
    generated_diagram = f"generated/{stem}.mmd"
    if model.source_path.parent.name != "samples" and model.source_path.parent.parent.name == "samples":
        generated_diagram = str(model.source_path.parent / "generated" / "diagram.mmd")
    return [
        str(model.source_path),
        generated_diagram,
        "preview report path supplied by run-preview",
    ]


def _elements_for_ref(model: MbdModelIR, ref: str) -> list[str]:
    elements: list[str] = []
    if ref in model.component.trace:
        elements.append(f"component:{model.component.name}")
    for function in model.functions:
        if ref in function.trace:
            elements.append(f"function:{function.name}")
    for flow in model.flows:
        if ref in flow.trace:
            elements.append(f"flow:{flow.source}->{flow.target}")
    for control in model.controls:
        if ref in control.trace:
            elements.append(f"control:{control.name}")
    for device in model.harness_devices:
        if ref in device.trace:
            elements.append(f"harness:{device.name}")
    return elements


def _initial_state(model: MbdModelIR) -> str:
    return model.transitions[0].source if model.transitions else "INITIAL"


def _initial_inputs(model: MbdModelIR) -> dict[str, Any]:
    return {
        name: _coerce_value(port.default)
        for name, port in model.ports.items()
        if port.direction == "in"
    }


def _initial_outputs(model: MbdModelIR) -> dict[str, Any]:
    return {
        name: _coerce_value(port.default)
        for name, port in model.ports.items()
        if port.direction == "out"
    }


def _resolve_value(token: str, context: dict[str, Any]) -> Any:
    if token in context:
        return context[token]
    if any(operator_text in token for operator_text in ["+", "-", "*", "/", "(", ")"]):
        try:
            return _evaluate_arithmetic_expression(token, context)
        except PreviewScenarioError:
            raise
        except Exception:
            pass
    return _coerce_value(token)


def _evaluate_arithmetic_expression(text: str, context: dict[str, Any]) -> Any:
    try:
        tree = ast.parse(text, mode="eval")
    except SyntaxError as exc:
        raise PreviewScenarioError(f"unsupported arithmetic expression: {text}") from exc
    return _evaluate_arithmetic_node(tree.body, context)


def _evaluate_arithmetic_node(node: ast.AST, context: dict[str, Any]) -> Any:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name):
        if node.id not in context:
            raise PreviewScenarioError(f"unknown arithmetic signal: {node.id}")
        return context[node.id]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _evaluate_arithmetic_node(node.operand, context)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp):
        operations = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
        }
        op = operations.get(type(node.op))
        if op is None:
            raise PreviewScenarioError("unsupported arithmetic operator")
        left = _require_number(_evaluate_arithmetic_node(node.left, context))
        right = _require_number(_evaluate_arithmetic_node(node.right, context))
        return op(left, right)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        args = [_evaluate_arithmetic_node(arg, context) for arg in node.args]
        if node.func.id == "clamp" and len(args) == 3:
            value, lower, upper = (_require_number(arg) for arg in args)
            return min(max(value, lower), upper)
        if node.func.id == "lookup1d" and len(args) == 2:
            return _lookup1d(_require_number(args[0]), _table_points(args[1]))
    raise PreviewScenarioError("unsupported arithmetic expression")


def _require_number(value: Any) -> int | float:
    if isinstance(value, (int, float)):
        return value
    raise PreviewScenarioError(f"non-numeric arithmetic value: {value!r}")


def _table_points(value: Any) -> list[tuple[float, float]]:
    if not isinstance(value, str):
        raise PreviewScenarioError("lookup1d table points must be a string parameter")
    points: list[tuple[float, float]] = []
    for item in value.split(","):
        left, separator, right = item.strip().partition(":")
        if not separator:
            left, separator, right = item.strip().partition("=")
        if not separator:
            raise PreviewScenarioError(f"invalid lookup1d table point: {item}")
        points.append((float(left), float(right)))
    if len(points) < 2:
        raise PreviewScenarioError("lookup1d requires at least two table points")
    return sorted(points)


def _lookup1d(value: int | float, points: list[tuple[float, float]]) -> int | float:
    if value <= points[0][0]:
        return _coerce_number(points[0][1])
    if value >= points[-1][0]:
        return _coerce_number(points[-1][1])
    for (left_x, left_y), (right_x, right_y) in zip(points, points[1:]):
        if left_x <= value <= right_x:
            ratio = (value - left_x) / (right_x - left_x)
            return _coerce_number(left_y + ratio * (right_y - left_y))
    return _coerce_number(points[-1][1])


def _coerce_number(value: float) -> int | float:
    return int(value) if float(value).is_integer() else value


def _state_snapshot(state: str, inputs: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "state": state,
        "inputs": dict(inputs),
        "outputs": dict(outputs),
    }


def _virtual_ic_observation(model: MbdModelIR, inputs: dict[str, Any]) -> dict[str, Any]:
    return {
        f"{model.component.name}.{name}": value
        for name, value in inputs.items()
    }


def _generated_outputs(model: MbdModelIR, outputs: dict[str, Any]) -> dict[str, Any]:
    return {
        **dict(outputs),
        "commandFlows": _command_flows(model, outputs),
        "previewCodeSource": "sample-specific preview C export, if available",
    }


def _command_flows(model: MbdModelIR, outputs: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    prefix = f"{model.component.name}."
    for flow in model.flows:
        if not flow.source.startswith(prefix):
            continue
        output_name = flow.source.removeprefix(prefix)
        if output_name in outputs:
            rows.append(
                {
                    "source": flow.source,
                    "target": flow.target,
                    "label": flow.label,
                    "value": outputs.get(output_name),
                    "trace": list(flow.trace),
                }
            )
    return rows


def _step_requirement_refs(applied: ControlRuleIR | None) -> set[str]:
    refs: set[str] = set()
    if applied is not None:
        refs.update(applied.trace)
    return refs


def _coerce_value(value: Any) -> Any:
    if isinstance(value, str):
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        try:
            number = float(value)
        except ValueError:
            return value
        if number.is_integer():
            return int(number)
        return number
    return value
