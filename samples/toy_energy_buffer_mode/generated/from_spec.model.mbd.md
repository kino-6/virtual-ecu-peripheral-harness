# Toy Energy Buffer Mode Specification

Generated from Spec Data Flow View and Control Semantics View in `samples/toy_energy_buffer_mode/spec.md`.
This file is deterministic authoring source for generated MBD review artifacts.

```mbd-spec-review
source samples/toy_energy_buffer_mode/spec.md
question Does the generated state-machine MBD implement Spec.md?
intent EBUF-001 | When `externalPowerAvailable` is false and `emptyDetected` is false while the controller is `CHARGE`, the controller shall enter `DISCHARGE`, set `supplyEnabled=true`, and set `chargeIndicator=false`.
intent EBUF-002 | When `emptyDetected` is true while the controller is `DISCHARGE`, the controller shall enter `EMPTY`, set `supplyEnabled=false`, and set `chargeIndicator=false`.
intent EBUF-003 | When `externalPowerAvailable` is true while the controller is `EMPTY`, the controller shall enter `CHARGE`, set `supplyEnabled=false`, and set `chargeIndicator=true`.
intent EBUF-004 | When `externalPowerAvailable` is true while the controller is `DISCHARGE`, the controller shall enter `CHARGE`, set `supplyEnabled=false`, and set `chargeIndicator=true`.
intent EBUF-005 | The model shall expose power availability, empty detection, supply command, charge indication, and mode state as separate reviewable MBD elements.
intent EBUF-006 | The preview report shall show scenario stimulus, observed behavior, expected behavior, Harness boundary evidence, and pass/fail result.
spec-initial CHARGE
spec-transition [*] --> CHARGE: initial
spec-transition CHARGE --> DISCHARGE: externalPowerAvailable == false and emptyDetected == false
spec-transition DISCHARGE --> EMPTY: emptyDetected == true
spec-transition EMPTY --> CHARGE: externalPowerAvailable == true
spec-transition DISCHARGE --> CHARGE: externalPowerAvailable == true
trace-intent EBUF-001 | CHARGE --> DISCHARGE | supplyEnabled=true, chargeIndicator=false
trace-intent EBUF-002 | DISCHARGE --> EMPTY | supplyEnabled=false, chargeIndicator=false
trace-intent EBUF-003 | EMPTY --> CHARGE | supplyEnabled=false, chargeIndicator=true
trace-intent EBUF-004 | DISCHARGE --> CHARGE | supplyEnabled=false, chargeIndicator=true
scenario source_loss_recovery | reports/source_loss_recovery.md
open-question SMQ-001 | Guard false behavior is treated as implicit self-hold in the preview subset; confirm this is intended.
advanced-state-semantics are MVP handoff notes; full Stateflow semantics require external MBD verification.
```

```mbd-component
component ToyEnergyBufferMode
trace EBUF-001 EBUF-002 EBUF-003 EBUF-004 EBUF-005 EBUF-006
bus virtual mode=preview wordBits=8

port in externalPowerAvailable: bool = true
port in emptyDetected: bool = false
port out supplyEnabled: bool = false
port out chargeIndicator: bool = true
```

```mbd-registers
STATUS 0x01 ro 8
  bit 0 supplyEnabled reset=0
  bit 1 chargeIndicator reset=1
```

```mbd-state
CHARGE --> DISCHARGE: externalPowerAvailable == false and emptyDetected == false
DISCHARGE --> EMPTY: emptyDetected == true
EMPTY --> CHARGE: externalPowerAvailable == true
DISCHARGE --> CHARGE: externalPowerAvailable == true
```

```mbd-decomposition
function ToyEnergyBufferModeController: responsibility=Own the CHARGE/DISCHARGE/EMPTY lifecycle and map state transitions to supplyEnabled and chargeIndicator outputs; owns=CHARGE,DISCHARGE,EMPTY,supplyEnabled,chargeIndicator; inputs=externalPowerAvailable,emptyDetected; outputs=state,supplyEnabled,chargeIndicator; trace=EBUF-001,EBUF-002,EBUF-003,EBUF-004,EBUF-005,EBUF-006; scenarios=source_loss_recovery
```

```mbd-flow
ToyPowerSource.externalPowerAvailable -> ToyEnergyBufferModeController.externalPowerAvailable: externalPowerAvailable trace EBUF-001 EBUF-003 EBUF-004
ToyEmptyMonitor.emptyDetected -> ToyEnergyBufferModeController.emptyDetected: emptyDetected trace EBUF-001 EBUF-002
ToyEnergyBufferModeController.supplyEnabled -> ToyEnergyBufferMode.supplyEnabled: supplyEnabled output trace EBUF-001 EBUF-002 EBUF-003 EBUF-004
ToyEnergyBufferMode.supplyEnabled -> ScenarioReport.observedBehavior: reported supplyEnabled trace EBUF-005
ToyEnergyBufferModeController.chargeIndicator -> ToyEnergyBufferMode.chargeIndicator: chargeIndicator output trace EBUF-001 EBUF-002 EBUF-003 EBUF-004
ToyEnergyBufferMode.chargeIndicator -> ScenarioReport.observedBehavior: reported chargeIndicator trace EBUF-005
```

```mbd-control
priority 10 rule charge_to_discharge: owner ToyEnergyBufferModeController from CHARGE when externalPowerAvailable == false and emptyDetected == false then state=DISCHARGE, supplyEnabled=true, chargeIndicator=false trace EBUF-001 EBUF-005 scenarios source_loss_recovery
priority 20 rule discharge_to_empty: owner ToyEnergyBufferModeController from DISCHARGE when emptyDetected == true then state=EMPTY, supplyEnabled=false, chargeIndicator=false trace EBUF-002 EBUF-005 scenarios source_loss_recovery
priority 30 rule empty_to_charge: owner ToyEnergyBufferModeController from EMPTY when externalPowerAvailable == true then state=CHARGE, supplyEnabled=false, chargeIndicator=true trace EBUF-003 EBUF-005 scenarios source_loss_recovery
priority 40 rule discharge_to_charge: owner ToyEnergyBufferModeController from DISCHARGE when externalPowerAvailable == true then state=CHARGE, supplyEnabled=false, chargeIndicator=true trace EBUF-004 EBUF-005 scenarios source_loss_recovery
```

```mbd-harness
device ToyPowerSource role=source boundary=virtual_ic trace EBUF-001 EBUF-002 EBUF-003
device ToyEmptyMonitor role=source boundary=virtual_ic trace EBUF-001 EBUF-002 EBUF-003
ecu ToyEnergyBufferMode role=controller boundary=hal trace EBUF-001 EBUF-002 EBUF-003 EBUF-004 EBUF-005 EBUF-006
```
