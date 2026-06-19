# Simple Threshold Indicator

> Generated review document from Mermaid-like MBD markup.
> Authoring source is the `.mbd.md` file; this document is a review artifact.

Source: `samples/simple_threshold_indicator/model.mbd.md`

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

- `SIMPLE-001`
- `SIMPLE-002`
- `SIMPLE-003`

## Component

- Name: `ToyThresholdIndicator`
- Bus: `virtual`
- Bus mode: `preview`
- Bus wordBits: `8`

## Functional Decomposition

| Function | Responsibility | Owns | Inputs | Outputs | Trace | Scenarios |
| --- | --- | --- | --- | --- | --- | --- |
| `ThresholdCompare` | Compare sampleValue against limit and own the active decision | `active`, `ACTIVE`, `IDLE` | `sampleValue`, `limit` | `active`, `state` | `SIMPLE-001`, `SIMPLE-002`, `SIMPLE-003` | `above_limit` |

## Ports

| Direction | Name | Type | Default |
| --- | --- | --- | --- |
| in | `sampleValue` | `count` | `0` |
| out | `active` | `bool` | `false` |

## Registers

### `STATUS`

- Address: `0x01`
- Access: `ro`
- Width: `8`

- `active` bits `0` reset `0`

## State Transitions

Lifecycle/topology view. Executable behavior is owned by `mbd-control` and derived generated views.

- `IDLE` -> `ACTIVE` when `sampleValue >= limit trace SIMPLE-001`
- `ACTIVE` -> `IDLE` when `sampleValue < limit trace SIMPLE-002`

## Flow Preview

- `ToyInputSource.sampleValue` -> `ThresholdCompare.sampleValue` (scenario input) trace `SIMPLE-001`
- `ToyThresholdIndicator.limit` -> `ThresholdCompare.limit` (threshold parameter) trace `SIMPLE-001, SIMPLE-002`
- `ThresholdCompare.active` -> `ToyThresholdIndicator.active` (comparison result) trace `SIMPLE-001, SIMPLE-002`
- `ToyThresholdIndicator.active` -> `ScenarioReport.observedBehavior` (reported output) trace `SIMPLE-003`

## Control Rules

- priority `10` `activate` owner `ThresholdCompare` from `*`: when `sampleValue >= limit` then `state=ACTIVE, active=true` trace `SIMPLE-001, SIMPLE-003` scenarios `above_limit`
- priority `20` `clear` owner `ThresholdCompare` from `*`: when `sampleValue < limit` then `state=IDLE, active=false` trace `SIMPLE-002, SIMPLE-003`

## Harness Boundary

- `ToyInputSource` role `source` boundary `virtual_ic` trace `SIMPLE-001`
- `ToyThresholdIndicator` role `controller` boundary `hal` trace `SIMPLE-001, SIMPLE-002, SIMPLE-003`

## Verification Direction

- Simulink `.m`, Modelica `.mo`, SCXML, Mermaid, PlantUML, and FMI metadata are generated handoff artifacts.
- Existing MBD tools are the intended verification backends.
- This repository does not claim certification.
