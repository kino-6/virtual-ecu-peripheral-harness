from __future__ import annotations

from html import escape

from veph.ir import MbdModelIR
from veph.model_loader import Block, Connection, PeripheralModel, Transition


def export_demo_html(model: PeripheralModel | MbdModelIR) -> str:
    if isinstance(model, MbdModelIR):
        return _export_ir_demo_html(model)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            f"  <title>{escape(model.name)} MBD Demo</title>",
            "  <style>",
            _css(),
            "  </style>",
            "</head>",
            "<body>",
            '  <main class="shell">',
            _hero(model),
            _mbd_block_diagram(model),
            _data_flow_svg(),
            _state_machine_svg(model),
            _model_tables(model),
            _artifact_policy(),
            "  </main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _export_ir_demo_html(model: MbdModelIR) -> str:
    flow_rows = "\n".join(
        f"          <tr><td>{escape(flow.source)}</td><td>{escape(flow.target)}</td><td>{escape(flow.label)}</td></tr>"
        for flow in model.flows
    )
    state_rows = "\n".join(
        f"          <tr><td>{escape(transition.source)}</td><td>{escape(transition.target)}</td><td>{escape(transition.condition)}</td></tr>"
        for transition in model.transitions
    )
    port_rows = "\n".join(
        f"          <tr><td>{escape(port.direction)}</td><td>{escape(port.name)}</td><td>{escape(port.type)}</td><td>{escape(port.default or '')}</td></tr>"
        for port in model.ports.values()
    )
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            f"  <title>{escape(model.component.name)} Markup-to-MBD Demo</title>",
            "  <style>",
            _css(),
            "  </style>",
            "</head>",
            "<body>",
            '  <main class="shell">',
            '    <section class="hero">',
            '      <div class="hero-copy">',
            "        <p>Author in text. Verify in MBD tools.</p>",
            f"        <h1>{escape(model.component.name)} Markup-to-MBD Demo</h1>",
            "        <span>Generated from Mermaid-like Markdown markup. This is a preview, not the verification backend.</span>",
            "      </div>",
            '      <div class="hero-facts" aria-label="model facts">',
            f"        <div><strong>{len(model.ports)}</strong><span>ports</span></div>",
            f"        <div><strong>{len(model.registers)}</strong><span>registers</span></div>",
            f"        <div><strong>{len(model.transitions)}</strong><span>state transitions</span></div>",
            f"        <div><strong>{len(model.flows)}</strong><span>flow edges</span></div>",
            "      </div>",
            "    </section>",
            '    <section class="panel">',
            "      <h2>Markup Sections</h2>",
            "      <p>The source is the Markdown authoring file. The IR and diagrams are generated artifacts.</p>",
            "      <ul>",
            *(f"        <li><code>{escape(section.language)}</code></li>" for section in model.sections),
            "      </ul>",
            "    </section>",
            '    <section class="grid">',
            '      <section class="panel">',
            "        <h2>Ports</h2>",
            "        <table><thead><tr><th>Dir</th><th>Name</th><th>Type</th><th>Default</th></tr></thead><tbody>",
            flow_or_empty(port_rows),
            "        </tbody></table>",
            "      </section>",
            '      <section class="panel">',
            "        <h2>State Handoff</h2>",
            "        <table><thead><tr><th>From</th><th>To</th><th>Condition</th></tr></thead><tbody>",
            flow_or_empty(state_rows),
            "        </tbody></table>",
            "      </section>",
            "    </section>",
            '    <section class="panel">',
            "      <h2>Flow Handoff</h2>",
            "      <table><thead><tr><th>Source</th><th>Target</th><th>Label</th></tr></thead><tbody>",
            flow_or_empty(flow_rows),
            "      </tbody></table>",
            "    </section>",
            '    <section class="panel policy">',
            "      <h2>Verification Boundary</h2>",
            "      <p>Use generated Simulink, Modelica, SCXML, and FMI-oriented artifacts for MBD tool handoff. Python remains preview-only.</p>",
            "    </section>",
            "  </main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def flow_or_empty(rows: str) -> str:
    return rows if rows else '          <tr><td colspan="4">None</td></tr>'


def _hero(model: PeripheralModel) -> str:
    return "\n".join(
        [
            '    <section class="hero">',
            '      <div class="hero-copy">',
            "        <p>Textual MBD YAML is the source of truth</p>",
            f"        <h1>{escape(model.name)} MBD Demo</h1>",
            f"        <span>{escape(model.description)}</span>",
            "      </div>",
            '      <div class="hero-facts" aria-label="model facts">',
            f"        <div><strong>{escape(model.kind)}</strong><span>model kind</span></div>",
            f"        <div><strong>{escape(model.bus.type.upper())} mode {model.bus.mode}</strong><span>bus</span></div>",
            f"        <div><strong>{len(model.registers)}</strong><span>registers</span></div>",
            f"        <div><strong>{len(model.states.nodes)}</strong><span>states</span></div>",
            "      </div>",
            "    </section>",
        ]
    )


def _data_flow_svg() -> str:
    nodes = [
        ("Textual MBD YAML", 30, 76, "canonical model"),
        ("Scenario YAML", 30, 190, "test stimulus"),
        ("Scenario Runner", 285, 134, "time ordered steps"),
        ("Peripheral Runtime", 540, 134, "register/state behavior"),
        ("Virtual SPI/HAL Boundary", 795, 134, "hardware replacement"),
        ("Product-like ECU code", 1050, 134, "unchanged logic"),
        ("Generated Artifacts", 540, 300, "docs, diagrams, exports"),
    ]
    arrows = [
        (230, 111, 285, 151),
        (230, 225, 285, 181),
        (485, 164, 540, 164),
        (740, 164, 795, 164),
        (995, 164, 1050, 164),
        (640, 200, 640, 300),
        (130, 111, 540, 316),
    ]
    parts = [
        '    <section class="panel">',
        "      <h2>Boundary Data Flow</h2>",
        "      <p>The model block diagram above defines peripheral behavior. This view shows how scenario inputs reach unchanged ECU-like code through the virtual hardware boundary.</p>",
        '      <svg class="diagram" viewBox="0 0 1280 390" role="img" aria-label="Data flow from Textual MBD YAML to virtual peripheral and generated artifacts">',
        "        <defs>",
        '          <marker id="arrow" markerWidth="12" markerHeight="12" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">',
        '            <path d="M0,0 L0,6 L9,3 z" fill="#2f5d62"></path>',
        "          </marker>",
        "        </defs>",
    ]
    for x1, y1, x2, y2 in arrows:
        parts.append(
            f'        <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="arrow"></line>'
        )
    for title, x, y, note in nodes:
        parts.extend(_svg_node(title, x, y, note))
    parts.extend(["      </svg>", "    </section>"])
    return "\n".join(parts)


def _mbd_block_diagram(model: PeripheralModel) -> str:
    positions = _block_positions(model)
    parts = [
        '    <section class="panel">',
        "      <h2>MBD Block Diagram</h2>",
        "      <p>Functional blocks, typed ports, and signal lines are generated from the YAML `blocks` and `connections` sections.</p>",
        '      <svg class="diagram mbd" viewBox="0 0 1280 560" role="img" aria-label="MBD block diagram with ports and signal connections">',
        "        <defs>",
        '          <marker id="signalArrow" markerWidth="12" markerHeight="12" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">',
        '            <path d="M0,0 L0,6 L9,3 z" fill="#256f3f"></path>',
        "          </marker>",
        "        </defs>",
    ]
    for connection in model.connections:
        parts.extend(_connection_line(connection, model.blocks, positions))
    for block in model.blocks.values():
        parts.extend(_block_svg(block, positions[block.name]))
    parts.extend(["      </svg>", "    </section>"])
    return "\n".join(parts)


def _block_positions(model: PeripheralModel) -> dict[str, tuple[int, int]]:
    preferred = {
        "VoltageInput": (50, 82),
        "ThresholdParameter": (50, 312),
        "UndervoltageComparator": (330, 160),
        "FaultLatch": (610, 160),
        "ReadyLogic": (610, 354),
        "RegisterMap": (900, 190),
    }
    positions: dict[str, tuple[int, int]] = {}
    fallback_index = 0
    for block_name in model.blocks:
        if block_name in preferred:
            positions[block_name] = preferred[block_name]
            continue
        row = fallback_index // 3
        col = fallback_index % 3
        positions[block_name] = (50 + col * 290, 82 + row * 210)
        fallback_index += 1
    return positions


def _block_svg(block: Block, position: tuple[int, int]) -> list[str]:
    x, y = position
    width = 230
    height = max(128, 68 + 24 * max(len(block.inputs), len(block.outputs), 1))
    parts = [
        f'        <rect x="{x}" y="{y}" width="{width}" height="{height}" rx="8" class="mbd-block"></rect>',
        f'        <text x="{x + 16}" y="{y + 28}" class="block-title">{escape(block.name)}</text>',
        f'        <text x="{x + 16}" y="{y + 50}" class="block-kind">{escape(block.kind)}</text>',
    ]
    for index, port in enumerate(block.inputs.values()):
        py = _port_y(y, index)
        parts.append(f'        <circle cx="{x}" cy="{py}" r="5" class="input-port"></circle>')
        parts.append(f'        <text x="{x + 14}" y="{py + 4}" class="port-label">{escape(port.name)} : {escape(port.type)}</text>')
    for index, port in enumerate(block.outputs.values()):
        py = _port_y(y, index)
        parts.append(f'        <circle cx="{x + width}" cy="{py}" r="5" class="output-port"></circle>')
        parts.append(f'        <text x="{x + width - 14}" y="{py + 4}" text-anchor="end" class="port-label">{escape(port.name)} : {escape(port.type)}</text>')
    return parts


def _connection_line(
    connection: Connection,
    blocks: dict[str, Block],
    positions: dict[str, tuple[int, int]],
) -> list[str]:
    source_block_name, source_port_name = connection.source.split(".", 1)
    target_block_name, target_port_name = connection.target.split(".", 1)
    source_block = blocks[source_block_name]
    target_block = blocks[target_block_name]
    sx, sy = positions[source_block_name]
    tx, ty = positions[target_block_name]
    source_index = list(source_block.outputs).index(source_port_name)
    target_index = list(target_block.inputs).index(target_port_name)
    x1 = sx + 230
    y1 = _port_y(sy, source_index)
    x2 = tx
    y2 = _port_y(ty, target_index)
    mid_x = (x1 + x2) / 2
    label_x = (x1 + x2) / 2
    label_y = min(y1, y2) - 10 if abs(y1 - y2) < 36 else (y1 + y2) / 2 - 8
    return [
        f'        <path d="M {x1} {y1} C {mid_x:.0f} {y1}, {mid_x:.0f} {y2}, {x2} {y2}" class="signal-line"></path>',
        f'        <text x="{label_x:.0f}" y="{label_y:.0f}" text-anchor="middle" class="signal-label">{escape(connection.signal)}</text>',
    ]


def _port_y(block_y: int, index: int) -> int:
    return block_y + 76 + index * 24


def _state_machine_svg(model: PeripheralModel) -> str:
    x_positions = [70 + index * 285 for index in range(len(model.states.nodes))]
    node_positions = dict(zip(model.states.nodes, x_positions))
    parts = [
        '    <section class="panel">',
        "      <h2>State Machine</h2>",
        "      <p>State nodes and transitions are generated from the YAML `states` section.</p>",
        '      <svg class="diagram" viewBox="0 0 1280 260" role="img" aria-label="State machine diagram">',
        "        <defs>",
        '          <marker id="stateArrow" markerWidth="12" markerHeight="12" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">',
        '            <path d="M0,0 L0,6 L9,3 z" fill="#475569"></path>',
        "          </marker>",
        "        </defs>",
    ]
    for transition in model.states.transitions:
        parts.extend(_transition_line(transition, node_positions))
    for node in model.states.nodes:
        x = node_positions[node]
        css_class = "state initial" if node == model.states.initial else "state"
        parts.append(f'        <rect x="{x}" y="92" width="210" height="72" rx="8" class="{css_class}"></rect>')
        parts.append(f'        <text x="{x + 105}" y="134" text-anchor="middle" class="state-label">{escape(node)}</text>')
    parts.extend(["      </svg>", "    </section>"])
    return "\n".join(parts)


def _transition_line(transition: Transition, node_positions: dict[str, int]) -> list[str]:
    x1 = node_positions[transition.source] + 210
    x2 = node_positions[transition.target]
    y = 128
    if x2 > x1:
        return [
            f'        <line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" class="state-arrow"></line>',
            f'        <text x="{(x1 + x2) / 2:.0f}" y="{y - 16}" text-anchor="middle" class="edge-label">{escape(transition.source)} -> {escape(transition.target)}</text>',
            f'        <text x="{(x1 + x2) / 2:.0f}" y="{y + 28}" text-anchor="middle" class="edge-note">{escape(transition.when)}</text>',
        ]
    arc_start = node_positions[transition.source] + 105
    arc_end = node_positions[transition.target] + 105
    return [
        f'        <path d="M {arc_start} 92 C {arc_start} 28, {arc_end} 28, {arc_end} 92" class="state-arrow"></path>',
        f'        <text x="{(arc_start + arc_end) / 2:.0f}" y="42" text-anchor="middle" class="edge-label">{escape(transition.source)} -> {escape(transition.target)}</text>',
        f'        <text x="{(arc_start + arc_end) / 2:.0f}" y="62" text-anchor="middle" class="edge-note">{escape(transition.when)}</text>',
    ]


def _model_tables(model: PeripheralModel) -> str:
    return "\n".join(
        [
            '    <section class="grid">',
            _register_table(model),
            _signal_fault_table(model),
            "    </section>",
        ]
    )


def _register_table(model: PeripheralModel) -> str:
    rows: list[str] = []
    for register in model.registers.values():
        field_text = ", ".join(f"{field.name}" for field in register.fields.values())
        rows.append(
            "          <tr>"
            f"<td>{escape(register.name)}</td>"
            f"<td>0x{register.address:02X}</td>"
            f"<td>{register.width}</td>"
            f"<td>{escape(register.access)}</td>"
            f"<td>{escape(field_text)}</td>"
            "</tr>"
        )
    return "\n".join(
        [
            '      <section class="panel">',
            "        <h2>Register View</h2>",
            "        <table>",
            "          <thead><tr><th>Register</th><th>Address</th><th>Width</th><th>Access</th><th>Fields</th></tr></thead>",
            "          <tbody>",
            *rows,
            "          </tbody>",
            "        </table>",
            "      </section>",
        ]
    )


def _signal_fault_table(model: PeripheralModel) -> str:
    signal_items = [
        f"          <li><strong>{escape(signal.name)}</strong>: default {escape(str(signal.default))} {escape(signal.unit or '')}</li>"
        for signal in model.input_signals.values()
    ]
    output_items = [
        f"          <li><strong>{escape(signal.name)}</strong>: {escape(signal.type or 'value')}</li>"
        for signal in model.output_signals.values()
    ]
    fault_items = [
        f"          <li><strong>{escape(fault.name)}</strong>: {escape(fault.effect)}</li>"
        for fault in model.faults.values()
    ]
    return "\n".join(
        [
            '      <section class="panel">',
            "        <h2>Signals And Faults</h2>",
            "        <h3>Inputs</h3>",
            "        <ul>",
            *signal_items,
            "        </ul>",
            "        <h3>Outputs</h3>",
            "        <ul>",
            *output_items,
            "        </ul>",
            "        <h3>Faults</h3>",
            "        <ul>",
            *fault_items,
            "        </ul>",
            "      </section>",
        ]
    )


def _artifact_policy() -> str:
    return "\n".join(
        [
            '    <section class="panel policy">',
            "      <h2>Generated Artifact Policy</h2>",
            "      <p>This page is generated output. Edit the Textual MBD YAML, then regenerate the demo. Tool-specific files are views, not the model source.</p>",
            "    </section>",
        ]
    )


def _svg_node(title: str, x: int, y: int, note: str) -> list[str]:
    return [
        f'        <rect x="{x}" y="{y}" width="200" height="70" rx="8" class="node"></rect>',
        f'        <text x="{x + 100}" y="{y + 30}" text-anchor="middle" class="node-title">{escape(title)}</text>',
        f'        <text x="{x + 100}" y="{y + 52}" text-anchor="middle" class="node-note">{escape(note)}</text>',
    ]


def _css() -> str:
    return """
    :root {
      color-scheme: light;
      --ink: #172026;
      --muted: #5f6f76;
      --line: #c7d2d6;
      --panel: #ffffff;
      --page: #eef3f2;
      --accent: #2f5d62;
      --accent-soft: #dcebea;
      --warn: #8a4b25;
      --warn-soft: #f6e7d8;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--page);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }
    .shell {
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 40px;
    }
    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1.4fr) minmax(280px, 0.8fr);
      gap: 20px;
      align-items: stretch;
      margin-bottom: 18px;
    }
    .hero-copy, .hero-facts, .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }
    .hero-copy { padding: 28px; }
    .hero-copy p {
      margin: 0 0 8px;
      color: var(--accent);
      font-size: 14px;
      font-weight: 700;
      text-transform: uppercase;
    }
    h1 {
      margin: 0 0 12px;
      font-size: clamp(32px, 5vw, 56px);
      letter-spacing: 0;
      line-height: 1;
    }
    h2 {
      margin: 0 0 8px;
      font-size: 22px;
      letter-spacing: 0;
    }
    h3 {
      margin: 18px 0 6px;
      font-size: 15px;
      letter-spacing: 0;
    }
    p, span, li, td, th { color: var(--muted); }
    .hero-facts {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 1px;
      overflow: hidden;
      background: var(--line);
    }
    .hero-facts div {
      background: var(--panel);
      padding: 18px;
    }
    .hero-facts strong {
      display: block;
      color: var(--ink);
      font-size: 20px;
    }
    .hero-facts span {
      display: block;
      margin-top: 4px;
      font-size: 13px;
    }
    .panel {
      padding: 22px;
      margin-bottom: 18px;
      overflow-x: auto;
    }
    .grid {
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
      gap: 18px;
    }
    .diagram {
      display: block;
      width: 100%;
      min-width: 820px;
      height: auto;
      margin-top: 16px;
      background: #f9fbfb;
      border: 1px solid var(--line);
      border-radius: 8px;
    }
    .node, .state {
      fill: #ffffff;
      stroke: #9fb2b7;
      stroke-width: 2;
    }
    .mbd-block {
      fill: #ffffff;
      stroke: #78909a;
      stroke-width: 2;
      filter: drop-shadow(0 2px 2px rgba(23, 32, 38, 0.08));
    }
    .initial { fill: var(--accent-soft); stroke: var(--accent); }
    .arrow, .state-arrow {
      stroke: var(--accent);
      stroke-width: 2.5;
      fill: none;
      marker-end: url(#arrow);
    }
    .state-arrow { stroke: #475569; marker-end: url(#stateArrow); }
    .signal-line {
      stroke: #256f3f;
      stroke-width: 2.5;
      fill: none;
      marker-end: url(#signalArrow);
    }
    .input-port { fill: #ffffff; stroke: #256f3f; stroke-width: 2; }
    .output-port { fill: #256f3f; stroke: #256f3f; stroke-width: 2; }
    .node-title, .state-label {
      fill: var(--ink);
      font-size: 17px;
      font-weight: 700;
    }
    .block-title {
      fill: var(--ink);
      font-size: 16px;
      font-weight: 800;
    }
    .block-kind {
      fill: var(--accent);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }
    .port-label {
      fill: #334155;
      font-size: 11px;
    }
    .signal-label {
      fill: #1f5f36;
      font-size: 12px;
      font-weight: 700;
    }
    .node-note, .edge-note {
      fill: var(--muted);
      font-size: 13px;
    }
    .edge-label {
      fill: #334155;
      font-size: 13px;
      font-weight: 700;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
      font-size: 14px;
    }
    th, td {
      padding: 10px 8px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }
    th { color: var(--ink); font-weight: 700; }
    ul {
      margin: 0;
      padding-left: 20px;
    }
    .policy {
      border-color: #e0c3a8;
      background: var(--warn-soft);
    }
    .policy h2 { color: var(--warn); }
    @media (max-width: 840px) {
      .hero, .grid { grid-template-columns: 1fr; }
      .shell { width: min(100vw - 20px, 1180px); padding-top: 10px; }
      .hero-copy, .panel { padding: 16px; }
      h1 { font-size: 34px; }
    }
    """.strip()
