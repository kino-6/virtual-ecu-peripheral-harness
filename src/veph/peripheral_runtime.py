from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import Any

from veph.model_loader import PeripheralModel, Register


class RuntimeError(Exception):
    """Raised when a runtime operation is invalid."""


@dataclass
class PeripheralRuntime:
    model: PeripheralModel
    state: str = field(init=False)
    registers: dict[str, int] = field(init=False)
    signals: dict[str, Any] = field(init=False)
    active_faults: set[str] = field(default_factory=set, init=False)
    trace: list[str] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.state = self.model.states.initial
        self.registers = {name: 0 for name in self.model.registers}
        self.signals = {name: signal.default for name, signal in self.model.input_signals.items()}
        for register in self.model.registers.values():
            for field_def in register.fields.values():
                self._set_field(register.name, field_def.name, field_def.reset)
        self._update_derived_registers()

    def apply_event(self, event: str) -> None:
        self.trace.append(f"event {event}")
        self._transition_on(event)
        self._update_derived_registers()

    def set_signal(self, name: str, value: Any) -> None:
        if name not in self.signals:
            raise RuntimeError(f"unknown signal: {name}")
        self.signals[name] = value
        self.trace.append(f"signal {name}={value}")
        self._evaluate_conditions()
        self._update_derived_registers()

    def inject_fault(self, name: str) -> None:
        if name not in self.model.faults:
            raise RuntimeError(f"unknown fault: {name}")
        self.active_faults.add(name)
        self.trace.append(f"fault injected {name}")
        if name == "undervoltage":
            self._latch_undervoltage()
        elif name == "spiTimeout":
            self._set_field("FAULT", "spiTimeout", 1)
        elif name == "stuckReadyBit":
            self._set_field("STATUS", "ready", 0)
        self._update_derived_registers()

    def read_register(self, name: str) -> int | None:
        self._require_register(name)
        if "spiTimeout" in self.active_faults:
            self.trace.append(f"read {name}: timeout")
            return None
        self._update_derived_registers()
        value = self.registers[name]
        self.trace.append(f"read {name}: 0x{value:02X}")
        return value

    def write_register(self, name: str, value: int) -> bool | None:
        register = self._require_register(name)
        if "spiTimeout" in self.active_faults:
            self.trace.append(f"write {name}: timeout")
            return None
        if register.access == "ro":
            raise RuntimeError(f"register {name} is read-only")
        self.registers[name] = int(value) & self._mask(register.width)
        self.trace.append(f"write {name}: 0x{self.registers[name]:02X}")
        if name == "CONTROL" and self.read_field("CONTROL", "enableMonitoring") == 1 and self.state == "INIT":
            self.apply_event("initSequenceOk")
        self._update_derived_registers()
        return True

    def read_field(self, register_name: str, field_name: str) -> int:
        register = self._require_register(register_name)
        field_def = register.fields[field_name]
        value = 0
        for offset, bit in enumerate(sorted(field_def.bits)):
            if self.registers[register_name] & (1 << bit):
                value |= 1 << offset
        return value

    def _set_field(self, register_name: str, field_name: str, value: int) -> None:
        register = self._require_register(register_name)
        field_def = register.fields[field_name]
        raw = self.registers[register_name]
        for bit in field_def.bits:
            raw &= ~(1 << bit)
        for offset, bit in enumerate(sorted(field_def.bits)):
            if int(value) & (1 << offset):
                raw |= 1 << bit
        self.registers[register_name] = raw & self._mask(register.width)

    def _transition_on(self, trigger: str) -> bool:
        for transition in self.model.states.transitions:
            if transition.source == self.state and transition.when == trigger:
                self.trace.append(f"state {self.state}->{transition.target} on {trigger}")
                self.state = transition.target
                return True
        return False

    def _evaluate_conditions(self) -> None:
        for transition in self.model.states.transitions:
            if transition.source == self.state and self._condition_is_true(transition.when):
                self.trace.append(f"state {self.state}->{transition.target} on {transition.when}")
                self.state = transition.target
                if transition.target == "FAULT_LATCHED":
                    self._latch_undervoltage()
                return

    def _condition_is_true(self, expression: str) -> bool:
        parts = expression.split()
        if len(parts) != 3:
            return False
        left, op_text, right = parts
        ops = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge, "==": operator.eq}
        if op_text not in ops:
            return False
        return bool(ops[op_text](float(self._resolve_value(left)), float(self._resolve_value(right))))

    def _resolve_value(self, name: str) -> Any:
        if name in self.signals:
            return self.signals[name]
        if name in self.model.parameters:
            return self.model.parameters[name]
        return float(name)

    def _latch_undervoltage(self) -> None:
        self.active_faults.add("undervoltage")
        self._set_field("STATUS", "undervoltageFault", 1)
        self._set_field("FAULT", "undervoltage", 1)
        self.state = "FAULT_LATCHED"

    def _update_derived_registers(self) -> None:
        if "VOLTAGE" in self.model.registers and "voltage" in self.signals:
            voltage = max(0, min(255, int(round(float(self.signals["voltage"])))))
            self._set_field("VOLTAGE", "volts", voltage)
        if "STATUS" in self.model.registers and "ready" in self.model.registers["STATUS"].fields:
            ready = 1 if self.state == "NORMAL" and "stuckReadyBit" not in self.active_faults else 0
            self._set_field("STATUS", "ready", ready)

    def _require_register(self, name: str) -> Register:
        if name not in self.model.registers:
            raise RuntimeError(f"unknown register: {name}")
        return self.model.registers[name]

    @staticmethod
    def _mask(width: int) -> int:
        return (1 << width) - 1
