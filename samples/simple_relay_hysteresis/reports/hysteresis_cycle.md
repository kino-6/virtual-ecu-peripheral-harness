# Scenario Report

- Scenario: `simple_relay_hysteresis_cycle`
- Result: **PASS**
- Final state: `OFF`
- Boundary: preview-only; not a certified code generation or verification backend.

## Model Inputs

```yaml
source: samples/simple_relay_hysteresis/model.mbd.md
sourceFormat: mbd-markdown
component: ToyRelayHysteresis
parameters:
  onThreshold: '70'
  offThreshold: '30'
ports:
  level:
    direction: in
    type: count
    default: '0'
  active:
    direction: out
    type: bool
    default: 'false'
controlRules:
- name: off_to_on
  owner: ToyRelayController
  priority: 10
  stateScope: 'OFF'
  condition: level >= onThreshold
  actions:
    state: 'ON'
    active: 'true'
  trace:
  - RLY-001
  - RLY-003
  - RLY-005
  scenarios:
  - hysteresis_cycle
- name: on_to_off
  owner: ToyRelayController
  priority: 20
  stateScope: 'ON'
  condition: level <= offThreshold
  actions:
    state: 'OFF'
    active: 'false'
  trace:
  - RLY-002
  - RLY-003
  - RLY-005
  scenarios:
  - hysteresis_cycle
controlSelectionPolicy: lowest numeric priority wins after state scope and guard match
requirementRefs:
- RLY-001
- RLY-002
- RLY-003
- RLY-004
- RLY-005
previewSubsetAssumption: 'Preview subset assumption: discrete scenario steps represent
  the Simulink-compatible subset. Timing behavior such as sensor invalid debounce
  is represented by explicit scenario inputs and must be verified by external MBD/product-test
  infrastructure.'
```

## Functional Decomposition Evidence

```yaml
- name: ToyRelayController
  responsibility: Own OFF/ON relay hysteresis and map threshold-crossing transitions
    to active output
  owns:
  - 'OFF'
  - 'ON'
  - active
  inputs:
  - level
  - onThreshold
  - offThreshold
  outputs:
  - state
  - active
  trace:
  - RLY-001
  - RLY-002
  - RLY-003
  - RLY-004
  - RLY-005
  scenarios:
  - hysteresis_cycle
```

## Traceability Matrix

```yaml
- requirement: RLY-001
  modelElements:
  - component:ToyRelayHysteresis
  - function:ToyRelayController
  - flow:ToyLevelSource.level->ToyRelayController.level
  - flow:ToyRelayHysteresis.onThreshold->ToyRelayController.onThreshold
  - flow:ToyRelayController.active->ToyRelayHysteresis.active
  - control:off_to_on
  - harness:ToyLevelSource
  - harness:ToyRelayHysteresis
  evidence:
  - samples/simple_relay_hysteresis/model.mbd.md
  - samples/simple_relay_hysteresis/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: RLY-002
  modelElements:
  - component:ToyRelayHysteresis
  - function:ToyRelayController
  - flow:ToyLevelSource.level->ToyRelayController.level
  - flow:ToyRelayHysteresis.offThreshold->ToyRelayController.offThreshold
  - flow:ToyRelayController.active->ToyRelayHysteresis.active
  - control:on_to_off
  - harness:ToyLevelSource
  - harness:ToyRelayHysteresis
  evidence:
  - samples/simple_relay_hysteresis/model.mbd.md
  - samples/simple_relay_hysteresis/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: RLY-003
  modelElements:
  - component:ToyRelayHysteresis
  - function:ToyRelayController
  - flow:ToyLevelSource.level->ToyRelayController.level
  - flow:ToyRelayController.active->ToyRelayHysteresis.active
  - control:off_to_on
  - control:on_to_off
  - harness:ToyLevelSource
  - harness:ToyRelayHysteresis
  evidence:
  - samples/simple_relay_hysteresis/model.mbd.md
  - samples/simple_relay_hysteresis/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: RLY-004
  modelElements:
  - component:ToyRelayHysteresis
  - function:ToyRelayController
  - flow:ToyLevelSource.level->ToyRelayController.level
  - flow:ToyRelayHysteresis.onThreshold->ToyRelayController.onThreshold
  - flow:ToyRelayHysteresis.offThreshold->ToyRelayController.offThreshold
  - harness:ToyLevelSource
  - harness:ToyRelayHysteresis
  evidence:
  - samples/simple_relay_hysteresis/model.mbd.md
  - samples/simple_relay_hysteresis/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: RLY-005
  modelElements:
  - component:ToyRelayHysteresis
  - function:ToyRelayController
  - flow:ToyRelayHysteresis.active->ScenarioReport.observedBehavior
  - control:off_to_on
  - control:on_to_off
  - harness:ToyRelayHysteresis
  evidence:
  - samples/simple_relay_hysteresis/model.mbd.md
  - samples/simple_relay_hysteresis/generated/diagram.mmd
  - preview report path supplied by run-preview
```

## Scenario Steps

```yaml
- atMs: 0
  setInput:
    name: level
    value: 75
- atMs: 10
  setInput:
    name: level
    value: 50
- atMs: 20
  setInput:
    name: level
    value: 25
```

## Harness Boundary Evidence

```yaml
- name: ToyLevelSource
  role: source
  boundary: virtual_ic
  trace:
  - RLY-001
  - RLY-002
  - RLY-003
  - RLY-004
- name: ToyRelayHysteresis
  role: controller
  boundary: hal
  trace:
  - RLY-001
  - RLY-002
  - RLY-003
  - RLY-004
  - RLY-005
```

## Per-Step Preview Execution

```yaml
- stepIndex: 0
  atMs: 0
  scenarioInput:
    name: level
    value: 75
  before:
    state: 'OFF'
    inputs:
      level: 0
    outputs:
      active: false
  virtualIcObservation:
    ToyRelayHysteresis.level: 75
  controlRuleEvaluations:
  - rule: off_to_on
    owner: ToyRelayController
    priority: 10
    stateScope: 'OFF'
    stateScopeMatched: true
    condition: level >= onThreshold
    matched: true
    selectable: true
    actionsIfMatched:
      state: 'ON'
      active: 'true'
    trace:
    - RLY-001
    - RLY-003
    - RLY-005
    scenarios:
    - hysteresis_cycle
  - rule: on_to_off
    owner: ToyRelayController
    priority: 20
    stateScope: 'ON'
    stateScopeMatched: false
    condition: level <= offThreshold
    matched: false
    selectable: false
    actionsIfMatched:
      state: 'OFF'
      active: 'false'
    trace:
    - RLY-002
    - RLY-003
    - RLY-005
    scenarios:
    - hysteresis_cycle
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: off_to_on
  appliedOwner: ToyRelayController
  generatedEcuCommandOutputs:
    active: true
    commandFlows:
    - source: ToyRelayHysteresis.active
      target: ScenarioReport.observedBehavior
      label: reported active output
      value: true
      trace:
      - RLY-005
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: 'ON'
    inputs:
      level: 75
    outputs:
      active: true
  requirementRefs:
  - RLY-001
  - RLY-003
  - RLY-005
- stepIndex: 1
  atMs: 10
  scenarioInput:
    name: level
    value: 50
  before:
    state: 'ON'
    inputs:
      level: 75
    outputs:
      active: true
  virtualIcObservation:
    ToyRelayHysteresis.level: 50
  controlRuleEvaluations:
  - rule: off_to_on
    owner: ToyRelayController
    priority: 10
    stateScope: 'OFF'
    stateScopeMatched: false
    condition: level >= onThreshold
    matched: false
    selectable: false
    actionsIfMatched:
      state: 'ON'
      active: 'true'
    trace:
    - RLY-001
    - RLY-003
    - RLY-005
    scenarios:
    - hysteresis_cycle
  - rule: on_to_off
    owner: ToyRelayController
    priority: 20
    stateScope: 'ON'
    stateScopeMatched: true
    condition: level <= offThreshold
    matched: false
    selectable: false
    actionsIfMatched:
      state: 'OFF'
      active: 'false'
    trace:
    - RLY-002
    - RLY-003
    - RLY-005
    scenarios:
    - hysteresis_cycle
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: null
  appliedOwner: null
  generatedEcuCommandOutputs:
    active: true
    commandFlows:
    - source: ToyRelayHysteresis.active
      target: ScenarioReport.observedBehavior
      label: reported active output
      value: true
      trace:
      - RLY-005
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: 'ON'
    inputs:
      level: 50
    outputs:
      active: true
  requirementRefs: []
- stepIndex: 2
  atMs: 20
  scenarioInput:
    name: level
    value: 25
  before:
    state: 'ON'
    inputs:
      level: 50
    outputs:
      active: true
  virtualIcObservation:
    ToyRelayHysteresis.level: 25
  controlRuleEvaluations:
  - rule: off_to_on
    owner: ToyRelayController
    priority: 10
    stateScope: 'OFF'
    stateScopeMatched: false
    condition: level >= onThreshold
    matched: false
    selectable: false
    actionsIfMatched:
      state: 'ON'
      active: 'true'
    trace:
    - RLY-001
    - RLY-003
    - RLY-005
    scenarios:
    - hysteresis_cycle
  - rule: on_to_off
    owner: ToyRelayController
    priority: 20
    stateScope: 'ON'
    stateScopeMatched: true
    condition: level <= offThreshold
    matched: true
    selectable: true
    actionsIfMatched:
      state: 'OFF'
      active: 'false'
    trace:
    - RLY-002
    - RLY-003
    - RLY-005
    scenarios:
    - hysteresis_cycle
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: on_to_off
  appliedOwner: ToyRelayController
  generatedEcuCommandOutputs:
    active: false
    commandFlows:
    - source: ToyRelayHysteresis.active
      target: ScenarioReport.observedBehavior
      label: reported active output
      value: false
      trace:
      - RLY-005
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: 'OFF'
    inputs:
      level: 25
    outputs:
      active: false
  requirementRefs:
  - RLY-002
  - RLY-003
  - RLY-005
```

## Observed Behavior

```yaml
finalState: 'OFF'
inputs:
  level: 25
outputs:
  active: false
appliedRules:
- off_to_on
- on_to_off
harnessDevices:
- name: ToyLevelSource
  role: source
  boundary: virtual_ic
- name: ToyRelayHysteresis
  role: controller
  boundary: hal
```

## Generated ECU Command Outputs

```yaml
active: false
commandFlows:
- source: ToyRelayHysteresis.active
  target: ScenarioReport.observedBehavior
  label: reported active output
  value: false
  trace:
  - RLY-005
previewCodeSource: sample-specific preview C export, if available
```

## Expected Behavior

```yaml
finalState: 'OFF'
outputs:
  active: false
```

## Pass/Fail Result

- PASS finalState: actual OFF, expected OFF
- PASS outputs.active: actual False, expected False

## Runtime Trace

- preview-only runtime started
- input level=75
- rule off_to_on applied
- input level=50
- input level=25
- rule on_to_off applied

## Register Reads

- No register reads recorded.
