from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioResult:
    name: str
    passed: bool
    final_state: str
    model_inputs: dict[str, object]
    scenario_steps: list[dict[str, object]]
    observed_behavior: dict[str, object]
    expected_behavior: dict[str, object]
    reads: list[dict[str, object]]
    trace: list[str]
    checks: list[str]
    generated_ecu_command_outputs: dict[str, object] | None = None
