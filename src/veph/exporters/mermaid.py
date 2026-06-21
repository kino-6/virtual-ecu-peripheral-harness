from __future__ import annotations

from veph.control_semantics import (
    expression_variables,
    find_threshold_pair,
    primary_output_action,
    report_for_signal,
    source_for_signal,
)
from veph.ir import ControlRuleIR, MbdModelIR


def export_mermaid(model: MbdModelIR) -> str:
    lines = [
        "flowchart LR",
        "  %% Generated semantic MBD preview from Mermaid-like MBD markup.",
        "  %% Existing MBD tools remain the verification backends.",
    ]
    semantic_lines = _semantic_block_diagram(model)
    if semantic_lines:
        lines.extend(semantic_lines)
        lines.append("  %% Detail trace carriers follow; semantic blocks above are the primary review artifact.")
    for flow in model.flows:
        source = _node_id(flow.source)
        target = _node_id(flow.target)
        lines.append(f'  {source}["{flow.source}"]')
        lines.append(f'  {target}["{flow.target}"]')
        if flow.trace:
            lines.append(f"  %% Trace: {', '.join(flow.trace)}")
        lines.append(f"  %% {source} --> {target}")
        if flow.label:
            lines.append(f'  {source} -->|"{flow.label}"| {target}')
        else:
            lines.append(f"  {source} --> {target}")
    for function in model.functions:
        function_id = _node_id(f"function_{function.name}")
        lines.append(f'  {function_id}["{function.name}<br/>{function.responsibility}"]')
        if function.trace:
            lines.append(f"  %% Function Trace: {', '.join(function.trace)}")
        for output in function.outputs:
            output_id = _node_id(output)
            lines.append(f'  {output_id}["{output}"]')
            lines.append(f'  {function_id} -->|"owns"| {output_id}')
    for control in model.controls:
        control_id = _node_id(f"rule_{control.name}")
        owner = f"<br/>owner {control.owner}" if control.owner else ""
        lines.append(f'  {control_id}{{"priority {control.priority}<br/>rule {control.name}{owner}<br/>from {control.state_scope}"}}')
        if control.trace:
            lines.append(f"  %% Trace: {', '.join(control.trace)}")
        if control.scenarios:
            lines.append(f"  %% Scenarios: {', '.join(control.scenarios)}")
        for target in control.actions:
            target_id = _node_id(target)
            lines.append(f'  {target_id}["{target}"]')
            lines.append(f'  {control_id} -->|"{control.condition}"| {target_id}')
    for device in model.harness_devices:
        device_id = _node_id(device.name)
        lines.append(f'  {device_id}["{device.name}<br/>{device.boundary}"]')
        if device.trace:
            lines.append(f"  %% Trace: {', '.join(device.trace)}")
    return "\n".join(lines) + "\n"


def _semantic_block_diagram(model: MbdModelIR) -> list[str]:
    threshold_pair = find_threshold_pair(model.controls)
    if threshold_pair is not None:
        true_rule, false_rule = threshold_pair
        return _threshold_pair_diagram(model, true_rule, false_rule)
    if model.controls:
        return _rule_diagram(model)
    return []


def _threshold_pair_diagram(
    model: MbdModelIR,
    true_rule: ControlRuleIR,
    false_rule: ControlRuleIR,
) -> list[str]:
    condition = true_rule.condition_expr
    variables = expression_variables(condition)
    primary_input = next((name for name in variables if name in model.ports), "")
    primary_parameter = next((name for name in variables if name in model.component.parameters), "")
    source = source_for_signal(model.flows, primary_input) or "ScenarioInput"
    output_name = primary_output_action(model, true_rule) or primary_output_action(model, false_rule) or "output"
    report = report_for_signal(model.flows, output_name) or "ScenarioReport.observedBehavior"

    source_id = _node_id(f"source_{source}")
    input_id = _node_id(f"input_{primary_input or 'input'}")
    parameter_id = _node_id(f"parameter_{primary_parameter or 'parameter'}")
    decision_id = _node_id(f"decision_{true_rule.name}_{false_rule.name}")
    true_action_id = _node_id(f"action_{true_rule.name}")
    false_action_id = _node_id(f"action_{false_rule.name}")
    report_id = _node_id("report_observed_behavior")
    lines = [
        "  %% Semantic MBD Block Diagram",
        f'  {source_id}["{source}"]',
        f'  {input_id}["Input Port: {primary_input or "input"}"]',
        f'  {parameter_id}["Parameter: {primary_parameter or "parameter"}"]',
        f'  {decision_id}{{"{true_rule.condition}?"}}',
        f'  {true_action_id}["{_output_action_label(model, true_rule)}"]',
        f'  {false_action_id}["{_output_action_label(model, false_rule)}"]',
        f'  {report_id}["{report}"]',
        f'  {source_id} -->|"{primary_input or "input"}"| {input_id}',
        f"  {input_id} --> {decision_id}",
        f"  {parameter_id} --> {decision_id}",
        f'  {decision_id} -->|"true"| {true_action_id}',
        f'  {decision_id} -->|"false"| {false_action_id}',
        f"  {true_action_id} --> {report_id}",
        f"  {false_action_id} --> {report_id}",
    ]
    trace = sorted(set(true_rule.trace + false_rule.trace))
    if trace:
        lines.append(f"  %% Semantic Trace: {', '.join(trace)}")
    return lines


def _rule_diagram(model: MbdModelIR) -> list[str]:
    lines = ["  %% Semantic MBD Block Diagram"]
    for control in model.controls:
        decision_id = _node_id(f"decision_{control.name}")
        action_id = _node_id(f"action_{control.name}")
        lines.append(f'  {decision_id}{{"{control.condition}?"}}')
        lines.append(f'  {action_id}["{_action_label(model, control)}"]')
        for variable in expression_variables(control.condition_expr):
            if variable in model.ports:
                variable_id = _node_id(f"input_{variable}")
                lines.append(f'  {variable_id}["Input Port: {variable}"]')
                lines.append(f"  {variable_id} --> {decision_id}")
            elif variable in model.component.parameters:
                variable_id = _node_id(f"parameter_{variable}")
                lines.append(f'  {variable_id}["Parameter: {variable}"]')
                lines.append(f"  {variable_id} --> {decision_id}")
        lines.append(f'  {decision_id} -->|"true / {control.name}"| {action_id}')
    return lines


def _action_label(model: MbdModelIR, control: ControlRuleIR) -> str:
    parts: list[str] = []
    for name, value in control.actions.items():
        port = model.ports.get(name)
        if port is not None and port.direction == "out":
            parts.append(f"Output {name} = {value}")
        elif name == "state":
            parts.append(f"State {value}")
        else:
            parts.append(f"{name} = {value}")
    return "<br/>".join(parts)


def _output_action_label(model: MbdModelIR, control: ControlRuleIR) -> str:
    parts: list[str] = []
    for name, value in control.actions.items():
        port = model.ports.get(name)
        if port is not None and port.direction == "out":
            parts.append(f"Output {name} = {value}")
    return "<br/>".join(parts) if parts else _action_label(model, control)


def _node_id(name: str) -> str:
    return name.replace(".", "_").replace(" ", "_").replace("-", "_")
