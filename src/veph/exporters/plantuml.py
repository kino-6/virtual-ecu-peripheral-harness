from __future__ import annotations

from veph.model_loader import PeripheralModel


def export_plantuml(model: PeripheralModel) -> str:
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
