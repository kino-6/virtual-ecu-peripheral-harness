# Toy Thermal Fan Control Specification

This specification is derived from `Requirements.md`. It describes a fictional
control example for MBD handoff and preview testing only.

## Trace Scope

- Requirements: `STK-001` - `STK-005`, `SYS-001` - `SYS-006`,
  `SWE-001` - `SWE-005`, `MBD-001` - `MBD-007`, `HAR-001` - `HAR-005`,
  `PROC-001` - `PROC-004`
- Source intent: fictional thermal fan control validation.
- Boundary: no real IC, real register map, production ECU logic, safety claim,
  certification claim, or tool qualification claim.

## Fictional IC Boundary

`ToyTempSensorIC` exposes a virtual temperature reading and a validity flag.
`ToyFanDriverIC` accepts a virtual fan duty command. Both devices are synthetic
and exist only to exercise the harness boundary.

Trace: `SYS-001`, `SYS-002`, `HAR-001`

## Controller Behavior

`ToyThermalFanController` reads `temperatureC` and `temperatureValid` through
HAL-style boundaries. It commands `fanDuty` and `fault`.

- When `temperatureValid` is false, the controller enters `FAULT` and commands
  `safeDuty`.
- When temperature is at or above `fanOnThreshold`, the controller enters
  `COOLING` and commands `coolingDuty`.
- When temperature is at or below `fanOffThreshold`, the controller enters
  `IDLE` and commands zero duty.
- Otherwise, the controller holds a reviewable nominal state and command.

Trace: `SYS-003`, `SYS-004`, `SYS-005`, `SWE-004`

## PDCA/TDD Path

1. Requirements define the fictional intent and trace IDs.
2. This specification explains behavior in human-readable form.
3. `examples/toy_thermal_fan_control.mbd.md` provides the public MBD authoring
   source.
4. Exporters generate Markdown, Mermaid, PlantUML, SCXML, Simulink `.m`,
   Modelica `.mo`, and FMI metadata handoff artifacts.
5. Preview scenarios provide smoke evidence and reports only; they do not
   replace verification in MBD tools.
6. Preview C scaffolding demonstrates a HAL-shaped controller boundary and is
   not certified.

Trace: `STK-005`, `PROC-002`, `PROC-003`, `PROC-004`
