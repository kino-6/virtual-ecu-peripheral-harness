# Toy Energy Buffer Mode

> Generated review document from Mermaid-like MBD markup.
> Authoring source is the `.mbd.md` file; this document is a review artifact.

Source: `samples/toy_energy_buffer_mode/model.mbd.md`

## Intent

Author in text. Verify in MBD tools. Python preview is only a preview/smoke-test helper.

## Traceability To Markup Sections

- `mbd-component`
- `mbd-registers`
- `mbd-state`
- `mbd-decomposition`
- `mbd-flow`
- `mbd-control`
- `mbd-harness`

## Requirements Trace

- `EBUF-001`
- `EBUF-002`
- `EBUF-003`
- `EBUF-004`
- `EBUF-005`
- `EBUF-006`

## Component

- Name: `ToyEnergyBufferMode`
- Bus: `virtual`
- Bus mode: `preview`
- Bus wordBits: `8`

## Functional Decomposition

| Function | Responsibility | Owns | Inputs | Outputs | Trace | Scenarios |
| --- | --- | --- | --- | --- | --- | --- |
| `ToyEnergyBufferModeController` | Own the CHARGE/DISCHARGE/EMPTY lifecycle and map source availability plus empty detection to supply and charge indication outputs | `CHARGE`, `DISCHARGE`, `EMPTY`, `supplyEnabled`, `chargeIndicator` | `externalPowerAvailable`, `emptyDetected` | `state`, `supplyEnabled`, `chargeIndicator` | `EBUF-001`, `EBUF-002`, `EBUF-003`, `EBUF-004`, `EBUF-005`, `EBUF-006` | `source_loss_recovery` |

## Ports

| Direction | Name | Type | Default |
| --- | --- | --- | --- |
| in | `externalPowerAvailable` | `bool` | `true` |
| in | `emptyDetected` | `bool` | `false` |
| out | `supplyEnabled` | `bool` | `false` |
| out | `chargeIndicator` | `bool` | `true` |

## Registers

### `STATUS`

- Address: `0x01`
- Access: `ro`
- Width: `8`

- `supplyEnabled` bits `0` reset `0`
- `chargeIndicator` bits `1` reset `1`

## State Transitions

Lifecycle/topology view. Executable behavior is owned by `mbd-control` and derived generated views.

- `CHARGE` -> `DISCHARGE` when `externalPowerAvailable == false and emptyDetected == false`
- `DISCHARGE` -> `EMPTY` when `emptyDetected == true`
- `EMPTY` -> `CHARGE` when `externalPowerAvailable == true`
- `DISCHARGE` -> `CHARGE` when `externalPowerAvailable == true`

## Flow Preview

- `ToyPowerSource.externalPowerAvailable` -> `ToyEnergyBufferModeController.externalPowerAvailable` (source availability) trace `EBUF-001, EBUF-003, EBUF-004, EBUF-005`
- `ToyEmptyMonitor.emptyDetected` -> `ToyEnergyBufferModeController.emptyDetected` (empty indication) trace `EBUF-001, EBUF-002, EBUF-005`
- `ToyEnergyBufferModeController.supplyEnabled` -> `ToyEnergyBufferMode.supplyEnabled` (supply command) trace `EBUF-001, EBUF-002, EBUF-003, EBUF-004, EBUF-005`
- `ToyEnergyBufferModeController.chargeIndicator` -> `ToyEnergyBufferMode.chargeIndicator` (charge indication) trace `EBUF-001, EBUF-002, EBUF-003, EBUF-004, EBUF-005`
- `ToyEnergyBufferMode.supplyEnabled` -> `ScenarioReport.observedBehavior` (reported supply command) trace `EBUF-006`
- `ToyEnergyBufferMode.chargeIndicator` -> `ScenarioReport.observedBehavior` (reported charge indication) trace `EBUF-006`

## Control Rules

- priority `10` `power_removed_discharge` owner `ToyEnergyBufferModeController` from `CHARGE`: when `externalPowerAvailable == false and emptyDetected == false` then `state=DISCHARGE, supplyEnabled=true, chargeIndicator=false` trace `EBUF-001, EBUF-006` scenarios `source_loss_recovery`
- priority `20` `discharge_empty` owner `ToyEnergyBufferModeController` from `DISCHARGE`: when `emptyDetected == true` then `state=EMPTY, supplyEnabled=false, chargeIndicator=false` trace `EBUF-002, EBUF-006` scenarios `source_loss_recovery`
- priority `30` `empty_reconnect_charge` owner `ToyEnergyBufferModeController` from `EMPTY`: when `externalPowerAvailable == true` then `state=CHARGE, supplyEnabled=false, chargeIndicator=true` trace `EBUF-003, EBUF-006` scenarios `source_loss_recovery`
- priority `40` `discharge_reconnect_charge` owner `ToyEnergyBufferModeController` from `DISCHARGE`: when `externalPowerAvailable == true` then `state=CHARGE, supplyEnabled=false, chargeIndicator=true` trace `EBUF-004, EBUF-006` scenarios `source_loss_recovery`

## Harness Boundary

- `ToyPowerSource` role `source` boundary `virtual_ic` trace `EBUF-001, EBUF-003, EBUF-004, EBUF-005`
- `ToyEmptyMonitor` role `source` boundary `virtual_ic` trace `EBUF-001, EBUF-002, EBUF-005`
- `ToyEnergyBufferMode` role `controller` boundary `hal` trace `EBUF-001, EBUF-002, EBUF-003, EBUF-004, EBUF-005, EBUF-006`

## Verification Direction

- Simulink `.m`, Modelica `.mo`, SCXML, Mermaid, PlantUML, and FMI metadata are generated handoff artifacts.
- Existing MBD tools are the intended verification backends.
- This repository does not claim certification.
