from __future__ import annotations

from veph.peripheral_runtime import PeripheralRuntime


class VirtualSpi:
    """Tiny SPI boundary that keeps ECU-like code separate from runtime internals."""

    def __init__(self, runtime: PeripheralRuntime):
        self.runtime = runtime

    def read_register(self, register_name: str) -> int | None:
        return self.runtime.read_register(register_name)

    def write_register(self, register_name: str, value: int) -> bool | None:
        return self.runtime.write_register(register_name, value)
