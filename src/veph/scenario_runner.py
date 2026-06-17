from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from veph.model_loader import PeripheralModel
from veph.peripheral_runtime import PeripheralRuntime
from veph.scenario_types import ScenarioResult


class ScenarioError(ValueError):
    """Raised when a scenario is malformed or expectations fail."""


def run_scenario_file(
    model: PeripheralModel,
    scenario_path: str | Path,
    report_path: str | Path | None = None,
) -> ScenarioResult:
    data = yaml.safe_load(Path(scenario_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ScenarioError("scenario file must contain a YAML mapping")
    result = run_scenario(model, data)
    if report_path is not None:
        from veph.report import render_report

        output = Path(report_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_report(result), encoding="utf-8")
    if not result.passed:
        raise ScenarioError(f"scenario {result.name} failed expectations")
    return result


def run_scenario(model: PeripheralModel, scenario: dict[str, Any]) -> ScenarioResult:
    if scenario.get("model") != model.name:
        raise ScenarioError(f"scenario model {scenario.get('model')!r} does not match {model.name!r}")

    runtime = PeripheralRuntime(model)
    reads: list[dict[str, object]] = []
    scenario_steps = sorted(scenario.get("steps", []), key=lambda item: item.get("atMs", 0))
    for step in scenario_steps:
        _apply_step(runtime, step, reads)

    expected_behavior = dict(scenario.get("expect", {}))
    observed_behavior = _observed_behavior(runtime, reads)
    checks = _evaluate_expectations(runtime, reads, expected_behavior)
    passed = all(check.startswith("PASS") for check in checks)
    return ScenarioResult(
        name=str(scenario.get("name", "unnamed")),
        passed=passed,
        final_state=runtime.state,
        model_inputs=_model_inputs(model),
        scenario_steps=list(scenario_steps),
        observed_behavior=observed_behavior,
        expected_behavior=expected_behavior,
        reads=reads,
        trace=list(runtime.trace),
        checks=checks,
    )


def _apply_step(runtime: PeripheralRuntime, step: dict[str, Any], reads: list[dict[str, object]]) -> None:
    if "event" in step:
        runtime.apply_event(str(step["event"]))
    elif "setSignal" in step:
        signal = step["setSignal"]
        runtime.set_signal(str(signal["name"]), signal["value"])
    elif "writeRegister" in step:
        write = step["writeRegister"]
        runtime.write_register(str(write["name"]), int(write["value"]))
    elif "readRegister" in step:
        read = step["readRegister"]
        register = str(read["name"])
        value = runtime.read_register(register)
        reads.append({"register": register, "response": "timeout" if value is None else value})
    elif "injectFault" in step:
        runtime.inject_fault(str(step["injectFault"]))
    else:
        raise ScenarioError(f"unsupported scenario step: {step}")


def _evaluate_expectations(
    runtime: PeripheralRuntime,
    reads: list[dict[str, object]],
    expect: dict[str, Any],
) -> list[str]:
    checks: list[str] = []
    final_state = expect.get("finalState")
    if final_state is not None:
        checks.append(_check("finalState", runtime.state, final_state))

    for path, expected in expect.get("registers", {}).items():
        register_name, field_name = str(path).split(".", 1)
        actual = runtime.read_field(register_name, field_name)
        checks.append(_check(str(path), actual, expected))

    expected_reads = expect.get("reads", [])
    for index, expected in enumerate(expected_reads):
        actual = reads[index] if index < len(reads) else None
        if actual is None:
            checks.append(f"FAIL read[{index}]: missing, expected {expected}")
            continue
        register_ok = actual["register"] == expected["register"]
        response_ok = actual["response"] == expected["response"]
        prefix = "PASS" if register_ok and response_ok else "FAIL"
        checks.append(f"{prefix} read[{index}]: actual {actual}, expected {expected}")

    return checks


def _check(name: str, actual: Any, expected: Any) -> str:
    prefix = "PASS" if actual == expected else "FAIL"
    return f"{prefix} {name}: actual {actual}, expected {expected}"


def _model_inputs(model: PeripheralModel) -> dict[str, object]:
    return {
        "canonicalModel": str(model.source_path) if model.source_path else None,
        "name": model.name,
        "kind": model.kind,
        "schemaVersion": model.schema_version,
        "bus": {
            "type": model.bus.type,
            "mode": model.bus.mode,
            "wordBits": model.bus.word_bits,
        },
        "initialState": model.states.initial,
        "parameters": dict(model.parameters),
        "inputSignals": {
            name: {"default": signal.default, "unit": signal.unit}
            for name, signal in model.input_signals.items()
        },
    }


def _observed_behavior(runtime: PeripheralRuntime, reads: list[dict[str, object]]) -> dict[str, object]:
    return {
        "finalState": runtime.state,
        "signals": dict(runtime.signals),
        "reads": list(reads),
        "registerFields": {
            register_name: {
                field_name: runtime.read_field(register_name, field_name)
                for field_name in register.fields
            }
            for register_name, register in runtime.model.registers.items()
        },
    }
