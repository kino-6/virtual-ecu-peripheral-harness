from __future__ import annotations

from xml.sax.saxutils import escape

from veph.model_loader import PeripheralModel


def export_scxml(model: PeripheralModel) -> str:
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
