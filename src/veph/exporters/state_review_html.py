from __future__ import annotations

import json
from html import escape

from veph.exporters.html_helpers import shorten as _shorten
from veph.exporters.html_helpers import svg_defs as _svg_defs
from veph.ir import ControlRuleIR, MbdModelIR, TransitionIR


def ir_state_machine_svg(model: MbdModelIR) -> str:
    states = ordered_states(model.transitions)
    positions = _ir_state_positions(states)
    rows = max(1, (len(states) + 3) // 4)
    height = 150 + rows * 170
    parts = [
        '    <section class="panel">',
        "      <h2>State Machine Diagram</h2>",
        "      <p>States and transitions are parsed from <code>mbd-state</code>. Review this together with the State Machine Review Package above; SCXML/Stateflow-oriented files are generated handoff views.</p>",
        f'      <svg class="diagram" viewBox="0 0 1180 {height}" role="img" aria-label="State machine generated from mbd-state">',
        *(_svg_defs("irStateArrow")),
    ]
    for transition in model.transitions:
        parts.extend(_ir_state_transition_line(transition, positions))
    for state, (x, y) in positions.items():
        parts.append(f'        <rect x="{x}" y="{y}" width="210" height="64" rx="8" class="state"></rect>')
        parts.append(f'        <text x="{x + 105}" y="{y + 39}" text-anchor="middle" class="state-label">{escape(state)}</text>')
    parts.extend(["      </svg>", "    </section>"])
    return "\n".join(parts)


def ir_state_machine_review_dashboard(model: MbdModelIR) -> str:
    if not model.transitions:
        return ""
    states = ordered_states(model.transitions)
    initial_state = states[0] if states else "unknown"
    transition_rows = "\n".join(
        _ir_state_machine_review_row(model, transition) for transition in model.transitions
    )
    inventory_rows = "\n".join(
        _ir_state_inventory_row(model, state, initial_state) for state in states
    )
    matrix_rows = "\n".join(_ir_transition_matrix_row(model, states, state) for state in states)
    diagnostic_rows = "\n".join(_ir_guard_diagnostic_row(model, state) for state in states)
    walkthrough_rows = "\n".join(
        _ir_scenario_walkthrough_row(model, index, transition)
        for index, transition in enumerate(model.transitions, start=1)
    )
    state_rows = "\n".join(
        f"          <tr><td>{escape(state)}</td><td>{escape(_outgoing_conditions(model, state))}</td><td>{escape(_state_output_summary(model, state))}</td></tr>"
        for state in states
    )
    matrix_headers = "".join(f"<th>{escape(state)}</th>" for state in states)
    return "\n".join(
        [
            '    <section class="panel state-review" data-state-machine-review>',
            "      <h2>State Machine Transition Review</h2>",
            "      <p>This is the state-machine review surface. Review the transition table first, then use the diagram as supporting evidence.</p>",
            "      <table class=\"review-table compact\">",
            "        <thead><tr><th>Review basis</th><th>What this artifact exposes</th></tr></thead>",
            "        <tbody>",
            "          <tr><td>Finite modes and initial/default state</td><td>Initial state, state inventory, and outgoing transition coverage.</td></tr>",
            "          <tr><td>Trigger / guard / effect semantics</td><td>Each transition row separates guard/event text from state and output actions.</td></tr>",
            "          <tr><td>Transition-system completeness</td><td>Transition matrix and guard diagnostics expose missing else/self-hold assumptions and multiple outgoing transitions.</td></tr>",
            "          <tr><td>Executable handoff boundary</td><td>SCXML/Stateflow-oriented handoff is generated separately; this page is the human review surface.</td></tr>",
            "          <tr><td>Scenario-based validation</td><td>Interactive step buttons let reviewers walk the expected path and compare state/output effects.</td></tr>",
            "        </tbody>",
            "      </table>",
            "      <div class=\"review-badges\">",
            f"        <span>Initial state: <strong data-current-state>{escape(initial_state)}</strong></span>",
            f"        <span>{len(states)} states</span>",
            f"        <span>{len(model.transitions)} transitions</span>",
            f"        <span>{len(model.controls)} control rules</span>",
            "      </div>",
            "      <div class=\"state-playback\">",
            "        <div class=\"playback-status\">",
            "          <span>Current outputs</span>",
            f"          <strong data-current-outputs>{escape(_initial_output_summary(model))}</strong>",
            "        </div>",
            "        <div class=\"playback-buttons\">",
            *(_state_playback_buttons(model)),
            "          <button type=\"button\" data-reset-state>Reset</button>",
            "        </div>",
            "      </div>",
            "      <h3>State Inventory</h3>",
            "      <table class=\"review-table compact\">",
            "        <thead><tr><th>State</th><th>Role</th><th>Incoming</th><th>Outgoing</th><th>Owned output effects</th><th>Review finding</th></tr></thead>",
            "        <tbody>",
            inventory_rows,
            "        </tbody>",
            "      </table>",
            "      <h3>Transition Table</h3>",
            "      <table class=\"review-table\">",
            "        <thead><tr><th>Transition</th><th>Trigger / Guard</th><th>Owning rule</th><th>Actions</th><th>Trace</th><th>Scenario evidence</th></tr></thead>",
            "        <tbody>",
            transition_rows,
            "        </tbody>",
            "      </table>",
            "      <h3>Transition Matrix</h3>",
            "      <table class=\"review-table compact transition-matrix\">",
            f"        <thead><tr><th>Source \\ Target</th>{matrix_headers}</tr></thead>",
            "        <tbody>",
            matrix_rows,
            "        </tbody>",
            "      </table>",
            "      <h3>Guard Diagnostics</h3>",
            "      <table class=\"review-table compact\">",
            "        <thead><tr><th>State</th><th>Outgoing guards</th><th>Determinism / completeness check</th><th>Required reviewer decision</th></tr></thead>",
            "        <tbody>",
            diagnostic_rows,
            "        </tbody>",
            "      </table>",
            "      <h3>Action Semantics</h3>",
            "      <table class=\"review-table compact\">",
            "        <thead><tr><th>Action class</th><th>Current support</th><th>Review implication</th></tr></thead>",
            "        <tbody>",
            "          <tr><td>Transition action</td><td>Supported through <code>mbd-control</code> actions on the selected transition.</td><td>State and output effects must appear in the transition row.</td></tr>",
            "          <tr><td>Entry / during / exit action</td><td>Unsupported in this preview subset.</td><td>Do not infer hidden Stateflow-style entry, during, or exit behavior.</td></tr>",
            "          <tr><td>Output timing</td><td>Outputs are reviewed as transition effects in the discrete scenario step.</td><td>Treat this as preview semantics; tool-backed timing verification is external.</td></tr>",
            "        </tbody>",
            "      </table>",
            "      <h3>Scenario Walk-Through</h3>",
            "      <table class=\"review-table compact\">",
            "        <thead><tr><th>Step</th><th>Expected source state</th><th>Input / event</th><th>Selected transition</th><th>Expected target state</th><th>Expected output effect</th><th>Trace</th><th>Scenario</th><th>Report evidence</th></tr></thead>",
            "        <tbody>",
            walkthrough_rows,
            "        </tbody>",
            "      </table>",
            "      <h3>Compact State Summary</h3>",
            "      <table class=\"review-table compact\">",
            "        <thead><tr><th>State</th><th>Allowed guard(s)</th><th>Output effect after transition</th></tr></thead>",
            "        <tbody>",
            state_rows,
            "        </tbody>",
            "      </table>",
            "      <div class=\"review-notes\">",
            "        <p><strong>Review gates:</strong> every state has an explicit outgoing rule for the intended path; every transition has one owning control rule; every effect is visible as state/output actions; every behavior row has requirement and scenario evidence.</p>",
            "        <p><strong>Unsupported in this slice:</strong> hierarchy, parallel states, history, time events, entry/exit/do actions, backtracking flowcharts, and multiple enabled outgoing transitions from the same state.</p>",
            "      </div>",
            "    </section>",
        ]
    )


def ir_state_machine_review_script(model: MbdModelIR) -> str:
    if not model.transitions:
        return ""
    initial_state = ordered_states(model.transitions)[0]
    initial_outputs = {
        port.name: port.default or ""
        for port in model.ports.values()
        if port.direction == "out"
    }
    steps = []
    for transition in model.transitions:
        rule = control_rule_for_transition(model.controls, transition)
        outputs = dict(initial_outputs)
        state = transition.target
        actions = rule.actions if rule is not None else {}
        for key, value in actions.items():
            if key == "state":
                state = value
            elif key in initial_outputs:
                outputs[key] = value
        steps.append(
            {
                "source": transition.source,
                "target": transition.target,
                "condition": transition.condition,
                "state": state,
                "outputs": outputs,
                "actions": actions,
            }
        )
    return "\n".join(
        [
            "  <script>",
            "    (() => {",
            "      const panel = document.querySelector('[data-state-machine-review]');",
            "      if (!panel) return;",
            f"      const initialState = {json.dumps(initial_state)};",
            f"      const initialOutputs = {json.dumps(initial_outputs, sort_keys=True)};",
            f"      const steps = {json.dumps(steps, sort_keys=True)};",
            "      const stateTarget = panel.querySelector('[data-current-state]');",
            "      const outputsTarget = panel.querySelector('[data-current-outputs]');",
            "      const renderOutputs = (outputs) => Object.entries(outputs).map(([k, v]) => `${k}=${v}`).join(', ');",
            "      const setReviewState = (state, outputs) => {",
            "        stateTarget.textContent = state;",
            "        outputsTarget.textContent = renderOutputs(outputs);",
            "      };",
            "      panel.querySelectorAll('[data-step-index]').forEach((button) => {",
            "        button.addEventListener('click', () => {",
            "          const step = steps[Number(button.dataset.stepIndex)];",
            "          setReviewState(step.state, step.outputs);",
            "          panel.querySelectorAll('[data-step-index]').forEach((item) => item.classList.toggle('active-step', item === button));",
            "        });",
            "      });",
            "      panel.querySelector('[data-reset-state]')?.addEventListener('click', () => {",
            "        setReviewState(initialState, initialOutputs);",
            "        panel.querySelectorAll('[data-step-index]').forEach((item) => item.classList.remove('active-step'));",
            "      });",
            "    })();",
            "  </script>",
        ]
    )


def ir_state_machine_review_package(model: MbdModelIR) -> str:
    if not model.transitions:
        return ""
    rows = "\n".join(_ir_state_machine_review_row(model, transition) for transition in model.transitions)
    return "\n".join(
        [
            '    <section class="panel">',
            "      <h2>State Machine Review Package</h2>",
            "      <p>State-machine review needs the transition diagram plus a table of guards, actions, traces, scenarios, and execution assumptions. This table is generated from <code>mbd-state</code> and <code>mbd-control</code> together.</p>",
            "      <table>",
            "        <thead><tr><th>Transition</th><th>Guard/Event</th><th>Owning rule</th><th>Actions</th><th>Trace</th><th>Scenario evidence</th></tr></thead>",
            "        <tbody>",
            rows,
            "        </tbody>",
            "      </table>",
            "    </section>",
        ]
    )


def control_rule_for_transition(
    controls: list[ControlRuleIR],
    transition: TransitionIR,
) -> ControlRuleIR | None:
    candidates = [
        control
        for control in controls
        if control.state_scope == transition.source
        and control.actions.get("state") == transition.target
        and control.condition == transition.condition
    ]
    if not candidates:
        candidates = [
            control
            for control in controls
            if control.state_scope == transition.source
            and control.actions.get("state") == transition.target
        ]
    if not candidates:
        return None
    return sorted(candidates, key=lambda item: (item.priority, item.name))[0]


def ordered_states(transitions: list[TransitionIR]) -> list[str]:
    states: list[str] = []
    for transition in transitions:
        for state in [transition.source, transition.target]:
            if state not in states:
                states.append(state)
    return states


def _ir_state_inventory_row(model: MbdModelIR, state: str, initial_state: str) -> str:
    incoming = [transition for transition in model.transitions if transition.target == state]
    outgoing = [transition for transition in model.transitions if transition.source == state]
    owned_outputs = sorted(
        {
            key
            for transition in outgoing
            for control in [control_rule_for_transition(model.controls, transition)]
            if control is not None
            for key in control.actions
            if key != "state"
        }
    )
    role = "initial/default" if state == initial_state else "reachable"
    if not incoming and state != initial_state:
        finding = "No incoming transition; review reachability."
    elif not outgoing:
        finding = "No outgoing transition; review terminal-state intent."
    else:
        finding = "Declared path is reviewable."
    return (
        "          <tr>"
        f"<td><code>{escape(state)}</code></td>"
        f"<td>{escape(role)}</td>"
        f"<td>{len(incoming)}</td>"
        f"<td>{len(outgoing)}</td>"
        f"<td>{escape(', '.join(owned_outputs) or 'none')}</td>"
        f"<td>{escape(finding)}</td>"
        "</tr>"
    )


def _ir_transition_matrix_row(model: MbdModelIR, states: list[str], source_state: str) -> str:
    cells = []
    for target_state in states:
        transitions = [
            transition
            for transition in model.transitions
            if transition.source == source_state and transition.target == target_state
        ]
        cell_text = "; ".join(
            f"{transition.condition} / {control_actions(control_rule_for_transition(model.controls, transition))}"
            for transition in transitions
        )
        cells.append(f"<td>{escape(cell_text or '-')}</td>")
    return f"          <tr><th>{escape(source_state)}</th>{''.join(cells)}</tr>"


def _ir_guard_diagnostic_row(model: MbdModelIR, state: str) -> str:
    outgoing = [transition for transition in model.transitions if transition.source == state]
    guards = [transition.condition for transition in outgoing]
    if not outgoing:
        check = "No outgoing transition declared."
        decision = "Confirm this state is intentionally terminal, or add an outgoing rule."
    elif len(outgoing) == 1:
        guard = guards[0].strip().lower()
        if guard in {"always", "true"}:
            check = "Single unconditional outgoing transition."
            decision = "Confirm automatic transition is intended."
        else:
            check = "Single guarded outgoing transition; false case is implicit self-hold."
            decision = "Confirm self-hold is intended or add an explicit else rule."
    elif len(set(guards)) != len(guards):
        check = "Duplicate outgoing guard detected."
        decision = "Resolve duplicate guard or document priority behavior."
    else:
        check = "Multiple outgoing guards; overlap analysis is not proven by this subset."
        decision = "Review guard mutual exclusivity and priority order."
    return (
        "          <tr>"
        f"<td><code>{escape(state)}</code></td>"
        f"<td>{escape(', '.join(guards) or 'none')}</td>"
        f"<td>{escape(check)}</td>"
        f"<td>{escape(decision)}</td>"
        "</tr>"
    )


def _ir_scenario_walkthrough_row(
    model: MbdModelIR,
    index: int,
    transition: TransitionIR,
) -> str:
    rule = control_rule_for_transition(model.controls, transition)
    rule_name = rule.name if rule is not None else "missing rule"
    actions = control_actions(rule)
    trace = ", ".join(rule.trace) if rule is not None and rule.trace else "Missing trace"
    scenarios = ", ".join(rule.scenarios) if rule is not None and rule.scenarios else "Missing scenario"
    report_evidence = _report_evidence_for_scenarios(rule.scenarios if rule is not None else [])
    return (
        "          <tr>"
        f"<td>{index}</td>"
        f"<td><code>{escape(transition.source)}</code></td>"
        f"<td>{escape(transition.condition)}</td>"
        f"<td>{escape(rule_name)}</td>"
        f"<td><code>{escape(transition.target)}</code></td>"
        f"<td>{escape(actions)}</td>"
        f"<td>{escape(trace)}</td>"
        f"<td>{escape(scenarios)}</td>"
        f"<td>{escape(report_evidence)}</td>"
        "</tr>"
    )


def _report_evidence_for_scenarios(scenarios: list[str]) -> str:
    if not scenarios:
        return "Missing report link"
    return ", ".join(f"reports/{scenario}.md" for scenario in scenarios)


def _state_playback_buttons(model: MbdModelIR) -> list[str]:
    buttons: list[str] = []
    for index, transition in enumerate(model.transitions):
        rule = control_rule_for_transition(model.controls, transition)
        label = f"{transition.source} -> {transition.target}"
        condition = transition.condition
        actions = control_actions(rule)
        buttons.append(
            f'          <button type="button" data-step-index="{index}">{escape(label)} <span>{escape(condition)}</span><small>{escape(actions)}</small></button>'
        )
    return buttons


def _outgoing_conditions(model: MbdModelIR, state: str) -> str:
    conditions = [transition.condition for transition in model.transitions if transition.source == state]
    return ", ".join(conditions) if conditions else "No outgoing transition"


def _state_output_summary(model: MbdModelIR, state: str) -> str:
    summaries: list[str] = []
    for transition in model.transitions:
        if transition.source != state:
            continue
        rule = control_rule_for_transition(model.controls, transition)
        if rule is not None:
            summaries.append(f"{transition.target}: {control_actions(rule)}")
    return "; ".join(summaries) if summaries else "No action evidence"


def _initial_output_summary(model: MbdModelIR) -> str:
    outputs = [
        f"{port.name}={port.default or 'unset'}"
        for port in model.ports.values()
        if port.direction == "out"
    ]
    return ", ".join(outputs) if outputs else "No outputs"


def control_actions(control: ControlRuleIR | None) -> str:
    if control is None:
        return "No matching control rule"
    return ", ".join(f"{key}={value}" for key, value in control.actions.items()) or "No actions"


def _ir_state_machine_review_row(model: MbdModelIR, transition: TransitionIR) -> str:
    rule = control_rule_for_transition(model.controls, transition)
    if rule is None:
        rule_name = "No matching control rule"
        actions = "Missing action evidence"
        trace = "Missing trace"
        scenarios = "Missing scenario"
    else:
        rule_name = f"{rule.name} (priority {rule.priority}, owner {rule.owner or 'unallocated'})"
        actions = ", ".join(f"{key}={value}" for key, value in rule.actions.items()) or "No actions"
        trace = ", ".join(rule.trace) or "Missing trace"
        scenarios = ", ".join(rule.scenarios) or "Missing scenario"
    return (
        "          <tr>"
        f"<td><code>{escape(transition.source)} -> {escape(transition.target)}</code></td>"
        f"<td>{escape(transition.condition)}</td>"
        f"<td>{escape(rule_name)}</td>"
        f"<td>{escape(actions)}</td>"
        f"<td>{escape(trace)}</td>"
        f"<td>{escape(scenarios)}</td>"
        "</tr>"
    )


def _ir_state_positions(states: list[str]) -> dict[str, tuple[int, int]]:
    positions: dict[str, tuple[int, int]] = {}
    for index, state in enumerate(states):
        column = index % 4
        row = index // 4
        positions[state] = (46 + column * 280, 64 + row * 170)
    return positions


def _ir_state_transition_line(transition: TransitionIR, positions: dict[str, tuple[int, int]]) -> list[str]:
    sx, sy = positions[transition.source]
    tx, ty = positions[transition.target]
    x1 = sx + 210
    y1 = sy + 32
    x2 = tx
    y2 = ty + 32
    if tx < sx:
        x1 = sx + 105
        y1 = sy + 64
        x2 = tx + 105
        y2 = ty + 64
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    return [
        f'        <path d="M {x1} {y1} C {mid_x:.0f} {y1}, {mid_x:.0f} {y2}, {x2} {y2}" class="ir-state-line"></path>',
        f'        <text x="{mid_x:.0f}" y="{mid_y - 10:.0f}" text-anchor="middle" class="edge-note">{escape(_shorten(transition.condition, 42))}</text>',
    ]
