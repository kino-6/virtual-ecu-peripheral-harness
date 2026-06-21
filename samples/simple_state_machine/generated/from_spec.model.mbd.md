# Simple State Machine Specification

Generated from Spec Mermaid Design Overview and stateDiagram-v2 in `samples/simple_state_machine/spec.md`.
This file is deterministic authoring source for generated MBD review artifacts.

```mbd-spec-review
source samples/simple_state_machine/spec.md
question Does the generated state-machine MBD implement Spec.md?
intent SM-001 | When `startCommand` is true while the controller is `IDLE`, the controller shall enter `RUNNING`, set `busy` to true, and clear `complete`.
intent SM-002 | When `finishCommand` is true while the controller is `RUNNING`, the controller shall enter `DONE`, clear `busy`, and set `complete` to true.
intent SM-003 | When `resetCommand` is true while the controller is `DONE`, the controller shall enter `IDLE`, clear `busy`, and clear `complete`.
intent SM-004 | The preview report shall show model inputs, scenario steps, observed behavior, expected behavior, and pass/fail result.
spec-initial IDLE
spec-transition [*] --> IDLE: initial
spec-transition IDLE --> RUNNING: startCommand == true
spec-transition RUNNING --> DONE: finishCommand == true
spec-transition DONE --> IDLE: resetCommand == true
trace-intent SM-001 | IDLE --> RUNNING | busy=true, complete=false
trace-intent SM-002 | RUNNING --> DONE | busy=false, complete=true
trace-intent SM-003 | DONE --> IDLE | busy=false, complete=false
scenario full_cycle | reports/full_cycle.md
open-question SMQ-001 | Guard false behavior is treated as implicit self-hold in the preview subset; confirm this is intended.
advanced-state-semantics are MVP handoff notes; full Stateflow semantics require external MBD verification.
```

```mbd-component
component ToyStateMachine
trace SM-001 SM-002 SM-003 SM-004
bus virtual mode=preview wordBits=8

port in startCommand: bool = false
port in finishCommand: bool = false
port in resetCommand: bool = false
port out busy: bool = false
port out complete: bool = false
```

```mbd-registers
STATUS 0x01 ro 8
  bit 0 busy reset=0
  bit 1 complete reset=0
```

```mbd-state
IDLE --> RUNNING: startCommand == true
RUNNING --> DONE: finishCommand == true
DONE --> IDLE: resetCommand == true
```

```mbd-decomposition
function ToyStateController: responsibility=Own the IDLE/RUNNING/DONE lifecycle and map state transitions to busy and complete outputs; owns=IDLE,RUNNING,DONE,busy,complete; inputs=startCommand,finishCommand,resetCommand; outputs=state,busy,complete; trace=SM-001,SM-002,SM-003,SM-004; scenarios=full_cycle
```

```mbd-flow
ToyCommandSource.startCommand -> ToyStateController.startCommand: startCommand trace SM-001
ToyCommandSource.finishCommand -> ToyStateController.finishCommand: finishCommand trace SM-002
ToyCommandSource.resetCommand -> ToyStateController.resetCommand: resetCommand trace SM-003
ToyStateController.busy -> ToyStateMachine.busy: busy output trace SM-001 SM-002 SM-003
ToyStateMachine.busy -> ScenarioReport.observedBehavior: reported busy trace SM-004
ToyStateController.complete -> ToyStateMachine.complete: complete output trace SM-001 SM-002 SM-003
ToyStateMachine.complete -> ScenarioReport.observedBehavior: reported complete trace SM-004
```

```mbd-control
priority 10 rule idle_to_running: owner ToyStateController from IDLE when startCommand == true then state=RUNNING, busy=true, complete=false trace SM-001 SM-004 scenarios full_cycle
priority 20 rule running_to_done: owner ToyStateController from RUNNING when finishCommand == true then state=DONE, busy=false, complete=true trace SM-002 SM-004 scenarios full_cycle
priority 30 rule done_to_idle: owner ToyStateController from DONE when resetCommand == true then state=IDLE, busy=false, complete=false trace SM-003 SM-004 scenarios full_cycle
```

```mbd-harness
device ToyCommandSource role=source boundary=virtual_ic trace SM-001 SM-002 SM-003
ecu ToyStateMachine role=controller boundary=hal trace SM-001 SM-002 SM-003 SM-004
```
