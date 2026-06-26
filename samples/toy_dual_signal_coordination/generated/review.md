# Toy Dual Signal Coordination

> Generated review document from Mermaid-like MBD markup.
> Authoring source is the `.mbd.md` file; this document is a review artifact.

Source: `samples/toy_dual_signal_coordination/model.mbd.md`

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

- `DSC-001`
- `DSC-002`
- `DSC-003`
- `DSC-004`
- `DSC-005`
- `DSC-006`
- `DSC-007`
- `DSC-PRE-001`
- `DSC-PRE-002`

## Component

- Name: `ToyDualSignalCoordinator`
- Bus: `virtual`
- Bus mode: `preview`
- Bus wordBits: `16`

## Functional Decomposition

| Function | Responsibility | Owns | Inputs | Outputs | Trace | Scenarios |
| --- | --- | --- | --- | --- | --- | --- |
| `ToyCrossingCoordinator` | Own request arbitration and all-stop clearance before changing directional grants | `MAIN_GO_SIDE_STOP`, `MAIN_WARN_SIDE_STOP`, `ALL_STOP_BEFORE_SIDE`, `MAIN_STOP_SIDE_GO`, `MAIN_STOP_SIDE_WARN`, `ALL_STOP_BEFORE_MAIN` | `sideRequest`, `mainWarningExpired`, `clearanceExpired`, `sideServed`, `sideWarningExpired` | `state` | `DSC-001`, `DSC-002`, `DSC-003`, `DSC-004`, `DSC-005`, `DSC-PRE-001`, `DSC-PRE-002` | `side_request_cycle` |
| `MainSignalStateMachine` | Map coordinated modes to the main signal go warn stop outputs | `mainGreen`, `mainYellow`, `mainRed` | `state` | `mainGreen`, `mainYellow`, `mainRed` | `DSC-001`, `DSC-002`, `DSC-003`, `DSC-004`, `DSC-006`, `DSC-007` | `side_request_cycle` |
| `SideSignalStateMachine` | Map coordinated modes to the side signal stop go warn outputs | `sideGreen`, `sideYellow`, `sideRed` | `state` | `sideGreen`, `sideYellow`, `sideRed` | `DSC-003`, `DSC-004`, `DSC-005`, `DSC-006`, `DSC-007` | `side_request_cycle` |
| `InterlockMonitor` | Expose the no-both-green invariant as preview evidence | `mainGreen`, `sideGreen` | `mainGreen`, `sideGreen` | `ScenarioReport.passFailResult` | `DSC-006`, `DSC-PRE-001` | `side_request_cycle` |

## Ports

| Direction | Name | Type | Default |
| --- | --- | --- | --- |
| in | `sideRequest` | `bool` | `false` |
| in | `mainWarningExpired` | `bool` | `false` |
| in | `clearanceExpired` | `bool` | `false` |
| in | `sideServed` | `bool` | `false` |
| in | `sideWarningExpired` | `bool` | `false` |
| out | `mainGreen` | `bool` | `true` |
| out | `mainYellow` | `bool` | `false` |
| out | `mainRed` | `bool` | `false` |
| out | `sideGreen` | `bool` | `false` |
| out | `sideYellow` | `bool` | `false` |
| out | `sideRed` | `bool` | `true` |

## Registers

### `INPUT_STATUS`

- Address: `0x01`
- Access: `ro`
- Width: `8`

- `sideRequest` bits `0` reset `0`
- `mainWarningExpired` bits `1` reset `0`
- `clearanceExpired` bits `2` reset `0`
- `sideServed` bits `3` reset `0`
- `sideWarningExpired` bits `4` reset `0`

### `SIGNAL_COMMAND`

- Address: `0x10`
- Access: `rw`
- Width: `16`

- `mainGreen` bits `0` reset `1`
- `mainYellow` bits `1` reset `0`
- `mainRed` bits `2` reset `0`
- `sideGreen` bits `8` reset `0`
- `sideYellow` bits `9` reset `0`
- `sideRed` bits `10` reset `1`

## State Transitions

Lifecycle/topology view. Executable behavior is owned by `mbd-control` and derived generated views.

- `MAIN_GO_SIDE_STOP` -> `MAIN_WARN_SIDE_STOP` when `sideRequest == true`
- `MAIN_WARN_SIDE_STOP` -> `ALL_STOP_BEFORE_SIDE` when `mainWarningExpired == true`
- `ALL_STOP_BEFORE_SIDE` -> `MAIN_STOP_SIDE_GO` when `clearanceExpired == true`
- `MAIN_STOP_SIDE_GO` -> `MAIN_STOP_SIDE_WARN` when `sideServed == true`
- `MAIN_STOP_SIDE_WARN` -> `ALL_STOP_BEFORE_MAIN` when `sideWarningExpired == true`
- `ALL_STOP_BEFORE_MAIN` -> `MAIN_GO_SIDE_STOP` when `clearanceExpired == true`

## Flow Preview

- `ToySideRequestSource.sideRequest` -> `ToyCrossingCoordinator.sideRequest` (side grant request) trace `DSC-002, DSC-004`
- `ToyMainWarningTimer.expired` -> `ToyCrossingCoordinator.mainWarningExpired` (main warning completion) trace `DSC-002, DSC-003`
- `ToyClearanceTimer.expired` -> `ToyCrossingCoordinator.clearanceExpired` (all-stop clearance completion) trace `DSC-003, DSC-004, DSC-005`
- `ToySideServiceSource.sideServed` -> `ToyCrossingCoordinator.sideServed` (side service completion) trace `DSC-005`
- `ToySideWarningTimer.expired` -> `ToyCrossingCoordinator.sideWarningExpired` (side warning completion) trace `DSC-005`
- `ToyCrossingCoordinator.state` -> `MainSignalStateMachine.state` (coordinated mode projection) trace `DSC-001, DSC-002, DSC-003, DSC-004, DSC-007`
- `ToyCrossingCoordinator.state` -> `SideSignalStateMachine.state` (coordinated mode projection) trace `DSC-003, DSC-004, DSC-005, DSC-007`
- `ToyDualSignalCoordinator.mainGreen` -> `ScenarioReport.observedBehavior` (main green evidence) trace `DSC-001, DSC-006`
- `ToyDualSignalCoordinator.mainYellow` -> `ScenarioReport.observedBehavior` (main warning evidence) trace `DSC-002`
- `ToyDualSignalCoordinator.mainRed` -> `ScenarioReport.observedBehavior` (main stop evidence) trace `DSC-003, DSC-004`
- `ToyDualSignalCoordinator.sideGreen` -> `ScenarioReport.observedBehavior` (side green evidence) trace `DSC-004, DSC-006`
- `ToyDualSignalCoordinator.sideYellow` -> `ScenarioReport.observedBehavior` (side warning evidence) trace `DSC-005`
- `ToyDualSignalCoordinator.sideRed` -> `ScenarioReport.observedBehavior` (side stop evidence) trace `DSC-001, DSC-002, DSC-003`

## Control Rules

- priority `10` `request_side_prepare_main` owner `ToyCrossingCoordinator` from `MAIN_GO_SIDE_STOP`: when `sideRequest == true` then `state=MAIN_WARN_SIDE_STOP, mainGreen=false, mainYellow=true, mainRed=false, sideGreen=false, sideYellow=false, sideRed=true` trace `DSC-002, DSC-006, DSC-007` scenarios `side_request_cycle`
- priority `20` `main_warning_to_all_stop` owner `ToyCrossingCoordinator` from `MAIN_WARN_SIDE_STOP`: when `mainWarningExpired == true` then `state=ALL_STOP_BEFORE_SIDE, mainGreen=false, mainYellow=false, mainRed=true, sideGreen=false, sideYellow=false, sideRed=true` trace `DSC-003, DSC-006, DSC-007` scenarios `side_request_cycle`
- priority `30` `clearance_to_side_go` owner `ToyCrossingCoordinator` from `ALL_STOP_BEFORE_SIDE`: when `clearanceExpired == true` then `state=MAIN_STOP_SIDE_GO, mainGreen=false, mainYellow=false, mainRed=true, sideGreen=true, sideYellow=false, sideRed=false` trace `DSC-004, DSC-006, DSC-007` scenarios `side_request_cycle`
- priority `40` `side_service_prepare_main` owner `ToyCrossingCoordinator` from `MAIN_STOP_SIDE_GO`: when `sideServed == true` then `state=MAIN_STOP_SIDE_WARN, mainGreen=false, mainYellow=false, mainRed=true, sideGreen=false, sideYellow=true, sideRed=false` trace `DSC-005, DSC-006, DSC-007` scenarios `side_request_cycle`
- priority `50` `side_warning_to_all_stop` owner `ToyCrossingCoordinator` from `MAIN_STOP_SIDE_WARN`: when `sideWarningExpired == true` then `state=ALL_STOP_BEFORE_MAIN, mainGreen=false, mainYellow=false, mainRed=true, sideGreen=false, sideYellow=false, sideRed=true` trace `DSC-003, DSC-005, DSC-006, DSC-007` scenarios `side_request_cycle`
- priority `60` `clearance_to_main_go` owner `ToyCrossingCoordinator` from `ALL_STOP_BEFORE_MAIN`: when `clearanceExpired == true` then `state=MAIN_GO_SIDE_STOP, mainGreen=true, mainYellow=false, mainRed=false, sideGreen=false, sideYellow=false, sideRed=true` trace `DSC-001, DSC-005, DSC-006, DSC-007` scenarios `side_request_cycle`

## Harness Boundary

- `ToySideRequestSource` role `stimulus` boundary `virtual_ic` trace `DSC-002, DSC-004, DSC-PRE-001`
- `ToyMainWarningTimer` role `timer` boundary `virtual_ic` trace `DSC-002, DSC-003, DSC-PRE-001`
- `ToyClearanceTimer` role `timer` boundary `virtual_ic` trace `DSC-003, DSC-004, DSC-005, DSC-PRE-001`
- `ToySideServiceSource` role `stimulus` boundary `virtual_ic` trace `DSC-005, DSC-PRE-001`
- `ToySideWarningTimer` role `timer` boundary `virtual_ic` trace `DSC-005, DSC-PRE-001`
- `ToyDualSignalCoordinator` role `controller` boundary `hal` trace `DSC-001, DSC-002, DSC-003, DSC-004, DSC-005, DSC-006, DSC-007`

## Verification Direction

- Simulink `.m`, Modelica `.mo`, SCXML, Mermaid, PlantUML, and FMI metadata are generated handoff artifacts.
- Existing MBD tools are the intended verification backends.
- This repository does not claim certification.
