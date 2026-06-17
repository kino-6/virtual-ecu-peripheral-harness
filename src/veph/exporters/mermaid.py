from __future__ import annotations

from veph.ir import MbdModelIR


def export_mermaid(model: MbdModelIR) -> str:
    lines = [
        "flowchart LR",
        "  %% Generated preview from Mermaid-like MBD markup.",
        "  %% Existing MBD tools remain the verification backends.",
    ]
    for flow in model.flows:
        source = _node_id(flow.source)
        target = _node_id(flow.target)
        lines.append(f'  {source}["{flow.source}"]')
        lines.append(f'  {target}["{flow.target}"]')
        if flow.trace:
            lines.append(f"  %% Trace: {', '.join(flow.trace)}")
        lines.append(f"  %% {source} --> {target}")
        if flow.label:
            lines.append(f'  {source} -->|"{flow.label}"| {target}')
        else:
            lines.append(f"  {source} --> {target}")
    for control in model.controls:
        control_id = _node_id(f"rule_{control.name}")
        lines.append(f'  {control_id}{{"rule {control.name}"}}')
        if control.trace:
            lines.append(f"  %% Trace: {', '.join(control.trace)}")
        for target in control.actions:
            target_id = _node_id(target)
            lines.append(f'  {target_id}["{target}"]')
            lines.append(f'  {control_id} -->|"{control.condition}"| {target_id}')
    for device in model.harness_devices:
        device_id = _node_id(device.name)
        lines.append(f'  {device_id}["{device.name}<br/>{device.boundary}"]')
        if device.trace:
            lines.append(f"  %% Trace: {', '.join(device.trace)}")
    return "\n".join(lines) + "\n"


def _node_id(name: str) -> str:
    return name.replace(".", "_").replace(" ", "_").replace("-", "_")
