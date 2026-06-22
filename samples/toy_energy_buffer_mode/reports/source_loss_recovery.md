# Scenario Report

- Scenario: `toy_energy_buffer_source_loss_recovery`
- Result: **PASS**
- Final state: `CHARGE`
- Boundary: preview-only; not a certified code generation or verification backend.

## Model Inputs

```yaml
source: samples/toy_energy_buffer_mode/model.mbd.md
sourceFormat: mbd-markdown
component: ToyEnergyBufferMode
parameters: {}
ports:
  externalPowerAvailable:
    direction: in
    type: bool
    default: 'true'
  emptyDetected:
    direction: in
    type: bool
    default: 'false'
  supplyEnabled:
    direction: out
    type: bool
    default: 'false'
  chargeIndicator:
    direction: out
    type: bool
    default: 'true'
controlRules:
- name: power_removed_discharge
  owner: ToyEnergyBufferModeController
  priority: 10
  stateScope: CHARGE
  condition: externalPowerAvailable == false and emptyDetected == false
  actions:
    state: DISCHARGE
    supplyEnabled: 'true'
    chargeIndicator: 'false'
  trace:
  - EBUF-001
  - EBUF-006
  scenarios:
  - source_loss_recovery
- name: discharge_empty
  owner: ToyEnergyBufferModeController
  priority: 20
  stateScope: DISCHARGE
  condition: emptyDetected == true
  actions:
    state: EMPTY
    supplyEnabled: 'false'
    chargeIndicator: 'false'
  trace:
  - EBUF-002
  - EBUF-006
  scenarios:
  - source_loss_recovery
- name: empty_reconnect_charge
  owner: ToyEnergyBufferModeController
  priority: 30
  stateScope: EMPTY
  condition: externalPowerAvailable == true
  actions:
    state: CHARGE
    supplyEnabled: 'false'
    chargeIndicator: 'true'
  trace:
  - EBUF-003
  - EBUF-006
  scenarios:
  - source_loss_recovery
- name: discharge_reconnect_charge
  owner: ToyEnergyBufferModeController
  priority: 40
  stateScope: DISCHARGE
  condition: externalPowerAvailable == true
  actions:
    state: CHARGE
    supplyEnabled: 'false'
    chargeIndicator: 'true'
  trace:
  - EBUF-004
  - EBUF-006
  scenarios:
  - source_loss_recovery
controlSelectionPolicy: lowest numeric priority wins after state scope and guard match
requirementRefs:
- EBUF-001
- EBUF-002
- EBUF-003
- EBUF-004
- EBUF-005
- EBUF-006
previewSubsetAssumption: 'Preview subset assumption: discrete scenario steps represent
  the Simulink-compatible subset. Timing behavior such as sensor invalid debounce
  is represented by explicit scenario inputs and must be verified by external MBD/product-test
  infrastructure.'
```

## Functional Decomposition Evidence

```yaml
- name: ToyEnergyBufferModeController
  responsibility: Own the CHARGE/DISCHARGE/EMPTY lifecycle and map source availability
    plus empty detection to supply and charge indication outputs
  owns:
  - CHARGE
  - DISCHARGE
  - EMPTY
  - supplyEnabled
  - chargeIndicator
  inputs:
  - externalPowerAvailable
  - emptyDetected
  outputs:
  - state
  - supplyEnabled
  - chargeIndicator
  trace:
  - EBUF-001
  - EBUF-002
  - EBUF-003
  - EBUF-004
  - EBUF-005
  - EBUF-006
  scenarios:
  - source_loss_recovery
```

## Traceability Matrix

```yaml
- requirement: EBUF-001
  modelElements:
  - component:ToyEnergyBufferMode
  - function:ToyEnergyBufferModeController
  - flow:ToyPowerSource.externalPowerAvailable->ToyEnergyBufferModeController.externalPowerAvailable
  - flow:ToyEmptyMonitor.emptyDetected->ToyEnergyBufferModeController.emptyDetected
  - flow:ToyEnergyBufferModeController.supplyEnabled->ToyEnergyBufferMode.supplyEnabled
  - flow:ToyEnergyBufferModeController.chargeIndicator->ToyEnergyBufferMode.chargeIndicator
  - control:power_removed_discharge
  - harness:ToyPowerSource
  - harness:ToyEmptyMonitor
  - harness:ToyEnergyBufferMode
  evidence:
  - samples/toy_energy_buffer_mode/model.mbd.md
  - samples/toy_energy_buffer_mode/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: EBUF-002
  modelElements:
  - component:ToyEnergyBufferMode
  - function:ToyEnergyBufferModeController
  - flow:ToyEmptyMonitor.emptyDetected->ToyEnergyBufferModeController.emptyDetected
  - flow:ToyEnergyBufferModeController.supplyEnabled->ToyEnergyBufferMode.supplyEnabled
  - flow:ToyEnergyBufferModeController.chargeIndicator->ToyEnergyBufferMode.chargeIndicator
  - control:discharge_empty
  - harness:ToyEmptyMonitor
  - harness:ToyEnergyBufferMode
  evidence:
  - samples/toy_energy_buffer_mode/model.mbd.md
  - samples/toy_energy_buffer_mode/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: EBUF-003
  modelElements:
  - component:ToyEnergyBufferMode
  - function:ToyEnergyBufferModeController
  - flow:ToyPowerSource.externalPowerAvailable->ToyEnergyBufferModeController.externalPowerAvailable
  - flow:ToyEnergyBufferModeController.supplyEnabled->ToyEnergyBufferMode.supplyEnabled
  - flow:ToyEnergyBufferModeController.chargeIndicator->ToyEnergyBufferMode.chargeIndicator
  - control:empty_reconnect_charge
  - harness:ToyPowerSource
  - harness:ToyEnergyBufferMode
  evidence:
  - samples/toy_energy_buffer_mode/model.mbd.md
  - samples/toy_energy_buffer_mode/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: EBUF-004
  modelElements:
  - component:ToyEnergyBufferMode
  - function:ToyEnergyBufferModeController
  - flow:ToyPowerSource.externalPowerAvailable->ToyEnergyBufferModeController.externalPowerAvailable
  - flow:ToyEnergyBufferModeController.supplyEnabled->ToyEnergyBufferMode.supplyEnabled
  - flow:ToyEnergyBufferModeController.chargeIndicator->ToyEnergyBufferMode.chargeIndicator
  - control:discharge_reconnect_charge
  - harness:ToyPowerSource
  - harness:ToyEnergyBufferMode
  evidence:
  - samples/toy_energy_buffer_mode/model.mbd.md
  - samples/toy_energy_buffer_mode/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: EBUF-005
  modelElements:
  - component:ToyEnergyBufferMode
  - function:ToyEnergyBufferModeController
  - flow:ToyPowerSource.externalPowerAvailable->ToyEnergyBufferModeController.externalPowerAvailable
  - flow:ToyEmptyMonitor.emptyDetected->ToyEnergyBufferModeController.emptyDetected
  - flow:ToyEnergyBufferModeController.supplyEnabled->ToyEnergyBufferMode.supplyEnabled
  - flow:ToyEnergyBufferModeController.chargeIndicator->ToyEnergyBufferMode.chargeIndicator
  - harness:ToyPowerSource
  - harness:ToyEmptyMonitor
  - harness:ToyEnergyBufferMode
  evidence:
  - samples/toy_energy_buffer_mode/model.mbd.md
  - samples/toy_energy_buffer_mode/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: EBUF-006
  modelElements:
  - component:ToyEnergyBufferMode
  - function:ToyEnergyBufferModeController
  - flow:ToyEnergyBufferMode.supplyEnabled->ScenarioReport.observedBehavior
  - flow:ToyEnergyBufferMode.chargeIndicator->ScenarioReport.observedBehavior
  - control:power_removed_discharge
  - control:discharge_empty
  - control:empty_reconnect_charge
  - control:discharge_reconnect_charge
  - harness:ToyEnergyBufferMode
  evidence:
  - samples/toy_energy_buffer_mode/model.mbd.md
  - samples/toy_energy_buffer_mode/generated/diagram.mmd
  - preview report path supplied by run-preview
```

## Scenario Steps

```yaml
- atMs: 0
  setInput:
    name: externalPowerAvailable
    value: false
- atMs: 10
  setInput:
    name: emptyDetected
    value: true
- atMs: 20
  setInput:
    name: externalPowerAvailable
    value: true
```

## Harness Boundary Evidence

```yaml
- name: ToyPowerSource
  role: source
  boundary: virtual_ic
  trace:
  - EBUF-001
  - EBUF-003
  - EBUF-004
  - EBUF-005
- name: ToyEmptyMonitor
  role: source
  boundary: virtual_ic
  trace:
  - EBUF-001
  - EBUF-002
  - EBUF-005
- name: ToyEnergyBufferMode
  role: controller
  boundary: hal
  trace:
  - EBUF-001
  - EBUF-002
  - EBUF-003
  - EBUF-004
  - EBUF-005
  - EBUF-006
```

## Per-Step Preview Execution

```yaml
- stepIndex: 0
  atMs: 0
  scenarioInput:
    name: externalPowerAvailable
    value: false
  before:
    state: CHARGE
    inputs:
      externalPowerAvailable: true
      emptyDetected: false
    outputs:
      supplyEnabled: false
      chargeIndicator: true
  virtualIcObservation:
    ToyEnergyBufferMode.externalPowerAvailable: false
    ToyEnergyBufferMode.emptyDetected: false
  controlRuleEvaluations:
  - rule: power_removed_discharge
    owner: ToyEnergyBufferModeController
    priority: 10
    stateScope: CHARGE
    stateScopeMatched: true
    condition: externalPowerAvailable == false and emptyDetected == false
    matched: true
    selectable: true
    actionsIfMatched:
      state: DISCHARGE
      supplyEnabled: 'true'
      chargeIndicator: 'false'
    trace:
    - EBUF-001
    - EBUF-006
    scenarios:
    - source_loss_recovery
  - rule: discharge_empty
    owner: ToyEnergyBufferModeController
    priority: 20
    stateScope: DISCHARGE
    stateScopeMatched: false
    condition: emptyDetected == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: EMPTY
      supplyEnabled: 'false'
      chargeIndicator: 'false'
    trace:
    - EBUF-002
    - EBUF-006
    scenarios:
    - source_loss_recovery
  - rule: empty_reconnect_charge
    owner: ToyEnergyBufferModeController
    priority: 30
    stateScope: EMPTY
    stateScopeMatched: false
    condition: externalPowerAvailable == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: CHARGE
      supplyEnabled: 'false'
      chargeIndicator: 'true'
    trace:
    - EBUF-003
    - EBUF-006
    scenarios:
    - source_loss_recovery
  - rule: discharge_reconnect_charge
    owner: ToyEnergyBufferModeController
    priority: 40
    stateScope: DISCHARGE
    stateScopeMatched: false
    condition: externalPowerAvailable == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: CHARGE
      supplyEnabled: 'false'
      chargeIndicator: 'true'
    trace:
    - EBUF-004
    - EBUF-006
    scenarios:
    - source_loss_recovery
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: power_removed_discharge
  appliedOwner: ToyEnergyBufferModeController
  generatedEcuCommandOutputs:
    supplyEnabled: true
    chargeIndicator: false
    commandFlows:
    - source: ToyEnergyBufferMode.supplyEnabled
      target: ScenarioReport.observedBehavior
      label: reported supply command
      value: true
      trace:
      - EBUF-006
    - source: ToyEnergyBufferMode.chargeIndicator
      target: ScenarioReport.observedBehavior
      label: reported charge indication
      value: false
      trace:
      - EBUF-006
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: DISCHARGE
    inputs:
      externalPowerAvailable: false
      emptyDetected: false
    outputs:
      supplyEnabled: true
      chargeIndicator: false
  requirementRefs:
  - EBUF-001
  - EBUF-006
- stepIndex: 1
  atMs: 10
  scenarioInput:
    name: emptyDetected
    value: true
  before:
    state: DISCHARGE
    inputs:
      externalPowerAvailable: false
      emptyDetected: false
    outputs:
      supplyEnabled: true
      chargeIndicator: false
  virtualIcObservation:
    ToyEnergyBufferMode.externalPowerAvailable: false
    ToyEnergyBufferMode.emptyDetected: true
  controlRuleEvaluations:
  - rule: power_removed_discharge
    owner: ToyEnergyBufferModeController
    priority: 10
    stateScope: CHARGE
    stateScopeMatched: false
    condition: externalPowerAvailable == false and emptyDetected == false
    matched: false
    selectable: false
    actionsIfMatched:
      state: DISCHARGE
      supplyEnabled: 'true'
      chargeIndicator: 'false'
    trace:
    - EBUF-001
    - EBUF-006
    scenarios:
    - source_loss_recovery
  - rule: discharge_empty
    owner: ToyEnergyBufferModeController
    priority: 20
    stateScope: DISCHARGE
    stateScopeMatched: true
    condition: emptyDetected == true
    matched: true
    selectable: true
    actionsIfMatched:
      state: EMPTY
      supplyEnabled: 'false'
      chargeIndicator: 'false'
    trace:
    - EBUF-002
    - EBUF-006
    scenarios:
    - source_loss_recovery
  - rule: empty_reconnect_charge
    owner: ToyEnergyBufferModeController
    priority: 30
    stateScope: EMPTY
    stateScopeMatched: false
    condition: externalPowerAvailable == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: CHARGE
      supplyEnabled: 'false'
      chargeIndicator: 'true'
    trace:
    - EBUF-003
    - EBUF-006
    scenarios:
    - source_loss_recovery
  - rule: discharge_reconnect_charge
    owner: ToyEnergyBufferModeController
    priority: 40
    stateScope: DISCHARGE
    stateScopeMatched: true
    condition: externalPowerAvailable == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: CHARGE
      supplyEnabled: 'false'
      chargeIndicator: 'true'
    trace:
    - EBUF-004
    - EBUF-006
    scenarios:
    - source_loss_recovery
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: discharge_empty
  appliedOwner: ToyEnergyBufferModeController
  generatedEcuCommandOutputs:
    supplyEnabled: false
    chargeIndicator: false
    commandFlows:
    - source: ToyEnergyBufferMode.supplyEnabled
      target: ScenarioReport.observedBehavior
      label: reported supply command
      value: false
      trace:
      - EBUF-006
    - source: ToyEnergyBufferMode.chargeIndicator
      target: ScenarioReport.observedBehavior
      label: reported charge indication
      value: false
      trace:
      - EBUF-006
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: EMPTY
    inputs:
      externalPowerAvailable: false
      emptyDetected: true
    outputs:
      supplyEnabled: false
      chargeIndicator: false
  requirementRefs:
  - EBUF-002
  - EBUF-006
- stepIndex: 2
  atMs: 20
  scenarioInput:
    name: externalPowerAvailable
    value: true
  before:
    state: EMPTY
    inputs:
      externalPowerAvailable: false
      emptyDetected: true
    outputs:
      supplyEnabled: false
      chargeIndicator: false
  virtualIcObservation:
    ToyEnergyBufferMode.externalPowerAvailable: true
    ToyEnergyBufferMode.emptyDetected: true
  controlRuleEvaluations:
  - rule: power_removed_discharge
    owner: ToyEnergyBufferModeController
    priority: 10
    stateScope: CHARGE
    stateScopeMatched: false
    condition: externalPowerAvailable == false and emptyDetected == false
    matched: false
    selectable: false
    actionsIfMatched:
      state: DISCHARGE
      supplyEnabled: 'true'
      chargeIndicator: 'false'
    trace:
    - EBUF-001
    - EBUF-006
    scenarios:
    - source_loss_recovery
  - rule: discharge_empty
    owner: ToyEnergyBufferModeController
    priority: 20
    stateScope: DISCHARGE
    stateScopeMatched: false
    condition: emptyDetected == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: EMPTY
      supplyEnabled: 'false'
      chargeIndicator: 'false'
    trace:
    - EBUF-002
    - EBUF-006
    scenarios:
    - source_loss_recovery
  - rule: empty_reconnect_charge
    owner: ToyEnergyBufferModeController
    priority: 30
    stateScope: EMPTY
    stateScopeMatched: true
    condition: externalPowerAvailable == true
    matched: true
    selectable: true
    actionsIfMatched:
      state: CHARGE
      supplyEnabled: 'false'
      chargeIndicator: 'true'
    trace:
    - EBUF-003
    - EBUF-006
    scenarios:
    - source_loss_recovery
  - rule: discharge_reconnect_charge
    owner: ToyEnergyBufferModeController
    priority: 40
    stateScope: DISCHARGE
    stateScopeMatched: false
    condition: externalPowerAvailable == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: CHARGE
      supplyEnabled: 'false'
      chargeIndicator: 'true'
    trace:
    - EBUF-004
    - EBUF-006
    scenarios:
    - source_loss_recovery
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: empty_reconnect_charge
  appliedOwner: ToyEnergyBufferModeController
  generatedEcuCommandOutputs:
    supplyEnabled: false
    chargeIndicator: true
    commandFlows:
    - source: ToyEnergyBufferMode.supplyEnabled
      target: ScenarioReport.observedBehavior
      label: reported supply command
      value: false
      trace:
      - EBUF-006
    - source: ToyEnergyBufferMode.chargeIndicator
      target: ScenarioReport.observedBehavior
      label: reported charge indication
      value: true
      trace:
      - EBUF-006
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: CHARGE
    inputs:
      externalPowerAvailable: true
      emptyDetected: true
    outputs:
      supplyEnabled: false
      chargeIndicator: true
  requirementRefs:
  - EBUF-003
  - EBUF-006
```

## Observed Behavior

```yaml
finalState: CHARGE
inputs:
  externalPowerAvailable: true
  emptyDetected: true
outputs:
  supplyEnabled: false
  chargeIndicator: true
appliedRules:
- power_removed_discharge
- discharge_empty
- empty_reconnect_charge
harnessDevices:
- name: ToyPowerSource
  role: source
  boundary: virtual_ic
- name: ToyEmptyMonitor
  role: source
  boundary: virtual_ic
- name: ToyEnergyBufferMode
  role: controller
  boundary: hal
```

## Generated ECU Command Outputs

```yaml
supplyEnabled: false
chargeIndicator: true
commandFlows:
- source: ToyEnergyBufferMode.supplyEnabled
  target: ScenarioReport.observedBehavior
  label: reported supply command
  value: false
  trace:
  - EBUF-006
- source: ToyEnergyBufferMode.chargeIndicator
  target: ScenarioReport.observedBehavior
  label: reported charge indication
  value: true
  trace:
  - EBUF-006
previewCodeSource: sample-specific preview C export, if available
```

## Expected Behavior

```yaml
finalState: CHARGE
outputs:
  supplyEnabled: false
  chargeIndicator: true
```

## Pass/Fail Result

- PASS finalState: actual CHARGE, expected CHARGE
- PASS outputs.supplyEnabled: actual False, expected False
- PASS outputs.chargeIndicator: actual True, expected True

## Runtime Trace

- preview-only runtime started
- input externalPowerAvailable=False
- rule power_removed_discharge applied
- input emptyDetected=True
- rule discharge_empty applied
- input externalPowerAvailable=True
- rule empty_reconnect_charge applied

## Register Reads

- No register reads recorded.
