# Toy Power Monitor IC

> Generated review document from Mermaid-like MBD markup.
> Authoring source is the `.mbd.md` file; this document is a review artifact.

Source: `examples/toy_power_monitor.mbd.md`

## Intent

Author in text. Verify in MBD tools. Python preview is only a preview/smoke-test helper.

## Traceability To Markup Sections

- `mbd-component`
- `mbd-registers`
- `mbd-state`
- `mbd-flow`

## Requirements Trace

- No explicit requirement references declared.

## Component

- Name: `ToyPowerMonitorIC`
- Bus: `spi`
- Bus mode: `0`
- Bus wordBits: `8`

## Ports

| Direction | Name | Type | Default |
| --- | --- | --- | --- |
| in | `voltage` | `V` | `12.0` |
| out | `ready` | `bool` | `` |
| out | `fault` | `bool` | `` |

## Registers

### `STATUS`

- Address: `0x01`
- Access: `ro`
- Width: `8`

- `ready` bits `7` reset `0`
- `undervoltageFault` bits `0` reset `0`

### `CONTROL`

- Address: `0x02`
- Access: `rw`
- Width: `8`

- `enable` bits `0` reset `0`

### `FAULT`

- Address: `0x03`
- Access: `ro`
- Width: `8`

- `undervoltage` bits `0` reset `0`
- `spiTimeout` bits `1` reset `0`

### `VOLTAGE`

- Address: `0x04`
- Access: `ro`
- Width: `8`

- `volts` bits `7..0` reset `12`

## State Transitions

- `RESET` -> `INIT` when `powerOn`
- `INIT` -> `NORMAL` when `initSequenceOk`
- `NORMAL` -> `FAULT_LATCHED` when `voltage < undervoltageThreshold`
- `FAULT_LATCHED` -> `RESET` when `clearFault`

## Flow Preview

- `ECU_App.control_task` -> `HAL_SPI` (write CONTROL.enable)
- `HAL_SPI` -> `ToyPowerMonitorIC.CONTROL` (spi write)
- `ToyPowerMonitorIC.STATUS` -> `HAL_SPI` (spi read)
- `HAL_SPI` -> `ECU_App.diagnostics` (STATUS.ready, STATUS.undervoltageFault)
- `ToyPowerMonitorIC.ready` -> `ECU_App.diagnostics` (ready signal)
- `ToyPowerMonitorIC.fault` -> `ECU_App.diagnostics` (fault signal)

## Control Rules

- No control rules declared.

## Harness Boundary

- No preview harness devices declared.

## Verification Direction

- Simulink `.m`, Modelica `.mo`, SCXML, Mermaid, PlantUML, and FMI metadata are generated handoff artifacts.
- Existing MBD tools are the intended verification backends.
- This repository does not claim certification.
