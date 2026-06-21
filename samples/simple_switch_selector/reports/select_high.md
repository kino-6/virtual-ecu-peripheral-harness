# Scenario Report

- Scenario: `simple_switch_select_high`
- Result: **PASS**
- Final state: `INITIAL`
- Boundary: preview-only; not a certified code generation or verification backend.

## Model Inputs

```yaml
source: samples/simple_switch_selector/model.mbd.md
sourceFormat: mbd-markdown
component: ToySwitchSelector
parameters:
  highValue: '100'
  lowValue: '25'
ports:
  selectHigh:
    direction: in
    type: bool
    default: 'false'
  selectedValue:
    direction: out
    type: count
    default: '25'
controlRules:
- name: select_high_value
  owner: SwitchSelector
  priority: 10
  stateScope: '*'
  condition: selectHigh == true
  actions:
    selectedValue: highValue
  trace:
  - SWS-001
  - SWS-003
  - SWS-004
  scenarios:
  - select_high
- name: select_low_value
  owner: SwitchSelector
  priority: 20
  stateScope: '*'
  condition: selectHigh != true
  actions:
    selectedValue: lowValue
  trace:
  - SWS-002
  - SWS-003
  - SWS-004
  scenarios:
  - select_high
controlSelectionPolicy: lowest numeric priority wins after state scope and guard match
requirementRefs:
- SWS-001
- SWS-002
- SWS-003
- SWS-004
previewSubsetAssumption: 'Preview subset assumption: discrete scenario steps represent
  the Simulink-compatible subset. Timing behavior such as sensor invalid debounce
  is represented by explicit scenario inputs and must be verified by external MBD/product-test
  infrastructure.'
```

## Functional Decomposition Evidence

```yaml
- name: SwitchSelector
  responsibility: Compare selectHigh and select highValue or lowValue using Switch-style
    simple conditional logic
  owns:
  - selectedValue
  inputs:
  - selectHigh
  - highValue
  - lowValue
  outputs:
  - selectedValue
  trace:
  - SWS-001
  - SWS-002
  - SWS-003
  - SWS-004
  scenarios:
  - select_high
```

## Traceability Matrix

```yaml
- requirement: SWS-001
  modelElements:
  - component:ToySwitchSelector
  - function:SwitchSelector
  - flow:ToySelectorSource.selectHigh->SwitchSelector.selectHigh
  - flow:ToySwitchSelector.highValue->SwitchSelector.highValue
  - flow:SwitchSelector.selectedValue->ToySwitchSelector.selectedValue
  - control:select_high_value
  - harness:ToySelectorSource
  - harness:ToySwitchSelector
  evidence:
  - samples/simple_switch_selector/model.mbd.md
  - samples/simple_switch_selector/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: SWS-002
  modelElements:
  - component:ToySwitchSelector
  - function:SwitchSelector
  - flow:ToySelectorSource.selectHigh->SwitchSelector.selectHigh
  - flow:ToySwitchSelector.lowValue->SwitchSelector.lowValue
  - flow:SwitchSelector.selectedValue->ToySwitchSelector.selectedValue
  - control:select_low_value
  - harness:ToySelectorSource
  - harness:ToySwitchSelector
  evidence:
  - samples/simple_switch_selector/model.mbd.md
  - samples/simple_switch_selector/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: SWS-003
  modelElements:
  - component:ToySwitchSelector
  - function:SwitchSelector
  - flow:ToySelectorSource.selectHigh->SwitchSelector.selectHigh
  - flow:ToySwitchSelector.highValue->SwitchSelector.highValue
  - flow:ToySwitchSelector.lowValue->SwitchSelector.lowValue
  - control:select_high_value
  - control:select_low_value
  - harness:ToySelectorSource
  - harness:ToySwitchSelector
  evidence:
  - samples/simple_switch_selector/model.mbd.md
  - samples/simple_switch_selector/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: SWS-004
  modelElements:
  - component:ToySwitchSelector
  - function:SwitchSelector
  - flow:ToySwitchSelector.selectedValue->ScenarioReport.observedBehavior
  - control:select_high_value
  - control:select_low_value
  - harness:ToySwitchSelector
  evidence:
  - samples/simple_switch_selector/model.mbd.md
  - samples/simple_switch_selector/generated/diagram.mmd
  - preview report path supplied by run-preview
```

## Scenario Steps

```yaml
- atMs: 0
  setInput:
    name: selectHigh
    value: true
```

## Harness Boundary Evidence

```yaml
- name: ToySelectorSource
  role: source
  boundary: virtual_ic
  trace:
  - SWS-001
  - SWS-002
  - SWS-003
- name: ToySwitchSelector
  role: controller
  boundary: hal
  trace:
  - SWS-001
  - SWS-002
  - SWS-003
  - SWS-004
```

## Per-Step Preview Execution

```yaml
- stepIndex: 0
  atMs: 0
  scenarioInput:
    name: selectHigh
    value: true
  before:
    state: INITIAL
    inputs:
      selectHigh: false
    outputs:
      selectedValue: 25
  virtualIcObservation:
    ToySwitchSelector.selectHigh: true
  controlRuleEvaluations:
  - rule: select_high_value
    owner: SwitchSelector
    priority: 10
    stateScope: '*'
    stateScopeMatched: true
    condition: selectHigh == true
    matched: true
    selectable: true
    actionsIfMatched:
      selectedValue: highValue
    trace:
    - SWS-001
    - SWS-003
    - SWS-004
    scenarios:
    - select_high
  - rule: select_low_value
    owner: SwitchSelector
    priority: 20
    stateScope: '*'
    stateScopeMatched: true
    condition: selectHigh != true
    matched: false
    selectable: false
    actionsIfMatched:
      selectedValue: lowValue
    trace:
    - SWS-002
    - SWS-003
    - SWS-004
    scenarios:
    - select_high
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: select_high_value
  appliedOwner: SwitchSelector
  generatedEcuCommandOutputs:
    selectedValue: 100
    commandFlows:
    - source: ToySwitchSelector.selectedValue
      target: ScenarioReport.observedBehavior
      label: reported selected value
      value: 100
      trace:
      - SWS-004
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: INITIAL
    inputs:
      selectHigh: true
    outputs:
      selectedValue: 100
  requirementRefs:
  - SWS-001
  - SWS-003
  - SWS-004
```

## Observed Behavior

```yaml
finalState: INITIAL
inputs:
  selectHigh: true
outputs:
  selectedValue: 100
appliedRules:
- select_high_value
harnessDevices:
- name: ToySelectorSource
  role: source
  boundary: virtual_ic
- name: ToySwitchSelector
  role: controller
  boundary: hal
```

## Generated ECU Command Outputs

```yaml
selectedValue: 100
commandFlows:
- source: ToySwitchSelector.selectedValue
  target: ScenarioReport.observedBehavior
  label: reported selected value
  value: 100
  trace:
  - SWS-004
previewCodeSource: sample-specific preview C export, if available
```

## Expected Behavior

```yaml
finalState: INITIAL
outputs:
  selectedValue: 100
```

## Pass/Fail Result

- PASS finalState: actual INITIAL, expected INITIAL
- PASS outputs.selectedValue: actual 100, expected 100

## Runtime Trace

- preview-only runtime started
- input selectHigh=True
- rule select_high_value applied

## Register Reads

- No register reads recorded.
