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
        lines.append(f"  %% {source} --> {target}")
        if flow.label:
            lines.append(f'  {source} -->|"{flow.label}"| {target}')
        else:
            lines.append(f"  {source} --> {target}")
    return "\n".join(lines) + "\n"


def _node_id(name: str) -> str:
    return name.replace(".", "_").replace(" ", "_").replace("-", "_")
