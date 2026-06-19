from __future__ import annotations

from dataclasses import asdict, dataclass, field
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
    trace: list[str] = field(default_factory=list)


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
    trace: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FunctionIR:
    name: str
    responsibility: str
    owns: list[str] = field(default_factory=list)
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    trace: list[str] = field(default_factory=list)
    scenarios: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ExpressionIR:
    kind: str
    source: str = ""
    value: str | int | float | bool | None = None
    name: str = ""
    operator: str = ""
    left: "ExpressionIR | None" = None
    right: "ExpressionIR | None" = None
    operands: list["ExpressionIR"] = field(default_factory=list)
    diagnostic: str = ""


@dataclass(frozen=True)
class ControlRuleIR:
    name: str
    condition: str
    actions: dict[str, str]
    priority: int = 1000
    state_scope: str = "*"
    owner: str = ""
    trace: list[str] = field(default_factory=list)
    scenarios: list[str] = field(default_factory=list)
    condition_expr: ExpressionIR = field(
        default_factory=lambda: ExpressionIR(
            kind="unsupported",
            diagnostic="condition expression was not parsed",
        )
    )


@dataclass(frozen=True)
class HarnessDeviceIR:
    name: str
    role: str
    boundary: str
    trace: list[str] = field(default_factory=list)


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
    functions: list[FunctionIR] = field(default_factory=list)
    controls: list[ControlRuleIR] = field(default_factory=list)
    harness_devices: list[HarnessDeviceIR] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["source_path"] = str(self.source_path)
        data["metadata"] = {
            "sourceFormat": "mbd-markdown",
            "irRole": "internal snapshot",
            "sourcePath": str(self.source_path),
            "requirementRefs": sorted(self.requirement_refs()),
        }
        return data

    def requirement_refs(self) -> set[str]:
        refs = set(self.component.trace)
        for flow in self.flows:
            refs.update(flow.trace)
        for function in self.functions:
            refs.update(function.trace)
        for control in self.controls:
            refs.update(control.trace)
        for device in self.harness_devices:
            refs.update(device.trace)
        return refs
