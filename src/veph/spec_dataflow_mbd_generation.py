from __future__ import annotations

from pathlib import Path

from veph.spec_dataflow import (
    ArithmeticBlockSpec,
    arithmetic_expressions,
    block_output_signal,
    output_expression,
    targets_for_node,
)
from veph.spec_mbd_alignment import MermaidFlowchart, SpecMbdAlignmentError
from veph.spec_mbd_flow_helpers import report_for_output_node, source_for_input
from veph.spec_mbd_labels import (
    constant_name as _constant_name,
    constant_value as _constant_value,
    input_name as _input_name,
    is_arithmetic as _is_arithmetic,
    is_constant as _is_constant,
    is_input as _is_input,
    is_output_port as _is_output_port,
    is_parameter as _is_parameter,
    node_port_type as _node_port_type,
    output_port_name as _output_port_name,
    parameter_name as _parameter_name,
)
from veph.spec_mbd_text import append_unique, ordered_unique, trace_suffix


def generate_arithmetic_dataflow_mbd_from_spec(
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
    generated_header: list[str],
    component_header: list[str],
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
    lines = [*generated_header, *component_header]
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
        source = source_for_input(flowchart, node.id)
        for target in targets_for_node(flowchart, node.id):
            if _is_arithmetic(flowchart.nodes[target]):
                append_unique(
                    lines,
                    emitted_flows,
                    f"{source}.{name} -> {flowchart.nodes[target].label}.{name}: {name}{trace_suffix(requirements[:1])}",
                )
    for node in parameter_nodes:
        name = _parameter_name(node)
        for target in targets_for_node(flowchart, node.id):
            if _is_arithmetic(flowchart.nodes[target]):
                append_unique(
                    lines,
                    emitted_flows,
                    f"{component_name}.{name} -> {flowchart.nodes[target].label}.{name}: {name}{trace_suffix(requirements[:2])}",
                )
    for node in constant_nodes:
        name = _constant_name(node)
        for target in targets_for_node(flowchart, node.id):
            if _is_arithmetic(flowchart.nodes[target]):
                append_unique(
                    lines,
                    emitted_flows,
                    f"{component_name}.{name} -> {flowchart.nodes[target].label}.{name}: constant value{trace_suffix(requirements[:2])}",
                )
    for edge in flowchart.edges:
        source_node = flowchart.nodes[edge.source_id]
        target_node = flowchart.nodes[edge.target_id]
        if _is_arithmetic(source_node) and _is_arithmetic(target_node):
            signal = edge.label or block_output_signal(blocks, source_node.id)
            append_unique(
                lines,
                emitted_flows,
                f"{source_node.label}.{signal} -> {target_node.label}.{signal}: {signal}{trace_suffix(requirements[:3])}",
            )
        if _is_arithmetic(source_node) and _is_output_port(target_node):
            output_name = _output_port_name(target_node)
            append_unique(
                lines,
                emitted_flows,
                f"{source_node.label}.{output_name} -> {component_name}.{output_name}: arithmetic output{trace_suffix(requirements[:3])}",
            )
    for node in output_nodes:
        name = _output_port_name(node)
        report = report_for_output_node(flowchart, node.id)
        append_unique(
            lines,
            emitted_flows,
            f"{component_name}.{name} -> {report}: reported {name}{trace_suffix(requirements[-1:])}",
        )
    lines.extend(["```", "", "```mbd-control"])
    for index, name in enumerate(output_names):
        lines.append(
            f"priority {10 + index * 10} rule compute_{name}: owner ArithmeticDataflow from * "
            f"when always then {name}={output_expressions[name]}{trace_suffix(requirements)}"
            f"{' scenarios ' + scenario if scenario else ''}"
        )
    lines.extend(["```", "", "```mbd-harness"])
    for source in ordered_unique(source_for_input(flowchart, node.id) for node in input_nodes):
        lines.append(f"device {source} role=source boundary=virtual_ic{trace_suffix(requirements[:1])}")
    lines.append(f"ecu {component_name} role=controller boundary=hal{trace_suffix(requirements)}")
    lines.extend(["```", ""])
    return "\n".join(lines)


def _dataflow_parameter_default(
    parameter_nodes,
    constant_nodes,
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
