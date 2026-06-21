from __future__ import annotations

import re

from veph.control_semantics import (
    expression_variables,
    find_threshold_pair,
    primary_condition_terms,
    primary_output_action,
    report_for_signal,
    source_for_signal,
)
from veph.ir import ControlRuleIR, MbdModelIR
from veph.spec_mbd_alignment import SemanticEdge, SemanticGraph, SpecMbdAlignmentError


def semantic_graph_from_mbd(model: MbdModelIR) -> SemanticGraph:
    pair = find_threshold_pair(model.controls)
    if pair is None:
        decision_graph = _decision_graph_from_controls(model)
        if decision_graph is not None:
            return decision_graph
        return _generic_flow_graph_from_mbd(model)
    true_rule, false_rule = pair
    primary_input, primary_parameter = primary_condition_terms(model, true_rule.condition_expr)
    source = source_for_signal(model.flows, primary_input) or "ScenarioInput"
    output_name = primary_output_action(model, true_rule) or primary_output_action(model, false_rule)
    if not output_name:
        raise SpecMbdAlignmentError("MBD semantic graph could not find an output port action")
    report = report_for_signal(model.flows, output_name) or "ScenarioReport.observedBehavior"
    condition = f"{true_rule.condition}?"
    true_output = _output_action_label(model, true_rule)
    false_output = _output_action_label(model, false_rule)
    nodes = {
        source,
        f"Input Port: {primary_input or 'input'}",
        condition,
        true_output,
        false_output,
        report,
    }
    edges = {
        SemanticEdge(source, primary_input or "input", f"Input Port: {primary_input or 'input'}"),
        SemanticEdge(f"Input Port: {primary_input or 'input'}", "", condition),
        SemanticEdge(condition, "true", true_output),
        SemanticEdge(condition, "false", false_output),
        SemanticEdge(true_output, "", report),
        SemanticEdge(false_output, "", report),
    }
    for parameter in _decision_parameter_names(model, true_rule, false_rule, primary_parameter):
        parameter_label = _parameter_semantic_label(model, parameter)
        nodes.add(parameter_label)
        edges.add(SemanticEdge(parameter_label, "", condition))
    return SemanticGraph(nodes=frozenset(nodes), edges=frozenset(edges))


def _decision_graph_from_controls(model: MbdModelIR) -> SemanticGraph | None:
    controls = sorted(
        [control for control in model.controls if control.state_scope == "*"],
        key=lambda item: (item.priority, item.name),
    )
    if len(controls) < 2:
        return None
    true_rule = controls[0]
    false_rule = controls[1]
    output_name = primary_output_action(model, true_rule) or primary_output_action(model, false_rule)
    if not output_name:
        return None
    condition = f"{true_rule.condition}?"
    report = report_for_signal(model.flows, output_name) or "ScenarioReport.observedBehavior"
    true_output = _output_action_label(model, true_rule)
    false_output = _output_action_label(model, false_rule)
    nodes = {condition, true_output, false_output, report}
    edges = {
        SemanticEdge(condition, "true", true_output),
        SemanticEdge(condition, "false", false_output),
        SemanticEdge(true_output, "", report),
        SemanticEdge(false_output, "", report),
    }
    for variable in expression_variables(true_rule.condition_expr):
        if variable in model.ports and model.ports[variable].direction == "in":
            source = source_for_signal(model.flows, variable) or "ScenarioInput"
            input_label = f"Input Port: {variable}"
            nodes.update({source, input_label})
            edges.add(SemanticEdge(source, variable, input_label))
            edges.add(SemanticEdge(input_label, "", condition))
        elif variable in model.component.parameters:
            parameter_label = _parameter_semantic_label(model, variable)
            nodes.add(parameter_label)
            edges.add(SemanticEdge(parameter_label, "", condition))
    return SemanticGraph(nodes=frozenset(nodes), edges=frozenset(edges))


def _decision_parameter_names(
    model: MbdModelIR,
    true_rule: ControlRuleIR,
    false_rule: ControlRuleIR,
    primary_parameter: str,
) -> list[str]:
    names: list[str] = []
    if primary_parameter:
        names.append(primary_parameter)
    for rule in (true_rule, false_rule):
        for value in rule.actions.values():
            if value in model.component.parameters and value not in names:
                names.append(value)
    return names


def _generic_flow_graph_from_mbd(model: MbdModelIR) -> SemanticGraph:
    function_names = {function.name for function in model.functions}
    input_ports = {name for name, port in model.ports.items() if port.direction == "in"}
    output_ports = {name for name, port in model.ports.items() if port.direction == "out"}
    parameters = set(model.component.parameters)
    nodes: set[str] = set()
    edges: set[SemanticEdge] = set()
    for flow in model.flows:
        source_root, source_signal = _split_endpoint(flow.source)
        target_root, target_signal = _split_endpoint(flow.target)
        if target_signal in input_ports and target_root in function_names:
            source_label = source_root
            input_label = _input_semantic_label(model, target_signal)
            nodes.update({source_label, input_label, target_root})
            edges.add(SemanticEdge(source_label, target_signal, input_label))
            edges.add(SemanticEdge(input_label, "", target_root))
            continue
        if source_signal in input_ports and target_root in function_names:
            input_label = _input_semantic_label(model, source_signal)
            nodes.update({input_label, target_root})
            edges.add(SemanticEdge(input_label, "", target_root))
            continue
        if source_signal in parameters and target_root in function_names:
            parameter_label = _parameter_semantic_label(model, source_signal)
            nodes.update({parameter_label, target_root})
            edges.add(SemanticEdge(parameter_label, "", target_root))
            continue
        if source_root in function_names and target_root in function_names:
            nodes.update({source_root, target_root})
            edges.add(SemanticEdge(source_root, source_signal or flow.label, target_root))
            continue
        if source_root in function_names and target_signal in output_ports:
            output_label = _output_semantic_label(model, target_signal)
            nodes.update({source_root, output_label})
            edges.add(SemanticEdge(source_root, "", output_label))
            continue
        if source_signal in output_ports and flow.target.startswith("ScenarioReport."):
            output_label = _output_semantic_label(model, source_signal)
            nodes.update({output_label, flow.target})
            edges.add(SemanticEdge(output_label, "", flow.target))
    if not nodes:
        raise SpecMbdAlignmentError("MBD semantic graph could not derive generic flow semantics")
    return SemanticGraph(nodes=frozenset(nodes), edges=frozenset(edges))


def _split_endpoint(endpoint: str) -> tuple[str, str]:
    root, separator, signal = endpoint.partition(".")
    return root, signal if separator else ""


def _parameter_semantic_label(model: MbdModelIR, parameter: str) -> str:
    for flow in model.flows:
        source_root, source_signal = _split_endpoint(flow.source)
        if (
            source_root == model.component.name
            and source_signal == parameter
            and "constant" in flow.label.lower()
        ):
            value = model.component.parameters[parameter].default
            return f"Constant: {parameter} = {value}"
    return f"Parameter: {parameter}"


def _input_semantic_label(model: MbdModelIR, name: str) -> str:
    suffix = _vector_suffix(model.ports[name].type)
    return f"Input Port: {name}{suffix}"


def _output_semantic_label(model: MbdModelIR, name: str) -> str:
    suffix = _vector_suffix(model.ports[name].type)
    return f"Output {name}{suffix}"


def _vector_suffix(type_name: str) -> str:
    match = re.search(r"(\[\d+\])$", type_name)
    return match.group(1) if match else ""


def _output_action_label(model: MbdModelIR, control: ControlRuleIR) -> str:
    parts: list[str] = []
    for name, value in control.actions.items():
        port = model.ports.get(name)
        if port is not None and port.direction == "out":
            parts.append(f"Output {name} = {value}")
    if not parts:
        raise SpecMbdAlignmentError(f"control rule {control.name!r} has no output action")
    return " / ".join(parts)
