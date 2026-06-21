# Simple Relay Hysteresis Specification

Generated from Spec Mermaid Design Overview and stateDiagram-v2 in `samples/simple_relay_hysteresis/spec.md`.
This file is deterministic authoring source for generated MBD review artifacts.

```mbd-spec-review
source samples/simple_relay_hysteresis/spec.md
question Does the generated state-machine MBD implement Spec.md?
intent RLY-001 | When `level` is greater than or equal to `onThreshold` while the controller is `OFF`, the controller shall enter `ON` and set `active` true.
intent RLY-002 | When `level` is less than or equal to `offThreshold` while the controller is `ON`, the controller shall enter `OFF` and set `active` false.
intent RLY-003 | When `level` is between the two thresholds, the controller shall keep its current state and output.
intent RLY-004 | The model shall expose `level`, `onThreshold`, `offThreshold`, and `active` as separate reviewable MBD elements.
intent RLY-005 | The preview report shall show model inputs, scenario steps, observed behavior, expected behavior, and pass/fail result.
spec-initial OFF
spec-transition [*] --> OFF: initial
spec-transition OFF --> ON: level >= onThreshold
spec-transition ON --> OFF: level <= offThreshold
trace-intent RLY-001 | OFF --> ON | active=true
trace-intent RLY-002 | ON --> OFF | active=false
scenario hysteresis_cycle | reports/hysteresis_cycle.md
open-question SMQ-001 | Guard false behavior is treated as implicit self-hold in the preview subset; confirm this is intended.
advanced-state-semantics are MVP handoff notes; full Stateflow semantics require external MBD verification.
```

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
function ToyRelayController: responsibility=Own the OFF/ON lifecycle and map state transitions to active outputs; owns=OFF,ON,active; inputs=level,onThreshold,offThreshold; outputs=state,active; trace=RLY-001,RLY-002,RLY-003,RLY-004,RLY-005; scenarios=hysteresis_cycle
```

```mbd-flow
ToyLevelSource.level -> ToyRelayController.level: level trace RLY-001 RLY-002
ToyRelayHysteresis.onThreshold -> ToyRelayController.onThreshold: onThreshold trace RLY-001
ToyRelayHysteresis.offThreshold -> ToyRelayController.offThreshold: offThreshold trace RLY-002
ToyRelayController.active -> ToyRelayHysteresis.active: active output trace RLY-001 RLY-002
ToyRelayHysteresis.active -> ScenarioReport.observedBehavior: reported active trace RLY-003
```

```mbd-control
priority 10 rule off_to_on: owner ToyRelayController from OFF when level >= onThreshold then state=ON, active=true trace RLY-001 RLY-003 scenarios hysteresis_cycle
priority 20 rule on_to_off: owner ToyRelayController from ON when level <= offThreshold then state=OFF, active=false trace RLY-002 RLY-003 scenarios hysteresis_cycle
```

```mbd-harness
device ToyLevelSource role=source boundary=virtual_ic trace RLY-001 RLY-002 RLY-003
ecu ToyRelayHysteresis role=controller boundary=hal trace RLY-001 RLY-002 RLY-003 RLY-004 RLY-005
```
