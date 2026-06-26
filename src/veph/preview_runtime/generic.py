from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from veph.ir import ControlRuleIR, FunctionIR, HarnessDeviceIR, MbdModelIR
from veph.markup_parser import parse_markup_file
from veph.preview_runtime.errors import PreviewScenarioError
from veph.preview_runtime.expression_eval import coerce_value as _coerce_value
from veph.preview_runtime.expression_eval import expression_is_true as _expression_is_true
from veph.preview_runtime.expression_eval import resolve_value as _resolve_value
from veph.scenario_types import ScenarioResult


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
            _step_evidence(
                model=model,
                step_index=index,
                step=step,
                signal=signal,
                before=before,
                after=after,
                inputs=inputs,
                outputs=outputs,
                evaluations=evaluations,
                applied=applied,
            )
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
    checks = _evaluate_expectations(state, outputs, expected_behavior, step_evidence)
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


def _evaluate_expectations(
    state: str,
    outputs: dict[str, Any],
    expect: dict[str, Any],
    step_evidence: list[dict[str, Any]],
) -> list[str]:
    checks: list[str] = []
    if "finalState" in expect:
        checks.append(_check("finalState", state, expect["finalState"]))
    for name, expected in expect.get("outputs", {}).items():
        checks.append(_check(f"outputs.{name}", outputs.get(name), expected))
    for pair in expect.get("neverBothTrue", []):
        if not isinstance(pair, list) or len(pair) != 2:
            raise PreviewScenarioError(f"neverBothTrue entries must be two-signal lists: {pair!r}")
        checks.append(_check_never_both_true(str(pair[0]), str(pair[1]), step_evidence))
    return checks


def _check(name: str, actual: Any, expected: Any) -> str:
    prefix = "PASS" if actual == expected else "FAIL"
    return f"{prefix} {name}: actual {actual}, expected {expected}"


def _check_never_both_true(
    left: str,
    right: str,
    step_evidence: list[dict[str, Any]],
) -> str:
    snapshots: list[tuple[str, dict[str, Any]]] = []
    if step_evidence:
        first_before = step_evidence[0].get("before", {})
        if isinstance(first_before, dict):
            snapshots.append(("initial", first_before))
    for step in step_evidence:
        after = step.get("after", {})
        label = f"step {step.get('stepIndex', '?')}"
        if isinstance(after, dict):
            snapshots.append((label, after))
    violations: list[str] = []
    for label, snapshot in snapshots:
        outputs = snapshot.get("outputs", {})
        if isinstance(outputs, dict) and outputs.get(left) is True and outputs.get(right) is True:
            violations.append(label)
    if violations:
        return (
            f"FAIL neverBothTrue.{left}.{right}: both true at {', '.join(violations)}, "
            "expected never true together"
        )
    return f"PASS neverBothTrue.{left}.{right}: no preview step had both true"


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


def _state_snapshot(state: str, inputs: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "state": state,
        "inputs": dict(inputs),
        "outputs": dict(outputs),
    }


def _step_evidence(
    *,
    model: MbdModelIR,
    step_index: int,
    step: dict[str, Any],
    signal: dict[str, Any],
    before: dict[str, Any],
    after: dict[str, Any],
    inputs: dict[str, Any],
    outputs: dict[str, Any],
    evaluations: list[dict[str, Any]],
    applied: ControlRuleIR | None,
) -> dict[str, Any]:
    return {
        "stepIndex": step_index,
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
