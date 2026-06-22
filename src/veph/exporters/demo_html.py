from __future__ import annotations

from html import escape

from veph.control_semantics import (
    find_threshold_pair,
    primary_condition_terms,
    primary_output_action,
    report_for_signal,
    source_for_signal,
)
from veph.exporters.evidence_html import (
    spec_verification_data as _spec_verification_data,
    spec_verification_summary_html as _spec_verification_summary_html,
)
from veph.exporters.html_helpers import (
    ir_svg_node as _ir_svg_node,
    semantic_svg_node as _semantic_svg_node,
    shorten as _shorten,
    svg_defs as _svg_defs,
    svg_node as _svg_node,
)
from veph.exporters.state_review_html import (
    control_actions as _control_actions,
    control_rule_for_transition as _control_rule_for_transition,
    ir_state_machine_review_dashboard as _ir_state_machine_review_dashboard,
    ir_state_machine_review_package as _ir_state_machine_review_package,
    ir_state_machine_review_script as _ir_state_machine_review_script,
    ir_state_machine_svg as _ir_state_machine_svg,
    ordered_states as _ordered_states,
)
from veph.ir import ControlRuleIR, MbdModelIR, TransitionIR
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
    has_spec_review = _has_spec_review(model)
    if has_spec_review:
        return _export_spec_review_html(model)
    function_rows = _ir_function_rows(model)
    req_rows = _ir_requirement_rows(model)
    control_rows = _ir_control_rows(model)
    harness_rows = _ir_harness_rows(model)
    flow_rows = _ir_flow_rows(model)
    state_rows = _ir_state_rows(model)
    port_rows = _ir_port_rows(model)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            f"  <title>{escape(model.component.name)} MBD Review Artifact</title>",
            "  <style>",
            _css(),
            "  </style>",
            "</head>",
            "<body>",
            '  <main class="shell">',
            '    <section class="hero">',
            '      <div class="hero-copy">',
            "        <p>Author in text. Review against the specification.</p>",
            f"        <h1>{escape(model.component.name)} MBD Review Artifact</h1>",
            "        <span>Generated from Mermaid-like Markdown markup. Use this page to ask whether the MBD matches the specification; external MBD tools remain the verification backend.</span>",
            "      </div>",
            '      <div class="hero-facts" aria-label="model facts">',
            f"        <div><strong>{len(model.ports)}</strong><span>ports</span></div>",
            f"        <div><strong>{len(model.functions)}</strong><span>functions</span></div>",
            f"        <div><strong>{len(model.controls)}</strong><span>control rules</span></div>",
            f"        <div><strong>{len(model.harness_devices)}</strong><span>harness boundaries</span></div>",
            "      </div>",
            "    </section>",
            _ir_spec_first_state_machine_review(model),
            _ir_review_objective_panel(model),
            _ir_review_evidence_map(model),
            "" if has_spec_review else _ir_state_machine_review_dashboard(model),
            _ir_review_pipeline_svg(model),
            _ir_design_overview_svg(model),
            _ir_semantic_mbd_svg(model),
            _ir_functional_decomposition_svg(model),
            '    <section class="panel">',
            "      <h2>Functional Decomposition</h2>",
            "      <p>This is the first architecture review view: responsibilities, owned signals, interfaces, requirement trace, and scenario evidence are allocated before detailed control rules.</p>",
            "      <table><thead><tr><th>Function</th><th>Responsibility</th><th>Owns</th><th>Inputs</th><th>Outputs</th><th>Trace</th><th>Scenarios</th></tr></thead><tbody>",
            flow_or_empty(function_rows, colspan=7),
            "      </tbody></table>",
            "    </section>",
            _ir_spec_compliance_review(model),
            _ir_mbd_review_checklist(),
            _ir_control_semantics_summary(),
            _ir_data_flow_svg(model),
            "" if has_spec_review else _ir_state_machine_review_package(model),
            "" if has_spec_review else _ir_state_machine_svg(model),
            _ir_harness_evidence_boundary_panel(model),
            _ir_harness_boundary_svg(model),
            '    <section class="panel">',
            "      <h2>Requirements Trace Matrix</h2>",
            "      <p>Each row links a requirement ID to the parsed MBD elements that carry it. This is evidence for review, not a certification claim.</p>",
            "      <table><thead><tr><th>Requirement</th><th>MBD elements</th></tr></thead><tbody>",
            flow_or_empty(req_rows, colspan=2),
            "      </tbody></table>",
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
            "        <p>Lifecycle/topology view derived from the control decision table; executable behavior is owned by <code>mbd-control</code>.</p>",
            "        <table><thead><tr><th>From</th><th>To</th><th>Condition</th></tr></thead><tbody>",
            flow_or_empty(state_rows),
            "        </tbody></table>",
            "      </section>",
            "    </section>",
            '    <section class="grid">',
            '      <section class="panel">',
            "        <h2>Control Decision Table</h2>",
            "        <p>Selection policy: lower numeric priority wins after state scope and guard match.</p>",
            "        <table><thead><tr><th>Priority</th><th>Rule</th><th>Owner</th><th>State scope</th><th>Guard</th><th>Actions</th><th>Trace</th><th>Scenarios</th></tr></thead><tbody>",
            flow_or_empty(control_rows, colspan=8),
            "        </tbody></table>",
            "      </section>",
            '      <section class="panel">',
            "        <h2>Harness Boundary</h2>",
            "        <table><thead><tr><th>Name</th><th>Role</th><th>Boundary</th><th>Trace</th></tr></thead><tbody>",
            flow_or_empty(harness_rows),
            "        </tbody></table>",
            "      </section>",
            "    </section>",
            '    <section class="panel">',
            "      <h2>Flow Handoff</h2>",
            "      <table><thead><tr><th>Source</th><th>Target</th><th>Label</th><th>Trace</th></tr></thead><tbody>",
            flow_or_empty(flow_rows),
            "      </tbody></table>",
            "    </section>",
            '    <section class="panel policy">',
            "      <h2>Verification Boundary</h2>",
            "      <p>Use generated Simulink, Modelica, SCXML, and FMI-oriented artifacts for MBD tool handoff. Python remains preview-only.</p>",
            "    </section>",
            "  </main>",
            _ir_state_machine_review_script(model),
            "</body>",
            "</html>",
            "",
        ]
    )


def _export_spec_review_html(model: MbdModelIR) -> str:
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="ja">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            f"  <title>{escape(model.component.name)} MBDレビュー</title>",
            "  <style>",
            _css(),
            "  </style>",
            "</head>",
            "<body>",
            '  <main class="shell compact-shell">',
            '    <section class="hero compact-hero">',
            '      <div class="hero-copy">',
            "        <p>Spec-first MBD review</p>",
            f"        <h1>{escape(model.component.name)} MBDレビュー</h1>",
            "        <span>まず一致/差分/未決だけを確認します。詳細証跡は補助資料です。</span>",
            "      </div>",
            '      <div class="hero-facts" aria-label="model facts">',
            f"        <div><strong>{len(model.ports)}</strong><span>ポート</span></div>",
            f"        <div><strong>{len(model.transitions)}</strong><span>遷移</span></div>",
            f"        <div><strong>{len(model.controls)}</strong><span>制御ルール</span></div>",
            f"        <div><strong>{len(model.requirement_refs())}</strong><span>要求ID</span></div>",
            "      </div>",
            "    </section>",
            _ir_spec_first_state_machine_review(model),
            _spec_review_footer(model),
            "  </main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def flow_or_empty(rows: str, colspan: int = 4) -> str:
    return rows if rows else f'          <tr><td colspan="{colspan}">None</td></tr>'


def _has_spec_review(model: MbdModelIR) -> bool:
    return any(section.language == "mbd-spec-review" for section in model.sections)


def _ir_spec_first_state_machine_review(model: MbdModelIR) -> str:
    spec = _spec_review_data(model)
    if spec is None or not model.transitions:
        return ""
    verification = _spec_verification_data(model, spec)
    intent_rows = "\n".join(_spec_intent_row(model, spec, item) for item in spec["intents"])
    transition_rows = "\n".join(
        _spec_transition_compare_row(model, transition)
        for transition in spec["transitions"]
    )
    open_question_rows = "\n".join(
        f"          <tr><td>{escape(_ja_open_question(question))}</td><td>受け入れ前に人間が判断する。</td></tr>"
        for question in spec["open_questions"]
    )
    unsupported_rows = "\n".join(
        f"          <tr><td>{escape(_ja_unsupported(item))}</td><td>この資料から挙動を推定しない。</td></tr>"
        for item in spec["unsupported"]
    )
    initial = spec["initial"] or (_ordered_states(model.transitions)[0] if model.transitions else "")
    generated_initial = _ordered_states(model.transitions)[0] if model.transitions else ""
    initial_status = "一致" if initial == generated_initial else "要確認"
    return "\n".join(
        [
            '    <section class="panel spec-first-review">',
            "      <h2>状態図レビュー</h2>",
            "      <p class=\"evidence-note\">初期状態、遷移方向、ガード条件、出力効果だけを見る。Harnessと要求詳細は後段の補助証跡。</p>",
            _one_minute_review_html(model, spec, initial, generated_initial, initial_status),
            "      <div class=\"review-compare\">",
            _state_review_svg("仕様の状態図", spec["transitions"], initial),
            _state_review_svg(
                "MBD状態図",
                [
                    {"source": transition.source, "target": transition.target, "condition": transition.condition}
                    for transition in model.transitions
                ],
                generated_initial,
            ),
            "      </div>",
            "      <h3>状態遷移の確認</h3>",
            "      <table class=\"review-table compact\">",
            "        <thead><tr><th>仕様</th><th>MBD</th><th>Trace</th><th>判定</th></tr></thead>",
            "        <tbody>",
            flow_or_empty(transition_rows, colspan=4),
            "        </tbody>",
            "      </table>",
            _spec_verification_summary_html(verification),
            "      <details class=\"review-details\">",
            "        <summary>要求ごとの確認</summary>",
            "        <table class=\"review-table compact\">",
            "          <thead><tr><th>要求</th><th>意図</th><th>MBD / シナリオ</th><th>判定</th></tr></thead>",
            "          <tbody>",
            flow_or_empty(intent_rows, colspan=4),
            "          </tbody>",
            "        </table>",
            "      </details>",
            "      <details class=\"review-details\">",
            "        <summary>未解決QA / 対象外</summary>",
            "        <table class=\"review-table compact\">",
            "          <thead><tr><th>確認事項</th><th>扱い</th></tr></thead>",
            "          <tbody>",
            flow_or_empty(open_question_rows, colspan=2),
            "          </tbody>",
            "        </table>",
            "        <table class=\"review-table compact\">",
            "          <thead><tr><th>対象外の挙動</th><th>レビュー上の扱い</th></tr></thead>",
            "          <tbody>",
            flow_or_empty(unsupported_rows, colspan=2),
            "          </tbody>",
            "        </table>",
            "      </details>",
            "    </section>",
        ]
    )


def _one_minute_review_html(
    model: MbdModelIR,
    spec: dict[str, object],
    initial: str,
    generated_initial: str,
    initial_status: str,
) -> str:
    transition_count = len(
        [transition for transition in spec["transitions"] if transition["source"] != "[*]"]  # type: ignore[index]
    )
    generated_count = len(model.transitions)
    open_count = len(spec["open_questions"])  # type: ignore[arg-type]
    return "\n".join(
        [
            "      <h3>1分レビュー</h3>",
            "      <table class=\"review-table compact\">",
            "        <thead><tr><th>状態図の観点</th><th>見るもの</th><th>結果</th></tr></thead>",
            "        <tbody>",
            f"          <tr><td>初期状態</td><td>開始状態</td><td>{escape(initial)} / {escape(generated_initial)} ({escape(initial_status)})</td></tr>",
            f"          <tr><td>状態遷移</td><td>方向とガード</td><td>{transition_count} / {generated_count}件</td></tr>",
            f"          <tr><td>出力効果</td><td>state / output action</td><td>{escape(_state_output_effect_summary(model))}</td></tr>",
            f"          <tr><td>未決事項</td><td>後段QA</td><td>{open_count}件</td></tr>",
            "        </tbody>",
            "      </table>",
        ]
    )


def _state_output_effect_summary(model: MbdModelIR) -> str:
    output_names = [port.name for port in model.ports.values() if port.direction == "out"]
    if not output_names:
        return "状態のみ"
    return ", ".join(output_names[:3])


def _verification_compact_summary(verification: list[dict[str, object]]) -> str:
    if not verification:
        return "未定義"
    statuses = sorted({str(row.get("status", "未確認")) for row in verification})
    steps = sum(int(str(row.get("steps") or "0")) for row in verification)
    return f"{'/'.join(statuses)} / {steps} step"


def _spec_review_data(model: MbdModelIR) -> dict[str, object] | None:
    body = next((section.body for section in model.sections if section.language == "mbd-spec-review"), "")
    if not body:
        return None
    data: dict[str, object] = {
        "source": "",
        "question": "",
        "initial": "",
        "intents": [],
        "transitions": [],
        "trace_intents": [],
        "scenarios": [],
        "open_questions": [],
        "unsupported": [],
    }
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("source "):
            data["source"] = line.removeprefix("source ").strip()
        elif line.startswith("question "):
            data["question"] = line.removeprefix("question ").strip()
        elif line.startswith("intent "):
            req, text = _split_pipe(line.removeprefix("intent "))
            data["intents"].append({"requirement": req, "text": text})  # type: ignore[index, union-attr]
        elif line.startswith("spec-initial "):
            data["initial"] = line.removeprefix("spec-initial ").strip()
        elif line.startswith("spec-transition "):
            data["transitions"].append(_parse_review_transition(line.removeprefix("spec-transition ")))  # type: ignore[index, union-attr]
        elif line.startswith("trace-intent "):
            data["trace_intents"].append(_parse_trace_intent_line(line.removeprefix("trace-intent ")))  # type: ignore[index, union-attr]
        elif line.startswith("scenario "):
            scenario, report = _split_pipe(line.removeprefix("scenario "))
            data["scenarios"].append((scenario, report))  # type: ignore[index, union-attr]
        elif line.startswith("open-question "):
            _, question = _split_pipe(line.removeprefix("open-question "))
            data["open_questions"].append(question)  # type: ignore[index, union-attr]
        elif line.startswith("unsupported "):
            data["unsupported"].append(line.removeprefix("unsupported ").strip())  # type: ignore[index, union-attr]
    return data


def _spec_review_footer(model: MbdModelIR) -> str:
    return "\n".join(
        [
            '    <section class="panel policy">',
            "      <h2>確認範囲</h2>",
            f"      <p><code>{escape(model.source_path.name)}</code> 由来のレビュー資料です。Python/Harnessはpreview-only、正式検証は外部MBD環境です。</p>",
            "    </section>",
        ]
    )


def _split_pipe(text: str) -> tuple[str, str]:
    left, separator, right = text.partition("|")
    if separator != "|":
        return text.strip(), ""
    return left.strip(), right.strip()


def _parse_review_transition(text: str) -> dict[str, str]:
    left, _, condition = text.partition(":")
    source, _, target = left.partition("-->")
    return {
        "source": source.strip(),
        "target": target.strip(),
        "condition": condition.strip(),
    }


def _parse_trace_intent_line(text: str) -> dict[str, str]:
    requirement, rest = _split_pipe(text)
    transition, actions = _split_pipe(rest)
    source, _, target = transition.partition("-->")
    return {
        "requirement": requirement,
        "source": source.strip(),
        "target": target.strip(),
        "actions": actions,
    }


def _spec_intent_row(model: MbdModelIR, spec: dict[str, object], item: dict[str, str]) -> str:
    requirement = item["requirement"]
    evidence_items = _ir_elements_for_ref(model, requirement)
    evidence = _review_evidence_summary(evidence_items) or "MBD証跡なし"
    scenario = ", ".join(_ir_scenarios_for_ref(model, requirement)) or "Missing scenario evidence"
    status = "一致" if evidence != "MBD証跡なし" and scenario != "Missing scenario evidence" else "要確認"
    intent = _ja_requirement_summary(spec, requirement) or item["text"]
    mbd_and_scenario = f"{evidence} / {scenario}" if scenario != "Missing scenario evidence" else evidence
    return (
        "          <tr>"
        f"<td><code>{escape(requirement)}</code></td>"
        f"<td>{escape(intent)}</td>"
        f"<td>{escape(mbd_and_scenario)}</td>"
        f"<td>{escape(status)}</td>"
        "</tr>"
    )


def _review_evidence_summary(elements: list[str]) -> str:
    controls = [element.removeprefix("control:") for element in elements if element.startswith("control:")]
    if controls:
        return ", ".join(controls)
    if any(element.startswith("function:") for element in elements):
        return "MBD要素あり"
    if elements:
        return "補助証跡あり"
    return ""


def _spec_transition_compare_row(model: MbdModelIR, spec_transition: dict[str, str]) -> str:
    source = spec_transition["source"]
    target = spec_transition["target"]
    condition = spec_transition["condition"]
    if source == "[*]":
        generated_initial = _ordered_states(model.transitions)[0] if model.transitions else ""
        status = "一致" if target == generated_initial else "要確認"
        return (
            "          <tr>"
            f"<td><code>[*] -> {escape(target)}</code></td>"
            f"<td>初期状態 <code>{escape(generated_initial)}</code></td>"
            "<td>仕様構造</td>"
            f"<td>{escape(status)}</td>"
            "</tr>"
        )
    transition = next(
        (
            candidate
            for candidate in model.transitions
            if candidate.source == source
            and candidate.target == target
            and candidate.condition == condition
        ),
        None,
    )
    rule = _control_rule_for_transition(model.controls, transition) if transition is not None else None
    generated = (
        f"{transition.source} -> {transition.target} / {transition.condition}"
        if transition is not None
        else "Missing generated transition"
    )
    actions = _control_actions(rule)
    trace = ", ".join(rule.trace) if rule is not None and rule.trace else "Missing trace"
    status = "一致" if transition is not None and rule is not None and rule.trace else "要確認"
    generated_summary = f"{generated} / {actions}" if transition is not None else generated
    return (
        "          <tr>"
        f"<td><code>{escape(source)} -> {escape(target)}</code> / {escape(condition)}</td>"
        f"<td>{escape(generated_summary)}</td>"
        f"<td>{escape(trace)}</td>"
        f"<td>{escape(status)}</td>"
        "</tr>"
    )


def _ja_requirement_summary(spec: dict[str, object], requirement: str) -> str:
    trace_intents = spec.get("trace_intents", [])
    for item in trace_intents:
        if item["requirement"] != requirement:  # type: ignore[index]
            continue
        transition = f"{item['source']} -> {item['target']}"  # type: ignore[index]
        actions = item["actions"]  # type: ignore[index]
        return f"{transition}。出力/状態更新: {actions}。"
    intent_text = _spec_intent_text(spec, requirement)
    if "between the two thresholds" in intent_text and "keep its current state" in intent_text:
        return "2つの閾値の間では遷移せず、現在状態と出力を保持する。"
    if "expose" in intent_text and "reviewable MBD elements" in intent_text:
        return "入力、パラメータ、状態、出力をレビュー可能なMBD要素として分離する。"
    if "preview report" in intent_text:
        return "レポートに入力、手順、観測結果、期待結果、Pass/Failを分けて示す。"
    if requirement in {"SM-004"}:
        return "レポートに入力、手順、観測結果、期待結果、Pass/Failを分けて示す。"
    return ""


def _spec_intent_text(spec: dict[str, object], requirement: str) -> str:
    intents = spec.get("intents", [])
    for item in intents:
        if item["requirement"] == requirement:  # type: ignore[index]
            return str(item["text"])  # type: ignore[index]
    return ""


def _ja_open_question(question: str) -> str:
    if "implicit self-hold" in question:
        return "ガードが偽の場合は、プレビュー上は暗黙の自己保持として扱う。この解釈でよいか。"
    return question


def _ja_unsupported(item: str) -> str:
    if "Entry/during/exit" in item:
        return "entry/during/exit、階層状態、並列状態、履歴、時間イベント"
    return item


def _state_review_svg(title: str, transitions: list[dict[str, str]], initial: str) -> str:
    state_names: list[str] = []
    for transition in transitions:
        for state in [transition["source"], transition["target"]]:
            if state != "[*]" and state not in state_names:
                state_names.append(state)
    if initial and initial not in state_names:
        state_names.insert(0, initial)
    positions = {state: 96 + index * 190 for index, state in enumerate(state_names)}
    width = max(760, 160 + max(1, len(state_names)) * 190)
    parts = [
        '        <div class="evidence-card">',
        f"          <h4>{escape(title)}</h4>",
        f'          <svg class="mini-state-diagram" viewBox="0 0 {width} 190" role="img" aria-label="{escape(title)}">',
        *(_svg_defs("miniStateArrow")),
    ]
    if initial:
        parts.extend(
            [
                '            <circle cx="34" cy="92" r="10" class="initial-dot"></circle>',
                f'            <line x1="48" y1="92" x2="{positions.get(initial, 96)}" y2="92" class="ir-state-line"></line>',
                f'            <text x="{(48 + positions.get(initial, 96)) / 2:.0f}" y="80" text-anchor="middle" class="edge-note">initial</text>',
            ]
        )
    for transition in transitions:
        if transition["source"] == "[*]":
            continue
        x1 = positions[transition["source"]] + 120
        x2 = positions[transition["target"]]
        y = 92 if x2 > x1 else 132
        if x2 > x1:
            parts.append(f'            <line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" class="ir-state-line"></line>')
        else:
            mid = (x1 + x2) / 2
            parts.append(f'            <path d="M {x1} 132 C {mid:.0f} 170, {mid:.0f} 170, {x2} 132" class="ir-state-line"></path>')
        parts.append(
            f'            <text x="{(x1 + x2) / 2:.0f}" y="{y - 12}" text-anchor="middle" class="edge-note">{escape(_shorten(transition["condition"], 34))}</text>'
        )
    for state, x in positions.items():
        parts.extend(
            [
                f'            <rect x="{x}" y="62" width="120" height="60" rx="8" class="state"></rect>',
                f'            <text x="{x + 60}" y="98" text-anchor="middle" class="state-label">{escape(state)}</text>',
            ]
        )
    parts.extend(["          </svg>", "        </div>"])
    return "\n".join(parts)


def _ir_design_overview_svg(model: MbdModelIR) -> str:
    functions = model.functions[:1]
    inputs = [port for port in model.ports.values() if port.direction == "in"]
    outputs = [port for port in model.ports.values() if port.direction == "out"]
    if not functions or not inputs or not outputs:
        return ""
    function = functions[0]
    source = next((device.name for device in model.harness_devices if device.role == "source"), "ScenarioInput")
    report = next((flow.target for flow in model.flows if flow.target.startswith("ScenarioReport.")), "ScenarioReport.observedBehavior")
    input_positions = _stack_positions(len(inputs), 52, 74)
    output_positions = _stack_positions(len(outputs), 88, 94)
    height = max(300, max(input_positions[-1], output_positions[-1]) + 96)
    parts = [
        '    <section class="panel">',
        "      <h2>Spec-Oriented Model Review Diagram</h2>",
        "      <p>Generated from parsed ports, functional allocation, flows, harness boundaries, and report endpoints. Use this view to check whether the MBD shape matches the specification-level Mermaid design overview before detailed control-rule review.</p>",
        f'      <svg class="diagram" viewBox="0 0 1180 {height}" role="img" aria-label="Design overview generated from MBD source">',
        *(_svg_defs("irDesignArrow")),
        *(_semantic_svg_node([source], 42, height // 2 - 35, 190, "scenario source")),
        *(_semantic_svg_node([function.name], 536, height // 2 - 35, 230, "function")),
        *(_semantic_svg_node([report], 1036, height // 2 - 35, 130, "report")),
    ]
    source_center_y = height // 2
    function_center_y = height // 2
    report_center_y = height // 2
    for port, y in zip(inputs, input_positions):
        center_y = y + 35
        parts.extend(_semantic_svg_node(["Input Port", port.name], 266, y, 210, "model input"))
        parts.append(f'        <line x1="232" y1="{source_center_y}" x2="266" y2="{center_y}" class="ir-arrow"></line>')
        parts.append(
            f'        <text x="249" y="{(source_center_y + center_y) / 2 - 8:.0f}" text-anchor="middle" class="edge-note">{escape(port.name)}</text>'
        )
        parts.append(f'        <line x1="476" y1="{center_y}" x2="536" y2="{function_center_y}" class="ir-arrow"></line>')
    for port, y in zip(outputs, output_positions):
        center_y = y + 35
        parts.extend(_semantic_svg_node([f"Output {port.name}"], 806, y, 190, "model output"))
        parts.append(f'        <line x1="766" y1="{function_center_y}" x2="806" y2="{center_y}" class="ir-arrow"></line>')
        parts.append(f'        <line x1="996" y1="{center_y}" x2="1036" y2="{report_center_y}" class="ir-arrow"></line>')
    parts.extend(["      </svg>", "    </section>"])
    return "\n".join(parts)


def _stack_positions(count: int, first_y: int, gap: int) -> list[int]:
    if count <= 1:
        return [118]
    return [first_y + index * gap for index in range(count)]


def _ir_semantic_mbd_svg(model: MbdModelIR) -> str:
    threshold_pair = find_threshold_pair(model.controls)
    if threshold_pair is None:
        return ""
    true_rule, false_rule = threshold_pair
    primary_input, primary_parameter = primary_condition_terms(model, true_rule.condition_expr)
    source = source_for_signal(model.flows, primary_input) or "ScenarioInput"
    output_name = primary_output_action(model, true_rule) or primary_output_action(model, false_rule) or "output"
    report = report_for_signal(model.flows, output_name) or "ScenarioReport.observedBehavior"
    return "\n".join(
        [
            '    <section class="panel">',
            "      <h2>Semantic MBD Block Diagram</h2>",
            "      <p>Generated from parsed ports, parameters, control expressions, actions, and flows. This is the review model; the Markdown source is only the authoring input.</p>",
            '      <svg class="diagram" viewBox="0 0 1180 310" role="img" aria-label="Semantic MBD block diagram generated from parsed model semantics">',
            *(_svg_defs("irSemanticArrow")),
            *(_semantic_svg_node([source], 42, 118, 190, "scenario source")),
            *(_semantic_svg_node(["Input Port", primary_input or "input"], 266, 118, 210, "model input")),
            *(_semantic_svg_node(["Parameter", primary_parameter or "parameter"], 266, 36, 210, "model parameter")),
            '        <polygon points="650,108 735,153 650,198 565,153" class="rule-condition"></polygon>',
            f'        <text x="650" y="148" text-anchor="middle" class="node-title small">{escape(_shorten(true_rule.condition + "?", 30))}</text>',
            *(_semantic_svg_node(_semantic_output_action_lines(model, true_rule), 796, 72, 226, "true")),
            *(_semantic_svg_node(_semantic_output_action_lines(model, false_rule), 796, 184, 226, "false")),
            *(_semantic_svg_node(["ScenarioReport", "observedBehavior"], 1036, 118, 130, "observed")),
            '        <line x1="232" y1="153" x2="266" y2="153" class="ir-arrow"></line>',
            f'        <text x="249" y="144" text-anchor="middle" class="edge-note">{escape(primary_input or "input")}</text>',
            '        <line x1="476" y1="153" x2="565" y2="153" class="ir-arrow"></line>',
            '        <line x1="476" y1="71" x2="596" y2="126" class="ir-arrow"></line>',
            '        <line x1="735" y1="153" x2="796" y2="107" class="ir-arrow"></line>',
            '        <text x="774" y="117" text-anchor="middle" class="edge-note">true</text>',
            '        <line x1="735" y1="153" x2="796" y2="219" class="ir-arrow"></line>',
            '        <text x="774" y="203" text-anchor="middle" class="edge-note">false</text>',
            '        <line x1="1022" y1="107" x2="1036" y2="153" class="ir-arrow"></line>',
            '        <line x1="1022" y1="219" x2="1036" y2="153" class="ir-arrow"></line>',
            "      </svg>",
            "    </section>",
        ]
    )


def _ir_function_rows(model: MbdModelIR) -> str:
    return "\n".join(
        "          <tr>"
        f"<td>{escape(function.name)}</td>"
        f"<td>{escape(function.responsibility)}</td>"
        f"<td>{escape(', '.join(function.owns))}</td>"
        f"<td>{escape(', '.join(function.inputs))}</td>"
        f"<td>{escape(', '.join(function.outputs))}</td>"
        f"<td>{escape(', '.join(function.trace))}</td>"
        f"<td>{escape(', '.join(function.scenarios))}</td>"
        "</tr>"
        for function in model.functions
    )


def _ir_requirement_rows(model: MbdModelIR) -> str:
    return "\n".join(
        f"          <tr><td>{escape(ref)}</td><td>{escape(', '.join(_ir_elements_for_ref(model, ref)))}</td></tr>"
        for ref in sorted(model.requirement_refs())
    )


def _ir_control_rows(model: MbdModelIR) -> str:
    return "\n".join(
        "          <tr>"
        f"<td>{escape(str(control.priority))}</td>"
        f"<td>{escape(control.name)}</td>"
        f"<td>{escape(control.owner or 'unallocated')}</td>"
        f"<td>{escape(control.state_scope)}</td>"
        f"<td>{escape(control.condition)}</td>"
        f"<td>{escape(', '.join(f'{key}={value}' for key, value in control.actions.items()))}</td>"
        f"<td>{escape(', '.join(control.trace))}</td>"
        f"<td>{escape(', '.join(control.scenarios))}</td>"
        "</tr>"
        for control in sorted(model.controls, key=lambda item: (item.priority, item.name))
    )


def _ir_harness_rows(model: MbdModelIR) -> str:
    return "\n".join(
        f"          <tr><td>{escape(device.name)}</td><td>{escape(device.role)}</td><td>{escape(device.boundary)}</td><td>{escape(', '.join(device.trace))}</td></tr>"
        for device in model.harness_devices
    )


def _ir_flow_rows(model: MbdModelIR) -> str:
    return "\n".join(
        f"          <tr><td>{escape(flow.source)}</td><td>{escape(flow.target)}</td><td>{escape(flow.label)}</td><td>{escape(', '.join(flow.trace))}</td></tr>"
        for flow in model.flows
    )


def _ir_state_rows(model: MbdModelIR) -> str:
    return "\n".join(
        f"          <tr><td>{escape(transition.source)}</td><td>{escape(transition.target)}</td><td>{escape(transition.condition)}</td></tr>"
        for transition in model.transitions
    )


def _ir_port_rows(model: MbdModelIR) -> str:
    return "\n".join(
        f"          <tr><td>{escape(port.direction)}</td><td>{escape(port.name)}</td><td>{escape(port.type)}</td><td>{escape(port.default or '')}</td></tr>"
        for port in model.ports.values()
    )


def _ir_elements_for_ref(model: MbdModelIR, ref: str) -> list[str]:
    elements: list[str] = []
    if ref in model.component.trace:
        elements.append(f"component:{model.component.name}")
    for function in model.functions:
        if ref in function.trace:
            elements.append(f"function:{function.name}")
    for flow in model.flows:
        if ref in flow.trace:
            elements.append(f"flow:{flow.source}->{flow.target}")
    for control in model.controls:
        if ref in control.trace:
            elements.append(f"control:{control.name}")
    for device in model.harness_devices:
        if ref in device.trace:
            elements.append(f"harness:{device.name}")
    return elements


def _ir_review_objective_panel(model: MbdModelIR) -> str:
    state_text = "present" if model.transitions else "not declared"
    scenario_count = len(
        {
            scenario
            for function in model.functions
            for scenario in function.scenarios
        }
        | {
            scenario
            for control in model.controls
            for scenario in control.scenarios
        }
    )
    return "\n".join(
        [
            '    <section class="panel review-gate">',
            "      <h2>Human Review Question</h2>",
            "      <p><strong>Does the generated MBD represent the specification as written?</strong> Review this artifact from top to bottom before opening tool-specific handoff files.</p>",
            "      <table>",
            "        <thead><tr><th>Concern</th><th>Generated evidence in this artifact</th></tr></thead>",
            "        <tbody>",
            f"          <tr><td>Specification fidelity</td><td>{len(model.requirement_refs())} requirement trace(s), spec-to-MBD compliance rows, and model-level diagrams.</td></tr>",
            f"          <tr><td>Model behavior</td><td>{len(model.controls)} priority-ordered control rule(s); state machine is {escape(state_text)}.</td></tr>",
            f"          <tr><td>Scenario evidence</td><td>{scenario_count} declared scenario link(s). Reports must separately show inputs, steps, observed behavior, expected behavior, and result.</td></tr>",
            f"          <tr><td>Harness evidence</td><td>{len(model.harness_devices)} declared boundary item(s). Harness does not own control decisions; scenario YAML cannot add control behavior.</td></tr>",
            "          <tr><td>Boundary</td><td>Generated handoff artifacts and Python preview are evidence aids only; the MBD source remains the authoring source.</td></tr>",
            "        </tbody>",
            "      </table>",
            "    </section>",
        ]
    )


def _ir_harness_evidence_boundary_panel(model: MbdModelIR) -> str:
    if not model.harness_devices:
        return ""
    harness_names = ", ".join(device.name for device in model.harness_devices)
    return "\n".join(
        [
            '    <section class="panel policy">',
            "      <h2>Harness Evidence Boundary</h2>",
            "      <p>Harness is a preview evidence layer. It supplies scenario stimulus, declared virtual IC/HAL boundaries, observed behavior, and report evidence; it is not the MBD verification backend.</p>",
            "      <p>Harness does not own control decisions, state transitions, output decisions, thresholds, recovery rules, or product behavior. Those decisions must come from the spec, MBD source, <code>mbd-control</code>, and functional decomposition; scenario YAML cannot add control behavior.</p>",
            f"      <p>Declared Harness boundary items: <code>{escape(harness_names)}</code>. Preview reports show what this Harness observed; formal verification remains external MBD/product-test infrastructure.</p>",
            "    </section>",
        ]
    )


def _ir_review_evidence_map(model: MbdModelIR) -> str:
    rows = [
        (
            "Specification intent",
            "sample spec / requirement IDs",
            "Check that names, states, inputs, outputs, and expected behavior match the human-readable spec.",
        ),
        (
            "Functional decomposition",
            f"{len(model.functions)} function(s)",
            "Check responsibility allocation before inspecting detailed logic.",
        ),
        (
            "Interface and data flow",
            f"{len(model.ports)} port(s), {len(model.flows)} flow(s)",
            "Check signal direction and harness/report boundaries.",
        ),
        (
            "State/control semantics",
            f"{len(model.transitions)} transition(s), {len(model.controls)} control rule(s)",
            "Check guard conditions, state scope, actions, priority, and unsupported assumptions.",
        ),
        (
            "Scenario/report evidence",
            "scenario links on functions and controls",
            "Check expected-vs-observed behavior outside this static page in generated reports.",
        ),
        (
            "Harness evidence",
            f"{len(model.harness_devices)} declared boundary item(s)",
            "Check that Harness is a preview evidence layer and scenario YAML cannot add control behavior.",
        ),
        (
            "Tool handoff",
            "Simulink, SCXML, Modelica, FMI metadata",
            "Check that semantics are structurally exported where supported, not only preserved as comments.",
        ),
    ]
    body = "\n".join(
        "          <tr>"
        f"<td>{escape(area)}</td>"
        f"<td>{escape(evidence)}</td>"
        f"<td>{escape(review)}</td>"
        "</tr>"
        for area, evidence, review in rows
    )
    return "\n".join(
        [
            '    <section class="panel">',
            "      <h2>Review Evidence Map</h2>",
            "      <p>This page is organized around the reviewer question, not around file formats. Tool-specific artifacts are supporting evidence.</p>",
            "      <table>",
            "        <thead><tr><th>Review area</th><th>Evidence source</th><th>What the reviewer checks</th></tr></thead>",
            "        <tbody>",
            body,
            "        </tbody>",
            "      </table>",
            "    </section>",
        ]
    )


def _ir_spec_compliance_review(model: MbdModelIR) -> str:
    rows = "\n".join(_ir_spec_row(model, req_id) for req_id in sorted(model.requirement_refs()))
    return "\n".join(
        [
            '    <section class="panel">',
            "      <h2>Spec-To-MBD Compliance Review</h2>",
            "      <p>This review gate is generated from requirement traces in the MBD source. Expected behavior remains in the sample specification; this table only shows model and scenario evidence.</p>",
            "      <table>",
            "        <thead><tr><th>Requirement</th><th>MBD evidence</th><th>Scenario evidence</th></tr></thead>",
            "        <tbody>",
            flow_or_empty(rows, colspan=3),
            "        </tbody>",
            "      </table>",
            "    </section>",
        ]
    )


def _ir_spec_row(model: MbdModelIR, req_id: str) -> str:
    evidence = ", ".join(_ir_elements_for_ref(model, req_id)) or "Missing concrete MBD trace"
    scenario = ", ".join(_ir_scenarios_for_ref(model, req_id)) or "No scenario trace declared"
    return (
        "          <tr>"
        f"<td><code>{escape(req_id)}</code></td>"
        f"<td>{escape(evidence)}</td>"
        f"<td>{escape(scenario)}</td>"
        "</tr>"
    )


def _ir_scenarios_for_ref(model: MbdModelIR, ref: str) -> list[str]:
    scenarios: list[str] = []
    for function in model.functions:
        if ref in function.trace:
            scenarios.extend(function.scenarios)
    for control in model.controls:
        if ref in control.trace:
            scenarios.extend(control.scenarios)
    return sorted(set(scenarios))


def _ir_mbd_review_checklist() -> str:
    rows = [
        (
            "Requirements traceability",
            "Each claim links to concrete MBD elements, scenarios, reports, or generated artifacts.",
            "Reject broad component-level trace as proof.",
        ),
        (
            "Interface and data-flow review",
            "Inputs, outputs, virtual ICs, HAL boundaries, actuators, and reports are directionally clear.",
            "Reject hidden harness shortcuts.",
        ),
        (
            "State/control behavior",
            "States, guard conditions, actions, latches, recovery rules, and unsupported timing assumptions are reviewable together.",
            "Reject split or contradictory behavior.",
        ),
        (
            "Requirements-based scenario evidence",
            "Scenarios show model inputs, steps, observed behavior, expected behavior, and pass/fail.",
            "Reject pass/fail without expected behavior.",
        ),
        (
            "Modeling standards and readability",
            "Names are stable, diagrams are readable, and views are simpler than the behavior under review.",
            "Reject needless visual complexity.",
        ),
        (
            "Generated artifact boundary",
            "Handoff files and preview C are generated outputs from the MBD source.",
            "Reject manual synchronization.",
        ),
    ]
    body = "\n".join(
        "          <tr>"
        f"<td>{escape(name)}</td>"
        f"<td>{escape(review)}</td>"
        f"<td>{escape(reject)}</td>"
        "</tr>"
        for name, review, reject in rows
    )
    return "\n".join(
        [
            '    <section class="panel">',
            "      <h2>MBD Review Checklist</h2>",
            "      <p>Lightweight review gates adapted from MBD traceability, requirements-based verification, modeling standards, and design-review practice.</p>",
            "      <table>",
            "        <thead><tr><th>Review area</th><th>What to check</th><th>Reject when</th></tr></thead>",
            "        <tbody>",
            body,
            "        </tbody>",
            "      </table>",
            "    </section>",
        ]
    )


def _ir_functional_decomposition_svg(model: MbdModelIR) -> str:
    if not model.functions:
        return "\n".join(
            [
                '    <section class="panel">',
                "      <h2>Functional Architecture</h2>",
                "      <p>No functional decomposition is declared in the MBD source.</p>",
                "    </section>",
            ]
        )
    row_height = 82
    height = 86 + row_height * len(model.functions)
    parts = [
        '    <section class="panel">',
        "      <h2>Functional Architecture</h2>",
        "      <p>Generated from <code>mbd-decomposition</code>. Each block owns signals or states and links to requirements and scenarios.</p>",
        f'      <svg class="diagram" viewBox="0 0 1180 {height}" role="img" aria-label="Functional decomposition generated from mbd-decomposition">',
        *(_svg_defs("irFunctionArrow")),
    ]
    for index, function in enumerate(model.functions):
        y = 44 + index * row_height
        owns = _shorten(", ".join(function.owns), 36)
        inputs = _shorten(", ".join(function.inputs), 38)
        outputs = _shorten(", ".join(function.outputs), 38)
        trace = _shorten(", ".join(function.trace), 34)
        parts.extend(
            [
                f'        <rect x="42" y="{y}" width="300" height="58" rx="8" class="node"></rect>',
                f'        <text x="58" y="{y + 22}" class="node-title small">{escape(function.name)}</text>',
                f'        <text x="58" y="{y + 43}" class="node-note">owns {escape(owns)}</text>',
                f'        <line x1="342" y1="{y + 29}" x2="396" y2="{y + 29}" class="ir-arrow"></line>',
                f'        <rect x="396" y="{y}" width="316" height="58" rx="8" class="rule-condition"></rect>',
                f'        <text x="412" y="{y + 24}" class="node-note">in {escape(inputs)}</text>',
                f'        <text x="412" y="{y + 44}" class="node-note">out {escape(outputs)}</text>',
                f'        <line x1="712" y1="{y + 29}" x2="766" y2="{y + 29}" class="ir-arrow"></line>',
                f'        <rect x="766" y="{y}" width="350" height="58" rx="8" class="rule-action"></rect>',
                f'        <text x="782" y="{y + 24}" class="node-note">trace {escape(trace)}</text>',
                f'        <text x="782" y="{y + 44}" class="edge-note">{escape(_shorten(function.responsibility, 54))}</text>',
            ]
        )
    parts.extend(["      </svg>", "    </section>"])
    return "\n".join(parts)


def _ir_control_semantics_summary() -> str:
    return "\n".join(
        [
            '    <section class="panel">',
            "      <h2>Control Semantics Ownership</h2>",
            "      <p><code>mbd-control</code> is the behavior owner for state and output decisions. State diagrams, SCXML, Simulink, Modelica, preview C, reports, and this HTML page are derived review or handoff views.</p>",
            "      <p>Selection policy: lower numeric priority wins after state scope and guard match. This removes hidden dependence on parser or runtime list order.</p>",
            "    </section>",
        ]
    )


def _ir_review_pipeline_svg(model: MbdModelIR) -> str:
    nodes = [
        ("Requirements", 40, 76, "IDs and intent"),
        ("Specification", 260, 76, "demo assumptions"),
        ("MBD Source", 480, 76, model.source_path.name),
        ("MBD IR", 700, 76, "parsed semantics"),
        ("Handoff Artifacts", 920, 34, "MBD tools"),
        ("Harness Reports", 920, 128, "preview evidence"),
    ]
    arrows = [
        (220, 111, 260, 111),
        (440, 111, 480, 111),
        (660, 111, 700, 111),
        (880, 111, 920, 69),
        (880, 111, 920, 163),
    ]
    parts = [
        '    <section class="panel">',
        "      <h2>MBD Review Pipeline</h2>",
        "      <p>The reviewer follows the generated chain from requirements to MBD IR, handoff artifacts, preview C, harness scenarios, and reports.</p>",
        '      <svg class="diagram" viewBox="0 0 1180 230" role="img" aria-label="MBD review pipeline from requirements to generated artifacts">',
        *(_svg_defs("irPipeArrow")),
    ]
    for x1, y1, x2, y2 in arrows:
        parts.append(
            f'        <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="ir-arrow"></line>'
        )
    for title, x, y, note in nodes:
        parts.extend(_svg_node(title, x, y, note))
    parts.extend(["      </svg>", "    </section>"])
    return "\n".join(parts)


def _ir_data_flow_svg(model: MbdModelIR) -> str:
    flows = model.flows
    positions = _ir_flow_node_positions(model, flows)
    height = max(360, 100 + 70 * max(_column_count(positions, column) for column in range(4)))
    parts = [
        '    <section class="panel">',
        "      <h2>MBD Data Flow Diagram</h2>",
        "      <p>Signals cross the virtual IC, HAL, controller, actuator, and report boundaries without modifying ECU logic for harness convenience.</p>",
        f'      <svg class="diagram" viewBox="0 0 1180 {height}" role="img" aria-label="MBD data flow generated from mbd-flow">',
        *(_svg_defs("irFlowArrow")),
    ]
    for flow in flows:
        parts.extend(_ir_flow_line(flow, positions))
    for name, (x, y, kind) in positions.items():
        parts.extend(_ir_svg_node(name, x, y, kind))
    parts.extend(["      </svg>", "    </section>"])
    return "\n".join(parts)


def _ir_flow_node_positions(model: MbdModelIR, flows: list[FlowIR]) -> dict[str, tuple[int, int, str]]:
    columns: list[list[str]] = [[], [], [], []]
    for flow in flows:
        for endpoint in [flow.source, flow.target]:
            column = _ir_flow_column(model, endpoint)
            if endpoint not in columns[column]:
                columns[column].append(endpoint)
    positions: dict[str, tuple[int, int, str]] = {}
    x_by_column = [36, 326, 616, 906]
    for column, endpoints in enumerate(columns):
        for index, endpoint in enumerate(endpoints):
            positions[endpoint] = (x_by_column[column], 46 + index * 70, _ir_flow_kind(model, endpoint))
    return positions


def _ir_flow_column(model: MbdModelIR, endpoint: str) -> int:
    role = _endpoint_role(model, endpoint)
    if role in {"sensor", "source"}:
        return 0
    if _is_component_parameter_endpoint(model, endpoint):
        return 1
    if endpoint.startswith("HAL_") or endpoint.startswith("HAL."):
        return 1
    if endpoint.startswith(model.component.name) or role == "controller":
        return 2
    return 3


def _ir_flow_kind(model: MbdModelIR, endpoint: str) -> str:
    role = _endpoint_role(model, endpoint)
    if role == "sensor":
        return "Virtual Sensor"
    if role == "source":
        return "Virtual Source"
    if _is_component_parameter_endpoint(model, endpoint):
        return "Parameter"
    if endpoint.startswith("HAL_") or endpoint.startswith("HAL."):
        return "HAL Boundary"
    if endpoint.startswith(model.component.name) or role == "controller":
        return "Controller"
    if endpoint.startswith("ScenarioReport"):
        return "Report"
    if role == "actuator":
        return "Virtual Actuator"
    return "External Endpoint"


def _endpoint_role(model: MbdModelIR, endpoint: str) -> str:
    root = endpoint.split(".", 1)[0]
    for device in model.harness_devices:
        if device.name == root:
            return device.role
    for function in model.functions:
        if function.name == root:
            return "controller"
    return ""


def _is_component_parameter_endpoint(model: MbdModelIR, endpoint: str) -> bool:
    prefix = f"{model.component.name}."
    if not endpoint.startswith(prefix):
        return False
    signal = endpoint.removeprefix(prefix)
    return signal in model.component.parameters


def _column_count(positions: dict[str, tuple[int, int, str]], column: int) -> int:
    x_by_column = [36, 326, 616, 906]
    return sum(1 for x, _, _ in positions.values() if x == x_by_column[column])


def _ir_flow_line(flow: FlowIR, positions: dict[str, tuple[int, int, str]]) -> list[str]:
    sx, sy, _ = positions[flow.source]
    tx, ty, _ = positions[flow.target]
    x1 = sx + 230
    y1 = sy + 27
    x2 = tx
    y2 = ty + 27
    mid_x = (x1 + x2) / 2
    label_y = min(y1, y2) - 8 if abs(y1 - y2) < 24 else (y1 + y2) / 2 - 8
    return [
        f'        <path d="M {x1} {y1} C {mid_x:.0f} {y1}, {mid_x:.0f} {y2}, {x2} {y2}" class="ir-flow-line"></path>',
        f'        <text x="{mid_x:.0f}" y="{label_y:.0f}" text-anchor="middle" class="signal-label">{escape(flow.label)}</text>',
    ]


def _ir_control_rule_svg(model: MbdModelIR) -> str:
    row_height = 78
    height = 72 + row_height * max(1, len(model.controls))
    parts = [
        '    <section class="panel">',
        "      <h2>Control Rule Map</h2>",
        "      <p>Each rule shows the condition, generated actions, and requirement trace carried by the MBD IR.</p>",
        f'      <svg class="diagram" viewBox="0 0 1180 {height}" role="img" aria-label="Control rule map generated from mbd-control">',
        *(_svg_defs("irRuleArrow")),
    ]
    for index, control in enumerate(model.controls):
        y = 42 + index * row_height
        condition = _shorten(control.condition, 44)
        actions = _shorten(", ".join(f"{key}={value}" for key, value in control.actions.items()), 56)
        trace = _shorten(", ".join(control.trace), 42)
        parts.extend(
            [
                f'        <rect x="42" y="{y}" width="290" height="50" rx="8" class="rule-condition"></rect>',
                f'        <text x="58" y="{y + 30}" class="node-note">{escape(condition)}</text>',
                f'        <line x1="332" y1="{y + 25}" x2="390" y2="{y + 25}" class="ir-arrow"></line>',
                f'        <rect x="390" y="{y}" width="220" height="50" rx="8" class="rule-node"></rect>',
                f'        <text x="500" y="{y + 30}" text-anchor="middle" class="node-title">{escape(control.name)}</text>',
                f'        <line x1="610" y1="{y + 25}" x2="668" y2="{y + 25}" class="ir-arrow"></line>',
                f'        <rect x="668" y="{y}" width="320" height="50" rx="8" class="rule-action"></rect>',
                f'        <text x="684" y="{y + 22}" class="node-note">{escape(actions)}</text>',
                f'        <text x="684" y="{y + 40}" class="edge-note">trace {escape(trace)}</text>',
            ]
        )
    parts.extend(["      </svg>", "    </section>"])
    return "\n".join(parts)


def _ir_harness_boundary_svg(model: MbdModelIR) -> str:
    sources = [device for device in model.harness_devices if device.role in {"source", "sensor"}]
    controllers = [device for device in model.harness_devices if device.role == "controller"]
    actuators = [device for device in model.harness_devices if device.role == "actuator"]
    controller = controllers[0].name if controllers else model.component.name
    source_names = [device.name for device in sources] or ["Scenario Inputs"]
    actuator_names = [device.name for device in actuators]
    height = 310
    parts = [
        '    <section class="panel">',
        "      <h2>Harness Boundary Diagram</h2>",
        "      <p>The harness surrounds the controller through HAL-style boundaries; it does not edit controller logic for simulation convenience.</p>",
        f'      <svg class="diagram" viewBox="0 0 1180 {height}" role="img" aria-label="Harness boundary generated from mbd-harness">',
        *(_svg_defs("irHarnessArrow")),
    ]
    parts.extend(_svg_node("Scenario Steps", 42, 118, "test sequence"))
    source_label = ", ".join(source_names)
    parts.extend(_svg_node(source_label, 286, 118, "declared source"))
    parts.extend(_svg_node(controller, 530, 118, "controller boundary"))
    report_x = 1010
    if actuator_names:
        for index, actuator in enumerate(actuator_names):
            parts.extend(_svg_node(actuator, 784, 72 + index * 94, "declared actuator"))
            parts.append(
                f'        <line x1="730" y1="153" x2="784" y2="{107 + index * 94}" class="ir-arrow"></line>'
            )
        parts.extend(_svg_node("Scenario Report", report_x, 118, "evidence"))
        parts.append('        <line x1="984" y1="153" x2="1010" y2="153" class="ir-arrow"></line>')
    else:
        parts.extend(_svg_node("Scenario Report", 784, 118, "evidence"))
        report_x = 784
    for x1, y1, x2, y2 in [(242, 153, 286, 153), (486, 153, 530, 153), (730, 153, report_x, 153)]:
        parts.append(f'        <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="ir-arrow"></line>')
    parts.extend(["      </svg>", "    </section>"])
    return "\n".join(parts)


def _semantic_action_lines(model: MbdModelIR, control: ControlRuleIR) -> list[str]:
    parts: list[str] = []
    for name, value in control.actions.items():
        port = model.ports.get(name)
        if port is not None and port.direction == "out":
            parts.append(f"Output {name} = {value}")
        elif name == "state":
            parts.append(f"State {value}")
        else:
            parts.append(f"{name} = {value}")
    return parts


def _semantic_output_action_lines(model: MbdModelIR, control: ControlRuleIR) -> list[str]:
    parts: list[str] = []
    for name, value in control.actions.items():
        port = model.ports.get(name)
        if port is not None and port.direction == "out":
            parts.append(f"Output {name} = {value}")
    return parts or _semantic_action_lines(model, control)


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
    .state-review {
      border-color: #9fb2b7;
      background: #fbfdfd;
    }
    .spec-first-review {
      border-color: #7aa0a7;
      background: #fbfdfd;
    }
    .review-compare {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin: 10px 0 16px;
    }
    .evidence-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
      padding: 12px;
      min-width: 0;
    }
    .evidence-card h4 {
      margin: 0 0 8px;
      font-size: 14px;
    }
    .mini-state-diagram {
      display: block;
      width: 100%;
      min-width: 0;
      height: auto;
      background: #f9fbfb;
      border: 1px solid var(--line);
      border-radius: 8px;
    }
    .initial-dot {
      fill: var(--accent);
      stroke: var(--accent);
    }
    .review-badges {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 14px 0;
    }
    .review-badges span {
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #ffffff;
      padding: 7px 11px;
      color: var(--ink);
      font-size: 13px;
    }
    .state-playback {
      display: grid;
      grid-template-columns: minmax(220px, 0.45fr) minmax(0, 1fr);
      gap: 14px;
      margin: 16px 0;
      align-items: stretch;
    }
    .playback-status {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
      padding: 16px;
    }
    .playback-status span {
      display: block;
      margin-bottom: 8px;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      color: var(--accent);
    }
    .playback-status strong {
      display: block;
      color: var(--ink);
      font-size: 16px;
    }
    .playback-buttons {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 8px;
    }
    .playback-buttons button {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
      color: var(--ink);
      padding: 10px;
      text-align: left;
      font: inherit;
      cursor: pointer;
    }
    .playback-buttons button:hover, .playback-buttons button.active-step {
      border-color: var(--accent);
      background: var(--accent-soft);
    }
    .playback-buttons span, .playback-buttons small {
      display: block;
      margin-top: 4px;
      color: var(--muted);
      font-size: 12px;
    }
    .review-table.compact {
      font-size: 13px;
    }
    .review-notes {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }
    .review-notes p {
      margin: 0;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
      padding: 12px;
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
    .ir-arrow, .ir-flow-line, .ir-state-line {
      stroke: var(--accent);
      stroke-width: 2.4;
      fill: none;
      marker-end: url(#arrow);
    }
    .ir-flow-line { stroke: #256f3f; }
    .ir-state-line { stroke: #475569; }
    .rule-condition {
      fill: #f8fafc;
      stroke: #9fb2b7;
      stroke-width: 1.5;
    }
    .rule-node {
      fill: var(--accent-soft);
      stroke: var(--accent);
      stroke-width: 1.8;
    }
    .rule-action {
      fill: #ffffff;
      stroke: #9fb2b7;
      stroke-width: 1.5;
    }
    .input-port { fill: #ffffff; stroke: #256f3f; stroke-width: 2; }
    .output-port { fill: #256f3f; stroke: #256f3f; stroke-width: 2; }
    .node-title, .state-label {
      fill: var(--ink);
      font-size: 17px;
      font-weight: 700;
    }
    .node-title.small { font-size: 12px; }
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
      .state-playback, .review-notes, .review-compare { grid-template-columns: 1fr; }
      .shell { width: min(100vw - 20px, 1180px); padding-top: 10px; }
      .hero-copy, .panel { padding: 16px; }
      h1 { font-size: 34px; }
    }
    """.strip()
