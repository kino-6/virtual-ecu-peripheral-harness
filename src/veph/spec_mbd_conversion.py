from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from veph.spec_dataflow import (
    ArithmeticBlockSpec,
    arithmetic_expressions,
    arithmetic_specs,
    block_output_signal,
    output_expression,
    targets_for_node,
)
from veph.spec_mbd_labels import (
    constant_name as _constant_name,
    constant_value as _constant_value,
    input_name as _input_name,
    is_arithmetic as _is_arithmetic,
    is_constant as _is_constant,
    is_input as _is_input,
    is_output as _is_output,
    is_output_port as _is_output_port,
    is_parameter as _is_parameter,
    is_report as _is_report,
    node_port_type as _node_port_type,
    output_action as _output_action,
    output_port_name as _output_port_name,
    parameter_name as _parameter_name,
)
from veph.spec_mbd_flow_helpers import (
    report_for_output_node as _report_for_output_node,
    source_for_input as _source_for_input,
    state_machine_function_name as _state_machine_function_name,
    trace_for_parameter as _trace_for_parameter,
)
from veph.spec_mbd_text import (
    append_unique as _append_unique,
    display_path as _display_path,
    format_actions as _format_actions,
    ordered_states as _ordered_states,
    ordered_unique as _ordered_unique,
    requirement_ids as _requirement_ids,
    requirement_texts as _requirement_texts,
    title as _title,
    trace_suffix as _trace_suffix,
)
from veph.spec_state_mbd_generation import generate_state_machine_mbd_from_spec
from veph.spec_state_model import (
    StateTransitionSpec,
    parse_spec_state_diagram,
)
from veph.spec_mbd_alignment import (
    MermaidEdge,
    MermaidFlowchart,
    MermaidNode,
    SpecMbdAlignmentError,
    parse_spec_design_overview_flowchart,
)


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
        arithmetic_blocks = arithmetic_specs(flowchart)
        if arithmetic_blocks:
            return _generate_arithmetic_dataflow_mbd_from_spec(
                spec,
                flowchart=flowchart,
                blocks=arithmetic_blocks,
                requirements=requirements,
                component_name=component_name,
                parameter_defaults=parameter_defaults or {},
                input_defaults=input_defaults or {},
                output_defaults=output_defaults or {},
                scenario=scenario,
            )
        if transitions:
            return generate_state_machine_mbd_from_spec(
                spec,
                flowchart=flowchart,
                transitions=transitions,
                requirements=requirements,
                component_name=component_name,
                parameter_defaults=parameter_defaults or {},
                input_defaults=input_defaults or {},
                output_defaults=output_defaults or {},
                scenario=scenario,
                generated_header=_generated_header(spec, "Spec Mermaid Design Overview and stateDiagram-v2"),
                component_header=_component_header(component_name, " ".join(requirements)),
            )
        raise SpecMbdAlignmentError(f"no supported decision or state-machine node found in {spec}")

    parameter_defaults = parameter_defaults or {}
    input_defaults = input_defaults or {}
    output_defaults = output_defaults or {}
    input_names = _ordered_unique(
        _input_name(node) for decision in decisions for node in decision.input_nodes
    )
    all_input_nodes = [node for decision in decisions for node in decision.input_nodes]
    parameter_names = _ordered_unique(
        [
            *(_parameter_name(node) for decision in decisions for node in decision.parameter_nodes),
            *(_constant_name(node) for decision in decisions for node in decision.constant_nodes),
        ]
    )
    output_names = _ordered_unique(
        _output_action(decision.true_output)[0] for decision in decisions
    )
    states = _ordered_states(transitions)
    trace_all = " ".join(requirements)
    lines = [
        *_generated_header(spec, "Spec Mermaid Design Overview"),
        *_component_header(component_name, trace_all),
    ]
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
        for constant_node in decision.constant_nodes:
            constant_name = _constant_name(constant_node)
            _append_unique(
                lines,
                emitted_flows,
                f"{component_name}.{constant_name} -> {function}.{constant_name}: constant value{_trace_suffix(requirements[:2])}",
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


def _generate_arithmetic_dataflow_mbd_from_spec(
    spec: Path,
    *,
    flowchart: MermaidFlowchart,
    blocks: list[ArithmeticBlockSpec],
    requirements: list[str],
    component_name: str,
    parameter_defaults: dict[str, str],
    input_defaults: dict[str, str],
    output_defaults: dict[str, str],
    scenario: str,
) -> str:
    input_nodes = [node for node in flowchart.nodes.values() if _is_input(node)]
    parameter_nodes = [node for node in flowchart.nodes.values() if _is_parameter(node)]
    constant_nodes = [node for node in flowchart.nodes.values() if _is_constant(node)]
    output_nodes = [node for node in flowchart.nodes.values() if _is_output_port(node)]
    if not input_nodes:
        raise SpecMbdAlignmentError(f"arithmetic dataflow spec has no Input Port nodes in {spec}")
    if not output_nodes:
        raise SpecMbdAlignmentError(f"arithmetic dataflow spec has no Output nodes in {spec}")
    block_expressions = arithmetic_expressions(flowchart, blocks)
    output_expressions = {
        _output_port_name(node): output_expression(flowchart, node, block_expressions)
        for node in output_nodes
    }
    input_names = [_input_name(node) for node in input_nodes]
    parameter_names = [
        *[_parameter_name(node) for node in parameter_nodes],
        *[_constant_name(node) for node in constant_nodes],
    ]
    output_names = [_output_port_name(node) for node in output_nodes]
    trace_all = " ".join(requirements)
    lines = [
        *_generated_header(spec, "Spec Mermaid Design Overview"),
        *_component_header(component_name, trace_all),
    ]
    for name in parameter_names:
        lines.append(
            f"parameter {name}: count = {_dataflow_parameter_default(parameter_nodes, constant_nodes, parameter_defaults, name)}"
        )
    lines.append("")
    for name in input_names:
        default = input_defaults.get(name, "0")
        node = next(node for node in input_nodes if _input_name(node) == name)
        lines.append(f"port in {name}: {_node_port_type(node, default)} = {default}")
    for name in output_names:
        default = output_defaults.get(name, "0")
        node = next(node for node in output_nodes if _output_port_name(node) == name)
        lines.append(f"port out {name}: {_node_port_type(node, default)} = {default}")
    lines.extend(["```", "", "```mbd-registers", "STATUS 0x01 ro 8"])
    for index, name in enumerate(output_names):
        lines.append(f"  bit {index} {name} reset={output_defaults.get(name, '0')}")
    lines.extend(
        [
            "```",
            "",
            "```mbd-state",
            "note: no state machine; this sample reviews arithmetic data flow",
            "```",
            "",
            "```mbd-decomposition",
        ]
    )
    for block in blocks:
        lines.append(
            f"function {block.node.label}: responsibility=Compute {block.output_signal} with {block.operator}; "
            f"owns={block.output_signal}; inputs={','.join(block.input_signals)}; outputs={block.output_signal}; "
            f"trace={','.join(requirements)}"
            f"{'; scenarios=' + scenario if scenario else ''}"
        )
    lines.extend(["```", "", "```mbd-flow"])
    emitted_flows: set[str] = set()
    for node in input_nodes:
        name = _input_name(node)
        source = _source_for_input(flowchart, node.id)
        for target in targets_for_node(flowchart, node.id):
            if _is_arithmetic(flowchart.nodes[target]):
                _append_unique(
                    lines,
                    emitted_flows,
                    f"{source}.{name} -> {flowchart.nodes[target].label}.{name}: {name}{_trace_suffix(requirements[:1])}",
                )
    for node in parameter_nodes:
        name = _parameter_name(node)
        for target in targets_for_node(flowchart, node.id):
            if _is_arithmetic(flowchart.nodes[target]):
                _append_unique(
                    lines,
                    emitted_flows,
                    f"{component_name}.{name} -> {flowchart.nodes[target].label}.{name}: {name}{_trace_suffix(requirements[:2])}",
                )
    for node in constant_nodes:
        name = _constant_name(node)
        for target in targets_for_node(flowchart, node.id):
            if _is_arithmetic(flowchart.nodes[target]):
                _append_unique(
                    lines,
                    emitted_flows,
                    f"{component_name}.{name} -> {flowchart.nodes[target].label}.{name}: constant value{_trace_suffix(requirements[:2])}",
                )
    for edge in flowchart.edges:
        source_node = flowchart.nodes[edge.source_id]
        target_node = flowchart.nodes[edge.target_id]
        if _is_arithmetic(source_node) and _is_arithmetic(target_node):
            signal = edge.label or block_output_signal(blocks, source_node.id)
            _append_unique(
                lines,
                emitted_flows,
                f"{source_node.label}.{signal} -> {target_node.label}.{signal}: {signal}{_trace_suffix(requirements[:3])}",
            )
        if _is_arithmetic(source_node) and _is_output_port(target_node):
            output_name = _output_port_name(target_node)
            _append_unique(
                lines,
                emitted_flows,
                f"{source_node.label}.{output_name} -> {component_name}.{output_name}: arithmetic output{_trace_suffix(requirements[:3])}",
            )
    for node in output_nodes:
        name = _output_port_name(node)
        report = _report_for_output_node(flowchart, node.id)
        _append_unique(
            lines,
            emitted_flows,
            f"{component_name}.{name} -> {report}: reported {name}{_trace_suffix(requirements[-1:])}",
        )
    lines.extend(["```", "", "```mbd-control"])
    for index, name in enumerate(output_names):
        lines.append(
            f"priority {10 + index * 10} rule compute_{name}: owner ArithmeticDataflow from * "
            f"when always then {name}={output_expressions[name]}{_trace_suffix(requirements)}"
            f"{' scenarios ' + scenario if scenario else ''}"
        )
    lines.extend(["```", "", "```mbd-harness"])
    for source in _ordered_unique(_source_for_input(flowchart, node.id) for node in input_nodes):
        lines.append(f"device {source} role=source boundary=virtual_ic{_trace_suffix(requirements[:1])}")
    lines.append(f"ecu {component_name} role=controller boundary=hal{_trace_suffix(requirements)}")
    lines.extend(["```", ""])
    return "\n".join(lines)


def _generated_header(spec: Path, source_description: str) -> list[str]:
    return [
        f"# {_title(spec)}",
        "",
        f"Generated from {source_description} in `{_display_path(spec)}`.",
        "This file is deterministic authoring source for generated MBD review artifacts.",
        "",
    ]


def _component_header(component_name: str, trace_all: str) -> list[str]:
    return [
        "```mbd-component",
        f"component {component_name}",
        f"trace {trace_all}".rstrip(),
        "bus virtual mode=preview wordBits=8",
    ]


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


def _dataflow_parameter_default(
    parameter_nodes: list[MermaidNode],
    constant_nodes: list[MermaidNode],
    parameter_defaults: dict[str, str],
    name: str,
) -> str:
    if name in parameter_defaults:
        return parameter_defaults[name]
    for node in constant_nodes:
        if _constant_name(node) == name:
            return _constant_value(node)
    for node in parameter_nodes:
        if _parameter_name(node) == name:
            return "0"
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
        return _ordered_unique([requirements[0], requirements[-1]])
    if len(requirements) > 1:
        return _ordered_unique([requirements[1], requirements[-1]])
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
