from __future__ import annotations

from html import escape
from pathlib import Path

from veph.ir import MbdModelIR
from veph.spec_mbd_alignment import (
    SemanticGraph,
    SpecMbdAlignmentReport,
    parse_spec_design_overview,
    semantic_graph_from_mbd,
)


def export_spec_mbd_viewer(
    spec_path: str | Path,
    converted_model: MbdModelIR,
    report: SpecMbdAlignmentReport,
) -> str:
    spec_graph = parse_spec_design_overview(spec_path)
    mbd_graph = semantic_graph_from_mbd(converted_model)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            "  <title>Spec Mermaid To MBD Review</title>",
            "  <style>",
            _css(),
            "  </style>",
            "</head>",
            "<body>",
            '  <main class="shell">',
            "    <section class=\"hero\">",
            "      <div>",
            "        <p>Spec Mermaid To MBD Review</p>",
            f"        <h1>{escape(converted_model.component.name)}</h1>",
            f"        <span>Alignment: {'PASS' if report.passed else 'FAIL'}</span>",
            "      </div>",
            "    </section>",
            _graph_panel("Spec Mermaid Semantic Graph", spec_graph),
            _graph_panel("Converted MBD Semantic Graph", mbd_graph),
            _alignment_panel(report),
            "  </main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _graph_panel(title: str, graph: SemanticGraph) -> str:
    return "\n".join(
        [
            '    <section class="panel">',
            f"      <h2>{escape(title)}</h2>",
            _graph_svg(graph),
            "      <table>",
            "        <thead><tr><th>Source</th><th>Label</th><th>Target</th></tr></thead>",
            "        <tbody>",
            *(
                "          <tr>"
                f"<td>{escape(edge.source)}</td>"
                f"<td>{escape(edge.label or '-')}</td>"
                f"<td>{escape(edge.target)}</td>"
                "</tr>"
                for edge in sorted(graph.edges)
            ),
            "        </tbody>",
            "      </table>",
            "    </section>",
        ]
    )


def _graph_svg(graph: SemanticGraph) -> str:
    nodes = _ordered_nodes(graph)
    positions = _graph_positions(nodes)
    width = 1180
    lines = [
        f'      <svg class="diagram" viewBox="0 0 {width} 260" role="img" aria-label="semantic graph">',
        "        <defs>",
        '          <marker id="arrow" markerWidth="12" markerHeight="12" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">',
        '            <path d="M0,0 L0,6 L9,3 z" fill="#2f5d62"></path>',
        "          </marker>",
        "        </defs>",
    ]
    for edge in sorted(graph.edges):
        sx, sy = positions[edge.source]
        tx, ty = positions[edge.target]
        x1 = sx + 132
        y1 = sy + 28
        x2 = tx
        y2 = ty + 28
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        lines.append(
            f'        <path d="M {x1} {y1} C {mid_x:.0f} {y1}, {mid_x:.0f} {y2}, {x2} {y2}" class="edge"></path>'
        )
        if edge.label:
            lines.append(
                f'        <text x="{mid_x:.0f}" y="{mid_y - 8:.0f}" text-anchor="middle" class="edge-label">{escape(edge.label)}</text>'
            )
    for node, (x, y) in positions.items():
        lines.extend(
            [
                f'        <rect x="{x}" y="{y}" width="132" height="56" rx="8" class="node"></rect>',
                f'        <text x="{x + 66}" y="{y + 25}" text-anchor="middle" class="node-title">{escape(_shorten(node, 22))}</text>',
                f'        <text x="{x + 66}" y="{y + 42}" text-anchor="middle" class="node-note">{escape(_node_kind(node))}</text>',
            ]
        )
    lines.append("      </svg>")
    return "\n".join(lines)


def _alignment_panel(report: SpecMbdAlignmentReport) -> str:
    return "\n".join(
        [
            '    <section class="panel">',
            "      <h2>Alignment Evidence</h2>",
            f"      <p>Result: <strong>{'PASS' if report.passed else 'FAIL'}</strong></p>",
            _list_block("Matched nodes", report.matched_nodes),
            _list_block("Matched edges", report.matched_edges),
            _list_block("Missing MBD nodes", report.missing_nodes),
            _list_block("Extra MBD nodes", report.extra_nodes),
            _list_block("Missing MBD edges", report.missing_edges),
            _list_block("Extra MBD edges", report.extra_edges),
            "    </section>",
        ]
    )


def _list_block(title: str, values: tuple[str, ...]) -> str:
    items = values or ("None",)
    return "\n".join(
        [
            f"      <h3>{escape(title)}</h3>",
            "      <ul>",
            *(f"        <li><code>{escape(value)}</code></li>" for value in items),
            "      </ul>",
        ]
    )


def _ordered_nodes(graph: SemanticGraph) -> list[str]:
    nodes: list[str] = []
    for edge in sorted(graph.edges):
        for node in [edge.source, edge.target]:
            if node not in nodes:
                nodes.append(node)
    for node in sorted(graph.nodes):
        if node not in nodes:
            nodes.append(node)
    return nodes


def _graph_positions(nodes: list[str]) -> dict[str, tuple[int, int]]:
    lanes: dict[int, list[str]] = {}
    for node in nodes:
        lanes.setdefault(_node_rank(node), []).append(node)
    x_by_rank = {0: 42, 1: 266, 2: 536, 3: 766, 4: 1016}
    positions: dict[str, tuple[int, int]] = {}
    for rank, ranked_nodes in lanes.items():
        ranked_nodes = sorted(ranked_nodes, key=_node_order_key)
        base_y = 102 if len(ranked_nodes) == 1 else 52
        for index, node in enumerate(ranked_nodes):
            positions[node] = (x_by_rank.get(rank, 42 + rank * 220), base_y + index * 94)
    return positions


def _node_order_key(node: str) -> tuple[int, str]:
    if node.endswith("= true"):
        return 0, node
    if node.endswith("= false"):
        return 1, node
    return 0, node


def _node_rank(node: str) -> int:
    if node.startswith("Input Port:"):
        return 1
    if node.startswith("Parameter:"):
        return 1
    if node.endswith("?"):
        return 2
    if node.startswith("Output "):
        return 3
    if node.startswith("ScenarioReport."):
        return 4
    return 0


def _node_kind(node: str) -> str:
    if node.startswith("Input Port:"):
        return "input"
    if node.startswith("Parameter:"):
        return "parameter"
    if node.endswith("?"):
        return "decision"
    if node.startswith("Output "):
        return "output"
    if node.startswith("ScenarioReport."):
        return "report"
    return "source"


def _shorten(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "..."


def _css() -> str:
    return "\n".join(
        [
            "    :root { color-scheme: light; --ink: #172026; --muted: #526066; --line: #c9d6d3; --accent: #2f5d62; --paper: #f7faf9; }",
            '    body { margin: 0; background: var(--paper); color: var(--ink); font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }',
            "    .shell { width: min(100% - 32px, 1180px); margin: 0 auto; padding: 24px 0 48px; }",
            "    .hero, .panel { background: #fff; border: 1px solid var(--line); border-radius: 8px; padding: 20px; margin-bottom: 16px; }",
            "    .hero p { margin: 0 0 4px; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; font-size: 12px; }",
            "    h1, h2, h3 { margin: 0 0 10px; }",
            "    h1 { font-size: 28px; }",
            "    h2 { font-size: 20px; }",
            "    h3 { font-size: 15px; margin-top: 16px; }",
            "    .diagram { width: 100%; min-height: 260px; background: #fbfdfc; border: 1px solid var(--line); border-radius: 8px; margin: 8px 0 14px; }",
            "    .node { fill: #fff; stroke: var(--accent); stroke-width: 1.4; }",
            "    .node-title { font-weight: 700; font-size: 11px; fill: var(--ink); }",
            "    .node-note, .edge-label { font-size: 10px; fill: var(--muted); }",
            "    .edge { fill: none; stroke: var(--accent); stroke-width: 1.5; marker-end: url(#arrow); }",
            "    table { width: 100%; border-collapse: collapse; }",
            "    th, td { border-top: 1px solid var(--line); padding: 8px; text-align: left; vertical-align: top; }",
            "    th { color: var(--muted); font-size: 12px; }",
            "    code { background: #eef5f3; border-radius: 4px; padding: 1px 4px; }",
        ]
    )
