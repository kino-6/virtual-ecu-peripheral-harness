from __future__ import annotations

from veph.model_loader import PeripheralModel


def export_markdown(model: PeripheralModel) -> str:
    lines = [
        f"# {model.name}",
        "",
        "> Generated artifact. This component is fictional and is provided for synthetic examples only.",
        "> Canonical source: Textual MBD YAML. Regenerate this file instead of editing it by hand.",
        "",
        "## Overview",
        "",
        model.description,
        "",
        "## Bus Interface",
        "",
        f"- Type: `{model.bus.type}`",
        f"- Mode: `{model.bus.mode}`",
        f"- Word bits: `{model.bus.word_bits}`",
        "",
        "## Register Map",
        "",
        "| Register | Address | Width | Access | Description |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for register in model.registers.values():
        lines.append(
            f"| {register.name} | 0x{register.address:02X} | {register.width} | "
            f"{register.access} | {register.description} |"
        )
    lines.extend(["", "## Fields", ""])
    for register in model.registers.values():
        lines.append(f"### {register.name}")
        lines.append("")
        lines.append("| Field | Bits | Reset |")
        lines.append("| --- | --- | ---: |")
        for field in register.fields.values():
            bits = ", ".join(str(bit) for bit in field.bits)
            lines.append(f"| {field.name} | {bits} | {field.reset} |")
        lines.append("")
    lines.extend(["## States And Transitions", ""])
    lines.append(f"- Initial: `{model.states.initial}`")
    for node in model.states.nodes:
        lines.append(f"- State: `{node}`")
    lines.append("")
    for transition in model.states.transitions:
        lines.append(f"- `{transition.source}` -> `{transition.target}` when `{transition.when}`")
    lines.extend(["", "## Signals", ""])
    for signal in model.input_signals.values():
        lines.append(f"- Input `{signal.name}` ({signal.unit or 'unitless'}), default `{signal.default}`")
    for signal in model.output_signals.values():
        lines.append(f"- Output `{signal.name}` ({signal.type or 'value'})")
    lines.extend(["", "## Functional Blocks", ""])
    if model.blocks:
        for block in model.blocks.values():
            lines.append(f"### `{block.name}`")
            lines.append("")
            lines.append(f"- Kind: `{block.kind}`")
            if block.description:
                lines.append(f"- Description: {block.description}")
            if block.inputs:
                inputs = ", ".join(
                    f"`{port.name}: {port.type}` ({port.signal})" for port in block.inputs.values()
                )
                lines.append(f"- Inputs: {inputs}")
            if block.outputs:
                outputs = ", ".join(
                    f"`{port.name}: {port.type}` ({port.signal})" for port in block.outputs.values()
                )
                lines.append(f"- Outputs: {outputs}")
            lines.append("")
    else:
        lines.append("- No functional blocks declared.")
        lines.append("")
    lines.extend(["## Connections", ""])
    if model.connections:
        for connection in model.connections:
            lines.append(f"- `{connection.source}` -> `{connection.target}` via `{connection.signal}`")
    else:
        lines.append("- No block connections declared.")
    lines.extend(["", "## Faults", ""])
    for fault in model.faults.values():
        lines.append(f"- `{fault.name}`: {fault.effect}")
    lines.extend(["", "## Timing", ""])
    for key, value in model.timing.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    return "\n".join(lines)
