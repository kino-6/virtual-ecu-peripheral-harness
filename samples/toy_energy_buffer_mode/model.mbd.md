# Toy Energy Buffer Mode

Fictional source-informed MBD authoring source for a Stateflow-style mode
management sample. This file is not a rendered MBD model deliverable; it is the
structured text input parsed into an internal IR and then exported to generated
review and handoff artifacts.

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
function ToyEnergyBufferModeController: responsibility=Own the CHARGE/DISCHARGE/EMPTY lifecycle and map source availability plus empty detection to supply and charge indication outputs; owns=CHARGE,DISCHARGE,EMPTY,supplyEnabled,chargeIndicator; inputs=externalPowerAvailable,emptyDetected; outputs=state,supplyEnabled,chargeIndicator; trace=EBUF-001,EBUF-002,EBUF-003,EBUF-004,EBUF-005,EBUF-006; scenarios=source_loss_recovery
```

```mbd-flow
ToyPowerSource.externalPowerAvailable -> ToyEnergyBufferModeController.externalPowerAvailable: source availability trace EBUF-001 EBUF-003 EBUF-004 EBUF-005
ToyEmptyMonitor.emptyDetected -> ToyEnergyBufferModeController.emptyDetected: empty indication trace EBUF-001 EBUF-002 EBUF-005
ToyEnergyBufferModeController.supplyEnabled -> ToyEnergyBufferMode.supplyEnabled: supply command trace EBUF-001 EBUF-002 EBUF-003 EBUF-004 EBUF-005
ToyEnergyBufferModeController.chargeIndicator -> ToyEnergyBufferMode.chargeIndicator: charge indication trace EBUF-001 EBUF-002 EBUF-003 EBUF-004 EBUF-005
ToyEnergyBufferMode.supplyEnabled -> ScenarioReport.observedBehavior: reported supply command trace EBUF-006
ToyEnergyBufferMode.chargeIndicator -> ScenarioReport.observedBehavior: reported charge indication trace EBUF-006
```

```mbd-control
priority 10 rule power_removed_discharge: owner ToyEnergyBufferModeController from CHARGE when externalPowerAvailable == false and emptyDetected == false then state=DISCHARGE, supplyEnabled=true, chargeIndicator=false trace EBUF-001 EBUF-006 scenarios source_loss_recovery
priority 20 rule discharge_empty: owner ToyEnergyBufferModeController from DISCHARGE when emptyDetected == true then state=EMPTY, supplyEnabled=false, chargeIndicator=false trace EBUF-002 EBUF-006 scenarios source_loss_recovery
priority 30 rule empty_reconnect_charge: owner ToyEnergyBufferModeController from EMPTY when externalPowerAvailable == true then state=CHARGE, supplyEnabled=false, chargeIndicator=true trace EBUF-003 EBUF-006 scenarios source_loss_recovery
priority 40 rule discharge_reconnect_charge: owner ToyEnergyBufferModeController from DISCHARGE when externalPowerAvailable == true then state=CHARGE, supplyEnabled=false, chargeIndicator=true trace EBUF-004 EBUF-006 scenarios source_loss_recovery
```

```mbd-harness
device ToyPowerSource role=source boundary=virtual_ic trace EBUF-001 EBUF-003 EBUF-004 EBUF-005
device ToyEmptyMonitor role=source boundary=virtual_ic trace EBUF-001 EBUF-002 EBUF-005
ecu ToyEnergyBufferMode role=controller boundary=hal trace EBUF-001 EBUF-002 EBUF-003 EBUF-004 EBUF-005 EBUF-006
```
