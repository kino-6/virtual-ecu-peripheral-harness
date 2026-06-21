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
    constant_nodes: tuple[MermaidNode, ...]
    true_output: MermaidNode
    false_output: MermaidNode
    report_node: MermaidNode


@dataclass(frozen=True)
class StateTraceIntent:
    requirement: str
    source: str
    target: str
    actions: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class StateActionSpec:
    state: str
    phase: str
    actions: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class AdvancedStateSpec:
    kind: str
    detail: str


@dataclass(frozen=True)
class ArithmeticBlockSpec:
    node: MermaidNode
    operator: str
    output_signal: str
    input_signals: tuple[str, ...]


OUTPUT_RE = re.compile(r"^Output\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.+)$")
OUTPUT_PORT_RE = re.compile(r"^Output\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)(?P<vector>\[\d+\])?$")
INPUT_RE = re.compile(r"^Input Port:\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)(?P<vector>\[\d+\])?$")
PARAMETER_RE = re.compile(r"^Parameter:\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)$")
CONSTANT_RE = re.compile(r"^Constant:\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.+)$")
STATE_FENCE_RE = re.compile(r"```mermaid\n(?P<body>.*?)```", re.DOTALL)
ARITHMETIC_OPERATORS = {"Gain", "Sum", "Product", "Saturation", "Lookup1D"}


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
        arithmetic_blocks = _arithmetic_specs(flowchart)
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
            return _generate_state_machine_mbd_from_spec(
                spec,
                flowchart=flowchart,
                transitions=transitions,
                requirements=requirements,
                component_name=component_name,
                parameter_defaults=parameter_defaults or {},
                input_defaults=input_defaults or {},
                output_defaults=output_defaults or {},
                scenario=scenario,
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
    block_expressions = _arithmetic_expressions(flowchart, blocks)
    output_expressions = {
        _output_port_name(node): _output_expression(flowchart, node, block_expressions)
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
        for target in _targets_for_node(flowchart, node.id):
            if _is_arithmetic(flowchart.nodes[target]):
                _append_unique(
                    lines,
                    emitted_flows,
                    f"{source}.{name} -> {flowchart.nodes[target].label}.{name}: {name}{_trace_suffix(requirements[:1])}",
                )
    for node in parameter_nodes:
        name = _parameter_name(node)
        for target in _targets_for_node(flowchart, node.id):
            if _is_arithmetic(flowchart.nodes[target]):
                _append_unique(
                    lines,
                    emitted_flows,
                    f"{component_name}.{name} -> {flowchart.nodes[target].label}.{name}: {name}{_trace_suffix(requirements[:2])}",
                )
    for node in constant_nodes:
        name = _constant_name(node)
        for target in _targets_for_node(flowchart, node.id):
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
            signal = edge.label or _block_output_signal(blocks, source_node.id)
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


def _generate_state_machine_mbd_from_spec(
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
) -> str:
    input_nodes = [node for node in flowchart.nodes.values() if _is_input(node)]
    parameter_nodes = [node for node in flowchart.nodes.values() if _is_parameter(node)]
    output_nodes = [node for node in flowchart.nodes.values() if _is_output_port(node)]
    if not input_nodes:
        raise SpecMbdAlignmentError(f"state-machine spec has no Input Port nodes in {spec}")
    if not output_nodes:
        raise SpecMbdAlignmentError(f"state-machine spec has no Output nodes in {spec}")
    function_name = _state_machine_function_name(flowchart, input_nodes, output_nodes)
    trace_intents = _state_trace_intents(spec)
    state_actions = parse_spec_state_actions(spec)
    advanced_states = parse_spec_advanced_state_semantics(spec)
    output_names = _ordered_unique(_output_port_name(node) for node in output_nodes)
    trace_all = " ".join(requirements)
    report_requirement = _report_requirement(requirements, trace_intents)

    lines = [
        *_generated_header(spec, "Spec Mermaid Design Overview and stateDiagram-v2"),
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
        *_component_header(component_name, trace_all),
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
    states = _ordered_states(transitions)
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
        source = _source_for_input(flowchart, node.id)
        trace = _trace_for_input(name, trace_intents, transitions)
        _append_unique(
            lines,
            emitted_flows,
            f"{source}.{name} -> {function_name}.{name}: {name}{_trace_suffix(trace)}",
        )
    for node in parameter_nodes:
        name = _parameter_name(node)
        _append_unique(
            lines,
            emitted_flows,
            f"{component_name}.{name} -> {function_name}.{name}: {name}{_trace_suffix(_trace_for_parameter(requirements, name))}",
        )
    for node in output_nodes:
        name = _output_port_name(node)
        trace = _trace_for_output(requirements, name, trace_intents)
        _append_unique(
            lines,
            emitted_flows,
            f"{function_name}.{name} -> {component_name}.{name}: {name} output{_trace_suffix(trace)}",
        )
        report = _report_for_output_node(flowchart, node.id)
        _append_unique(
            lines,
            emitted_flows,
            f"{component_name}.{name} -> {report}: reported {name}{_trace_suffix([report_requirement] if report_requirement else [])}",
        )
    lines.extend(["```", "", "```mbd-control"])
    priority = 10
    for transition in transitions:
        if transition.source == "[*]":
            continue
        trace = _trace_for_transition(trace_intents, transition)
        actions = [("state", transition.target)]
        if trace is not None:
            actions.extend(trace.actions)
        else:
            actions.extend((name, output_defaults.get(name, "false")) for name in output_names)
        trace_refs = [trace.requirement] if trace else []
        if report_requirement:
            trace_refs.append(report_requirement)
        lines.append(
            f"priority {priority} rule {_rule_name(transition)}: owner {function_name} from {transition.source} "
            f"when {transition.condition} then {_format_actions(actions)}{_trace_suffix(_ordered_unique(trace_refs))}"
            f"{' scenarios ' + scenario if scenario else ''}"
        )
        priority += 10
    for action in state_actions:
        lines.append(
            f"priority {priority} rule {action.state.lower()}_{action.phase}_action: owner {function_name} "
            f"from {action.state} when always then {_format_actions(list(action.actions))}{_trace_suffix(requirements)}"
            f"{' scenarios ' + scenario if scenario else ''}"
        )
        priority += 10
    lines.extend(["```", "", "```mbd-harness"])
    for source in _ordered_unique(_source_for_input(flowchart, node.id) for node in input_nodes):
        lines.append(f"device {source} role=source boundary=virtual_ic{_trace_suffix(requirements[:3])}")
    lines.append(f"ecu {component_name} role=controller boundary=hal{_trace_suffix(requirements)}")
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
        f"source {_display_path(spec)}",
        "question Does the generated state-machine MBD implement Spec.md?",
    ]
    requirement_texts = _requirement_texts(spec)
    for requirement in requirements:
        text = requirement_texts.get(requirement, "")
        if text:
            lines.append(f"intent {requirement} | {text}")
    initial = _initial_state(transitions)
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


def parse_spec_state_diagram(path: str | Path) -> list[StateTransitionSpec]:
    spec_path = Path(path)
    for body in _mermaid_bodies(spec_path):
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        if not lines or lines[0] != "stateDiagram-v2":
            continue
        transitions: list[StateTransitionSpec] = []
        for line in lines[1:]:
            if _parse_state_action_line(line) is not None:
                continue
            if _advanced_state_line_kind(line) is not None:
                continue
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


def parse_spec_advanced_state_semantics(path: str | Path) -> list[AdvancedStateSpec]:
    spec_path = Path(path)
    notes: list[AdvancedStateSpec] = []
    for body in _mermaid_bodies(spec_path):
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        if not lines or lines[0] != "stateDiagram-v2":
            continue
        for line in lines[1:]:
            kind = _advanced_state_line_kind(line)
            if kind is not None:
                notes.append(AdvancedStateSpec(kind=kind, detail=line))
                continue
            transition = re.match(r"(?P<source>\S+)\s+-->\s+(?P<target>[^:]+)(?::\s*(?P<condition>.+))?", line)
            if transition and (transition.group("source") == "[H]" or transition.group("target") == "[H]"):
                notes.append(AdvancedStateSpec(kind="history", detail=line))
            if transition and (transition.group("condition") or "").startswith("after "):
                notes.append(AdvancedStateSpec(kind="temporal", detail=line))
        return _dedupe_advanced_notes(notes)
    return []


def _advanced_state_line_kind(line: str) -> str | None:
    if re.match(r"state\s+[A-Za-z_][A-Za-z0-9_]*\s*\{", line):
        return "hierarchy"
    if line == "}":
        return "hierarchy"
    if line == "--":
        return "parallel"
    return None


def _dedupe_advanced_notes(notes: list[AdvancedStateSpec]) -> list[AdvancedStateSpec]:
    result: list[AdvancedStateSpec] = []
    seen: set[tuple[str, str]] = set()
    for note in notes:
        key = (note.kind, note.detail)
        if key in seen:
            continue
        seen.add(key)
        result.append(note)
    return result


def parse_spec_state_actions(path: str | Path) -> list[StateActionSpec]:
    spec_path = Path(path)
    actions: list[StateActionSpec] = []
    for body in _mermaid_bodies(spec_path):
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        if not lines or lines[0] != "stateDiagram-v2":
            continue
        for line in lines[1:]:
            parsed = _parse_state_action_line(line)
            if parsed is not None:
                actions.append(parsed)
        return actions
    return []


def _parse_state_action_line(line: str) -> StateActionSpec | None:
    match = re.match(
        r"(?P<state>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?P<phase>entry|during|exit)\s+(?P<actions>.+)",
        line,
    )
    if match is None:
        return None
    return StateActionSpec(
        state=match.group("state"),
        phase=match.group("phase"),
        actions=tuple(_parse_state_action_pairs(match.group("actions"))),
    )


def _parse_state_action_pairs(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for item in text.split(","):
        name, separator, value = item.strip().partition("=")
        if separator != "=" or not name.strip() or not value.strip():
            raise SpecMbdAlignmentError(f"invalid state action: {item}")
        pairs.append((name.strip(), value.strip()))
    return pairs


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


def _arithmetic_specs(flowchart: MermaidFlowchart) -> list[ArithmeticBlockSpec]:
    specs: list[ArithmeticBlockSpec] = []
    for node in flowchart.nodes.values():
        if not _is_arithmetic(node):
            continue
        incoming = [edge for edge in flowchart.edges if edge.target_id == node.id]
        input_signals = tuple(_signal_for_edge_source(flowchart, edge) for edge in incoming)
        output_signal = _arithmetic_output_signal(flowchart, node.id)
        specs.append(
            ArithmeticBlockSpec(
                node=node,
                operator=_operator_label(node),
                output_signal=output_signal,
                input_signals=input_signals,
            )
        )
    return specs


def _arithmetic_expressions(
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
                if _is_arithmetic(source):
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


def _output_expression(
    flowchart: MermaidFlowchart,
    output_node: MermaidNode,
    block_expressions: dict[str, str],
) -> str:
    incoming = [edge for edge in flowchart.edges if edge.target_id == output_node.id]
    if len(incoming) != 1:
        raise SpecMbdAlignmentError(f"output node must have exactly one arithmetic source: {output_node.label}")
    source = flowchart.nodes[incoming[0].source_id]
    if not _is_arithmetic(source):
        return _signal_for_edge_source(flowchart, incoming[0])
    signal = incoming[0].label or _output_port_name(output_node)
    if signal in block_expressions:
        return block_expressions[signal]
    produced = next(
        (value for key, value in block_expressions.items() if key == _output_port_name(output_node)),
        "",
    )
    if produced:
        return produced
    candidates = list(block_expressions.values())
    if len(candidates) == 1:
        return candidates[0]
    output_name = _output_port_name(output_node)
    for edge in flowchart.edges:
        if edge.source_id == source.id:
            signal = edge.label or output_name
            if signal in block_expressions:
                return block_expressions[signal]
    raise SpecMbdAlignmentError(f"could not derive expression for output {output_node.label}")


def _arithmetic_output_signal(flowchart: MermaidFlowchart, node_id: str) -> str:
    outgoing = [edge for edge in flowchart.edges if edge.source_id == node_id]
    if len(outgoing) != 1:
        raise SpecMbdAlignmentError(f"arithmetic block {node_id} must have exactly one outgoing signal")
    target = flowchart.nodes[outgoing[0].target_id]
    if outgoing[0].label:
        return outgoing[0].label
    if _is_output_port(target):
        return _output_port_name(target)
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
    if _is_input(source):
        return _input_name(source)
    if _is_parameter(source):
        return _parameter_name(source)
    if _is_constant(source):
        return _constant_name(source)
    if _is_arithmetic(source):
        return _arithmetic_output_signal(flowchart, source.id)
    raise SpecMbdAlignmentError(f"edge into arithmetic block lacks a signal label from {source.label}")


def _targets_for_node(flowchart: MermaidFlowchart, node_id: str) -> list[str]:
    return [edge.target_id for edge in flowchart.edges if edge.source_id == node_id]


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


def _report_for_output_node(flowchart: MermaidFlowchart, output_id: str) -> str:
    for edge in flowchart.edges:
        if edge.source_id == output_id and _is_report(flowchart.nodes[edge.target_id]):
            return flowchart.nodes[edge.target_id].label
    return "ScenarioReport.observedBehavior"


def _source_for_input(flowchart: MermaidFlowchart, input_id: str) -> str:
    for edge in flowchart.edges:
        if edge.target_id == input_id:
            source = flowchart.nodes[edge.source_id]
            if not _is_parameter(source):
                return source.label
    return "ScenarioInput"


def _state_machine_function_name(
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


def _is_input(node: MermaidNode) -> bool:
    return INPUT_RE.match(node.label) is not None


def _is_parameter(node: MermaidNode) -> bool:
    return PARAMETER_RE.match(node.label) is not None


def _is_constant(node: MermaidNode) -> bool:
    return CONSTANT_RE.match(node.label) is not None


def _is_arithmetic(node: MermaidNode) -> bool:
    return _operator_label(node) in ARITHMETIC_OPERATORS


def _operator_label(node: MermaidNode) -> str:
    return node.label.rsplit("/", 1)[-1]


def _is_output(node: MermaidNode) -> bool:
    return OUTPUT_RE.match(node.label) is not None


def _is_output_port(node: MermaidNode) -> bool:
    return OUTPUT_PORT_RE.match(node.label) is not None


def _is_report(node: MermaidNode) -> bool:
    return node.label.startswith("ScenarioReport.")


def _input_name(node: MermaidNode) -> str:
    match = INPUT_RE.match(node.label)
    if match is None:
        raise SpecMbdAlignmentError(f"not an input port node: {node.label}")
    return match.group("name")


def _output_port_name(node: MermaidNode) -> str:
    match = OUTPUT_PORT_RE.match(node.label)
    if match is None:
        raise SpecMbdAlignmentError(f"not an output port node: {node.label}")
    return match.group("name")


def _parameter_name(node: MermaidNode) -> str:
    match = PARAMETER_RE.match(node.label)
    if match is None:
        raise SpecMbdAlignmentError(f"not a parameter node: {node.label}")
    return match.group("name")


def _constant_name(node: MermaidNode) -> str:
    match = CONSTANT_RE.match(node.label)
    if match is None:
        raise SpecMbdAlignmentError(f"not a constant node: {node.label}")
    return match.group("name")


def _constant_value(node: MermaidNode) -> str:
    match = CONSTANT_RE.match(node.label)
    if match is None:
        raise SpecMbdAlignmentError(f"not a constant node: {node.label}")
    return match.group("value").strip()


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


def _port_type(default: str) -> str:
    return "bool" if default in {"true", "false"} else "count"


def _node_port_type(node: MermaidNode, default: str) -> str:
    vector = _vector_suffix(node)
    return f"{_port_type(default)}{vector}"


def _vector_suffix(node: MermaidNode) -> str:
    for pattern in (INPUT_RE, OUTPUT_PORT_RE):
        match = pattern.match(node.label)
        if match is not None:
            return match.group("vector") or ""
    return ""


def _state_trace_intents(path: Path) -> list[StateTraceIntent]:
    intents: list[StateTraceIntent] = []
    text = path.read_text(encoding="utf-8")
    for match in re.finditer(r"^-\s+`(?P<req>[^`]+)`:\s*(?P<body>.+)$", text, re.MULTILINE):
        body = match.group("body")
        transition_match = re.search(
            r"`?(?P<source>[A-Za-z_][A-Za-z0-9_]*)\s+-->\s+(?P<target>[A-Za-z_][A-Za-z0-9_]*)`?",
            body,
        )
        if transition_match is None:
            continue
        actions = tuple(
            (action.group("name"), action.group("value"))
            for action in re.finditer(
                r"`?(?P<name>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>true|false|[A-Za-z_][A-Za-z0-9_]*)`?",
                body,
            )
        )
        intents.append(
            StateTraceIntent(
                requirement=match.group("req"),
                source=transition_match.group("source"),
                target=transition_match.group("target"),
                actions=actions,
            )
        )
    return intents


def _trace_for_transition(
    intents: list[StateTraceIntent],
    transition: StateTransitionSpec,
) -> StateTraceIntent | None:
    for intent in intents:
        if intent.source == transition.source and intent.target == transition.target:
            return intent
    return None


def _report_requirement(requirements: list[str], intents: list[StateTraceIntent]) -> str:
    intent_requirements = {intent.requirement for intent in intents}
    for requirement in requirements:
        if requirement not in intent_requirements:
            return requirement
    return requirements[-1] if requirements else ""


def _requirement_texts(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    current: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^-\s+`(?P<req>[^`]+)`:\s*(?P<body>.+)$", raw_line)
        if match:
            current = match.group("req")
            values.setdefault(current, match.group("body").strip())
            continue
        if current is None:
            continue
        if raw_line.startswith("- "):
            current = None
            continue
        if raw_line.startswith("  ") and raw_line.strip():
            values[current] = f"{values[current]} {raw_line.strip()}"
            continue
        if not raw_line.strip():
            current = None
    return values


def _initial_state(transitions: list[StateTransitionSpec]) -> str:
    for transition in transitions:
        if transition.source == "[*]":
            return transition.target
    return ""


def _trace_for_input(
    input_name: str,
    intents: list[StateTraceIntent],
    transitions: list[StateTransitionSpec],
) -> list[str]:
    matched: list[str] = []
    for transition in transitions:
        if re.search(rf"\b{re.escape(input_name)}\b", transition.condition):
            intent = _trace_for_transition(intents, transition)
            if intent is not None:
                matched.append(intent.requirement)
    return _ordered_unique(matched)


def _trace_for_output(
    requirements: list[str],
    output_name: str,
    intents: list[StateTraceIntent],
) -> list[str]:
    matched = [
        intent.requirement
        for intent in intents
        if any(name == output_name for name, _ in intent.actions)
    ]
    return _ordered_unique(matched) or requirements[:1]


def _trace_for_parameter(requirements: list[str], parameter_name: str) -> list[str]:
    if "on" in parameter_name.lower():
        return requirements[:1]
    if "off" in parameter_name.lower():
        return requirements[1:2] or requirements[:1]
    return requirements[:2]


def _rule_name(transition: StateTransitionSpec) -> str:
    return f"{transition.source.lower()}_to_{transition.target.lower()}"


def _format_actions(actions: list[tuple[str, str]]) -> str:
    return ", ".join(f"{name}={value}" for name, value in actions)


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


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _requirement_ids(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return _ordered_unique(re.findall(r"^-\s+`([^`]+)`:", text, re.MULTILINE))


def _mermaid_bodies(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [match.group("body").strip() for match in STATE_FENCE_RE.finditer(text)]
