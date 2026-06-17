# ToyPowerMonitorIC Manual

ToyPowerMonitorIC is a fictional peripheral used only for the virtual ECU
peripheral harness MVP. It is intentionally tiny: a status register, a control
register, a fault register, a quantized voltage register, and a reset-cause
register.

This manual is synthetic documentation for testing Textual MBD workflows. It is
not based on a real integrated circuit, datasheet, ECU, vehicle platform, or
company project.

## Startup

After `powerOn`, the peripheral moves from `RESET` to `INIT`. Writing `0x01` to
`CONTROL` represents a simple initialization sequence and moves the model to
`NORMAL`.

## Faults

If voltage drops below the configured threshold, the model latches an
undervoltage fault. An injected SPI timeout causes SPI reads and writes to return
no response. A stuck ready bit keeps the `STATUS.ready` field cleared.
