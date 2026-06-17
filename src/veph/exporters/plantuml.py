from __future__ import annotations

from veph.ir import MbdModelIR
from veph.model_loader import PeripheralModel


def export_plantuml(model: PeripheralModel | MbdModelIR) -> str:
    if isinstance(model, MbdModelIR):
        lines = [
            "@startuml",
            "' Generated preview from Mermaid-like MBD markup.",
            "' Existing MBD tools are the intended verification backends.",
            f"title {model.component.name} State Preview",
            f"[*] --> {model.transitions[0].source if model.transitions else 'INITIAL'}",
        ]
        for transition in model.transitions:
            lines.append(f"{transition.source} --> {transition.target} : {transition.condition}")
        lines.append("@enduml")
        return "\n".join(lines) + "\n"

    lines = [
        "@startuml",
        "' Generated from canonical Textual MBD YAML. Do not edit as source.",
        "' Fictional component for synthetic examples only.",
        f"title {model.name} State Machine",
        f"[*] --> {model.states.initial}",
    ]
    for transition in model.states.transitions:
        lines.append(f"{transition.source} --> {transition.target} : {transition.when}")
    lines.append("@enduml")
    return "\n".join(lines) + "\n"
