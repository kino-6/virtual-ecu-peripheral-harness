from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ModelValidationError(ValueError):
    """Raised when a Textual MBD model is malformed."""


@dataclass(frozen=True)
class Bus:
    type: str
    mode: int
    word_bits: int


@dataclass(frozen=True)
class Field:
    name: str
    bits: list[int]
    reset: int


@dataclass(frozen=True)
class Register:
    name: str
    address: int
    width: int
    access: str
    fields: dict[str, Field]
    description: str = ""


@dataclass(frozen=True)
class Transition:
    source: str
    target: str
    when: str


@dataclass(frozen=True)
class StateMachine:
    initial: str
    nodes: list[str]
    transitions: list[Transition]


@dataclass(frozen=True)
class Signal:
    name: str
    unit: str | None = None
    type: str | None = None
    default: Any = None


@dataclass(frozen=True)
class Fault:
    name: str
    effect: str


@dataclass(frozen=True)
class Port:
    name: str
    signal: str
    type: str = "value"


@dataclass(frozen=True)
class Block:
    name: str
    kind: str
    inputs: dict[str, Port]
    outputs: dict[str, Port]
    description: str = ""


@dataclass(frozen=True)
class Connection:
    source: str
    target: str
    signal: str


@dataclass(frozen=True)
class PeripheralModel:
    schema_version: str
    kind: str
    name: str
    description: str
    bus: Bus
    registers: dict[str, Register]
    states: StateMachine
    input_signals: dict[str, Signal]
    output_signals: dict[str, Signal]
    faults: dict[str, Fault]
    blocks: dict[str, Block]
    connections: list[Connection]
    timing: dict[str, Any]
    parameters: dict[str, Any]
    source_path: Path | None = None


def load_yaml(path: str | Path) -> dict[str, Any]:
    model_path = Path(path)
    data = yaml.safe_load(model_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ModelValidationError("model file must contain a YAML mapping")
    return data


def load_model(path: str | Path) -> PeripheralModel:
    model_path = Path(path)
    data = load_yaml(model_path)
    validate_model_data(data)
    return _build_model(data, model_path)


def validate_model_data(data: dict[str, Any]) -> None:
    if data.get("kind") != "PeripheralModel":
        raise ModelValidationError("kind must be PeripheralModel")

    required = ["schemaVersion", "name", "bus", "registers", "states", "signals", "faults", "timing"]
    for section in required:
        if section not in data:
            raise ModelValidationError(f"missing required section: {section}")

    bus = data["bus"]
    if not isinstance(bus, dict) or bus.get("type") != "spi":
        raise ModelValidationError("bus.type must be spi for this MVP")

    registers = data["registers"]
    if not isinstance(registers, dict) or not registers:
        raise ModelValidationError("registers must be a non-empty mapping")

    addresses: set[int] = set()
    for name, register in registers.items():
        if not isinstance(register, dict):
            raise ModelValidationError(f"register {name} must be a mapping")
        for key in ["address", "width", "access", "fields"]:
            if key not in register:
                raise ModelValidationError(f"register {name} missing {key}")
        if register["access"] not in {"ro", "rw", "wo"}:
            raise ModelValidationError(f"register {name} has invalid access")
        address = _as_int(register["address"])
        if address in addresses:
            raise ModelValidationError(f"duplicate register address: {address}")
        addresses.add(address)
        width = _as_int(register["width"])
        if width <= 0:
            raise ModelValidationError(f"register {name} width must be positive")
        fields = register["fields"]
        if not isinstance(fields, dict) or not fields:
            raise ModelValidationError(f"register {name} fields must be a non-empty mapping")
        for field_name, field in fields.items():
            if "bits" not in field:
                raise ModelValidationError(f"field {name}.{field_name} missing bits")
            bits = [_as_int(bit) for bit in field["bits"]]
            if any(bit < 0 or bit >= width for bit in bits):
                raise ModelValidationError(f"field {name}.{field_name} bit outside register width")

    states = data["states"]
    if states.get("initial") not in states.get("nodes", []):
        raise ModelValidationError("states.initial must be listed in states.nodes")
    for transition in states.get("transitions", []):
        if transition.get("from") not in states["nodes"] or transition.get("to") not in states["nodes"]:
            raise ModelValidationError("state transition references unknown node")

    _validate_blocks_and_connections(data)


def _build_model(data: dict[str, Any], source_path: Path) -> PeripheralModel:
    bus = Bus(
        type=str(data["bus"]["type"]),
        mode=_as_int(data["bus"].get("mode", 0)),
        word_bits=_as_int(data["bus"].get("wordBits", 8)),
    )
    registers = {
        name: Register(
            name=name,
            address=_as_int(raw["address"]),
            width=_as_int(raw["width"]),
            access=str(raw["access"]),
            description=str(raw.get("description", "")),
            fields={
                field_name: Field(
                    name=field_name,
                    bits=[_as_int(bit) for bit in raw_field["bits"]],
                    reset=_as_int(raw_field.get("reset", 0)),
                )
                for field_name, raw_field in raw["fields"].items()
            },
        )
        for name, raw in data["registers"].items()
    }
    states = StateMachine(
        initial=str(data["states"]["initial"]),
        nodes=[str(node) for node in data["states"]["nodes"]],
        transitions=[
            Transition(source=str(raw["from"]), target=str(raw["to"]), when=str(raw["when"]))
            for raw in data["states"].get("transitions", [])
        ],
    )
    input_signals = {
        raw["name"]: Signal(name=raw["name"], unit=raw.get("unit"), default=raw.get("default"))
        for raw in data["signals"].get("inputs", [])
    }
    output_signals = {
        raw["name"]: Signal(name=raw["name"], type=raw.get("type"), default=raw.get("default"))
        for raw in data["signals"].get("outputs", [])
    }
    faults = {
        raw["name"]: Fault(name=raw["name"], effect=str(raw.get("effect", "")))
        for raw in data.get("faults", [])
    }
    blocks = {
        raw["name"]: Block(
            name=str(raw["name"]),
            kind=str(raw["kind"]),
            description=str(raw.get("description", "")),
            inputs={
                port["name"]: Port(
                    name=str(port["name"]),
                    signal=str(port.get("signal", port["name"])),
                    type=str(port.get("type", "value")),
                )
                for port in raw.get("inputs", [])
            },
            outputs={
                port["name"]: Port(
                    name=str(port["name"]),
                    signal=str(port.get("signal", port["name"])),
                    type=str(port.get("type", "value")),
                )
                for port in raw.get("outputs", [])
            },
        )
        for raw in data.get("blocks", [])
    }
    connections = [
        Connection(source=str(raw["from"]), target=str(raw["to"]), signal=str(raw.get("signal", "")))
        for raw in data.get("connections", [])
    ]
    return PeripheralModel(
        schema_version=str(data["schemaVersion"]),
        kind=str(data["kind"]),
        name=str(data["name"]),
        description=str(data.get("description", "")),
        bus=bus,
        registers=registers,
        states=states,
        input_signals=input_signals,
        output_signals=output_signals,
        faults=faults,
        blocks=blocks,
        connections=connections,
        timing=dict(data.get("timing", {})),
        parameters=dict(data.get("parameters", {})),
        source_path=source_path,
    )


def _as_int(value: Any) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value, 0)
    if isinstance(value, float) and value.is_integer():
        return int(value)
    raise ModelValidationError(f"expected integer-compatible value, got {value!r}")


def _validate_blocks_and_connections(data: dict[str, Any]) -> None:
    blocks = data.get("blocks", [])
    connections = data.get("connections", [])
    if not blocks and connections:
        raise ModelValidationError("connections require blocks")
    if not isinstance(blocks, list):
        raise ModelValidationError("blocks must be a list")
    if not isinstance(connections, list):
        raise ModelValidationError("connections must be a list")

    endpoints: set[str] = set()
    block_names: set[str] = set()
    for block in blocks:
        if not isinstance(block, dict):
            raise ModelValidationError("block entries must be mappings")
        for key in ["name", "kind"]:
            if key not in block:
                raise ModelValidationError(f"block missing {key}")
        block_name = str(block["name"])
        if block_name in block_names:
            raise ModelValidationError(f"duplicate block: {block_name}")
        block_names.add(block_name)
        for direction in ["inputs", "outputs"]:
            ports = block.get(direction, [])
            if not isinstance(ports, list):
                raise ModelValidationError(f"block {block_name} {direction} must be a list")
            port_names: set[str] = set()
            for port in ports:
                if "name" not in port:
                    raise ModelValidationError(f"block {block_name} port missing name")
                port_name = str(port["name"])
                if port_name in port_names:
                    raise ModelValidationError(f"duplicate port: {block_name}.{port_name}")
                port_names.add(port_name)
                endpoints.add(f"{block_name}.{port_name}")

    for connection in connections:
        if not isinstance(connection, dict):
            raise ModelValidationError("connection entries must be mappings")
        for key in ["from", "to"]:
            if key not in connection:
                raise ModelValidationError(f"connection missing {key}")
        source = str(connection["from"])
        target = str(connection["to"])
        if source not in endpoints or target not in endpoints:
            raise ModelValidationError(f"unknown connection endpoint: {source} -> {target}")
