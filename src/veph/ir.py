from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PortIR:
    name: str
    direction: str
    type: str
    default: str | None = None


@dataclass(frozen=True)
class ParameterIR:
    name: str
    type: str
    default: str


@dataclass(frozen=True)
class ComponentIR:
    name: str
    bus: dict[str, str]
    parameters: dict[str, ParameterIR]


@dataclass(frozen=True)
class RegisterFieldIR:
    name: str
    bit: int | None
    bits: str
    reset: str


@dataclass(frozen=True)
class RegisterIR:
    name: str
    address: str
    access: str
    width: int
    fields: dict[str, RegisterFieldIR]


@dataclass(frozen=True)
class TransitionIR:
    source: str
    target: str
    condition: str


@dataclass(frozen=True)
class FlowIR:
    source: str
    target: str
    label: str = ""


@dataclass(frozen=True)
class MarkupSectionIR:
    language: str
    body: str


@dataclass(frozen=True)
class MbdModelIR:
    title: str
    component: ComponentIR
    ports: dict[str, PortIR]
    registers: dict[str, RegisterIR]
    transitions: list[TransitionIR]
    flows: list[FlowIR]
    sections: list[MarkupSectionIR]
    source_path: Path

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["source_path"] = str(self.source_path)
        data["metadata"] = {
            "sourceFormat": "mbd-markdown",
            "irRole": "internal snapshot",
            "sourcePath": str(self.source_path),
        }
        return data
