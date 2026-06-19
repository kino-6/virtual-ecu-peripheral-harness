# Scenario Report

- Scenario: `thermal_fan_normal`
- Result: **PASS**
- Final state: `COOLING`
- Boundary: preview-only; not a certified code generation or verification backend.

## Model Inputs

```yaml
source: examples/toy_thermal_fan_control.mbd.md
sourceFormat: mbd-markdown
component: ToyThermalFanController
parameters:
  fanOnThreshold: '75'
  fanOffThreshold: '65'
  coolingDuty: '80'
  safeDuty: '35'
ports:
  temperatureC:
    direction: in
    type: degC
    default: '25'
  temperatureValid:
    direction: in
    type: bool
    default: 'true'
  fanDuty:
    direction: out
    type: percent
    default: '0'
  fault:
    direction: out
    type: bool
    default: 'false'
controlRules:
- name: sensorFault
  owner: ''
  priority: 1000
  stateScope: '*'
  condition: temperatureValid == false
  actions:
    state: FAULT
    fanDuty: safeDuty
    fault: 'true'
  trace:
  - SYS-005
  - HAR-004
  scenarios: []
- name: highTemperature
  owner: ''
  priority: 1001
  stateScope: '*'
  condition: temperatureC >= fanOnThreshold
  actions:
    state: COOLING
    fanDuty: coolingDuty
    fault: 'false'
  trace:
  - SYS-003
  - SYS-006
  scenarios: []
- name: lowTemperature
  owner: ''
  priority: 1002
  stateScope: '*'
  condition: temperatureC <= fanOffThreshold
  actions:
    state: IDLE
    fanDuty: '0'
    fault: 'false'
  trace:
  - SYS-004
  - SYS-006
  scenarios: []
controlSelectionPolicy: lowest numeric priority wins after state scope and guard match
requirementRefs:
- HAR-001
- HAR-002
- HAR-004
- HAR-005
- STK-001
- SWE-001
- SWE-004
- SYS-001
- SYS-002
- SYS-003
- SYS-004
- SYS-005
- SYS-006
previewSubsetAssumption: 'Preview subset assumption: discrete scenario steps represent
  the Simulink-compatible subset. Timing behavior such as sensor invalid debounce
  is represented by explicit scenario inputs and must be verified by external MBD/product-test
  infrastructure.'
```

## Functional Decomposition Evidence

```yaml
[]
```

## Traceability Matrix

```yaml
- requirement: HAR-001
  modelElements:
  - flow:ToyTempSensorIC.temperatureC->HAL_SPI.read_temperature
  - flow:HAL_PWM.set_fan_duty->ToyFanDriverIC.dutyCommand
  - harness:ToyTempSensorIC
  - harness:ToyFanDriverIC
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - preview report path supplied by run-preview
- requirement: HAR-002
  modelElements:
  - flow:HAL_SPI.read_temperature->ToyThermalFanController.temperatureC
  - harness:ToyThermalFanController
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - preview report path supplied by run-preview
- requirement: HAR-004
  modelElements:
  - flow:ToyThermalFanController.fault->ScenarioReport.observedBehavior
  - control:sensorFault
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - preview report path supplied by run-preview
- requirement: HAR-005
  modelElements:
  - component:ToyThermalFanController
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - preview report path supplied by run-preview
- requirement: STK-001
  modelElements:
  - component:ToyThermalFanController
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - preview report path supplied by run-preview
- requirement: SWE-001
  modelElements:
  - component:ToyThermalFanController
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - preview report path supplied by run-preview
- requirement: SWE-004
  modelElements:
  - flow:HAL_SPI.read_temperature->ToyThermalFanController.temperatureC
  - flow:ToyThermalFanController.fanDuty->HAL_PWM.set_fan_duty
  - harness:ToyThermalFanController
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - preview report path supplied by run-preview
- requirement: SYS-001
  modelElements:
  - component:ToyThermalFanController
  - flow:ToyTempSensorIC.temperatureC->HAL_SPI.read_temperature
  - harness:ToyTempSensorIC
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - preview report path supplied by run-preview
- requirement: SYS-002
  modelElements:
  - component:ToyThermalFanController
  - flow:ToyThermalFanController.fanDuty->HAL_PWM.set_fan_duty
  - flow:HAL_PWM.set_fan_duty->ToyFanDriverIC.dutyCommand
  - harness:ToyFanDriverIC
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - preview report path supplied by run-preview
- requirement: SYS-003
  modelElements:
  - component:ToyThermalFanController
  - control:highTemperature
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - preview report path supplied by run-preview
- requirement: SYS-004
  modelElements:
  - component:ToyThermalFanController
  - control:lowTemperature
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - preview report path supplied by run-preview
- requirement: SYS-005
  modelElements:
  - component:ToyThermalFanController
  - control:sensorFault
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - preview report path supplied by run-preview
- requirement: SYS-006
  modelElements:
  - component:ToyThermalFanController
  - flow:ToyThermalFanController.fault->ScenarioReport.observedBehavior
  - control:highTemperature
  - control:lowTemperature
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - preview report path supplied by run-preview
```

## Scenario Steps

```yaml
- atMs: 0
  setInput:
    name: temperatureC
    value: 25
- atMs: 10
  setInput:
    name: temperatureValid
    value: true
- atMs: 100
  setInput:
    name: temperatureC
    value: 82
```

## Harness Boundary Evidence

```yaml
- name: ToyTempSensorIC
  role: sensor
  boundary: virtual_ic
  trace:
  - HAR-001
  - SYS-001
- name: ToyFanDriverIC
  role: actuator
  boundary: virtual_ic
  trace:
  - HAR-001
  - SYS-002
- name: ToyThermalFanController
  role: controller
  boundary: hal
  trace:
  - HAR-002
  - SWE-004
```

## Per-Step Preview Execution

```yaml
- stepIndex: 0
  atMs: 0
  scenarioInput:
    name: temperatureC
    value: 25
  before:
    state: RESET
    inputs:
      temperatureC: 25
      temperatureValid: true
    outputs:
      fanDuty: 0
      fault: false
  virtualIcObservation:
    ToyThermalFanController.temperatureC: 25
    ToyThermalFanController.temperatureValid: true
  controlRuleEvaluations:
  - rule: sensorFault
    owner: ''
    priority: 1000
    stateScope: '*'
    stateScopeMatched: true
    condition: temperatureValid == false
    matched: false
    selectable: false
    actionsIfMatched:
      state: FAULT
      fanDuty: safeDuty
      fault: 'true'
    trace:
    - SYS-005
    - HAR-004
    scenarios: []
  - rule: highTemperature
    owner: ''
    priority: 1001
    stateScope: '*'
    stateScopeMatched: true
    condition: temperatureC >= fanOnThreshold
    matched: false
    selectable: false
    actionsIfMatched:
      state: COOLING
      fanDuty: coolingDuty
      fault: 'false'
    trace:
    - SYS-003
    - SYS-006
    scenarios: []
  - rule: lowTemperature
    owner: ''
    priority: 1002
    stateScope: '*'
    stateScopeMatched: true
    condition: temperatureC <= fanOffThreshold
    matched: true
    selectable: true
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      fault: 'false'
    trace:
    - SYS-004
    - SYS-006
    scenarios: []
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: lowTemperature
  appliedOwner: ''
  generatedEcuCommandOutputs:
    fanDuty: 0
    fault: false
    commandFlows:
    - source: ToyThermalFanController.fanDuty
      target: HAL_PWM.set_fan_duty
      label: generated ECU command
      value: 0
      trace:
      - SYS-002
      - SWE-004
    - source: ToyThermalFanController.fault
      target: ScenarioReport.observedBehavior
      label: fault observation
      value: false
      trace:
      - SYS-006
      - HAR-004
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: IDLE
    inputs:
      temperatureC: 25
      temperatureValid: true
    outputs:
      fanDuty: 0
      fault: false
  requirementRefs:
  - SYS-004
  - SYS-006
- stepIndex: 1
  atMs: 10
  scenarioInput:
    name: temperatureValid
    value: true
  before:
    state: IDLE
    inputs:
      temperatureC: 25
      temperatureValid: true
    outputs:
      fanDuty: 0
      fault: false
  virtualIcObservation:
    ToyThermalFanController.temperatureC: 25
    ToyThermalFanController.temperatureValid: true
  controlRuleEvaluations:
  - rule: sensorFault
    owner: ''
    priority: 1000
    stateScope: '*'
    stateScopeMatched: true
    condition: temperatureValid == false
    matched: false
    selectable: false
    actionsIfMatched:
      state: FAULT
      fanDuty: safeDuty
      fault: 'true'
    trace:
    - SYS-005
    - HAR-004
    scenarios: []
  - rule: highTemperature
    owner: ''
    priority: 1001
    stateScope: '*'
    stateScopeMatched: true
    condition: temperatureC >= fanOnThreshold
    matched: false
    selectable: false
    actionsIfMatched:
      state: COOLING
      fanDuty: coolingDuty
      fault: 'false'
    trace:
    - SYS-003
    - SYS-006
    scenarios: []
  - rule: lowTemperature
    owner: ''
    priority: 1002
    stateScope: '*'
    stateScopeMatched: true
    condition: temperatureC <= fanOffThreshold
    matched: true
    selectable: true
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      fault: 'false'
    trace:
    - SYS-004
    - SYS-006
    scenarios: []
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: lowTemperature
  appliedOwner: ''
  generatedEcuCommandOutputs:
    fanDuty: 0
    fault: false
    commandFlows:
    - source: ToyThermalFanController.fanDuty
      target: HAL_PWM.set_fan_duty
      label: generated ECU command
      value: 0
      trace:
      - SYS-002
      - SWE-004
    - source: ToyThermalFanController.fault
      target: ScenarioReport.observedBehavior
      label: fault observation
      value: false
      trace:
      - SYS-006
      - HAR-004
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: IDLE
    inputs:
      temperatureC: 25
      temperatureValid: true
    outputs:
      fanDuty: 0
      fault: false
  requirementRefs:
  - SYS-004
  - SYS-006
- stepIndex: 2
  atMs: 100
  scenarioInput:
    name: temperatureC
    value: 82
  before:
    state: IDLE
    inputs:
      temperatureC: 25
      temperatureValid: true
    outputs:
      fanDuty: 0
      fault: false
  virtualIcObservation:
    ToyThermalFanController.temperatureC: 82
    ToyThermalFanController.temperatureValid: true
  controlRuleEvaluations:
  - rule: sensorFault
    owner: ''
    priority: 1000
    stateScope: '*'
    stateScopeMatched: true
    condition: temperatureValid == false
    matched: false
    selectable: false
    actionsIfMatched:
      state: FAULT
      fanDuty: safeDuty
      fault: 'true'
    trace:
    - SYS-005
    - HAR-004
    scenarios: []
  - rule: highTemperature
    owner: ''
    priority: 1001
    stateScope: '*'
    stateScopeMatched: true
    condition: temperatureC >= fanOnThreshold
    matched: true
    selectable: true
    actionsIfMatched:
      state: COOLING
      fanDuty: coolingDuty
      fault: 'false'
    trace:
    - SYS-003
    - SYS-006
    scenarios: []
  - rule: lowTemperature
    owner: ''
    priority: 1002
    stateScope: '*'
    stateScopeMatched: true
    condition: temperatureC <= fanOffThreshold
    matched: false
    selectable: false
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      fault: 'false'
    trace:
    - SYS-004
    - SYS-006
    scenarios: []
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: highTemperature
  appliedOwner: ''
  generatedEcuCommandOutputs:
    fanDuty: 80
    fault: false
    commandFlows:
    - source: ToyThermalFanController.fanDuty
      target: HAL_PWM.set_fan_duty
      label: generated ECU command
      value: 80
      trace:
      - SYS-002
      - SWE-004
    - source: ToyThermalFanController.fault
      target: ScenarioReport.observedBehavior
      label: fault observation
      value: false
      trace:
      - SYS-006
      - HAR-004
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: COOLING
    inputs:
      temperatureC: 82
      temperatureValid: true
    outputs:
      fanDuty: 80
      fault: false
  requirementRefs:
  - SYS-003
  - SYS-006
```

## Observed Behavior

```yaml
finalState: COOLING
inputs:
  temperatureC: 82
  temperatureValid: true
outputs:
  fanDuty: 80
  fault: false
appliedRules:
- lowTemperature
- lowTemperature
- highTemperature
harnessDevices:
- name: ToyTempSensorIC
  role: sensor
  boundary: virtual_ic
- name: ToyFanDriverIC
  role: actuator
  boundary: virtual_ic
- name: ToyThermalFanController
  role: controller
  boundary: hal
```

## Generated ECU Command Outputs

```yaml
fanDuty: 80
fault: false
commandFlows:
- source: ToyThermalFanController.fanDuty
  target: HAL_PWM.set_fan_duty
  label: generated ECU command
  value: 80
  trace:
  - SYS-002
  - SWE-004
- source: ToyThermalFanController.fault
  target: ScenarioReport.observedBehavior
  label: fault observation
  value: false
  trace:
  - SYS-006
  - HAR-004
previewCodeSource: sample-specific preview C export, if available
```

## Expected Behavior

```yaml
finalState: COOLING
outputs:
  fanDuty: 80
  fault: false
```

## Pass/Fail Result

- PASS finalState: actual COOLING, expected COOLING
- PASS outputs.fanDuty: actual 80, expected 80
- PASS outputs.fault: actual False, expected False

## Runtime Trace

- preview-only runtime started
- input temperatureC=25
- rule lowTemperature applied
- input temperatureValid=True
- rule lowTemperature applied
- input temperatureC=82
- rule highTemperature applied

## Register Reads

- No register reads recorded.
