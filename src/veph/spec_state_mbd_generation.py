from __future__ import annotations

from pathlib import Path

from veph.spec_mbd_alignment import MermaidFlowchart, SpecMbdAlignmentError
from veph.spec_mbd_flow_helpers import (
    report_for_output_node,
    source_for_input,
    state_machine_function_name,
    trace_for_parameter,
)
from veph.spec_mbd_labels import (
    input_name as _input_name,
    is_input as _is_input,
    is_parameter as _is_parameter,
    is_output_port as _is_output_port,
    node_port_type as _node_port_type,
    output_port_name as _output_port_name,
    parameter_name as _parameter_name,
)
from veph.spec_mbd_text import (
    append_unique,
    display_path,
    format_actions,
    ordered_states,
    ordered_unique,
    requirement_texts,
    trace_suffix,
)
from veph.spec_state_model import (
    AdvancedStateSpec,
    StateActionSpec,
    StateTraceIntent,
    StateTransitionSpec,
    initial_state,
    parse_spec_advanced_state_semantics,
    parse_spec_state_actions,
    report_requirement as state_report_requirement,
    rule_name,
    state_trace_intents,
    trace_for_input,
    trace_for_output,
    trace_for_transition,
)


def generate_state_machine_mbd_from_spec(
    spec: Path,
    *,
    flowchart: MermaidFlowchart,
    transitions: list[StateTransitionSpec],
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
    output_nodes = [node for node in flowchart.nodes.values() if _is_output_port(node)]
    if not input_nodes:
        raise SpecMbdAlignmentError(f"state-machine spec has no Input Port nodes in {spec}")
    if not output_nodes:
        raise SpecMbdAlignmentError(f"state-machine spec has no Output nodes in {spec}")
    function_name = state_machine_function_name(flowchart, input_nodes, output_nodes)
    trace_intents = state_trace_intents(spec)
    state_actions = parse_spec_state_actions(spec)
    advanced_states = parse_spec_advanced_state_semantics(spec)
    output_names = ordered_unique(_output_port_name(node) for node in output_nodes)
    report_requirement = state_report_requirement(requirements, trace_intents)

    lines = [
        *generated_header,
        *_state_machine_spec_review_section(
            spec,
            requirements=requirements,
            transitions=transitions,
            trace_intents=trace_intents,
            state_actions=state_actions,
            advanced_states=advanced_states,
            scenario=scenario,
        ),
        "",
        *component_header,
        "",
    ]
    for node in parameter_nodes:
        name = _parameter_name(node)
        lines.append(f"parameter {name}: count = {parameter_defaults.get(name, '0')}")
    if parameter_nodes:
        lines.append("")
    for node in input_nodes:
        name = _input_name(node)
        default = input_defaults.get(name, "false")
        lines.append(f"port in {name}: {_node_port_type(node, default)} = {default}")
    for name in output_names:
        default = output_defaults.get(name, "false")
        node = next(node for node in output_nodes if _output_port_name(node) == name)
        lines.append(f"port out {name}: {_node_port_type(node, default)} = {default}")
    lines.extend(["```", "", "```mbd-registers"])
    lines.append("STATUS 0x01 ro 8")
    for index, name in enumerate(output_names):
        reset = "1" if output_defaults.get(name) == "true" else "0"
        lines.append(f"  bit {index} {name} reset={reset}")
    lines.extend(["```", "", "```mbd-state"])
    for transition in transitions:
        if transition.source == "[*]":
            continue
        lines.append(f"{transition.source} --> {transition.target}: {transition.condition}")
    states = ordered_states(transitions)
    input_names = [_input_name(node) for node in input_nodes]
    parameter_names = [_parameter_name(node) for node in parameter_nodes]
    lines.extend(["```", "", "```mbd-decomposition"])
    lines.append(
        f"function {function_name}: responsibility=Own the {'/'.join(states)} lifecycle and map state transitions to "
        f"{' and '.join(output_names)} outputs; owns={','.join([*states, *output_names])}; "
        f"inputs={','.join([*input_names, *parameter_names])}; outputs={','.join(['state', *output_names])}; "
        f"trace={','.join(requirements)}"
        f"{'; scenarios=' + scenario if scenario else ''}"
    )
    lines.extend(["```", "", "```mbd-flow"])
    emitted_flows: set[str] = set()
    for node in input_nodes:
        name = _input_name(node)
        source = source_for_input(flowchart, node.id)
        trace = trace_for_input(name, trace_intents, transitions)
        append_unique(
            lines,
            emitted_flows,
            f"{source}.{name} -> {function_name}.{name}: {name}{trace_suffix(trace)}",
        )
    for node in parameter_nodes:
        name = _parameter_name(node)
        append_unique(
            lines,
            emitted_flows,
            f"{component_name}.{name} -> {function_name}.{name}: {name}{trace_suffix(trace_for_parameter(requirements, name))}",
        )
    for node in output_nodes:
        name = _output_port_name(node)
        trace = trace_for_output(requirements, name, trace_intents)
        append_unique(
            lines,
            emitted_flows,
            f"{function_name}.{name} -> {component_name}.{name}: {name} output{trace_suffix(trace)}",
        )
        report = report_for_output_node(flowchart, node.id)
        append_unique(
            lines,
            emitted_flows,
            f"{component_name}.{name} -> {report}: reported {name}{trace_suffix([report_requirement] if report_requirement else [])}",
        )
    lines.extend(["```", "", "```mbd-control"])
    priority = 10
    for transition in transitions:
        if transition.source == "[*]":
            continue
        trace = trace_for_transition(trace_intents, transition)
        actions = [("state", transition.target)]
        if trace is not None:
            actions.extend(trace.actions)
        else:
            actions.extend((name, output_defaults.get(name, "false")) for name in output_names)
        trace_refs = [trace.requirement] if trace else []
        if report_requirement:
            trace_refs.append(report_requirement)
        lines.append(
            f"priority {priority} rule {rule_name(transition)}: owner {function_name} from {transition.source} "
            f"when {transition.condition} then {format_actions(actions)}{trace_suffix(ordered_unique(trace_refs))}"
            f"{' scenarios ' + scenario if scenario else ''}"
        )
        priority += 10
    for action in state_actions:
        lines.append(
            f"priority {priority} rule {action.state.lower()}_{action.phase}_action: owner {function_name} "
            f"from {action.state} when always then {format_actions(list(action.actions))}{trace_suffix(requirements)}"
            f"{' scenarios ' + scenario if scenario else ''}"
        )
        priority += 10
    lines.extend(["```", "", "```mbd-harness"])
    for source in ordered_unique(source_for_input(flowchart, node.id) for node in input_nodes):
        lines.append(f"device {source} role=source boundary=virtual_ic{trace_suffix(requirements[:3])}")
    lines.append(f"ecu {component_name} role=controller boundary=hal{trace_suffix(requirements)}")
    lines.extend(["```", ""])
    return "\n".join(lines)


def _state_machine_spec_review_section(
    spec: Path,
    *,
    requirements: list[str],
    transitions: list[StateTransitionSpec],
    trace_intents: list[StateTraceIntent],
    state_actions: list[StateActionSpec],
    advanced_states: list[AdvancedStateSpec],
    scenario: str,
) -> list[str]:
    lines = [
        "```mbd-spec-review",
        f"source {display_path(spec)}",
        "question Does the generated state-machine MBD implement Spec.md?",
    ]
    texts = requirement_texts(spec)
    for requirement in requirements:
        text = texts.get(requirement, "")
        if text:
            lines.append(f"intent {requirement} | {text}")
    initial = initial_state(transitions)
    if initial:
        lines.append(f"spec-initial {initial}")
    for transition in transitions:
        lines.append(f"spec-transition {transition.source} --> {transition.target}: {transition.condition}")
    for intent in trace_intents:
        actions = ", ".join(f"{name}={value}" for name, value in intent.actions)
        lines.append(
            f"trace-intent {intent.requirement} | {intent.source} --> {intent.target}"
            f" | {actions}"
        )
    for action in state_actions:
        actions = ", ".join(f"{name}={value}" for name, value in action.actions)
        lines.append(f"state-action {action.state} {action.phase} | {actions}")
    for advanced in advanced_states:
        lines.append(f"advanced-state {advanced.kind} | {advanced.detail}")
    if scenario:
        lines.append(f"scenario {scenario} | reports/{scenario}.md")
    lines.extend(
        [
            "open-question SMQ-001 | Guard false behavior is treated as implicit self-hold in the preview subset; confirm this is intended.",
            "advanced-state-semantics are MVP handoff notes; full Stateflow semantics require external MBD verification.",
            "```",
        ]
    )
    return lines
