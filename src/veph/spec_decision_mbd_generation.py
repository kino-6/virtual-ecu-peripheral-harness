from __future__ import annotations

import re
from dataclasses import dataclass

from veph.spec_mbd_alignment import MermaidEdge, MermaidFlowchart, MermaidNode, SpecMbdAlignmentError
from veph.spec_mbd_flow_helpers import source_for_input
from veph.spec_mbd_labels import (
    constant_name as _constant_name,
    constant_value as _constant_value,
    input_name as _input_name,
    is_constant as _is_constant,
    is_input as _is_input,
    is_output as _is_output,
    is_parameter as _is_parameter,
    is_report as _is_report,
    node_port_type as _node_port_type,
    output_action as _output_action,
    parameter_name as _parameter_name,
)
from veph.spec_mbd_text import append_unique, ordered_states, ordered_unique, trace_suffix
from veph.spec_state_model import StateTransitionSpec


@dataclass(frozen=True)
class DecisionSpec:
    node: MermaidNode
    condition: str
    input_nodes: tuple[MermaidNode, ...]
    parameter_nodes: tuple[MermaidNode, ...]
    constant_nodes: tuple[MermaidNode, ...]
    true_output: MermaidNode
    false_output: MermaidNode
    report_node: MermaidNode


def decision_specs(flowchart: MermaidFlowchart) -> list[DecisionSpec]:
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
        constant_nodes = tuple(
            flowchart.nodes[edge.source_id]
            for edge in incoming
            if _is_constant(flowchart.nodes[edge.source_id])
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
                constant_nodes=constant_nodes,
                true_output=true_output,
                false_output=false_output,
                report_node=report_node,
            )
        )
    return specs


def generate_decision_mbd_from_spec(
    *,
    flowchart: MermaidFlowchart,
    transitions: list[StateTransitionSpec],
    requirements: list[str],
    decisions: list[DecisionSpec],
    component_name: str,
    parameter_defaults: dict[str, str],
    input_defaults: dict[str, str],
    output_defaults: dict[str, str],
    scenario: str,
    generated_header: list[str],
    component_header: list[str],
) -> str:
    input_names = ordered_unique(
        _input_name(node) for decision in decisions for node in decision.input_nodes
    )
    all_input_nodes = [node for decision in decisions for node in decision.input_nodes]
    parameter_names = ordered_unique(
        [
            *(_parameter_name(node) for decision in decisions for node in decision.parameter_nodes),
            *(_constant_name(node) for decision in decisions for node in decision.constant_nodes),
        ]
    )
    output_names = ordered_unique(
        _output_action(decision.true_output)[0] for decision in decisions
    )
    lines = [*generated_header, *component_header]
    for name in parameter_names:
        lines.append(f"parameter {name}: count = {_parameter_default(decisions, parameter_defaults, name)}")
    lines.append("")
    for name in input_names:
        default = input_defaults.get(name, "0")
        node = next(node for node in all_input_nodes if _input_name(node) == name)
        lines.append(f"port in {name}: {_node_port_type(node, default)} = {default}")
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
                f"{trace_suffix(_trace_for_condition(requirements, transition.condition))}"
            )
    else:
        lines.append("note: no state diagram declared in spec")
    lines.extend(["```", "", "```mbd-decomposition"])
    for decision in decisions:
        function = _function_name(decision)
        owns = ordered_unique(
            [
                _output_action(decision.true_output)[0],
                *[transition.target for transition in transitions if transition.source != "[*]"],
            ]
        )
        inputs = [
            *[_input_name(node) for node in decision.input_nodes],
            *[_parameter_name(node) for node in decision.parameter_nodes],
            *[_constant_name(node) for node in decision.constant_nodes],
        ]
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
            source = source_for_input(flowchart, input_node.id)
            append_unique(
                lines,
                emitted_flows,
                f"{source}.{input_name} -> {function}.{input_name}: scenario input{trace_suffix(requirements[:1])}",
            )
        for parameter_node in decision.parameter_nodes:
            parameter_name = _parameter_name(parameter_node)
            append_unique(
                lines,
                emitted_flows,
                f"{component_name}.{parameter_name} -> {function}.{parameter_name}: threshold parameter{trace_suffix(requirements[:2])}",
            )
        for constant_node in decision.constant_nodes:
            constant_name = _constant_name(constant_node)
            append_unique(
                lines,
                emitted_flows,
                f"{component_name}.{constant_name} -> {function}.{constant_name}: constant value{trace_suffix(requirements[:2])}",
            )
        output_name = _output_action(decision.true_output)[0]
        append_unique(
            lines,
            emitted_flows,
            f"{function}.{output_name} -> {component_name}.{output_name}: comparison result{trace_suffix(requirements[:2])}",
        )
        append_unique(
            lines,
            emitted_flows,
            f"{component_name}.{output_name} -> {decision.report_node.label}: reported output{trace_suffix(requirements[-1:])}",
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
            f"when {decision.condition} then {true_actions}{trace_suffix(true_trace)}"
            f"{' scenarios ' + scenario if scenario else ''}"
        )
        lines.append(
            f"priority {20 + index * 20} rule {false_name}_false: owner {function} from * "
            f"when {false_condition} then {false_actions}{trace_suffix(false_trace)}"
        )
    lines.extend(["```", "", "```mbd-harness"])
    source_names = ordered_unique(
        source_for_input(flowchart, node.id)
        for decision in decisions
        for node in decision.input_nodes
    )
    for source in source_names:
        lines.append(f"device {source} role=source boundary=virtual_ic{trace_suffix(requirements[:1])}")
    lines.append(f"ecu {component_name} role=controller boundary=hal{trace_suffix(requirements)}")
    lines.extend(["```", ""])
    return "\n".join(lines)


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


def _parameter_default(
    decisions: list[DecisionSpec],
    parameter_defaults: dict[str, str],
    name: str,
) -> str:
    if name in parameter_defaults:
        return parameter_defaults[name]
    for decision in decisions:
        for node in decision.constant_nodes:
            if _constant_name(node) == name:
                return _constant_value(node)
    return "0"


def _function_name(decision: DecisionSpec) -> str:
    return _pascal(decision.node.id)


def _pascal(text: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", text)
    return "".join(part[:1].upper() + part[1:] for part in parts if part) or "Decision"


def _state_for_condition(transitions: list[StateTransitionSpec], condition: str) -> str:
    for transition in transitions:
        if transition.condition == condition:
            return transition.target
    return ""


def _false_condition(transitions: list[StateTransitionSpec], true_condition: str) -> str:
    for transition in transitions:
        if _is_complementary_condition(true_condition, transition.condition):
            return transition.condition
    complement = _complement_condition(true_condition)
    if complement:
        return complement
    return "always"


def _complement_condition(condition: str) -> str:
    if " or " in condition:
        complements = [_complement_condition(part.strip()) for part in condition.split(" or ")]
        if all(complements):
            return " and ".join(complements)
    if " and " in condition:
        complements = [_complement_condition(part.strip()) for part in condition.split(" and ")]
        if all(complements):
            return " or ".join(complements)
    if condition.startswith("not "):
        return condition.removeprefix("not ").strip()
    match = re.fullmatch(r"(.+?)\s*(>=|<=|>|<|==|!=)\s*(.+)", condition)
    if match is None:
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", condition):
            return f"not {condition}"
        return ""
    left = match.group(1).strip()
    operator = match.group(2)
    right = match.group(3).strip()
    complement = {
        ">=": "<",
        "<": ">=",
        ">": "<=",
        "<=": ">",
        "==": "!=",
        "!=": "==",
    }[operator]
    return f"{left} {complement} {right}"


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
        return ordered_unique([requirements[0], requirements[-1]])
    if len(requirements) > 1:
        return ordered_unique([requirements[1], requirements[-1]])
    return requirements


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
