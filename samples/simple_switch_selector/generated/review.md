# Simple Switch Selector

> Generated review document from Mermaid-like MBD markup.
> Authoring source is the `.mbd.md` file; this document is a review artifact.

Source: `samples/simple_switch_selector/model.mbd.md`

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

- `SWS-001`
- `SWS-002`
- `SWS-003`
- `SWS-004`

## Component

- Name: `ToySwitchSelector`
- Bus: `virtual`
- Bus mode: `preview`
- Bus wordBits: `8`

## Functional Decomposition

| Function | Responsibility | Owns | Inputs | Outputs | Trace | Scenarios |
| --- | --- | --- | --- | --- | --- | --- |
| `SwitchSelector` | Compare selectHigh and select highValue or lowValue using Switch-style simple conditional logic | `selectedValue` | `selectHigh`, `highValue`, `lowValue` | `selectedValue` | `SWS-001`, `SWS-002`, `SWS-003`, `SWS-004` | `select_high` |

## Ports

| Direction | Name | Type | Default |
| --- | --- | --- | --- |
| in | `selectHigh` | `bool` | `false` |
| out | `selectedValue` | `count` | `25` |

## Registers

### `STATUS`

- Address: `0x01`
- Access: `ro`
- Width: `8`

- `selectedValue` bits `0` reset `25`

## State Transitions

Lifecycle/topology view. Executable behavior is owned by `mbd-control` and derived generated views.


## Flow Preview

- `ToySelectorSource.selectHigh` -> `SwitchSelector.selectHigh` (selector input) trace `SWS-001, SWS-002, SWS-003`
- `ToySwitchSelector.highValue` -> `SwitchSelector.highValue` (high constant value) trace `SWS-001, SWS-003`
- `ToySwitchSelector.lowValue` -> `SwitchSelector.lowValue` (low constant value) trace `SWS-002, SWS-003`
- `SwitchSelector.selectedValue` -> `ToySwitchSelector.selectedValue` (selected output) trace `SWS-001, SWS-002`
- `ToySwitchSelector.selectedValue` -> `ScenarioReport.observedBehavior` (reported selected value) trace `SWS-004`

## Control Rules

- priority `10` `select_high_value` owner `SwitchSelector` from `*`: when `selectHigh == true` then `selectedValue=highValue` trace `SWS-001, SWS-003, SWS-004` scenarios `select_high`
- priority `20` `select_low_value` owner `SwitchSelector` from `*`: when `selectHigh != true` then `selectedValue=lowValue` trace `SWS-002, SWS-003, SWS-004` scenarios `select_high`

## Harness Boundary

- `ToySelectorSource` role `source` boundary `virtual_ic` trace `SWS-001, SWS-002, SWS-003`
- `ToySwitchSelector` role `controller` boundary `hal` trace `SWS-001, SWS-002, SWS-003, SWS-004`

## Verification Direction

- Simulink `.m`, Modelica `.mo`, SCXML, Mermaid, PlantUML, and FMI metadata are generated handoff artifacts.
- Existing MBD tools are the intended verification backends.
- This repository does not claim certification.
