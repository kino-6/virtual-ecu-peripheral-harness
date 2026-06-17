from __future__ import annotations

from veph.model_loader import PeripheralModel


def export_modelica(model: PeripheralModel) -> str:
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
