from __future__ import annotations

import re
from pathlib import Path

from veph.ir import (
    ComponentIR,
    ControlRuleIR,
    ExpressionIR,
    FlowIR,
    FunctionIR,
    HarnessDeviceIR,
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
    functions = _parse_decomposition(by_language.get("mbd-decomposition", ""))
    controls = _parse_control(by_language.get("mbd-control", ""))
    harness_devices = _parse_harness(by_language.get("mbd-harness", ""))
    return MbdModelIR(
        title=title,
        component=component,
        ports=ports,
        registers=registers,
        transitions=transitions,
        flows=flows,
        sections=sections,
        source_path=source_path,
        functions=functions,
        controls=controls,
        harness_devices=harness_devices,
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
    trace: list[str] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("component "):
            component_name = line.split()[1]
        elif line.startswith("trace "):
            trace = _parse_trace(line.removeprefix("trace "))
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
    return ComponentIR(name=component_name, bus=bus, parameters=parameters, trace=trace), ports


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
        if line.startswith("note:"):
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
        left, _, right = line.partition(":")
        label, trace = _split_trace(right.strip())
        source, arrow, target = left.partition("->")
        if arrow != "->":
            raise MarkupParseError(f"invalid flow line: {line}")
        flows.append(FlowIR(source=source.strip(), target=target.strip(), label=label.strip(), trace=trace))
    return flows


def _parse_decomposition(body: str) -> list[FunctionIR]:
    functions: list[FunctionIR] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("system ") or line.startswith("note:"):
            continue
        name_part, separator, attr_part = line.partition(":")
        if separator != ":" or not name_part.startswith("function "):
            raise MarkupParseError(f"invalid decomposition line: {line}")
        attrs = _parse_semicolon_attrs(attr_part)
        functions.append(
            FunctionIR(
                name=name_part.removeprefix("function ").strip(),
                responsibility=attrs.get("responsibility", ""),
                owns=_split_csv(attrs.get("owns", "")),
                inputs=_split_csv(attrs.get("inputs", "")),
                outputs=_split_csv(attrs.get("outputs", "")),
                trace=_split_csv(attrs.get("trace", "")),
                scenarios=_split_csv(attrs.get("scenarios", "")),
            )
        )
    return functions


def _parse_control(body: str) -> list[ControlRuleIR]:
    controls: list[ControlRuleIR] = []
    for index, raw_line in enumerate(body.splitlines()):
        line = raw_line.strip()
        if not line:
            continue
        match = re.match(r"(?:priority\s+(?P<priority>\d+)\s+)?rule\s+(?P<name>[^:]+):\s+(?P<body>.+)", line)
        if not match:
            raise MarkupParseError(f"invalid control line: {line}")
        priority = int(match.group("priority")) if match.group("priority") else 1000 + index
        name = match.group("name").strip()
        rule_part = match.group("body").strip()
        owner = ""
        if rule_part.startswith("owner "):
            owner_part, separator, rule_part = rule_part.removeprefix("owner ").partition(" from ")
            if separator != " from ":
                raise MarkupParseError(f"control rule missing from after owner: {line}")
            owner = owner_part.strip()
            rule_part = f"from {rule_part.strip()}"
        state_scope = "*"
        if rule_part.startswith("from "):
            state_scope_part, separator, rule_part = rule_part.removeprefix("from ").partition(" when ")
            if separator != " when ":
                raise MarkupParseError(f"control rule missing when after from: {line}")
            state_scope = state_scope_part.strip()
            rule_part = f"when {rule_part.strip()}"
        if not rule_part.startswith("when "):
            raise MarkupParseError(f"control rule missing when: {line}")
        condition_part, then_separator, action_part = rule_part.removeprefix("when ").partition(" then ")
        if then_separator != " then ":
            raise MarkupParseError(f"control rule missing then: {line}")
        action_text, trace, scenarios = _split_trace_and_scenarios(action_part)
        actions = _parse_actions(action_text)
        condition = condition_part.strip()
        controls.append(
            ControlRuleIR(
                name=name,
                condition=condition,
                actions=actions,
                priority=priority,
                state_scope=state_scope,
                owner=owner,
                trace=trace,
                scenarios=scenarios,
                condition_expr=_parse_expression(condition),
            )
        )
    return controls


def _parse_harness(body: str) -> list[HarnessDeviceIR]:
    devices: list[HarnessDeviceIR] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2 or parts[0] not in {"device", "ecu"}:
            raise MarkupParseError(f"invalid harness line: {line}")
        role = parts[0]
        name = parts[1]
        attr_tokens, trace = _split_trace_tokens(parts[2:])
        attrs = _parse_attrs(attr_tokens)
        devices.append(
            HarnessDeviceIR(
                name=name,
                role=attrs.get("role", role),
                boundary=attrs.get("boundary", ""),
                trace=trace,
            )
        )
    return devices


def _parse_actions(text: str) -> dict[str, str]:
    actions: dict[str, str] = {}
    for item in text.split(","):
        item = item.strip()
        if not item:
            continue
        key, separator, value = item.partition("=")
        if separator != "=" or not key.strip() or not value.strip():
            raise MarkupParseError(f"invalid control action: {item}")
        actions[key.strip()] = value.strip()
    if not actions:
        raise MarkupParseError("control rule must contain at least one action")
    return actions


def _parse_attrs(tokens: list[str]) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for token in tokens:
        key, separator, value = token.partition("=")
        if separator != "=" or not key or not value:
            raise MarkupParseError(f"invalid attribute token: {token}")
        attrs[key] = value
    return attrs


def _parse_semicolon_attrs(text: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for item in text.split(";"):
        item = item.strip()
        if not item:
            continue
        key, separator, value = item.partition("=")
        if separator != "=" or not key.strip() or not value.strip():
            raise MarkupParseError(f"invalid decomposition attribute: {item}")
        attrs[key.strip()] = value.strip()
    return attrs


def _split_csv(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


TOKEN_RE = re.compile(r"<=|>=|==|!=|<|>|[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?|\S")
COMPARISON_OPERATORS = {"==", "!=", "<", "<=", ">", ">="}


def _parse_expression(text: str) -> ExpressionIR:
    tokens = TOKEN_RE.findall(text)
    parser = _ExpressionParser(tokens, text)
    try:
        expression = parser.parse()
    except MarkupParseError as exc:
        return ExpressionIR(kind="unsupported", source=text, diagnostic=str(exc))
    if parser.has_remaining():
        return ExpressionIR(
            kind="unsupported",
            source=text,
            diagnostic=f"unsupported expression token: {parser.peek()}",
        )
    return expression


class _ExpressionParser:
    def __init__(self, tokens: list[str], source: str) -> None:
        self.tokens = tokens
        self.source = source
        self.index = 0

    def parse(self) -> ExpressionIR:
        if not self.tokens:
            raise MarkupParseError("empty control expression")
        return self._parse_or()

    def has_remaining(self) -> bool:
        return self.index < len(self.tokens)

    def peek(self) -> str:
        return self.tokens[self.index] if self.has_remaining() else ""

    def _take(self) -> str:
        token = self.peek()
        self.index += 1
        return token

    def _parse_or(self) -> ExpressionIR:
        operands = [self._parse_and()]
        while self.peek() == "or":
            self._take()
            operands.append(self._parse_and())
        if len(operands) == 1:
            return operands[0]
        return ExpressionIR(kind="logical", source=self.source, operator="or", operands=operands)

    def _parse_and(self) -> ExpressionIR:
        operands = [self._parse_comparison()]
        while self.peek() == "and":
            self._take()
            operands.append(self._parse_comparison())
        if len(operands) == 1:
            return operands[0]
        return ExpressionIR(kind="logical", source=self.source, operator="and", operands=operands)

    def _parse_comparison(self) -> ExpressionIR:
        left = self._parse_atom()
        if self.peek() not in COMPARISON_OPERATORS:
            return left
        operator = self._take()
        right = self._parse_atom()
        return ExpressionIR(
            kind="comparison",
            source=self.source,
            operator=operator,
            left=left,
            right=right,
        )

    def _parse_atom(self) -> ExpressionIR:
        token = self._take()
        lowered = token.lower()
        if token == "always":
            return ExpressionIR(kind="always", source=self.source)
        if lowered == "true":
            return ExpressionIR(kind="boolean", source=self.source, value=True)
        if lowered == "false":
            return ExpressionIR(kind="boolean", source=self.source, value=False)
        if re.fullmatch(r"\d+(?:\.\d+)?", token):
            value: int | float = float(token) if "." in token else int(token)
            return ExpressionIR(kind="number", source=self.source, value=value)
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token):
            return ExpressionIR(kind="variable", source=self.source, name=token)
        raise MarkupParseError(f"unsupported expression token: {token}")


def _split_trace_tokens(tokens: list[str]) -> tuple[list[str], list[str]]:
    if "trace" not in tokens:
        return tokens, []
    index = tokens.index("trace")
    return tokens[:index], _parse_trace(" ".join(tokens[index + 1 :]))


def _split_trace(text: str) -> tuple[str, list[str]]:
    left, separator, right = text.partition(" trace ")
    if separator:
        return left.strip(), _parse_trace(right)
    return text.strip(), []


def _split_trace_and_scenarios(text: str) -> tuple[str, list[str], list[str]]:
    trace_text, scenario_separator, scenarios_text = text.partition(" scenarios ")
    action_text, trace = _split_trace(trace_text)
    scenarios = _parse_trace(scenarios_text) if scenario_separator else []
    return action_text, trace, scenarios


def _parse_trace(text: str) -> list[str]:
    return [item.strip() for item in text.split() if item.strip()]
