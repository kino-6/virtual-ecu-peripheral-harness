from __future__ import annotations

import yaml

from veph.scenario_types import ScenarioResult


def render_report(result: ScenarioResult) -> str:
    status = "PASS" if result.passed else "FAIL"
    model_inputs = _without_keys(result.model_inputs, {"traceabilityMatrix", "harnessBoundary"})
    lines = [
        "# Scenario Report",
        "",
        f"- Scenario: `{result.name}`",
        f"- Result: **{status}**",
        f"- Final state: `{result.final_state}`",
        "- Boundary: preview-only; not a certified code generation or verification backend.",
        "",
        "## Model Inputs",
        "",
        _as_yaml(model_inputs),
        "## Traceability Matrix",
        "",
        _as_yaml(result.model_inputs.get("traceabilityMatrix", [])),
        "## Scenario Steps",
        "",
        _as_yaml(result.scenario_steps),
        "## Harness Boundary Evidence",
        "",
        _as_yaml(result.model_inputs.get("harnessBoundary", [])),
        "## Per-Step Preview Execution",
        "",
        _as_yaml(result.observed_behavior.get("stepEvidence", [])),
        "## Observed Behavior",
        "",
        _as_yaml(result.observed_behavior),
        "## Generated ECU Command Outputs",
        "",
        _as_yaml(result.generated_ecu_command_outputs or {}),
        "## Expected Behavior",
        "",
        _as_yaml(result.expected_behavior),
        "## Pass/Fail Result",
        "",
    ]
    lines.extend(f"- {item}" for item in result.checks)
    lines.extend(["", "## Runtime Trace", ""])
    if result.trace:
        lines.extend(f"- {item}" for item in result.trace)
    else:
        lines.append("- No runtime trace entries.")
    lines.extend(["", "## Register Reads", ""])
    if result.reads:
        lines.extend(f"- {read['register']}: {read['response']}" for read in result.reads)
    else:
        lines.append("- No register reads recorded.")
    lines.append("")
    return "\n".join(lines)


def _as_yaml(value: object) -> str:
    return "```yaml\n" + yaml.safe_dump(value, sort_keys=False).strip() + "\n```\n"


def _without_keys(value: dict[str, object], keys: set[str]) -> dict[str, object]:
    return {key: item for key, item in value.items() if key not in keys}
