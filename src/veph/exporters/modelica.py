from __future__ import annotations

from veph.ir import MbdModelIR
from veph.model_loader import PeripheralModel


def export_modelica(model: PeripheralModel | MbdModelIR) -> str:
    if isinstance(model, MbdModelIR):
        lines = [
            f"model {model.component.name}",
            "  // Generated from Mermaid-like MBD markup.",
            "  // Readable Modelica handoff artifact; not a complete physical model.",
        ]
        for parameter in model.component.parameters.values():
            lines.append(f"  parameter Real {parameter.name} = {parameter.default};")
        for port in model.ports.values():
            direction = "input" if port.direction == "in" else "output"
            type_name = "Boolean" if port.type == "bool" else "Real"
            default = f"(start={port.default})" if port.default else ""
            lines.append(f"  {direction} {type_name} {port.name}{default};")
        lines.append("  discrete Integer state;")
        lines.append("equation")
        lines.append("  // State placeholders generated from markup:")
        for index, state in enumerate(_state_names(model)):
            lines.append(f"  // {index}: {state}")
        lines.append("  // Control rule handoff summary:")
        for control in model.controls:
            actions = ", ".join(f"{key}={value}" for key, value in control.actions.items())
            trace = ", ".join(control.trace)
            lines.append(f"  // {control.name}: when {control.condition} then {actions} trace {trace}")
        lines.append(f"end {model.component.name};")
        return "\n".join(lines) + "\n"

    class_name = model.name.replace("IC", "")
    lines = [
        f"model {class_name}",
        f'  // Generated from fictional Textual MBD model {model.name}.',
        "  // Canonical source: Textual MBD YAML. Regenerate instead of editing as source.",
    ]
    for name, value in model.parameters.items():
        lines.append(f"  parameter Real {name} = {value};")
    for signal in model.input_signals.values():
        unit = f' "{signal.unit}"' if signal.unit else ""
        default = signal.default if signal.default is not None else 0
        lines.append(f"  input Real {signal.name}(start={default}){unit};")
    for signal in model.output_signals.values():
        type_name = "Boolean" if signal.type == "bool" else "Real"
        lines.append(f"  output {type_name} {signal.name};")
    lines.append("  discrete Integer state;")
    lines.append("equation")
    lines.append("  // State encoding:")
    for index, node in enumerate(model.states.nodes):
        lines.append(f"  // {index}: {node}")
    if "ready" in model.output_signals:
        normal_index = model.states.nodes.index("NORMAL") if "NORMAL" in model.states.nodes else -1
        lines.append(f"  ready = state == {normal_index};")
    lines.append(f"end {class_name};")
    return "\n".join(lines) + "\n"


def _state_names(model: MbdModelIR) -> list[str]:
    names: list[str] = []
    for transition in model.transitions:
        if transition.source not in names:
            names.append(transition.source)
        if transition.target not in names:
            names.append(transition.target)
    return names
