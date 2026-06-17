from __future__ import annotations

from veph.ir import MbdModelIR
from veph.model_loader import PeripheralModel


def export_simulink_m(model: PeripheralModel | MbdModelIR) -> str:
    if isinstance(model, MbdModelIR):
        lines = [
            f"% Generated from Mermaid-like MBD markup for {model.component.name}.",
            "% Handoff artifact for MATLAB/Simulink environments; not executed by this repo.",
            f"model = '{model.component.name}Model';",
            "new_system(model);",
            "open_system(model);",
        ]
        block_names = sorted({flow.source for flow in model.flows} | {flow.target for flow in model.flows})
        for index, block_name in enumerate(block_names):
            safe = _simulink_block_name(block_name)
            x = 80 + (index % 3) * 220
            y = 80 + (index // 3) * 120
            lines.append(f"add_block('simulink/Commonly Used Blocks/Subsystem', [model '/{safe}']);")
            lines.append(f"set_param([model '/{safe}'], 'Position', [{x} {y} {x + 150} {y + 60}]);")
        for flow in model.flows:
            lines.append(
                f"add_line(model, '{_simulink_block_name(flow.source)}/1', '{_simulink_block_name(flow.target)}/1', 'autorouting', 'on');"
            )
        lines.append("% State transition summary:")
        for transition in model.transitions:
            lines.append(f"% {transition.source} -> {transition.target} when {transition.condition}")
        lines.append("save_system(model);")
        return "\n".join(lines) + "\n"

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


def _simulink_block_name(name: str) -> str:
    return name.replace(".", "_").replace(" ", "_")
