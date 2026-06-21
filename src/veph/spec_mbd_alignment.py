from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from veph.control_semantics import (
    expression_variables,
    find_threshold_pair,
    primary_condition_terms,
    primary_output_action,
    report_for_signal,
    source_for_signal,
)
from veph.ir import ControlRuleIR, MbdModelIR
from veph.markup_parser import parse_markup_file


class SpecMbdAlignmentError(ValueError):
    """Raised when spec Mermaid cannot be compared with MBD semantics."""


@dataclass(frozen=True, order=True)
class SemanticEdge:
    source: str
    label: str
    target: str

    def render(self) -> str:
        if self.label:
            return f"{self.source} --{self.label}--> {self.target}"
        return f"{self.source} --> {self.target}"


@dataclass(frozen=True)
class SemanticGraph:
    nodes: frozenset[str]
    edges: frozenset[SemanticEdge]

    def has_edge(self, source: str, label: str, target: str) -> bool:
        return SemanticEdge(source=source, label=label, target=target) in self.edges


@dataclass(frozen=True)
class MermaidNode:
    id: str
    label: str
    shape: str


@dataclass(frozen=True)
class MermaidEdge:
    source_id: str
    label: str
    target_id: str


@dataclass(frozen=True)
class MermaidFlowchart:
    nodes: dict[str, MermaidNode]
    edges: tuple[MermaidEdge, ...]

    def semantic_graph(self) -> SemanticGraph:
        return SemanticGraph(
            nodes=frozenset(node.label for node in self.nodes.values()),
            edges=frozenset(
                SemanticEdge(
                    source=self.nodes[edge.source_id].label,
                    label=edge.label,
                    target=self.nodes[edge.target_id].label,
                )
                for edge in self.edges
            ),
        )


@dataclass(frozen=True)
class SpecMbdAlignmentReport:
    spec_path: Path
    mbd_path: Path
    matched_nodes: tuple[str, ...] = field(default_factory=tuple)
    matched_edges: tuple[str, ...] = field(default_factory=tuple)
    missing_nodes: tuple[str, ...] = field(default_factory=tuple)
    extra_nodes: tuple[str, ...] = field(default_factory=tuple)
    missing_edges: tuple[str, ...] = field(default_factory=tuple)
    extra_edges: tuple[str, ...] = field(default_factory=tuple)

    @property
    def passed(self) -> bool:
        return not (
            self.missing_nodes
            or self.extra_nodes
            or self.missing_edges
            or self.extra_edges
        )

    def to_markdown(self) -> str:
        lines = [
            "# Spec To MBD Semantic Alignment",
            "",
            f"Spec: `{self.spec_path}`",
            f"MBD source: `{self.mbd_path}`",
            "",
            f"Spec-to-MBD semantic alignment: **{'PASS' if self.passed else 'FAIL'}**",
            "",
            "## Matched nodes",
            *_bullet_or_none(self.matched_nodes),
            "",
            "## Matched edges",
            *_bullet_or_none(self.matched_edges),
            "",
            "## Missing MBD nodes",
            *_bullet_or_none(self.missing_nodes),
            "",
            "## Extra MBD nodes",
            *_bullet_or_none(self.extra_nodes),
            "",
            "## Missing MBD edges",
            *_bullet_or_none(self.missing_edges),
            "",
            "## Extra MBD edges",
            *_bullet_or_none(self.extra_edges),
            "",
        ]
        return "\n".join(lines)


NODE_RE = re.compile(r"^(?P<id>[A-Za-z_][A-Za-z0-9_-]*)(?P<bracket>[\[{])(?P<label>.+)(?P<close>[\]}])$")
EDGE_RE = re.compile(
    r"^(?P<source>.+?)\s*-->(?:\|(?P<label>[^|]+)\|)?\s*(?P<target>.+)$"
)
MERMAID_FENCE_RE = re.compile(r"```mermaid\n(?P<body>.*?)```", re.DOTALL)


def compare_spec_to_mbd(spec_path: str | Path, mbd_path: str | Path) -> SpecMbdAlignmentReport:
    spec = Path(spec_path)
    mbd = Path(mbd_path)
    return compare_spec_to_mbd_model(spec, parse_markup_file(mbd), mbd)


def compare_spec_to_mbd_model(
    spec_path: str | Path,
    model: MbdModelIR,
    mbd_path: str | Path,
) -> SpecMbdAlignmentReport:
    spec = Path(spec_path)
    mbd = Path(mbd_path)
    spec_graph = parse_spec_design_overview(spec)
    mbd_graph = semantic_graph_from_mbd(model)
    matched_nodes = tuple(sorted(spec_graph.nodes & mbd_graph.nodes))
    matched_edges = tuple(edge.render() for edge in sorted(spec_graph.edges & mbd_graph.edges))
    missing_nodes = tuple(sorted(spec_graph.nodes - mbd_graph.nodes))
    extra_nodes = tuple(sorted(mbd_graph.nodes - spec_graph.nodes))
    missing_edges = tuple(edge.render() for edge in sorted(spec_graph.edges - mbd_graph.edges))
    extra_edges = tuple(edge.render() for edge in sorted(mbd_graph.edges - spec_graph.edges))
    return SpecMbdAlignmentReport(
        spec_path=spec,
        mbd_path=mbd,
        matched_nodes=matched_nodes,
        matched_edges=matched_edges,
        missing_nodes=missing_nodes,
        extra_nodes=extra_nodes,
        missing_edges=missing_edges,
        extra_edges=extra_edges,
    )


def parse_spec_design_overview(path: str | Path) -> SemanticGraph:
    return parse_spec_design_overview_flowchart(path).semantic_graph()


def parse_spec_design_overview_flowchart(path: str | Path) -> MermaidFlowchart:
    spec_path = Path(path)
    text = spec_path.read_text(encoding="utf-8")
    body = _extract_design_overview_mermaid(text, spec_path)
    return parse_mermaid_flowchart_model(body, spec_path)


def parse_mermaid_flowchart(body: str, source_path: Path | None = None) -> SemanticGraph:
    return parse_mermaid_flowchart_model(body, source_path).semantic_graph()


def parse_mermaid_flowchart_model(body: str, source_path: Path | None = None) -> MermaidFlowchart:
    nodes: dict[str, MermaidNode] = {}
    edges: list[MermaidEdge] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("%%"):
            continue
        if line in {"flowchart LR", "flowchart TD", "graph LR", "graph TD"}:
            continue
        edge_match = EDGE_RE.match(line)
        if edge_match:
            source = _parse_mermaid_endpoint(edge_match.group("source").strip())
            target = _parse_mermaid_endpoint(edge_match.group("target").strip())
            if source.label:
                nodes[source.id] = source
            if target.label:
                nodes[target.id] = target
            _require_known_node(source.id, nodes, line, source_path)
            _require_known_node(target.id, nodes, line, source_path)
            edges.append(
                MermaidEdge(
                    source_id=source.id,
                    label=(edge_match.group("label") or "").strip(),
                    target_id=target.id,
                )
            )
            continue
        node = _parse_mermaid_endpoint(line)
        if node.label:
            nodes[node.id] = node
            continue
        location = f" in {source_path}" if source_path is not None else ""
        raise SpecMbdAlignmentError(f"unsupported Mermaid line{location}: {line}")
    return MermaidFlowchart(nodes=nodes, edges=tuple(edges))


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


def _extract_design_overview_mermaid(text: str, source_path: Path) -> str:
    header = re.search(r"^##\s+Design Overview\s*$", text, re.MULTILINE)
    if header is None:
        raise SpecMbdAlignmentError(f"missing Design Overview section in {source_path}")
    match = MERMAID_FENCE_RE.search(text, pos=header.end())
    if match is None:
        raise SpecMbdAlignmentError(f"missing Mermaid fence after Design Overview in {source_path}")
    return match.group("body").strip()


def _parse_mermaid_endpoint(text: str) -> MermaidNode:
    match = NODE_RE.match(text)
    if match is None:
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", text):
            return MermaidNode(id=text, label="", shape="reference")
        return MermaidNode(id=text, label="", shape="unsupported")
    bracket = match.group("bracket")
    close = match.group("close")
    if (bracket, close) not in {("[", "]"), ("{", "}")}:
        return MermaidNode(id=text, label="", shape="unsupported")
    shape = "decision" if bracket == "{" else "node"
    return MermaidNode(id=match.group("id"), label=match.group("label").strip().strip('"'), shape=shape)


def _require_known_node(
    node_id: str,
    nodes: dict[str, MermaidNode],
    line: str,
    source_path: Path | None,
) -> None:
    if node_id in nodes:
        return
    location = f" in {source_path}" if source_path is not None else ""
    raise SpecMbdAlignmentError(f"Mermaid edge references undefined node {node_id!r}{location}: {line}")


def _output_action_label(model: MbdModelIR, control: ControlRuleIR) -> str:
    parts: list[str] = []
    for name, value in control.actions.items():
        port = model.ports.get(name)
        if port is not None and port.direction == "out":
            parts.append(f"Output {name} = {value}")
    if not parts:
        raise SpecMbdAlignmentError(f"control rule {control.name!r} has no output action")
    return " / ".join(parts)


def _bullet_or_none(items: tuple[str, ...]) -> list[str]:
    if not items:
        return ["- None"]
    return [f"- `{item}`" for item in items]
