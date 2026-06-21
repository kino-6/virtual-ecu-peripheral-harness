from __future__ import annotations

from veph.spec_mbd_alignment import MermaidFlowchart, MermaidNode, SpecMbdAlignmentError
from veph.spec_mbd_labels import (
    is_parameter as _is_parameter,
    is_report as _is_report,
    output_port_name as _output_port_name,
)


def report_for_output_node(flowchart: MermaidFlowchart, output_id: str) -> str:
    for edge in flowchart.edges:
        if edge.source_id == output_id and _is_report(flowchart.nodes[edge.target_id]):
            return flowchart.nodes[edge.target_id].label
    return "ScenarioReport.observedBehavior"


def source_for_input(flowchart: MermaidFlowchart, input_id: str) -> str:
    for edge in flowchart.edges:
        if edge.target_id == input_id:
            source = flowchart.nodes[edge.source_id]
            if not _is_parameter(source):
                return source.label
    return "ScenarioInput"


def state_machine_function_name(
    flowchart: MermaidFlowchart,
    input_nodes: list[MermaidNode],
    output_nodes: list[MermaidNode],
) -> str:
    input_ids = {node.id for node in input_nodes}
    output_ids = {node.id for node in output_nodes}
    candidates: list[str] = []
    for node in flowchart.nodes.values():
        if node.id in input_ids or node.id in output_ids:
            continue
        if _is_parameter(node) or _is_report(node):
            continue
        incoming_from_inputs = any(
            edge.target_id == node.id and edge.source_id in input_ids for edge in flowchart.edges
        )
        outgoing_to_outputs = any(
            edge.source_id == node.id and edge.target_id in output_ids for edge in flowchart.edges
        )
        if incoming_from_inputs and outgoing_to_outputs:
            candidates.append(node.label)
    if len(candidates) != 1:
        raise SpecMbdAlignmentError(
            "state-machine Design Overview must have exactly one controller node between inputs and outputs"
        )
    return candidates[0]


def trace_for_parameter(requirements: list[str], parameter_name: str) -> list[str]:
    if "on" in parameter_name.lower():
        return requirements[:1]
    if "off" in parameter_name.lower():
        return requirements[1:2] or requirements[:1]
    return requirements[:2]
