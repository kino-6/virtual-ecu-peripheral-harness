from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from veph.spec_mbd_alignment import (
    MermaidEdge,
    MermaidFlowchart,
    MermaidNode,
    SpecMbdAlignmentError,
    parse_spec_design_overview_flowchart,
)


@dataclass(frozen=True)
class StateTransitionSpec:
    source: str
    target: str
    condition: str


@dataclass(frozen=True)
class DecisionSpec:
    node: MermaidNode
    condition: str
    input_nodes: tuple[MermaidNode, ...]
    parameter_nodes: tuple[MermaidNode, ...]
    true_output: MermaidNode
    false_output: MermaidNode
    report_node: MermaidNode


OUTPUT_RE = re.compile(r"^Output\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.+)$")
INPUT_RE = re.compile(r"^Input Port:\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)$")
PARAMETER_RE = re.compile(r"^Parameter:\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)$")
STATE_FENCE_RE = re.compile(r"```mermaid\n(?P<body>.*?)```", re.DOTALL)


def generate_mbd_from_spec(
    spec_path: str | Path,
    *,
    component_name: str,
    parameter_defaults: dict[str, str] | None = None,
    input_defaults: dict[str, str] | None = None,
    output_defaults: dict[str, str] | None = None,
    scenario: str = "",
) -> str:
    spec = Path(spec_path)
    flowchart = parse_spec_design_overview_flowchart(spec)
    transitions = parse_spec_state_diagram(spec)
    requirements = _requirement_ids(spec)
    decisions = _decision_specs(flowchart)
    if not decisions:
        raise SpecMbdAlignmentError(f"no supported decision node found in {spec}")

    parameter_defaults = parameter_defaults or {}
    input_defaults = input_defaults or {}
    output_defaults = output_defaults or {}
    input_names = _ordered_unique(
        _input_name(node) for decision in decisions for node in decision.input_nodes
    )
    parameter_names = _ordered_unique(
        _parameter_name(node) for decision in decisions for node in decision.parameter_nodes
    )
    output_names = _ordered_unique(
        _output_action(decision.true_output)[0] for decision in decisions
    )
    states = _ordered_states(transitions)
    trace_all = " ".join(requirements)
    lines = [
        f"# {_title(spec)}",
        "",
        f"Generated from Spec Mermaid Design Overview in `{spec}`.",
        "This file is deterministic authoring source for generated MBD review artifacts.",
        "",
        "```mbd-component",
        f"component {component_name}",
        f"trace {trace_all}".rstrip(),
        "bus virtual mode=preview wordBits=8",
    ]
    for name in parameter_names:
        lines.append(f"parameter {name}: count = {parameter_defaults.get(name, '0')}")
    lines.append("")
    for name in input_names:
        lines.append(f"port in {name}: count = {input_defaults.get(name, '0')}")
    for name in output_names:
        default = output_defaults.get(name, _default_output_value(decisions, name))
        lines.append(f"port out {name}: {_output_type(decisions, name)} = {default}")
    lines.extend(["```", "", "```mbd-registers"])
    if output_names:
        lines.append("STATUS 0x01 ro 8")
        for index, name in enumerate(output_names):
            reset = "1" if output_defaults.get(name) == "true" else "0"
            lines.append(f"  bit {index} {name} reset={reset}")
    else:
        lines.append("STATUS 0x01 ro 8")
    lines.extend(["```", "", "```mbd-state"])
    if transitions:
        for transition in transitions:
            if transition.source == "[*]":
                continue
            lines.append(
                f"{transition.source} --> {transition.target}: {transition.condition}"
                f"{_trace_suffix(_trace_for_condition(requirements, transition.condition))}"
            )
    else:
        lines.append("note: no state diagram declared in spec")
    lines.extend(["```", "", "```mbd-decomposition"])
    for decision in decisions:
        function = _function_name(decision)
        owns = _ordered_unique(
            [
                _output_action(decision.true_output)[0],
                *[transition.target for transition in transitions if transition.source != "[*]"],
            ]
        )
        inputs = [*[_input_name(node) for node in decision.input_nodes], *[_parameter_name(node) for node in decision.parameter_nodes]]
        lines.append(
            f"function {function}: responsibility=Evaluate {decision.condition} and map decision branches to outputs; "
            f"owns={','.join(owns)}; inputs={','.join(inputs)}; outputs={_output_action(decision.true_output)[0]}; "
            f"trace={','.join(requirements)}"
            f"{'; scenarios=' + scenario if scenario else ''}"
        )
    lines.extend(["```", "", "```mbd-flow"])
    emitted_flows: set[str] = set()
    for decision in decisions:
        function = _function_name(decision)
        for input_node in decision.input_nodes:
            input_name = _input_name(input_node)
            source = _source_for_input(flowchart, input_node.id)
            _append_unique(
                lines,
                emitted_flows,
                f"{source}.{input_name} -> {function}.{input_name}: scenario input{_trace_suffix(requirements[:1])}",
            )
        for parameter_node in decision.parameter_nodes:
            parameter_name = _parameter_name(parameter_node)
            _append_unique(
                lines,
                emitted_flows,
                f"{component_name}.{parameter_name} -> {function}.{parameter_name}: threshold parameter{_trace_suffix(requirements[:2])}",
            )
        output_name = _output_action(decision.true_output)[0]
        _append_unique(
            lines,
            emitted_flows,
            f"{function}.{output_name} -> {component_name}.{output_name}: comparison result{_trace_suffix(requirements[:2])}",
        )
        _append_unique(
            lines,
            emitted_flows,
            f"{component_name}.{output_name} -> {decision.report_node.label}: reported output{_trace_suffix(requirements[-1:])}",
        )
    lines.extend(["```", "", "```mbd-control"])
    for index, decision in enumerate(decisions):
        true_name, true_value = _output_action(decision.true_output)
        false_name, false_value = _output_action(decision.false_output)
        true_state = _state_for_condition(transitions, decision.condition)
        false_condition = _false_condition(transitions, decision.condition)
        false_state = _state_for_condition(transitions, false_condition)
        true_actions = _actions(true_state, true_name, true_value)
        false_actions = _actions(false_state, false_name, false_value)
        function = _function_name(decision)
        true_trace = _trace_for_condition(requirements, decision.condition)
        false_trace = _trace_for_condition(requirements, false_condition)
        lines.append(
            f"priority {10 + index * 20} rule {true_name}_true: owner {function} from * "
            f"when {decision.condition} then {true_actions}{_trace_suffix(true_trace)}"
            f"{' scenarios ' + scenario if scenario else ''}"
        )
        lines.append(
            f"priority {20 + index * 20} rule {false_name}_false: owner {function} from * "
            f"when {false_condition} then {false_actions}{_trace_suffix(false_trace)}"
        )
    lines.extend(["```", "", "```mbd-harness"])
    source_names = _ordered_unique(
        _source_for_input(flowchart, node.id)
        for decision in decisions
        for node in decision.input_nodes
    )
    for source in source_names:
        lines.append(f"device {source} role=source boundary=virtual_ic{_trace_suffix(requirements[:1])}")
    lines.append(f"ecu {component_name} role=controller boundary=hal{_trace_suffix(requirements)}")
    lines.extend(["```", ""])
    return "\n".join(lines)


def parse_spec_state_diagram(path: str | Path) -> list[StateTransitionSpec]:
    spec_path = Path(path)
    for body in _mermaid_bodies(spec_path):
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        if not lines or lines[0] != "stateDiagram-v2":
            continue
        transitions: list[StateTransitionSpec] = []
        for line in lines[1:]:
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


def _decision_specs(flowchart: MermaidFlowchart) -> list[DecisionSpec]:
    specs: list[DecisionSpec] = []
    for node in flowchart.nodes.values():
        if node.shape != "decision":
            continue
        incoming = [edge for edge in flowchart.edges if edge.target_id == node.id]
        outgoing = [edge for edge in flowchart.edges if edge.source_id == node.id]
        input_nodes = tuple(
            flowchart.nodes[edge.source_id]
            for edge in incoming
            if _is_input(flowchart.nodes[edge.source_id])
        )
        parameter_nodes = tuple(
            flowchart.nodes[edge.source_id]
            for edge in incoming
            if _is_parameter(flowchart.nodes[edge.source_id])
        )
        true_output = _branch_output(flowchart, outgoing, "true")
        false_output = _branch_output(flowchart, outgoing, "false")
        report_node = _report_for_outputs(flowchart, [true_output, false_output])
        specs.append(
            DecisionSpec(
                node=node,
                condition=node.label.removesuffix("?").strip(),
                input_nodes=input_nodes,
                parameter_nodes=parameter_nodes,
                true_output=true_output,
                false_output=false_output,
                report_node=report_node,
            )
        )
    return specs


def _branch_output(flowchart: MermaidFlowchart, edges: list[MermaidEdge], label: str) -> MermaidNode:
    for edge in edges:
        if edge.label == label and _is_output(flowchart.nodes[edge.target_id]):
            return flowchart.nodes[edge.target_id]
    raise SpecMbdAlignmentError(f"decision node is missing {label!r} output branch")


def _report_for_outputs(flowchart: MermaidFlowchart, outputs: list[MermaidNode]) -> MermaidNode:
    for output in outputs:
        for edge in flowchart.edges:
            if edge.source_id == output.id and _is_report(flowchart.nodes[edge.target_id]):
                return flowchart.nodes[edge.target_id]
    raise SpecMbdAlignmentError("output actions do not connect to a ScenarioReport endpoint")


def _source_for_input(flowchart: MermaidFlowchart, input_id: str) -> str:
    for edge in flowchart.edges:
        if edge.target_id == input_id:
            source = flowchart.nodes[edge.source_id]
            if not _is_parameter(source):
                return source.label
    return "ScenarioInput"


def _is_input(node: MermaidNode) -> bool:
    return INPUT_RE.match(node.label) is not None


def _is_parameter(node: MermaidNode) -> bool:
    return PARAMETER_RE.match(node.label) is not None


def _is_output(node: MermaidNode) -> bool:
    return OUTPUT_RE.match(node.label) is not None


def _is_report(node: MermaidNode) -> bool:
    return node.label.startswith("ScenarioReport.")


def _input_name(node: MermaidNode) -> str:
    match = INPUT_RE.match(node.label)
    if match is None:
        raise SpecMbdAlignmentError(f"not an input port node: {node.label}")
    return match.group("name")


def _parameter_name(node: MermaidNode) -> str:
    match = PARAMETER_RE.match(node.label)
    if match is None:
        raise SpecMbdAlignmentError(f"not a parameter node: {node.label}")
    return match.group("name")


def _output_action(node: MermaidNode) -> tuple[str, str]:
    match = OUTPUT_RE.match(node.label)
    if match is None:
        raise SpecMbdAlignmentError(f"not an output action node: {node.label}")
    return match.group("name"), match.group("value").strip()


def _function_name(decision: DecisionSpec) -> str:
    return _pascal(decision.node.id)


def _pascal(text: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", text)
    return "".join(part[:1].upper() + part[1:] for part in parts if part) or "Decision"


def _ordered_unique(items) -> list[str]:
    values: list[str] = []
    for item in items:
        if item and item not in values:
            values.append(item)
    return values


def _ordered_states(transitions: list[StateTransitionSpec]) -> list[str]:
    values: list[str] = []
    for transition in transitions:
        for state in [transition.source, transition.target]:
            if state != "[*]" and state not in values:
                values.append(state)
    return values


def _state_for_condition(transitions: list[StateTransitionSpec], condition: str) -> str:
    for transition in transitions:
        if transition.condition == condition:
            return transition.target
    return ""


def _false_condition(transitions: list[StateTransitionSpec], true_condition: str) -> str:
    for transition in transitions:
        if _is_complementary_condition(true_condition, transition.condition):
            return transition.condition
    return "always"


def _is_complementary_condition(first: str, second: str) -> bool:
    first_match = re.fullmatch(r"(.+?)\s*(>=|<=|>|<|==|!=)\s*(.+)", first)
    second_match = re.fullmatch(r"(.+?)\s*(>=|<=|>|<|==|!=)\s*(.+)", second)
    if first_match is None or second_match is None:
        return False
    if first_match.group(1).strip() != second_match.group(1).strip():
        return False
    if first_match.group(3).strip() != second_match.group(3).strip():
        return False
    return (first_match.group(2), second_match.group(2)) in {
        (">=", "<"),
        ("<", ">="),
        (">", "<="),
        ("<=", ">"),
        ("==", "!="),
        ("!=", "=="),
    }


def _actions(state: str, output_name: str, output_value: str) -> str:
    actions = []
    if state:
        actions.append(f"state={state}")
    actions.append(f"{output_name}={output_value}")
    return ", ".join(actions)


def _trace_for_condition(requirements: list[str], condition: str) -> list[str]:
    if not requirements:
        return []
    if ">=" in condition or ">" in condition or "== true" in condition:
        return _ordered_unique([requirements[0], requirements[-1]])
    if len(requirements) > 1:
        return _ordered_unique([requirements[1], requirements[-1]])
    return requirements


def _trace_suffix(requirements: list[str]) -> str:
    return f" trace {' '.join(requirements)}" if requirements else ""


def _default_output_value(decisions: list[DecisionSpec], output_name: str) -> str:
    for decision in decisions:
        name, value = _output_action(decision.false_output)
        if name == output_name:
            return value
    return "false"


def _output_type(decisions: list[DecisionSpec], output_name: str) -> str:
    values = []
    for decision in decisions:
        for node in [decision.true_output, decision.false_output]:
            name, value = _output_action(node)
            if name == output_name:
                values.append(value)
    return "bool" if all(value in {"true", "false"} for value in values) else "count"


def _append_unique(lines: list[str], emitted: set[str], line: str) -> None:
    if line in emitted:
        return
    emitted.add(line)
    lines.append(line)


def _title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return path.stem


def _requirement_ids(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return _ordered_unique(re.findall(r"^-\s+`([^`]+)`:", text, re.MULTILINE))


def _mermaid_bodies(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [match.group("body").strip() for match in STATE_FENCE_RE.finditer(text)]
