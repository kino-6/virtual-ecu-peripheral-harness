from __future__ import annotations

import json
from pathlib import Path

from veph.ir import MbdModelIR


def export_fmi_metadata(model: MbdModelIR) -> str:
    data = {
        "component": model.component.name,
        "source": _source_display(model.source_path),
        "sourceFormat": "mbd-markdown",
        "fmiIntent": "metadata stub only; no FMU is generated",
        "inputs": [
            {"name": port.name, "type": port.type, "default": port.default}
            for port in model.ports.values()
            if port.direction == "in"
        ],
        "outputs": [
            {"name": port.name, "type": port.type, "default": port.default}
            for port in model.ports.values()
            if port.direction == "out"
        ],
        "parameters": [
            {"name": parameter.name, "type": parameter.type, "default": parameter.default}
            for parameter in model.component.parameters.values()
        ],
        "states": _state_names(model),
        "registers": [
            {"name": register.name, "address": register.address, "access": register.access}
            for register in model.registers.values()
        ],
    }
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def _state_names(model: MbdModelIR) -> list[str]:
    states: list[str] = []
    for transition in model.transitions:
        if transition.source not in states:
            states.append(transition.source)
        if transition.target not in states:
            states.append(transition.target)
    return states


def _source_display(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)
