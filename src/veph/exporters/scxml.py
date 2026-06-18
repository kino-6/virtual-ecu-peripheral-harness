from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from veph.ir import MbdModelIR
from veph.model_loader import PeripheralModel


def export_scxml(model: PeripheralModel | MbdModelIR) -> str:
    if isinstance(model, MbdModelIR):
        states = _ir_state_names(model)
        initial = states[0] if states else "INITIAL"
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<scxml xmlns="http://www.w3.org/2005/07/scxml" version="1.0" initial="{escape(initial)}">',
            f"  <!-- Generated state-machine handoff from {escape(_source_display(model.source_path))}. -->",
            "  <!-- Lifecycle/topology view. Executable control priority is owned by mbd-control. -->",
            f"  <!-- Requirement refs: {escape(', '.join(sorted(model.requirement_refs())))} -->",
        ]
        for control in sorted(model.controls, key=lambda item: (item.priority, item.name)):
            lines.append(
                "  <!-- "
                f"priority {control.priority} {escape(control.name)} from {escape(control.state_scope)} "
                f"when {escape(control.condition)} "
                f"trace {escape(', '.join(control.trace))} "
                f"scenarios {escape(', '.join(control.scenarios))}"
                " -->"
            )
        for state in states:
            outgoing = [transition for transition in model.transitions if transition.source == state]
            if outgoing:
                lines.append(f'  <state id="{escape(state)}">')
                for transition in outgoing:
                    lines.append(
                        f'    <transition event="{escape(transition.condition)}" target="{escape(transition.target)}" />'
                    )
                lines.append("  </state>")
            else:
                lines.append(f'  <state id="{escape(state)}" />')
        lines.append("</scxml>")
        return "\n".join(lines) + "\n"

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<scxml xmlns="http://www.w3.org/2005/07/scxml" version="1.0" initial="{escape(model.states.initial)}">',
        f'  <!-- {escape(model.name)} fictional generated state machine. -->',
        "  <!-- Canonical source: Textual MBD YAML. Regenerate instead of editing as source. -->",
    ]
    for node in model.states.nodes:
        outgoing = [transition for transition in model.states.transitions if transition.source == node]
        if outgoing:
            lines.append(f'  <state id="{escape(node)}">')
            for transition in outgoing:
                lines.append(
                    f'    <transition event="{escape(transition.when)}" target="{escape(transition.target)}" />'
                )
            lines.append("  </state>")
        else:
            lines.append(f'  <state id="{escape(node)}" />')
    lines.append("</scxml>")
    return "\n".join(lines) + "\n"


def _ir_state_names(model: MbdModelIR) -> list[str]:
    states: list[str] = []
    for transition in model.transitions:
        if transition.source not in states:
            states.append(transition.source)
        if transition.target not in states:
            states.append(transition.target)
    return states


def _source_display(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)
