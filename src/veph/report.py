from __future__ import annotations

import yaml

from veph.scenario_types import ScenarioResult


def render_report(result: ScenarioResult) -> str:
    status = "PASS" if result.passed else "FAIL"
    lines = [
        "# Scenario Report",
        "",
        f"- Scenario: `{result.name}`",
        f"- Result: **{status}**",
        f"- Final state: `{result.final_state}`",
        "",
        "## Model Inputs",
        "",
        _as_yaml(result.model_inputs),
        "## Scenario Steps",
        "",
        _as_yaml(result.scenario_steps),
        "## Observed Behavior",
        "",
        _as_yaml(result.observed_behavior),
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
