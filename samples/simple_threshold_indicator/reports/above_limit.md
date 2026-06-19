# Scenario Report

- Scenario: `simple_threshold_above_limit`
- Result: **PASS**
- Final state: `ACTIVE`
- Boundary: preview-only; not a certified code generation or verification backend.

## Model Inputs

```yaml
source: samples/simple_threshold_indicator/model.mbd.md
sourceFormat: mbd-markdown
component: ToyThresholdIndicator
parameters:
  limit: '10'
ports:
  sampleValue:
    direction: in
    type: count
    default: '0'
  active:
    direction: out
    type: bool
    default: 'false'
controlRules:
- name: activate
  owner: ThresholdCompare
  priority: 10
  stateScope: '*'
  condition: sampleValue >= limit
  actions:
    state: ACTIVE
    active: 'true'
  trace:
  - SIMPLE-001
  - SIMPLE-003
  scenarios:
  - above_limit
- name: clear
  owner: ThresholdCompare
  priority: 20
  stateScope: '*'
  condition: sampleValue < limit
  actions:
    state: IDLE
    active: 'false'
  trace:
  - SIMPLE-002
  - SIMPLE-003
  scenarios: []
controlSelectionPolicy: lowest numeric priority wins after state scope and guard match
requirementRefs:
- SIMPLE-001
- SIMPLE-002
- SIMPLE-003
previewSubsetAssumption: 'Preview subset assumption: discrete scenario steps represent
  the Simulink-compatible subset. Timing behavior such as sensor invalid debounce
  is represented by explicit scenario inputs and must be verified by external MBD/product-test
  infrastructure.'
```

## Functional Decomposition Evidence

```yaml
- name: ThresholdCompare
  responsibility: Compare sampleValue against limit and own the active decision
  owns:
  - active
  - ACTIVE
  - IDLE
  inputs:
  - sampleValue
  - limit
  outputs:
  - active
  - state
  trace:
  - SIMPLE-001
  - SIMPLE-002
  - SIMPLE-003
  scenarios:
  - above_limit
```

## Traceability Matrix

```yaml
- requirement: SIMPLE-001
  modelElements:
  - component:ToyThresholdIndicator
  - function:ThresholdCompare
  - flow:ToyInputSource.sampleValue->ThresholdCompare.sampleValue
  - flow:ToyThresholdIndicator.limit->ThresholdCompare.limit
  - flow:ThresholdCompare.active->ToyThresholdIndicator.active
  - control:activate
  - harness:ToyInputSource
  - harness:ToyThresholdIndicator
  evidence:
  - samples/simple_threshold_indicator/model.mbd.md
  - samples/simple_threshold_indicator/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: SIMPLE-002
  modelElements:
  - component:ToyThresholdIndicator
  - function:ThresholdCompare
  - flow:ToyThresholdIndicator.limit->ThresholdCompare.limit
  - flow:ThresholdCompare.active->ToyThresholdIndicator.active
  - control:clear
  - harness:ToyThresholdIndicator
  evidence:
  - samples/simple_threshold_indicator/model.mbd.md
  - samples/simple_threshold_indicator/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: SIMPLE-003
  modelElements:
  - component:ToyThresholdIndicator
  - function:ThresholdCompare
  - flow:ToyThresholdIndicator.active->ScenarioReport.observedBehavior
  - control:activate
  - control:clear
  - harness:ToyThresholdIndicator
  evidence:
  - samples/simple_threshold_indicator/model.mbd.md
  - samples/simple_threshold_indicator/generated/diagram.mmd
  - preview report path supplied by run-preview
```

## Scenario Steps

```yaml
- atMs: 0
  setInput:
    name: sampleValue
    value: 12
```

## Harness Boundary Evidence

```yaml
- name: ToyInputSource
  role: source
  boundary: virtual_ic
  trace:
  - SIMPLE-001
- name: ToyThresholdIndicator
  role: controller
  boundary: hal
  trace:
  - SIMPLE-001
  - SIMPLE-002
  - SIMPLE-003
```

## Per-Step Preview Execution

```yaml
- stepIndex: 0
  atMs: 0
  scenarioInput:
    name: sampleValue
    value: 12
  before:
    state: IDLE
    inputs:
      sampleValue: 0
    outputs:
      active: false
  virtualIcObservation:
    ToyThresholdIndicator.sampleValue: 12
  controlRuleEvaluations:
  - rule: activate
    owner: ThresholdCompare
    priority: 10
    stateScope: '*'
    stateScopeMatched: true
    condition: sampleValue >= limit
    matched: true
    selectable: true
    actionsIfMatched:
      state: ACTIVE
      active: 'true'
    trace:
    - SIMPLE-001
    - SIMPLE-003
    scenarios:
    - above_limit
  - rule: clear
    owner: ThresholdCompare
    priority: 20
    stateScope: '*'
    stateScopeMatched: true
    condition: sampleValue < limit
    matched: false
    selectable: false
    actionsIfMatched:
      state: IDLE
      active: 'false'
    trace:
    - SIMPLE-002
    - SIMPLE-003
    scenarios: []
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: activate
  appliedOwner: ThresholdCompare
  generatedEcuCommandOutputs:
    active: true
    commandFlows:
    - source: ToyThresholdIndicator.active
      target: ScenarioReport.observedBehavior
      label: reported output
      value: true
      trace:
      - SIMPLE-003
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: ACTIVE
    inputs:
      sampleValue: 12
    outputs:
      active: true
  requirementRefs:
  - SIMPLE-001
  - SIMPLE-003
```

## Observed Behavior

```yaml
finalState: ACTIVE
inputs:
  sampleValue: 12
outputs:
  active: true
appliedRules:
- activate
harnessDevices:
- name: ToyInputSource
  role: source
  boundary: virtual_ic
- name: ToyThresholdIndicator
  role: controller
  boundary: hal
```

## Generated ECU Command Outputs

```yaml
active: true
commandFlows:
- source: ToyThresholdIndicator.active
  target: ScenarioReport.observedBehavior
  label: reported output
  value: true
  trace:
  - SIMPLE-003
previewCodeSource: sample-specific preview C export, if available
```

## Expected Behavior

```yaml
finalState: ACTIVE
outputs:
  active: true
```

## Pass/Fail Result

- PASS finalState: actual ACTIVE, expected ACTIVE
- PASS outputs.active: actual True, expected True

## Runtime Trace

- preview-only runtime started
- input sampleValue=12
- rule activate applied

## Register Reads

- No register reads recorded.
