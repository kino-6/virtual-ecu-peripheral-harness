from __future__ import annotations

import re
from pathlib import Path

from veph.spec_state_model import StateTransitionSpec


def format_actions(actions: list[tuple[str, str]]) -> str:
    return ", ".join(f"{name}={value}" for name, value in actions)


def ordered_unique(items) -> list[str]:
    values: list[str] = []
    for item in items:
        if item and item not in values:
            values.append(item)
    return values


def ordered_states(transitions: list[StateTransitionSpec]) -> list[str]:
    values: list[str] = []
    for transition in transitions:
        for state in [transition.source, transition.target]:
            if state != "[*]" and state not in values:
                values.append(state)
    return values


def trace_suffix(requirements: list[str]) -> str:
    return f" trace {' '.join(requirements)}" if requirements else ""


def append_unique(lines: list[str], emitted: set[str], line: str) -> None:
    if line in emitted:
        return
    emitted.add(line)
    lines.append(line)


def title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return path.stem


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def requirement_ids(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return ordered_unique(re.findall(r"^-\s+`([^`]+)`:", text, re.MULTILINE))


def requirement_texts(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    current: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^-\s+`(?P<req>[^`]+)`:\s*(?P<body>.+)$", raw_line)
        if match:
            current = match.group("req")
            values.setdefault(current, match.group("body").strip())
            continue
        if current is None:
            continue
        if raw_line.startswith("- "):
            current = None
            continue
        if raw_line.startswith("  ") and raw_line.strip():
            values[current] = f"{values[current]} {raw_line.strip()}"
            continue
        if not raw_line.strip():
            current = None
    return values
