# Toy Thermal Protection Controller

> Generated review document from Mermaid-like MBD markup.
> Authoring source is the `.mbd.md` file; this document is a review artifact.

Source: `examples/toy_thermal_protection_controller.mbd.md`

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

- `CGEN-003`
- `ENG-002`
- `HAR-001`
- `HAR-002`
- `HAR-003`
- `HAR-004`
- `HAR-006`
- `SWE-001`
- `SWE-002`
- `SWE-003`
- `SWE-004`
- `SYS-001`
- `SYS-002`
- `SYS-003`
- `SYS-004`
- `SYS-005`
- `SYS-006`
- `SYS-007`
- `SYS-008`
- `SYS-009`

## Component

- Name: `ToyThermalProtectionController`
- Bus: `virtual`
- Bus mode: `preview`
- Bus wordBits: `16`

## Ports

| Direction | Name | Type | Default |
| --- | --- | --- | --- |
| in | `temperatureC` | `degC` | `25` |
| in | `temperatureValid` | `bool` | `true` |
| in | `invalidDebounced` | `bool` | `false` |
| in | `recoveryRequest` | `bool` | `false` |
| out | `fanDuty` | `percent` | `0` |
| out | `deratingCommand` | `percent` | `0` |
| out | `diagnosticFault` | `bool` | `false` |
| out | `safeCommandActive` | `bool` | `false` |

## Registers

### `TP_TEMP_STATUS`

- Address: `0x10`
- Access: `ro`
- Width: `16`

- `valid` bits `15` reset `1`
- `temperatureCode` bits `14..0` reset `25`

### `TP_CONTROL_STATUS`

- Address: `0x20`
- Access: `ro`
- Width: `16`

- `fanDutyMirror` bits `7..0` reset `0`
- `deratingActive` bits `8` reset `0`
- `safeCommandActive` bits `9` reset `0`
- `diagnosticFault` bits `10` reset `0`

### `TP_COMMAND`

- Address: `0x30`
- Access: `rw`
- Width: `16`

- `fanDutyCommand` bits `7..0` reset `0`
- `deratingCommand` bits `14..8` reset `0`
- `commandValid` bits `15` reset `0`

## State Transitions

- `RESET` -> `IDLE` when `temperatureValid == true`
- `IDLE` -> `COOLING` when `temperatureC >= coolingOnThreshold`
- `COOLING` -> `IDLE` when `temperatureC <= coolingOffThreshold`
- `COOLING` -> `DERATING` when `temperatureC >= deratingEntryThreshold`
- `DERATING` -> `COOLING` when `temperatureC < deratingEntryThreshold`
- `IDLE` -> `SENSOR_FAULT` when `temperatureValid == false`
- `COOLING` -> `SENSOR_FAULT` when `temperatureValid == false`
- `DERATING` -> `SENSOR_FAULT` when `temperatureValid == false`
- `SENSOR_FAULT` -> `FAULT_LATCHED` when `invalidDebounced == true`
- `FAULT_LATCHED` -> `IDLE` when `temperatureValid == true and invalidDebounced == false and recoveryRequest == true`

## Flow Preview

- `ToyTempSensorIC.temperatureC` -> `HAL_SPI.read_temperature` (virtual sensor sample) trace `SYS-001, HAR-001`
- `ToyTempSensorIC.temperatureValid` -> `HAL_SPI.read_temperature` (virtual validity sample) trace `SYS-001, SYS-006, HAR-001`
- `ToyTempSensorIC.invalidDebounced` -> `ToyThermalProtectionController.invalidDebounced` (preview debounce input) trace `SYS-007, ENG-002, HAR-003`
- `HAL_SPI.read_temperature` -> `ToyThermalProtectionController.temperatureC` (HAL temperature input) trace `SWE-004, HAR-002`
- `ToyThermalProtectionController.fanDuty` -> `HAL_PWM.set_fan_duty` (generated ECU fan command) trace `SYS-002, SWE-004, CGEN-003`
- `ToyThermalProtectionController.deratingCommand` -> `HAL_LIMITER.set_derating` (generated ECU derating command) trace `SYS-005, SWE-004, CGEN-003`
- `HAL_PWM.set_fan_duty` -> `ToyFanDriverIC.dutyCommand` (virtual actuator command) trace `SYS-002, HAR-001`
- `HAL_LIMITER.set_derating` -> `ToyLoadLimiterIC.limitCommand` (virtual load limiter command) trace `SYS-005, HAR-006`
- `ToyThermalProtectionController.diagnosticFault` -> `ScenarioReport.observedBehavior` (diagnostic observation) trace `SYS-006, SYS-007, HAR-004`
- `ToyThermalProtectionController.safeCommandActive` -> `ScenarioReport.passFailResult` (scenario pass/fail evidence) trace `SYS-009, HAR-004`

## Control Rules

- `recoverFromLatch`: when `state == FAULT_LATCHED and temperatureValid == true and invalidDebounced == false and recoveryRequest == true` then `state=IDLE, fanDuty=0, deratingCommand=0, diagnosticFault=false, safeCommandActive=false` trace `SYS-008, HAR-006`
- `faultLatch`: when `invalidDebounced == true` then `state=FAULT_LATCHED, fanDuty=safeDuty, deratingCommand=0, diagnosticFault=true, safeCommandActive=true` trace `SYS-007, SYS-006, HAR-004`
- `holdLatchedFault`: when `state == FAULT_LATCHED` then `state=FAULT_LATCHED, fanDuty=safeDuty, deratingCommand=0, diagnosticFault=true, safeCommandActive=true` trace `SYS-007, HAR-004`
- `sensorInvalid`: when `temperatureValid == false` then `state=SENSOR_FAULT, fanDuty=safeDuty, deratingCommand=0, diagnosticFault=true, safeCommandActive=true` trace `SYS-006, HAR-004`
- `derating`: when `temperatureC >= deratingEntryThreshold` then `state=DERATING, fanDuty=deratingFanDuty, deratingCommand=deratingLimit, diagnosticFault=false, safeCommandActive=false` trace `SYS-005, SYS-002, HAR-004`
- `highCooling`: when `temperatureC >= coolingOnThreshold` then `state=COOLING, fanDuty=coolingDuty, deratingCommand=0, diagnosticFault=false, safeCommandActive=false` trace `SYS-003, SYS-002, HAR-004`
- `lowCooling`: when `temperatureC <= coolingOffThreshold` then `state=IDLE, fanDuty=0, deratingCommand=0, diagnosticFault=false, safeCommandActive=false` trace `SYS-004, HAR-004`

## Harness Boundary

- `ToyTempSensorIC` role `sensor` boundary `virtual_ic` trace `HAR-001, SYS-001, SYS-006, SYS-007`
- `ToyFanDriverIC` role `actuator` boundary `virtual_ic` trace `HAR-001, SYS-002`
- `ToyLoadLimiterIC` role `actuator` boundary `virtual_ic` trace `HAR-006, SYS-005`
- `ToyThermalProtectionController` role `controller` boundary `hal` trace `HAR-002, SWE-004, CGEN-003`

## Verification Direction

- Simulink `.m`, Modelica `.mo`, SCXML, Mermaid, PlantUML, and FMI metadata are generated handoff artifacts.
- Existing MBD tools are the intended verification backends.
- This repository does not claim certification.
