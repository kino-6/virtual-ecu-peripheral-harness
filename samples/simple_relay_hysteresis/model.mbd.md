# Simple Relay Hysteresis

Fictional minimal MBD authoring source for a Relay-style hysteresis sample.
This file is not the rendered MBD model deliverable; it is the structured text
input parsed into an internal IR and then exported to generated review and
handoff artifacts.

```mbd-component
component ToyRelayHysteresis
trace RLY-001 RLY-002 RLY-003 RLY-004 RLY-005
bus virtual mode=preview wordBits=8
parameter onThreshold: count = 70
parameter offThreshold: count = 30

port in level: count = 0
port out active: bool = false
```

```mbd-registers
STATUS 0x01 ro 8
  bit 0 active reset=0
```

```mbd-state
OFF --> ON: level >= onThreshold
ON --> OFF: level <= offThreshold
```

```mbd-decomposition
function ToyRelayController: responsibility=Own OFF/ON relay hysteresis and map threshold-crossing transitions to active output; owns=OFF,ON,active; inputs=level,onThreshold,offThreshold; outputs=state,active; trace=RLY-001,RLY-002,RLY-003,RLY-004,RLY-005; scenarios=hysteresis_cycle
```

```mbd-flow
ToyLevelSource.level -> ToyRelayController.level: scenario input trace RLY-001 RLY-002 RLY-003 RLY-004
ToyRelayHysteresis.onThreshold -> ToyRelayController.onThreshold: switch-on threshold trace RLY-001 RLY-004
ToyRelayHysteresis.offThreshold -> ToyRelayController.offThreshold: switch-off threshold trace RLY-002 RLY-004
ToyRelayController.active -> ToyRelayHysteresis.active: relay output trace RLY-001 RLY-002 RLY-003
ToyRelayHysteresis.active -> ScenarioReport.observedBehavior: reported active output trace RLY-005
```

```mbd-control
priority 10 rule off_to_on: owner ToyRelayController from OFF when level >= onThreshold then state=ON, active=true trace RLY-001 RLY-003 RLY-005 scenarios hysteresis_cycle
priority 20 rule on_to_off: owner ToyRelayController from ON when level <= offThreshold then state=OFF, active=false trace RLY-002 RLY-003 RLY-005 scenarios hysteresis_cycle
```

```mbd-harness
device ToyLevelSource role=source boundary=virtual_ic trace RLY-001 RLY-002 RLY-003 RLY-004
ecu ToyRelayHysteresis role=controller boundary=hal trace RLY-001 RLY-002 RLY-003 RLY-004 RLY-005
```
