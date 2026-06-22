from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from veph.scenario_types import ScenarioResult
from veph.spec_mbd_alignment import mermaid_bodies_for_section


@dataclass(frozen=True)
class SequenceExpectation:
    source_state: str
    target_state: str
    outputs: tuple[tuple[str, str], ...]

    def render(self) -> str:
        output_text = ", ".join(f"{name}={value}" for name, value in self.outputs)
        return f"{self.source_state} -> {self.target_state}" + (f", {output_text}" if output_text else "")


@dataclass(frozen=True)
class SequenceExpectationReport:
    expectations: tuple[SequenceExpectation, ...]
    matched: tuple[str, ...]
    missing: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.missing


TRANSITION_RE = re.compile(r"\b(?P<source>[A-Z][A-Z0-9_]*)\s*->\s*(?P<target>[A-Z][A-Z0-9_]*)\b")
OUTPUT_RE = re.compile(r"\b(?P<name>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>true|false|[A-Z0-9_]+|\d+)\b")


def sequence_expectations_from_spec(path: str | Path) -> tuple[SequenceExpectation, ...]:
    spec_path = Path(path)
    text = spec_path.read_text(encoding="utf-8")
    expectations: list[SequenceExpectation] = []
    for body in mermaid_bodies_for_section(text, spec_path, "Sequence View"):
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        if not lines or lines[0] != "sequenceDiagram":
            continue
        for line in lines[1:]:
            if "-->>" not in line or ":" not in line:
                continue
            payload = line.split(":", 1)[1].strip()
            transition = TRANSITION_RE.search(payload)
            if transition is None:
                continue
            outputs = tuple((match.group("name"), match.group("value")) for match in OUTPUT_RE.finditer(payload))
            expectations.append(
                SequenceExpectation(
                    source_state=transition.group("source"),
                    target_state=transition.group("target"),
                    outputs=outputs,
                )
            )
    return tuple(expectations)


def compare_sequence_expectations(
    spec_path: str | Path,
    result: ScenarioResult,
) -> SequenceExpectationReport:
    expectations = sequence_expectations_from_spec(spec_path)
    matched: list[str] = []
    missing: list[str] = []
    step_evidence = result.observed_behavior.get("stepEvidence", [])
    if not isinstance(step_evidence, list):
        step_evidence = []
    for expectation in expectations:
        rendered = expectation.render()
        if any(_step_matches(expectation, step) for step in step_evidence):
            matched.append(rendered)
        else:
            missing.append(rendered)
    return SequenceExpectationReport(
        expectations=expectations,
        matched=tuple(matched),
        missing=tuple(missing),
    )


def _step_matches(expectation: SequenceExpectation, step: object) -> bool:
    if not isinstance(step, dict):
        return False
    before = step.get("before")
    after = step.get("after")
    if not isinstance(before, dict) or not isinstance(after, dict):
        return False
    if before.get("state") != expectation.source_state or after.get("state") != expectation.target_state:
        return False
    outputs = after.get("outputs")
    if not isinstance(outputs, dict):
        return False
    return all(outputs.get(name) == _coerce_expected_value(value) for name, value in expectation.outputs)


def _coerce_expected_value(value: str) -> Any:
    if value == "true":
        return True
    if value == "false":
        return False
    try:
        return int(value)
    except ValueError:
        return value
