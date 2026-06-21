# Simple State Machine

> Generated review document from Mermaid-like MBD markup.
> Authoring source is the `.mbd.md` file; this document is a review artifact.

Source: `samples/simple_state_machine/model.mbd.md`

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

- `SM-001`
- `SM-002`
- `SM-003`
- `SM-004`

## Component

- Name: `ToyStateMachine`
- Bus: `virtual`
- Bus mode: `preview`
- Bus wordBits: `8`

## Functional Decomposition

| Function | Responsibility | Owns | Inputs | Outputs | Trace | Scenarios |
| --- | --- | --- | --- | --- | --- | --- |
| `ToyStateController` | Own the IDLE/RUNNING/DONE lifecycle and map state transitions to busy and complete outputs | `IDLE`, `RUNNING`, `DONE`, `busy`, `complete` | `startCommand`, `finishCommand`, `resetCommand` | `state`, `busy`, `complete` | `SM-001`, `SM-002`, `SM-003`, `SM-004` | `full_cycle` |

## Ports

| Direction | Name | Type | Default |
| --- | --- | --- | --- |
| in | `startCommand` | `bool` | `false` |
| in | `finishCommand` | `bool` | `false` |
| in | `resetCommand` | `bool` | `false` |
| out | `busy` | `bool` | `false` |
| out | `complete` | `bool` | `false` |

## Registers

### `STATUS`

- Address: `0x01`
- Access: `ro`
- Width: `8`

- `busy` bits `0` reset `0`
- `complete` bits `1` reset `0`

## State Transitions

Lifecycle/topology view. Executable behavior is owned by `mbd-control` and derived generated views.

- `IDLE` -> `RUNNING` when `startCommand == true`
- `RUNNING` -> `DONE` when `finishCommand == true`
- `DONE` -> `IDLE` when `resetCommand == true`

## Flow Preview

- `ToyCommandSource.startCommand` -> `ToyStateController.startCommand` (start request) trace `SM-001`
- `ToyCommandSource.finishCommand` -> `ToyStateController.finishCommand` (finish request) trace `SM-002`
- `ToyCommandSource.resetCommand` -> `ToyStateController.resetCommand` (reset request) trace `SM-003`
- `ToyStateController.busy` -> `ToyStateMachine.busy` (busy command) trace `SM-001, SM-002, SM-003`
- `ToyStateController.complete` -> `ToyStateMachine.complete` (completion command) trace `SM-002, SM-003`
- `ToyStateMachine.busy` -> `ScenarioReport.observedBehavior` (reported busy output) trace `SM-004`
- `ToyStateMachine.complete` -> `ScenarioReport.observedBehavior` (reported complete output) trace `SM-004`

## Control Rules

- priority `10` `start_running` owner `ToyStateController` from `IDLE`: when `startCommand == true` then `state=RUNNING, busy=true, complete=false` trace `SM-001, SM-004` scenarios `full_cycle`
- priority `20` `finish_done` owner `ToyStateController` from `RUNNING`: when `finishCommand == true` then `state=DONE, busy=false, complete=true` trace `SM-002, SM-004` scenarios `full_cycle`
- priority `30` `reset_idle` owner `ToyStateController` from `DONE`: when `resetCommand == true` then `state=IDLE, busy=false, complete=false` trace `SM-003, SM-004` scenarios `full_cycle`

## Harness Boundary

- `ToyCommandSource` role `source` boundary `virtual_ic` trace `SM-001, SM-002, SM-003`
- `ToyStateMachine` role `controller` boundary `hal` trace `SM-001, SM-002, SM-003, SM-004`

## Verification Direction

- Simulink `.m`, Modelica `.mo`, SCXML, Mermaid, PlantUML, and FMI metadata are generated handoff artifacts.
- Existing MBD tools are the intended verification backends.
- This repository does not claim certification.
