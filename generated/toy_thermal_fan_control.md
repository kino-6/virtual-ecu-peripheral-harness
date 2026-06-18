# Toy Thermal Fan Control

> Generated review document from Mermaid-like MBD markup.
> Authoring source is the `.mbd.md` file; this document is a review artifact.

Source: `examples/toy_thermal_fan_control.mbd.md`

## Intent

Author in text. Verify in MBD tools. Python preview is only a preview/smoke-test helper.

## Traceability To Markup Sections

- `mbd-component`
- `mbd-registers`
- `mbd-state`
- `mbd-flow`
- `mbd-control`
- `mbd-harness`

## Requirements Trace

- `HAR-001`
- `HAR-002`
- `HAR-004`
- `HAR-005`
- `STK-001`
- `SWE-001`
- `SWE-004`
- `SYS-001`
- `SYS-002`
- `SYS-003`
- `SYS-004`
- `SYS-005`
- `SYS-006`

## Component

- Name: `ToyThermalFanController`
- Bus: `virtual`
- Bus mode: `preview`
- Bus wordBits: `16`

## Ports

| Direction | Name | Type | Default |
| --- | --- | --- | --- |
| in | `temperatureC` | `degC` | `25` |
| in | `temperatureValid` | `bool` | `true` |
| out | `fanDuty` | `percent` | `0` |
| out | `fault` | `bool` | `false` |

## Registers

### `TEMP_STATUS`

- Address: `0x10`
- Access: `ro`
- Width: `16`

- `valid` bits `15` reset `1`
- `temperatureRaw` bits `14..0` reset `25`

### `FAN_COMMAND`

- Address: `0x20`
- Access: `rw`
- Width: `16`

- `dutyCommand` bits `7..0` reset `0`
- `commandValid` bits `15` reset `0`

### `FAULT_STATUS`

- Address: `0x30`
- Access: `ro`
- Width: `8`

- `sensorInvalid` bits `0` reset `0`

## State Transitions

Lifecycle/topology view. Executable behavior is owned by `mbd-control` and derived generated views.

- `RESET` -> `IDLE` when `powerOn`
- `IDLE` -> `COOLING` when `temperatureC >= fanOnThreshold`
- `COOLING` -> `IDLE` when `temperatureC <= fanOffThreshold`
- `IDLE` -> `FAULT` when `temperatureValid == false`
- `COOLING` -> `FAULT` when `temperatureValid == false`
- `FAULT` -> `IDLE` when `temperatureValid == true`

## Flow Preview

- `ToyTempSensorIC.temperatureC` -> `HAL_SPI.read_temperature` (virtual sensor sample) trace `SYS-001, HAR-001`
- `HAL_SPI.read_temperature` -> `ToyThermalFanController.temperatureC` (HAL input) trace `SWE-004, HAR-002`
- `ToyThermalFanController.fanDuty` -> `HAL_PWM.set_fan_duty` (generated ECU command) trace `SYS-002, SWE-004`
- `HAL_PWM.set_fan_duty` -> `ToyFanDriverIC.dutyCommand` (virtual actuator command) trace `SYS-002, HAR-001`
- `ToyThermalFanController.fault` -> `ScenarioReport.observedBehavior` (fault observation) trace `SYS-006, HAR-004`

## Control Rules

- priority `1000` `sensorFault` from `*`: when `temperatureValid == false` then `state=FAULT, fanDuty=safeDuty, fault=true` trace `SYS-005, HAR-004`
- priority `1001` `highTemperature` from `*`: when `temperatureC >= fanOnThreshold` then `state=COOLING, fanDuty=coolingDuty, fault=false` trace `SYS-003, SYS-006`
- priority `1002` `lowTemperature` from `*`: when `temperatureC <= fanOffThreshold` then `state=IDLE, fanDuty=0, fault=false` trace `SYS-004, SYS-006`

## Harness Boundary

- `ToyTempSensorIC` role `sensor` boundary `virtual_ic` trace `HAR-001, SYS-001`
- `ToyFanDriverIC` role `actuator` boundary `virtual_ic` trace `HAR-001, SYS-002`
- `ToyThermalFanController` role `controller` boundary `hal` trace `HAR-002, SWE-004`

## Verification Direction

- Simulink `.m`, Modelica `.mo`, SCXML, Mermaid, PlantUML, and FMI metadata are generated handoff artifacts.
- Existing MBD tools are the intended verification backends.
- This repository does not claim certification.
