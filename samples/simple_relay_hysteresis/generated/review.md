# Simple Relay Hysteresis

> Generated review document from Mermaid-like MBD markup.
> Authoring source is the `.mbd.md` file; this document is a review artifact.

Source: `samples/simple_relay_hysteresis/model.mbd.md`

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

- `RLY-001`
- `RLY-002`
- `RLY-003`
- `RLY-004`
- `RLY-005`

## Component

- Name: `ToyRelayHysteresis`
- Bus: `virtual`
- Bus mode: `preview`
- Bus wordBits: `8`

## Functional Decomposition

| Function | Responsibility | Owns | Inputs | Outputs | Trace | Scenarios |
| --- | --- | --- | --- | --- | --- | --- |
| `ToyRelayController` | Own OFF/ON relay hysteresis and map threshold-crossing transitions to active output | `OFF`, `ON`, `active` | `level`, `onThreshold`, `offThreshold` | `state`, `active` | `RLY-001`, `RLY-002`, `RLY-003`, `RLY-004`, `RLY-005` | `hysteresis_cycle` |

## Ports

| Direction | Name | Type | Default |
| --- | --- | --- | --- |
| in | `level` | `count` | `0` |
| out | `active` | `bool` | `false` |

## Registers

### `STATUS`

- Address: `0x01`
- Access: `ro`
- Width: `8`

- `active` bits `0` reset `0`

## State Transitions

Lifecycle/topology view. Executable behavior is owned by `mbd-control` and derived generated views.

- `OFF` -> `ON` when `level >= onThreshold`
- `ON` -> `OFF` when `level <= offThreshold`

## Flow Preview

- `ToyLevelSource.level` -> `ToyRelayController.level` (scenario input) trace `RLY-001, RLY-002, RLY-003, RLY-004`
- `ToyRelayHysteresis.onThreshold` -> `ToyRelayController.onThreshold` (switch-on threshold) trace `RLY-001, RLY-004`
- `ToyRelayHysteresis.offThreshold` -> `ToyRelayController.offThreshold` (switch-off threshold) trace `RLY-002, RLY-004`
- `ToyRelayController.active` -> `ToyRelayHysteresis.active` (relay output) trace `RLY-001, RLY-002, RLY-003`
- `ToyRelayHysteresis.active` -> `ScenarioReport.observedBehavior` (reported active output) trace `RLY-005`

## Control Rules

- priority `10` `off_to_on` owner `ToyRelayController` from `OFF`: when `level >= onThreshold` then `state=ON, active=true` trace `RLY-001, RLY-003, RLY-005` scenarios `hysteresis_cycle`
- priority `20` `on_to_off` owner `ToyRelayController` from `ON`: when `level <= offThreshold` then `state=OFF, active=false` trace `RLY-002, RLY-003, RLY-005` scenarios `hysteresis_cycle`

## Harness Boundary

- `ToyLevelSource` role `source` boundary `virtual_ic` trace `RLY-001, RLY-002, RLY-003, RLY-004`
- `ToyRelayHysteresis` role `controller` boundary `hal` trace `RLY-001, RLY-002, RLY-003, RLY-004, RLY-005`

## Verification Direction

- Simulink `.m`, Modelica `.mo`, SCXML, Mermaid, PlantUML, and FMI metadata are generated handoff artifacts.
- Existing MBD tools are the intended verification backends.
- This repository does not claim certification.
