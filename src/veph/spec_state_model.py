from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from veph.spec_mbd_alignment import SpecMbdAlignmentError, mermaid_bodies_for_section


@dataclass(frozen=True)
class StateTransitionSpec:
    source: str
    target: str
    condition: str


@dataclass(frozen=True)
class StateTraceIntent:
    requirement: str
    source: str
    target: str
    actions: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class StateActionSpec:
    state: str
    phase: str
    actions: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class AdvancedStateSpec:
    kind: str
    detail: str


STATE_FENCE_RE = re.compile(r"```mermaid\n(?P<body>.*?)```", re.DOTALL)


def parse_spec_state_diagram(path: str | Path) -> list[StateTransitionSpec]:
    spec_path = Path(path)
    for body in _mermaid_bodies(spec_path):
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        if not lines or lines[0] != "stateDiagram-v2":
            continue
        transitions: list[StateTransitionSpec] = []
        for line in lines[1:]:
            if _parse_state_action_line(line) is not None:
                continue
            if _advanced_state_line_kind(line) is not None:
                continue
            match = re.match(r"(?P<source>\S+)\s+-->\s+(?P<target>[^:]+)(?::\s*(?P<condition>.+))?", line)
            if not match:
                raise SpecMbdAlignmentError(f"unsupported stateDiagram line in {spec_path}: {line}")
            transitions.append(
                StateTransitionSpec(
                    source=match.group("source").strip(),
                    target=match.group("target").strip(),
                    condition=(match.group("condition") or "initial").strip(),
                )
            )
        return transitions
    return []


def parse_spec_advanced_state_semantics(path: str | Path) -> list[AdvancedStateSpec]:
    spec_path = Path(path)
    notes: list[AdvancedStateSpec] = []
    for body in _mermaid_bodies(spec_path):
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        if not lines or lines[0] != "stateDiagram-v2":
            continue
        for line in lines[1:]:
            kind = _advanced_state_line_kind(line)
            if kind is not None:
                notes.append(AdvancedStateSpec(kind=kind, detail=line))
                continue
            transition = re.match(r"(?P<source>\S+)\s+-->\s+(?P<target>[^:]+)(?::\s*(?P<condition>.+))?", line)
            if transition and (transition.group("source") == "[H]" or transition.group("target") == "[H]"):
                notes.append(AdvancedStateSpec(kind="history", detail=line))
            if transition and (transition.group("condition") or "").startswith("after "):
                notes.append(AdvancedStateSpec(kind="temporal", detail=line))
        return _dedupe_advanced_notes(notes)
    return []


def parse_spec_state_actions(path: str | Path) -> list[StateActionSpec]:
    spec_path = Path(path)
    actions: list[StateActionSpec] = []
    for body in _mermaid_bodies(spec_path):
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        if not lines or lines[0] != "stateDiagram-v2":
            continue
        for line in lines[1:]:
            parsed = _parse_state_action_line(line)
            if parsed is not None:
                actions.append(parsed)
        return actions
    return []


def state_trace_intents(path: Path) -> list[StateTraceIntent]:
    intents: list[StateTraceIntent] = []
    text = path.read_text(encoding="utf-8")
    for match in re.finditer(r"^-\s+`(?P<req>[^`]+)`:\s*(?P<body>.+)$", text, re.MULTILINE):
        body = match.group("body")
        transition_match = re.search(
            r"`?(?P<source>[A-Za-z_][A-Za-z0-9_]*)\s+-->\s+(?P<target>[A-Za-z_][A-Za-z0-9_]*)`?",
            body,
        )
        if transition_match is None:
            continue
        actions = tuple(
            (action.group("name"), action.group("value"))
            for action in re.finditer(
                r"`?(?P<name>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>true|false|[A-Za-z_][A-Za-z0-9_]*)`?",
                body,
            )
        )
        intents.append(
            StateTraceIntent(
                requirement=match.group("req"),
                source=transition_match.group("source"),
                target=transition_match.group("target"),
                actions=actions,
            )
        )
    return intents


def trace_for_transition(
    intents: list[StateTraceIntent],
    transition: StateTransitionSpec,
) -> StateTraceIntent | None:
    for intent in intents:
        if intent.source == transition.source and intent.target == transition.target:
            return intent
    return None


def report_requirement(requirements: list[str], intents: list[StateTraceIntent]) -> str:
    intent_requirements = {intent.requirement for intent in intents}
    for requirement in requirements:
        if requirement not in intent_requirements:
            return requirement
    return requirements[-1] if requirements else ""


def trace_for_input(
    input_name: str,
    intents: list[StateTraceIntent],
    transitions: list[StateTransitionSpec],
) -> list[str]:
    matched: list[str] = []
    for transition in transitions:
        if re.search(rf"\b{re.escape(input_name)}\b", transition.condition):
            intent = trace_for_transition(intents, transition)
            if intent is not None:
                matched.append(intent.requirement)
    return _ordered_unique(matched)


def trace_for_output(
    requirements: list[str],
    output_name: str,
    intents: list[StateTraceIntent],
) -> list[str]:
    matched = [
        intent.requirement
        for intent in intents
        if any(name == output_name for name, _ in intent.actions)
    ]
    return _ordered_unique(matched) or requirements[:1]


def initial_state(transitions: list[StateTransitionSpec]) -> str:
    for transition in transitions:
        if transition.source == "[*]":
            return transition.target
    return ""


def rule_name(transition: StateTransitionSpec) -> str:
    return f"{transition.source.lower()}_to_{transition.target.lower()}"


def _parse_state_action_line(line: str) -> StateActionSpec | None:
    match = re.match(
        r"(?P<state>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?P<phase>entry|during|exit)\s+(?P<actions>.+)",
        line,
    )
    if match is None:
        return None
    return StateActionSpec(
        state=match.group("state"),
        phase=match.group("phase"),
        actions=tuple(_parse_state_action_pairs(match.group("actions"))),
    )


def _parse_state_action_pairs(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for item in text.split(","):
        name, separator, value = item.strip().partition("=")
        if separator != "=" or not name.strip() or not value.strip():
            raise SpecMbdAlignmentError(f"invalid state action: {item}")
        pairs.append((name.strip(), value.strip()))
    return pairs


def _advanced_state_line_kind(line: str) -> str | None:
    if re.match(r"state\s+[A-Za-z_][A-Za-z0-9_]*\s*\{", line):
        return "hierarchy"
    if line == "}":
        return "hierarchy"
    if line == "--":
        return "parallel"
    return None


def _dedupe_advanced_notes(notes: list[AdvancedStateSpec]) -> list[AdvancedStateSpec]:
    result: list[AdvancedStateSpec] = []
    seen: set[tuple[str, str]] = set()
    for note in notes:
        key = (note.kind, note.detail)
        if key in seen:
            continue
        seen.add(key)
        result.append(note)
    return result


def _mermaid_bodies(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    control_bodies = list(mermaid_bodies_for_section(text, path, "Control Semantics View"))
    if control_bodies:
        return control_bodies
    return [match.group("body").strip() for match in STATE_FENCE_RE.finditer(text)]


def _ordered_unique(items) -> list[str]:
    values: list[str] = []
    for item in items:
        if item and item not in values:
            values.append(item)
    return values
