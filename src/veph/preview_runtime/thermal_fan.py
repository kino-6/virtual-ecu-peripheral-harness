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

    scenario_steps = sorted(scenario.get("steps", []), key=lambda item: item.get("atMs", 0))
    for step in scenario_steps:
        if "setInput" not in step:
            raise PreviewScenarioError(f"unsupported preview scenario step: {step}")
        signal = step["setInput"]
        name = str(signal["name"])
        if name not in inputs:
            raise PreviewScenarioError(f"unknown input: {name}")
        inputs[name] = _coerce_value(signal["value"])
        trace.append(f"input {name}={inputs[name]}")
        state, applied = _evaluate_controls(model.controls, state, inputs, outputs, parameters)
        if applied is not None:
            applied_rules.append(applied.name)
            trace.append(f"rule {applied.name} applied")

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
    }
    generated_outputs = {
        "fanDuty": outputs.get("fanDuty"),
        "fault": outputs.get("fault"),
        "halCalls": [
            "hal_spi_read_temperature_c",
            "hal_pwm_set_fan_duty",
        ],
    }
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
) -> tuple[str, ControlRuleIR | None]:
    context = {**parameters, **inputs, **outputs, "state": state}
    for control in controls:
        if _condition_is_true(control.condition, context):
            for key, value in control.actions.items():
                resolved = _resolve_value(value, context)
                if key == "state":
                    state = str(resolved)
                    context["state"] = state
                else:
                    outputs[key] = resolved
                    context[key] = resolved
            return state, control
    return state, None


def _condition_is_true(expression: str, context: dict[str, Any]) -> bool:
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
        "requirementRefs": sorted(model.requirement_refs()),
    }


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
