# Scenario Report

- Scenario: `simple_state_machine_full_cycle`
- Result: **PASS**
- Final state: `IDLE`
- Boundary: preview-only; not a certified code generation or verification backend.

## Model Inputs

```yaml
source: samples/simple_state_machine/model.mbd.md
sourceFormat: mbd-markdown
component: ToyStateMachine
parameters: {}
ports:
  startCommand:
    direction: in
    type: bool
    default: 'false'
  finishCommand:
    direction: in
    type: bool
    default: 'false'
  resetCommand:
    direction: in
    type: bool
    default: 'false'
  busy:
    direction: out
    type: bool
    default: 'false'
  complete:
    direction: out
    type: bool
    default: 'false'
controlRules:
- name: start_running
  owner: ToyStateController
  priority: 10
  stateScope: IDLE
  condition: startCommand == true
  actions:
    state: RUNNING
    busy: 'true'
    complete: 'false'
  trace:
  - SM-001
  - SM-004
  scenarios:
  - full_cycle
- name: finish_done
  owner: ToyStateController
  priority: 20
  stateScope: RUNNING
  condition: finishCommand == true
  actions:
    state: DONE
    busy: 'false'
    complete: 'true'
  trace:
  - SM-002
  - SM-004
  scenarios:
  - full_cycle
- name: reset_idle
  owner: ToyStateController
  priority: 30
  stateScope: DONE
  condition: resetCommand == true
  actions:
    state: IDLE
    busy: 'false'
    complete: 'false'
  trace:
  - SM-003
  - SM-004
  scenarios:
  - full_cycle
controlSelectionPolicy: lowest numeric priority wins after state scope and guard match
requirementRefs:
- SM-001
- SM-002
- SM-003
- SM-004
previewSubsetAssumption: 'Preview subset assumption: discrete scenario steps represent
  the Simulink-compatible subset. Timing behavior such as sensor invalid debounce
  is represented by explicit scenario inputs and must be verified by external MBD/product-test
  infrastructure.'
```

## Functional Decomposition Evidence

```yaml
- name: ToyStateController
  responsibility: Own the IDLE/RUNNING/DONE lifecycle and map state transitions to
    busy and complete outputs
  owns:
  - IDLE
  - RUNNING
  - DONE
  - busy
  - complete
  inputs:
  - startCommand
  - finishCommand
  - resetCommand
  outputs:
  - state
  - busy
  - complete
  trace:
  - SM-001
  - SM-002
  - SM-003
  - SM-004
  scenarios:
  - full_cycle
```

## Traceability Matrix

```yaml
- requirement: SM-001
  modelElements:
  - component:ToyStateMachine
  - function:ToyStateController
  - flow:ToyCommandSource.startCommand->ToyStateController.startCommand
  - flow:ToyStateController.busy->ToyStateMachine.busy
  - control:start_running
  - harness:ToyCommandSource
  - harness:ToyStateMachine
  evidence:
  - samples/simple_state_machine/model.mbd.md
  - samples/simple_state_machine/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: SM-002
  modelElements:
  - component:ToyStateMachine
  - function:ToyStateController
  - flow:ToyCommandSource.finishCommand->ToyStateController.finishCommand
  - flow:ToyStateController.busy->ToyStateMachine.busy
  - flow:ToyStateController.complete->ToyStateMachine.complete
  - control:finish_done
  - harness:ToyCommandSource
  - harness:ToyStateMachine
  evidence:
  - samples/simple_state_machine/model.mbd.md
  - samples/simple_state_machine/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: SM-003
  modelElements:
  - component:ToyStateMachine
  - function:ToyStateController
  - flow:ToyCommandSource.resetCommand->ToyStateController.resetCommand
  - flow:ToyStateController.busy->ToyStateMachine.busy
  - flow:ToyStateController.complete->ToyStateMachine.complete
  - control:reset_idle
  - harness:ToyCommandSource
  - harness:ToyStateMachine
  evidence:
  - samples/simple_state_machine/model.mbd.md
  - samples/simple_state_machine/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: SM-004
  modelElements:
  - component:ToyStateMachine
  - function:ToyStateController
  - flow:ToyStateMachine.busy->ScenarioReport.observedBehavior
  - flow:ToyStateMachine.complete->ScenarioReport.observedBehavior
  - control:start_running
  - control:finish_done
  - control:reset_idle
  - harness:ToyStateMachine
  evidence:
  - samples/simple_state_machine/model.mbd.md
  - samples/simple_state_machine/generated/diagram.mmd
  - preview report path supplied by run-preview
```

## Scenario Steps

```yaml
- atMs: 0
  setInput:
    name: startCommand
    value: true
- atMs: 10
  setInput:
    name: finishCommand
    value: true
- atMs: 20
  setInput:
    name: resetCommand
    value: true
```

## Harness Boundary Evidence

```yaml
- name: ToyCommandSource
  role: source
  boundary: virtual_ic
  trace:
  - SM-001
  - SM-002
  - SM-003
- name: ToyStateMachine
  role: controller
  boundary: hal
  trace:
  - SM-001
  - SM-002
  - SM-003
  - SM-004
```

## Per-Step Preview Execution

```yaml
- stepIndex: 0
  atMs: 0
  scenarioInput:
    name: startCommand
    value: true
  before:
    state: IDLE
    inputs:
      startCommand: false
      finishCommand: false
      resetCommand: false
    outputs:
      busy: false
      complete: false
  virtualIcObservation:
    ToyStateMachine.startCommand: true
    ToyStateMachine.finishCommand: false
    ToyStateMachine.resetCommand: false
  controlRuleEvaluations:
  - rule: start_running
    owner: ToyStateController
    priority: 10
    stateScope: IDLE
    stateScopeMatched: true
    condition: startCommand == true
    matched: true
    selectable: true
    actionsIfMatched:
      state: RUNNING
      busy: 'true'
      complete: 'false'
    trace:
    - SM-001
    - SM-004
    scenarios:
    - full_cycle
  - rule: finish_done
    owner: ToyStateController
    priority: 20
    stateScope: RUNNING
    stateScopeMatched: false
    condition: finishCommand == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: DONE
      busy: 'false'
      complete: 'true'
    trace:
    - SM-002
    - SM-004
    scenarios:
    - full_cycle
  - rule: reset_idle
    owner: ToyStateController
    priority: 30
    stateScope: DONE
    stateScopeMatched: false
    condition: resetCommand == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: IDLE
      busy: 'false'
      complete: 'false'
    trace:
    - SM-003
    - SM-004
    scenarios:
    - full_cycle
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: start_running
  appliedOwner: ToyStateController
  generatedEcuCommandOutputs:
    busy: true
    complete: false
    commandFlows:
    - source: ToyStateMachine.busy
      target: ScenarioReport.observedBehavior
      label: reported busy output
      value: true
      trace:
      - SM-004
    - source: ToyStateMachine.complete
      target: ScenarioReport.observedBehavior
      label: reported complete output
      value: false
      trace:
      - SM-004
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: RUNNING
    inputs:
      startCommand: true
      finishCommand: false
      resetCommand: false
    outputs:
      busy: true
      complete: false
  requirementRefs:
  - SM-001
  - SM-004
- stepIndex: 1
  atMs: 10
  scenarioInput:
    name: finishCommand
    value: true
  before:
    state: RUNNING
    inputs:
      startCommand: true
      finishCommand: false
      resetCommand: false
    outputs:
      busy: true
      complete: false
  virtualIcObservation:
    ToyStateMachine.startCommand: true
    ToyStateMachine.finishCommand: true
    ToyStateMachine.resetCommand: false
  controlRuleEvaluations:
  - rule: start_running
    owner: ToyStateController
    priority: 10
    stateScope: IDLE
    stateScopeMatched: false
    condition: startCommand == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: RUNNING
      busy: 'true'
      complete: 'false'
    trace:
    - SM-001
    - SM-004
    scenarios:
    - full_cycle
  - rule: finish_done
    owner: ToyStateController
    priority: 20
    stateScope: RUNNING
    stateScopeMatched: true
    condition: finishCommand == true
    matched: true
    selectable: true
    actionsIfMatched:
      state: DONE
      busy: 'false'
      complete: 'true'
    trace:
    - SM-002
    - SM-004
    scenarios:
    - full_cycle
  - rule: reset_idle
    owner: ToyStateController
    priority: 30
    stateScope: DONE
    stateScopeMatched: false
    condition: resetCommand == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: IDLE
      busy: 'false'
      complete: 'false'
    trace:
    - SM-003
    - SM-004
    scenarios:
    - full_cycle
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: finish_done
  appliedOwner: ToyStateController
  generatedEcuCommandOutputs:
    busy: false
    complete: true
    commandFlows:
    - source: ToyStateMachine.busy
      target: ScenarioReport.observedBehavior
      label: reported busy output
      value: false
      trace:
      - SM-004
    - source: ToyStateMachine.complete
      target: ScenarioReport.observedBehavior
      label: reported complete output
      value: true
      trace:
      - SM-004
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: DONE
    inputs:
      startCommand: true
      finishCommand: true
      resetCommand: false
    outputs:
      busy: false
      complete: true
  requirementRefs:
  - SM-002
  - SM-004
- stepIndex: 2
  atMs: 20
  scenarioInput:
    name: resetCommand
    value: true
  before:
    state: DONE
    inputs:
      startCommand: true
      finishCommand: true
      resetCommand: false
    outputs:
      busy: false
      complete: true
  virtualIcObservation:
    ToyStateMachine.startCommand: true
    ToyStateMachine.finishCommand: true
    ToyStateMachine.resetCommand: true
  controlRuleEvaluations:
  - rule: start_running
    owner: ToyStateController
    priority: 10
    stateScope: IDLE
    stateScopeMatched: false
    condition: startCommand == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: RUNNING
      busy: 'true'
      complete: 'false'
    trace:
    - SM-001
    - SM-004
    scenarios:
    - full_cycle
  - rule: finish_done
    owner: ToyStateController
    priority: 20
    stateScope: RUNNING
    stateScopeMatched: false
    condition: finishCommand == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: DONE
      busy: 'false'
      complete: 'true'
    trace:
    - SM-002
    - SM-004
    scenarios:
    - full_cycle
  - rule: reset_idle
    owner: ToyStateController
    priority: 30
    stateScope: DONE
    stateScopeMatched: true
    condition: resetCommand == true
    matched: true
    selectable: true
    actionsIfMatched:
      state: IDLE
      busy: 'false'
      complete: 'false'
    trace:
    - SM-003
    - SM-004
    scenarios:
    - full_cycle
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: reset_idle
  appliedOwner: ToyStateController
  generatedEcuCommandOutputs:
    busy: false
    complete: false
    commandFlows:
    - source: ToyStateMachine.busy
      target: ScenarioReport.observedBehavior
      label: reported busy output
      value: false
      trace:
      - SM-004
    - source: ToyStateMachine.complete
      target: ScenarioReport.observedBehavior
      label: reported complete output
      value: false
      trace:
      - SM-004
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: IDLE
    inputs:
      startCommand: true
      finishCommand: true
      resetCommand: true
    outputs:
      busy: false
      complete: false
  requirementRefs:
  - SM-003
  - SM-004
```

## Observed Behavior

```yaml
finalState: IDLE
inputs:
  startCommand: true
  finishCommand: true
  resetCommand: true
outputs:
  busy: false
  complete: false
appliedRules:
- start_running
- finish_done
- reset_idle
harnessDevices:
- name: ToyCommandSource
  role: source
  boundary: virtual_ic
- name: ToyStateMachine
  role: controller
  boundary: hal
```

## Generated ECU Command Outputs

```yaml
busy: false
complete: false
commandFlows:
- source: ToyStateMachine.busy
  target: ScenarioReport.observedBehavior
  label: reported busy output
  value: false
  trace:
  - SM-004
- source: ToyStateMachine.complete
  target: ScenarioReport.observedBehavior
  label: reported complete output
  value: false
  trace:
  - SM-004
previewCodeSource: sample-specific preview C export, if available
```

## Expected Behavior

```yaml
finalState: IDLE
outputs:
  busy: false
  complete: false
```

## Pass/Fail Result

- PASS finalState: actual IDLE, expected IDLE
- PASS outputs.busy: actual False, expected False
- PASS outputs.complete: actual False, expected False

## Runtime Trace

- preview-only runtime started
- input startCommand=True
- rule start_running applied
- input finishCommand=True
- rule finish_done applied
- input resetCommand=True
- rule reset_idle applied

## Register Reads

- No register reads recorded.
