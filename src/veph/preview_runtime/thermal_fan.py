from __future__ import annotations

import operator
from pathlib import Path
from typing import Any

import yaml

from veph.ir import ControlRuleIR, MbdModelIR
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
                "virtualIcObservation": _virtual_ic_observation(inputs),
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
        matched = _condition_is_true(control.condition, context)
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


def _condition_is_true(expression: str, context: dict[str, Any]) -> bool:
    if expression == "always":
        return True
    clauses = [clause.strip() for clause in expression.split(" and ")]
    return all(_simple_condition_is_true(clause, context) for clause in clauses)


def _simple_condition_is_true(expression: str, context: dict[str, Any]) -> bool:
    parts = expression.split()
    if len(parts) != 3:
        raise PreviewScenarioError(f"unsupported condition: {expression}")
    left, op_text, right = parts
    ops = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge, "==": operator.eq}
    if op_text not in ops:
        raise PreviewScenarioError(f"unsupported operator: {op_text}")
    left_value = _resolve_value(left, context)
    right_value = _resolve_value(right, context)
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
            {
                "name": control.name,
                "owner": control.owner,
                "priority": control.priority,
                "stateScope": control.state_scope,
                "condition": control.condition,
                "actions": dict(control.actions),
                "trace": list(control.trace),
                "scenarios": list(control.scenarios),
            }
            for control in model.controls
        ],
        "functionalDecomposition": [
            {
                "name": function.name,
                "responsibility": function.responsibility,
                "owns": list(function.owns),
                "inputs": list(function.inputs),
                "outputs": list(function.outputs),
                "trace": list(function.trace),
                "scenarios": list(function.scenarios),
            }
            for function in model.functions
        ],
        "controlSelectionPolicy": "lowest numeric priority wins after state scope and guard match",
        "harnessBoundary": [
            {
                "name": device.name,
                "role": device.role,
                "boundary": device.boundary,
                "trace": list(device.trace),
            }
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
    if model.component.name == "ToyThermalProtectionController":
        return [
            "examples/toy_thermal_protection_controller.mbd.md",
            "generated/toy_thermal_protection_controller.mmd",
            "generated/protection_ecu_preview/controller.c",
            "reports/thermal_protection_normal.md",
            "reports/thermal_protection_boundary.md",
            "reports/thermal_protection_derating.md",
            "reports/thermal_protection_fault_latch.md",
            "reports/thermal_protection_recovery.md",
        ]
    return [
        "examples/toy_thermal_fan_control.mbd.md",
        "generated/toy_thermal_fan_control.mmd",
        "generated/ecu_preview/controller.c",
        "reports/thermal_fan_normal.md or reports/thermal_fan_fault.md",
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
    return _coerce_value(token)


def _state_snapshot(state: str, inputs: dict[str, Any], outputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "state": state,
        "inputs": dict(inputs),
        "outputs": dict(outputs),
    }


def _virtual_ic_observation(inputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "ToyTempSensorIC.temperatureC": inputs.get("temperatureC"),
        "ToyTempSensorIC.temperatureValid": inputs.get("temperatureValid"),
    }


def _generated_outputs(model: MbdModelIR, outputs: dict[str, Any]) -> dict[str, Any]:
    if model.component.name == "ToyThermalProtectionController":
        return {
            **dict(outputs),
            "halCalls": [
                {
                    "api": "hal_spi_read_temperature_c",
                    "direction": "virtual IC to controller",
                    "source": "ToyTempSensorIC",
                },
                {
                    "api": "hal_pwm_set_fan_duty",
                    "direction": "controller to virtual IC",
                    "target": "ToyFanDriverIC",
                    "value": outputs.get("fanDuty"),
                },
                {
                    "api": "hal_load_limiter_set_derating",
                    "direction": "controller to virtual IC",
                    "target": "ToyLoadLimiterIC",
                    "value": outputs.get("deratingCommand"),
                },
            ],
            "controllerSource": "generated/protection_ecu_preview/controller.c",
        }
    return {
        "fanDuty": outputs.get("fanDuty"),
        "fault": outputs.get("fault"),
        "halCalls": [
            {
                "api": "hal_spi_read_temperature_c",
                "direction": "virtual IC to controller",
                "source": "ToyTempSensorIC",
            },
            {
                "api": "hal_pwm_set_fan_duty",
                "direction": "controller to virtual IC",
                "target": "ToyFanDriverIC",
                "value": outputs.get("fanDuty"),
            },
        ],
        "controllerSource": "generated/ecu_preview/controller.c",
    }


def _step_requirement_refs(applied: ControlRuleIR | None) -> set[str]:
    refs = {"HAR-001", "HAR-002", "HAR-004"}
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
