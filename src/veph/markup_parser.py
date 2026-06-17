from __future__ import annotations

import re
from pathlib import Path

from veph.ir import (
    ComponentIR,
    FlowIR,
    MarkupSectionIR,
    MbdModelIR,
    ParameterIR,
    PortIR,
    RegisterFieldIR,
    RegisterIR,
    TransitionIR,
)


class MarkupParseError(ValueError):
    """Raised when an MBD markdown file cannot be parsed."""


FENCE_RE = re.compile(r"```(mbd-[a-z-]+)\n(.*?)```", re.DOTALL)


def parse_markup_file(path: str | Path) -> MbdModelIR:
    source_path = Path(path)
    text = source_path.read_text(encoding="utf-8")
    return parse_markup(text, source_path)


def parse_markup(text: str, source_path: Path) -> MbdModelIR:
    title = _parse_title(text)
    sections = [
        MarkupSectionIR(language=match.group(1), body=match.group(2).strip())
        for match in FENCE_RE.finditer(text)
    ]
    by_language = {section.language: section.body for section in sections}
    required = ["mbd-component", "mbd-registers", "mbd-state", "mbd-flow"]
    for language in required:
        if language not in by_language:
            raise MarkupParseError(f"missing required section: {language}")

    component, ports = _parse_component(by_language["mbd-component"])
    registers = _parse_registers(by_language["mbd-registers"])
    transitions = _parse_state(by_language["mbd-state"])
    flows = _parse_flow(by_language["mbd-flow"])
    return MbdModelIR(
        title=title,
        component=component,
        ports=ports,
        registers=registers,
        transitions=transitions,
        flows=flows,
        sections=sections,
        source_path=source_path,
    )


def _parse_title(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    raise MarkupParseError("missing markdown title")


def _parse_component(body: str) -> tuple[ComponentIR, dict[str, PortIR]]:
    component_name: str | None = None
    bus: dict[str, str] = {}
    parameters: dict[str, ParameterIR] = {}
    ports: dict[str, PortIR] = {}
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("component "):
            component_name = line.split()[1]
        elif line.startswith("bus "):
            parts = line.split()
            bus = {"type": parts[1]}
            for token in parts[2:]:
                key, value = token.split("=", 1)
                bus[key] = value
        elif line.startswith("parameter "):
            name, type_name, default = _parse_typed_default(line.removeprefix("parameter "))
            parameters[name] = ParameterIR(name=name, type=type_name, default=default or "")
        elif line.startswith("port "):
            match = re.match(r"port\s+(in|out)\s+(.+)", line)
            if not match:
                raise MarkupParseError(f"invalid port line: {line}")
            direction = match.group(1)
            name, type_name, default = _parse_typed_default(match.group(2))
            ports[name] = PortIR(name=name, direction=direction, type=type_name, default=default)
        else:
            raise MarkupParseError(f"unknown component line: {line}")
    if component_name is None:
        raise MarkupParseError("component section missing component declaration")
    return ComponentIR(name=component_name, bus=bus, parameters=parameters), ports


def _parse_typed_default(text: str) -> tuple[str, str, str | None]:
    left, _, default = text.partition("=")
    name_part, _, type_part = left.partition(":")
    name = name_part.strip()
    type_name = type_part.strip()
    if not name or not type_name:
        raise MarkupParseError(f"invalid typed declaration: {text}")
    return name, type_name, default.strip() if default else None


def _parse_registers(body: str) -> dict[str, RegisterIR]:
    registers: dict[str, RegisterIR] = {}
    current: RegisterIR | None = None
    for raw_line in body.splitlines():
        if not raw_line.strip():
            continue
        if raw_line.startswith(" ") and current is not None:
            field = _parse_register_field(raw_line.strip())
            current.fields[field.name] = field
            continue
        parts = raw_line.split()
        if len(parts) != 4:
            raise MarkupParseError(f"invalid register line: {raw_line}")
        current = RegisterIR(name=parts[0], address=parts[1], access=parts[2], width=int(parts[3]), fields={})
        registers[current.name] = current
    return registers


def _parse_register_field(line: str) -> RegisterFieldIR:
    parts = line.split()
    if parts[0] == "bit":
        bit = int(parts[1])
        name = parts[2]
        bits = parts[1]
        reset = _token_value(parts[3], "reset")
        return RegisterFieldIR(name=name, bit=bit, bits=bits, reset=reset)
    if parts[0] == "bits":
        bit_range = parts[1]
        name = parts[2]
        reset = _token_value(parts[3], "reset")
        first_bit = int(bit_range.split("..", 1)[0])
        return RegisterFieldIR(name=name, bit=first_bit, bits=bit_range, reset=reset)
    raise MarkupParseError(f"invalid register field line: {line}")


def _token_value(token: str, expected_key: str) -> str:
    key, _, value = token.partition("=")
    if key != expected_key or not value:
        raise MarkupParseError(f"expected {expected_key}=value, got {token}")
    return value


def _parse_state(body: str) -> list[TransitionIR]:
    transitions: list[TransitionIR] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = re.match(r"(.+?)\s+-->\s+(.+?):\s+(.+)", line)
        if not match:
            raise MarkupParseError(f"invalid state transition: {line}")
        transitions.append(
            TransitionIR(
                source=match.group(1).strip(),
                target=match.group(2).strip(),
                condition=match.group(3).strip(),
            )
        )
    return transitions


def _parse_flow(body: str) -> list[FlowIR]:
    flows: list[FlowIR] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        left, _, label = line.partition(":")
        source, arrow, target = left.partition("->")
        if arrow != "->":
            raise MarkupParseError(f"invalid flow line: {line}")
        flows.append(FlowIR(source=source.strip(), target=target.strip(), label=label.strip()))
    return flows
