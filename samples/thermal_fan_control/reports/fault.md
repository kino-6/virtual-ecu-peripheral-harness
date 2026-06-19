# Scenario Report

- Scenario: `thermal_fan_fault`
- Result: **PASS**
- Final state: `FAULT`
- Boundary: preview-only; not a certified code generation or verification backend.

## Model Inputs

```yaml
source: samples/thermal_fan_control/model.mbd.md
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
  - samples/thermal_fan_control/model.mbd.md
  - samples/thermal_fan_control/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: HAR-002
  modelElements:
  - flow:HAL_SPI.read_temperature->ToyThermalFanController.temperatureC
  - harness:ToyThermalFanController
  evidence:
  - samples/thermal_fan_control/model.mbd.md
  - samples/thermal_fan_control/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: HAR-004
  modelElements:
  - flow:ToyThermalFanController.fault->ScenarioReport.observedBehavior
  - control:sensorFault
  evidence:
  - samples/thermal_fan_control/model.mbd.md
  - samples/thermal_fan_control/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: HAR-005
  modelElements:
  - component:ToyThermalFanController
  evidence:
  - samples/thermal_fan_control/model.mbd.md
  - samples/thermal_fan_control/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: STK-001
  modelElements:
  - component:ToyThermalFanController
  evidence:
  - samples/thermal_fan_control/model.mbd.md
  - samples/thermal_fan_control/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: SWE-001
  modelElements:
  - component:ToyThermalFanController
  evidence:
  - samples/thermal_fan_control/model.mbd.md
  - samples/thermal_fan_control/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: SWE-004
  modelElements:
  - flow:HAL_SPI.read_temperature->ToyThermalFanController.temperatureC
  - flow:ToyThermalFanController.fanDuty->HAL_PWM.set_fan_duty
  - harness:ToyThermalFanController
  evidence:
  - samples/thermal_fan_control/model.mbd.md
  - samples/thermal_fan_control/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: SYS-001
  modelElements:
  - component:ToyThermalFanController
  - flow:ToyTempSensorIC.temperatureC->HAL_SPI.read_temperature
  - harness:ToyTempSensorIC
  evidence:
  - samples/thermal_fan_control/model.mbd.md
  - samples/thermal_fan_control/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: SYS-002
  modelElements:
  - component:ToyThermalFanController
  - flow:ToyThermalFanController.fanDuty->HAL_PWM.set_fan_duty
  - flow:HAL_PWM.set_fan_duty->ToyFanDriverIC.dutyCommand
  - harness:ToyFanDriverIC
  evidence:
  - samples/thermal_fan_control/model.mbd.md
  - samples/thermal_fan_control/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: SYS-003
  modelElements:
  - component:ToyThermalFanController
  - control:highTemperature
  evidence:
  - samples/thermal_fan_control/model.mbd.md
  - samples/thermal_fan_control/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: SYS-004
  modelElements:
  - component:ToyThermalFanController
  - control:lowTemperature
  evidence:
  - samples/thermal_fan_control/model.mbd.md
  - samples/thermal_fan_control/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: SYS-005
  modelElements:
  - component:ToyThermalFanController
  - control:sensorFault
  evidence:
  - samples/thermal_fan_control/model.mbd.md
  - samples/thermal_fan_control/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: SYS-006
  modelElements:
  - component:ToyThermalFanController
  - flow:ToyThermalFanController.fault->ScenarioReport.observedBehavior
  - control:highTemperature
  - control:lowTemperature
  evidence:
  - samples/thermal_fan_control/model.mbd.md
  - samples/thermal_fan_control/generated/diagram.mmd
  - preview report path supplied by run-preview
```

## Scenario Steps

```yaml
- atMs: 0
  setInput:
    name: temperatureC
    value: 82
- atMs: 20
  setInput:
    name: temperatureValid
    value: false
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
    value: 82
  before:
    state: RESET
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
- stepIndex: 1
  atMs: 20
  scenarioInput:
    name: temperatureValid
    value: false
  before:
    state: COOLING
    inputs:
      temperatureC: 82
      temperatureValid: true
    outputs:
      fanDuty: 80
      fault: false
  virtualIcObservation:
    ToyThermalFanController.temperatureC: 82
    ToyThermalFanController.temperatureValid: false
  controlRuleEvaluations:
  - rule: sensorFault
    owner: ''
    priority: 1000
    stateScope: '*'
    stateScopeMatched: true
    condition: temperatureValid == false
    matched: true
    selectable: true
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
  appliedRule: sensorFault
  appliedOwner: ''
  generatedEcuCommandOutputs:
    fanDuty: 35
    fault: true
    commandFlows:
    - source: ToyThermalFanController.fanDuty
      target: HAL_PWM.set_fan_duty
      label: generated ECU command
      value: 35
      trace:
      - SYS-002
      - SWE-004
    - source: ToyThermalFanController.fault
      target: ScenarioReport.observedBehavior
      label: fault observation
      value: true
      trace:
      - SYS-006
      - HAR-004
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: FAULT
    inputs:
      temperatureC: 82
      temperatureValid: false
    outputs:
      fanDuty: 35
      fault: true
  requirementRefs:
  - HAR-004
  - SYS-005
```

## Observed Behavior

```yaml
finalState: FAULT
inputs:
  temperatureC: 82
  temperatureValid: false
outputs:
  fanDuty: 35
  fault: true
appliedRules:
- highTemperature
- sensorFault
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
fanDuty: 35
fault: true
commandFlows:
- source: ToyThermalFanController.fanDuty
  target: HAL_PWM.set_fan_duty
  label: generated ECU command
  value: 35
  trace:
  - SYS-002
  - SWE-004
- source: ToyThermalFanController.fault
  target: ScenarioReport.observedBehavior
  label: fault observation
  value: true
  trace:
  - SYS-006
  - HAR-004
previewCodeSource: sample-specific preview C export, if available
```

## Expected Behavior

```yaml
finalState: FAULT
outputs:
  fanDuty: 35
  fault: true
```

## Pass/Fail Result

- PASS finalState: actual FAULT, expected FAULT
- PASS outputs.fanDuty: actual 35, expected 35
- PASS outputs.fault: actual True, expected True

## Runtime Trace

- preview-only runtime started
- input temperatureC=82
- rule highTemperature applied
- input temperatureValid=False
- rule sensorFault applied

## Register Reads

- No register reads recorded.
