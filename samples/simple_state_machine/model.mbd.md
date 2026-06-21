# Simple State Machine

Fictional minimal MBD authoring source for a state-machine-centered sample.
This file is not the rendered MBD model deliverable; it is the structured text
input parsed into an internal IR and then exported to generated review and
handoff artifacts.

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
ToyCommandSource.startCommand -> ToyStateController.startCommand: start request trace SM-001
ToyCommandSource.finishCommand -> ToyStateController.finishCommand: finish request trace SM-002
ToyCommandSource.resetCommand -> ToyStateController.resetCommand: reset request trace SM-003
ToyStateController.busy -> ToyStateMachine.busy: busy command trace SM-001 SM-002 SM-003
ToyStateController.complete -> ToyStateMachine.complete: completion command trace SM-002 SM-003
ToyStateMachine.busy -> ScenarioReport.observedBehavior: reported busy output trace SM-004
ToyStateMachine.complete -> ScenarioReport.observedBehavior: reported complete output trace SM-004
```

```mbd-control
priority 10 rule start_running: owner ToyStateController from IDLE when startCommand == true then state=RUNNING, busy=true, complete=false trace SM-001 SM-004 scenarios full_cycle
priority 20 rule finish_done: owner ToyStateController from RUNNING when finishCommand == true then state=DONE, busy=false, complete=true trace SM-002 SM-004 scenarios full_cycle
priority 30 rule reset_idle: owner ToyStateController from DONE when resetCommand == true then state=IDLE, busy=false, complete=false trace SM-003 SM-004 scenarios full_cycle
```

```mbd-harness
device ToyCommandSource role=source boundary=virtual_ic trace SM-001 SM-002 SM-003
ecu ToyStateMachine role=controller boundary=hal trace SM-001 SM-002 SM-003 SM-004
```
