from __future__ import annotations

from veph.model_loader import PeripheralModel


def export_simulink_m(model: PeripheralModel) -> str:
    system_name = model.name.replace("IC", "Model")
    lines = [
        f"% Generated from fictional Textual MBD model {model.name}.",
        "% Canonical source: Textual MBD YAML. Regenerate instead of editing as source.",
        "% This best-effort script requires MATLAB/Simulink if executed.",
        f"model = '{system_name}';",
        "new_system(model);",
        "open_system(model);",
        f"add_block('simulink/Sources/Constant', [model '/Voltage']);",
        f"add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/UndervoltageThreshold']);",
        f"set_param([model '/UndervoltageThreshold'], 'const', '{model.parameters.get('undervoltageThreshold', 7.0)}');",
        f"add_block('simulink/Sinks/Display', [model '/StatusDisplay']);",
        f"add_line(model, 'Voltage/1', 'UndervoltageThreshold/1');",
        f"add_line(model, 'UndervoltageThreshold/1', 'StatusDisplay/1');",
        "% State machine summary:",
    ]
    for transition in model.states.transitions:
        lines.append(f"% {transition.source} -> {transition.target} when {transition.when}")
    lines.append("save_system(model);")
    return "\n".join(lines) + "\n"
