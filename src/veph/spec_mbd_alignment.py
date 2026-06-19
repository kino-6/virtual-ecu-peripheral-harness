from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from veph.ir import ControlRuleIR, ExpressionIR, FlowIR, MbdModelIR
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
    spec_graph = parse_spec_design_overview(spec)
    mbd_graph = semantic_graph_from_mbd(parse_markup_file(mbd))
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
    spec_path = Path(path)
    text = spec_path.read_text(encoding="utf-8")
    body = _extract_design_overview_mermaid(text, spec_path)
    return parse_mermaid_flowchart(body, spec_path)


def parse_mermaid_flowchart(body: str, source_path: Path | None = None) -> SemanticGraph:
    node_labels: dict[str, str] = {}
    raw_edges: list[tuple[str, str, str]] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("%%"):
            continue
        if line in {"flowchart LR", "flowchart TD", "graph LR", "graph TD"}:
            continue
        edge_match = EDGE_RE.match(line)
        if edge_match:
            source_id, source_label = _parse_mermaid_endpoint(edge_match.group("source").strip())
            target_id, target_label = _parse_mermaid_endpoint(edge_match.group("target").strip())
            if source_label:
                node_labels[source_id] = source_label
            if target_label:
                node_labels[target_id] = target_label
            raw_edges.append(
                (
                    source_id,
                    (edge_match.group("label") or "").strip(),
                    target_id,
                )
            )
            continue
        node_id, node_label = _parse_mermaid_endpoint(line)
        if node_label:
            node_labels[node_id] = node_label
            continue
        location = f" in {source_path}" if source_path is not None else ""
        raise SpecMbdAlignmentError(f"unsupported Mermaid line{location}: {line}")

    nodes = frozenset(node_labels.values())
    edges = frozenset(
        SemanticEdge(
            source=node_labels.get(source_id, source_id),
            label=label,
            target=node_labels.get(target_id, target_id),
        )
        for source_id, label, target_id in raw_edges
    )
    return SemanticGraph(nodes=nodes, edges=edges)


def semantic_graph_from_mbd(model: MbdModelIR) -> SemanticGraph:
    pair = _find_threshold_pair(model.controls)
    if pair is None:
        raise SpecMbdAlignmentError(
            "MBD semantic graph currently supports one complementary threshold control pair"
        )
    true_rule, false_rule = pair
    primary_input, primary_parameter = _primary_condition_terms(model, true_rule.condition_expr)
    source = _source_for_signal(model.flows, primary_input) or "ScenarioInput"
    output_name = _primary_output_action(model, true_rule) or _primary_output_action(model, false_rule)
    if not output_name:
        raise SpecMbdAlignmentError("MBD semantic graph could not find an output port action")
    report = _report_for_signal(model.flows, output_name) or "ScenarioReport.observedBehavior"
    condition = f"{true_rule.condition}?"
    true_output = _output_action_label(model, true_rule)
    false_output = _output_action_label(model, false_rule)
    nodes = frozenset(
        {
            source,
            f"Input Port: {primary_input or 'input'}",
            f"Parameter: {primary_parameter or 'parameter'}",
            condition,
            true_output,
            false_output,
            report,
        }
    )
    edges = frozenset(
        {
            SemanticEdge(source, primary_input or "input", f"Input Port: {primary_input or 'input'}"),
            SemanticEdge(f"Input Port: {primary_input or 'input'}", "", condition),
            SemanticEdge(f"Parameter: {primary_parameter or 'parameter'}", "", condition),
            SemanticEdge(condition, "true", true_output),
            SemanticEdge(condition, "false", false_output),
            SemanticEdge(true_output, "", report),
            SemanticEdge(false_output, "", report),
        }
    )
    return SemanticGraph(nodes=nodes, edges=edges)


def _extract_design_overview_mermaid(text: str, source_path: Path) -> str:
    header = re.search(r"^##\s+Design Overview\s*$", text, re.MULTILINE)
    if header is None:
        raise SpecMbdAlignmentError(f"missing Design Overview section in {source_path}")
    match = MERMAID_FENCE_RE.search(text, pos=header.end())
    if match is None:
        raise SpecMbdAlignmentError(f"missing Mermaid fence after Design Overview in {source_path}")
    return match.group("body").strip()


def _parse_mermaid_endpoint(text: str) -> tuple[str, str]:
    match = NODE_RE.match(text)
    if match is None:
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", text):
            return text, ""
        return text, ""
    bracket = match.group("bracket")
    close = match.group("close")
    if (bracket, close) not in {("[", "]"), ("{", "}")}:
        return text, ""
    return match.group("id"), match.group("label").strip().strip('"')


def _find_threshold_pair(controls: list[ControlRuleIR]) -> tuple[ControlRuleIR, ControlRuleIR] | None:
    for first in controls:
        first_key = _comparison_key(first.condition_expr)
        if first_key is None:
            continue
        for second in controls:
            if first is second:
                continue
            second_key = _comparison_key(second.condition_expr)
            if second_key is None:
                continue
            left, right, operator = first_key
            if (left, right) == second_key[:2] and _is_complement(operator, second_key[2]):
                return (first, second) if first.priority <= second.priority else (second, first)
    return None


def _comparison_key(expression: ExpressionIR) -> tuple[str, str, str] | None:
    if expression.kind != "comparison" or expression.left is None or expression.right is None:
        return None
    left = _expression_name(expression.left)
    right = _expression_name(expression.right)
    if not left or not right:
        return None
    return left, right, expression.operator


def _expression_name(expression: ExpressionIR) -> str:
    if expression.kind == "variable":
        return expression.name
    if expression.kind in {"number", "boolean"}:
        return str(expression.value).lower()
    return ""


def _is_complement(first: str, second: str) -> bool:
    return (first, second) in {
        (">=", "<"),
        ("<", ">="),
        (">", "<="),
        ("<=", ">"),
        ("==", "!="),
        ("!=", "=="),
    }


def _primary_condition_terms(model: MbdModelIR, expression: ExpressionIR) -> tuple[str, str]:
    variables = _expression_variables(expression)
    primary_input = next((name for name in variables if name in model.ports), "")
    primary_parameter = next((name for name in variables if name in model.component.parameters), "")
    return primary_input, primary_parameter


def _expression_variables(expression: ExpressionIR) -> list[str]:
    if expression.kind == "variable":
        return [expression.name]
    variables: list[str] = []
    if expression.left is not None:
        variables.extend(_expression_variables(expression.left))
    if expression.right is not None:
        variables.extend(_expression_variables(expression.right))
    for operand in expression.operands:
        variables.extend(_expression_variables(operand))
    return list(dict.fromkeys(variables))


def _source_for_signal(flows: list[FlowIR], signal: str) -> str:
    if not signal:
        return ""
    for flow in flows:
        target_signal = flow.target.rsplit(".", 1)[-1]
        source_root = flow.source.split(".", 1)[0]
        if target_signal == signal and source_root != "ScenarioReport":
            return source_root
    return ""


def _report_for_signal(flows: list[FlowIR], signal: str) -> str:
    if not signal:
        return ""
    for flow in flows:
        source_signal = flow.source.rsplit(".", 1)[-1]
        if source_signal == signal and flow.target.startswith("ScenarioReport."):
            return flow.target
    return ""


def _primary_output_action(model: MbdModelIR, control: ControlRuleIR) -> str:
    for name in control.actions:
        port = model.ports.get(name)
        if port is not None and port.direction == "out":
            return name
    return ""


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
