from __future__ import annotations

from pathlib import Path

from veph.ir import MbdModelIR
from veph.model_loader import PeripheralModel


def export_markdown(model: PeripheralModel | MbdModelIR) -> str:
    if isinstance(model, MbdModelIR):
        return _export_ir_markdown(model)
    return _export_legacy_markdown(model)


def _export_ir_markdown(model: MbdModelIR) -> str:
    lines = [
        f"# {model.title}",
        "",
        "> Generated review document from Mermaid-like MBD markup.",
        "> Authoring source is the `.mbd.md` file; this document is a review artifact.",
        "",
        f"Source: `{_source_display(model.source_path)}`",
        "",
        "## Intent",
        "",
        "Author in text. Verify in MBD tools. Python preview is only a preview/smoke-test helper.",
        "",
        "## Traceability To Markup Sections",
        "",
    ]
    for section in model.sections:
        lines.append(f"- `{section.language}`")
    lines.extend(["", "## Requirements Trace", ""])
    refs = sorted(model.requirement_refs())
    if refs:
        for ref in refs:
            lines.append(f"- `{ref}`")
    else:
        lines.append("- No explicit requirement references declared.")
    lines.extend(
        [
            "",
            "## Component",
            "",
            f"- Name: `{model.component.name}`",
            f"- Bus: `{model.component.bus.get('type', 'unknown')}`",
        ]
    )
    for key, value in model.component.bus.items():
        if key != "type":
            lines.append(f"- Bus {key}: `{value}`")
    lines.extend(["", "## Ports", "", "| Direction | Name | Type | Default |", "| --- | --- | --- | --- |"])
    for port in model.ports.values():
        lines.append(f"| {port.direction} | `{port.name}` | `{port.type}` | `{port.default or ''}` |")
    lines.extend(["", "## Registers", ""])
    for register in model.registers.values():
        lines.append(f"### `{register.name}`")
        lines.append("")
        lines.append(f"- Address: `{register.address}`")
        lines.append(f"- Access: `{register.access}`")
        lines.append(f"- Width: `{register.width}`")
        lines.append("")
        for field in register.fields.values():
            lines.append(f"- `{field.name}` bits `{field.bits}` reset `{field.reset}`")
        lines.append("")
    lines.extend(["## State Transitions", ""])
    lines.append("Lifecycle/topology view. Executable behavior is owned by `mbd-control` and derived generated views.")
    lines.append("")
    for transition in model.transitions:
        lines.append(f"- `{transition.source}` -> `{transition.target}` when `{transition.condition}`")
    lines.extend(["", "## Flow Preview", ""])
    for flow in model.flows:
        label = f" ({flow.label})" if flow.label else ""
        trace = f" trace `{', '.join(flow.trace)}`" if flow.trace else ""
        lines.append(f"- `{flow.source}` -> `{flow.target}`{label}{trace}")
    lines.extend(["", "## Control Rules", ""])
    if model.controls:
        for control in model.controls:
            actions = ", ".join(f"{key}={value}" for key, value in control.actions.items())
            trace = f" trace `{', '.join(control.trace)}`" if control.trace else ""
            scenarios = f" scenarios `{', '.join(control.scenarios)}`" if control.scenarios else ""
            lines.append(
                f"- priority `{control.priority}` `{control.name}` from `{control.state_scope}`: "
                f"when `{control.condition}` then `{actions}`{trace}{scenarios}"
            )
    else:
        lines.append("- No control rules declared.")
    lines.extend(["", "## Harness Boundary", ""])
    if model.harness_devices:
        for device in model.harness_devices:
            trace = f" trace `{', '.join(device.trace)}`" if device.trace else ""
            lines.append(f"- `{device.name}` role `{device.role}` boundary `{device.boundary}`{trace}")
    else:
        lines.append("- No preview harness devices declared.")
    lines.extend(
        [
            "",
            "## Verification Direction",
            "",
            "- Simulink `.m`, Modelica `.mo`, SCXML, Mermaid, PlantUML, and FMI metadata are generated handoff artifacts.",
            "- Existing MBD tools are the intended verification backends.",
            "- This repository does not claim certification.",
            "",
        ]
    )
    return "\n".join(lines)


def _source_display(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def _export_legacy_markdown(model: PeripheralModel) -> str:
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
