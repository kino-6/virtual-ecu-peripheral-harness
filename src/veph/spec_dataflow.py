from __future__ import annotations

from dataclasses import dataclass

from veph.spec_mbd_alignment import MermaidEdge, MermaidFlowchart, MermaidNode, SpecMbdAlignmentError
from veph.spec_mbd_labels import (
    constant_name,
    input_name,
    is_arithmetic,
    is_constant,
    is_input,
    is_output_port,
    is_parameter,
    operator_label,
    output_port_name,
    parameter_name,
)


@dataclass(frozen=True)
class ArithmeticBlockSpec:
    node: MermaidNode
    operator: str
    output_signal: str
    input_signals: tuple[str, ...]


def arithmetic_specs(flowchart: MermaidFlowchart) -> list[ArithmeticBlockSpec]:
    specs: list[ArithmeticBlockSpec] = []
    for node in flowchart.nodes.values():
        if not is_arithmetic(node):
            continue
        incoming = [edge for edge in flowchart.edges if edge.target_id == node.id]
        input_signals = tuple(_signal_for_edge_source(flowchart, edge) for edge in incoming)
        output_signal = _arithmetic_output_signal(flowchart, node.id)
        specs.append(
            ArithmeticBlockSpec(
                node=node,
                operator=operator_label(node),
                output_signal=output_signal,
                input_signals=input_signals,
            )
        )
    return specs


def arithmetic_expressions(
    flowchart: MermaidFlowchart,
    blocks: list[ArithmeticBlockSpec],
) -> dict[str, str]:
    expressions: dict[str, str] = {}
    pending = list(blocks)
    while pending:
        progressed = False
        for block in list(pending):
            terms: list[str] = []
            for edge in [edge for edge in flowchart.edges if edge.target_id == block.node.id]:
                source = flowchart.nodes[edge.source_id]
                if is_arithmetic(source):
                    signal = edge.label or _block_output_signal(blocks, source.id)
                    if signal not in expressions:
                        break
                    terms.append(expressions[signal])
                else:
                    terms.append(_signal_for_edge_source(flowchart, edge))
            else:
                expressions[block.output_signal] = _format_arithmetic_expression(block.operator, terms)
                pending.remove(block)
                progressed = True
        if not progressed:
            unresolved = ", ".join(block.node.id for block in pending)
            raise SpecMbdAlignmentError(f"arithmetic dataflow has unresolved or cyclic blocks: {unresolved}")
    return expressions


def output_expression(
    flowchart: MermaidFlowchart,
    output_node: MermaidNode,
    block_expressions: dict[str, str],
) -> str:
    incoming = [edge for edge in flowchart.edges if edge.target_id == output_node.id]
    if len(incoming) != 1:
        raise SpecMbdAlignmentError(f"output node must have exactly one arithmetic source: {output_node.label}")
    source = flowchart.nodes[incoming[0].source_id]
    if not is_arithmetic(source):
        return _signal_for_edge_source(flowchart, incoming[0])
    signal = incoming[0].label or output_port_name(output_node)
    if signal in block_expressions:
        return block_expressions[signal]
    produced = next(
        (value for key, value in block_expressions.items() if key == output_port_name(output_node)),
        "",
    )
    if produced:
        return produced
    candidates = list(block_expressions.values())
    if len(candidates) == 1:
        return candidates[0]
    output_name = output_port_name(output_node)
    for edge in flowchart.edges:
        if edge.source_id == source.id:
            signal = edge.label or output_name
            if signal in block_expressions:
                return block_expressions[signal]
    raise SpecMbdAlignmentError(f"could not derive expression for output {output_node.label}")


def targets_for_node(flowchart: MermaidFlowchart, node_id: str) -> list[str]:
    return [edge.target_id for edge in flowchart.edges if edge.source_id == node_id]


def block_output_signal(blocks: list[ArithmeticBlockSpec], node_id: str) -> str:
    return _block_output_signal(blocks, node_id)


def _format_arithmetic_expression(operator: str, terms: list[str]) -> str:
    if len(terms) < 2:
        raise SpecMbdAlignmentError(f"{operator} block requires at least two input signals")
    if operator == "Sum":
        return " + ".join(_parenthesize_term(term) for term in terms)
    if operator in {"Gain", "Product"}:
        return " * ".join(_parenthesize_term(term) for term in terms)
    if operator == "Saturation":
        value = next((term for term in terms if "limit" not in term.lower()), terms[0])
        lower = next((term for term in terms if any(key in term.lower() for key in ["lower", "min"])), "")
        upper = next((term for term in terms if any(key in term.lower() for key in ["upper", "max"])), "")
        if not lower or not upper:
            raise SpecMbdAlignmentError("Saturation block requires lower/min and upper/max signals")
        return f"clamp({value}, {lower}, {upper})"
    if operator == "Lookup1D":
        table = next((term for term in terms if "table" in term.lower()), "")
        value = next((term for term in terms if term != table), "")
        if not table or not value:
            raise SpecMbdAlignmentError("Lookup1D block requires a value signal and table signal")
        return f"lookup1d({value}, {table})"
    raise SpecMbdAlignmentError(f"unsupported arithmetic operator: {operator}")


def _parenthesize_term(term: str) -> str:
    if " + " in term or " - " in term:
        return f"({term})"
    return term


def _arithmetic_output_signal(flowchart: MermaidFlowchart, node_id: str) -> str:
    outgoing = [edge for edge in flowchart.edges if edge.source_id == node_id]
    if len(outgoing) != 1:
        raise SpecMbdAlignmentError(f"arithmetic block {node_id} must have exactly one outgoing signal")
    target = flowchart.nodes[outgoing[0].target_id]
    if outgoing[0].label:
        return outgoing[0].label
    if is_output_port(target):
        return output_port_name(target)
    raise SpecMbdAlignmentError(f"arithmetic block {node_id} outgoing edge must label its signal")


def _block_output_signal(blocks: list[ArithmeticBlockSpec], node_id: str) -> str:
    for block in blocks:
        if block.node.id == node_id:
            return block.output_signal
    raise SpecMbdAlignmentError(f"unknown arithmetic block: {node_id}")


def _signal_for_edge_source(flowchart: MermaidFlowchart, edge: MermaidEdge) -> str:
    source = flowchart.nodes[edge.source_id]
    if edge.label:
        return edge.label
    if is_input(source):
        return input_name(source)
    if is_parameter(source):
        return parameter_name(source)
    if is_constant(source):
        return constant_name(source)
    if is_arithmetic(source):
        return _arithmetic_output_signal(flowchart, source.id)
    raise SpecMbdAlignmentError(f"edge into arithmetic block lacks a signal label from {source.label}")
