# Scenario Report

- Scenario: `thermal_fan_fault`
- Result: **PASS**
- Final state: `FAULT`
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
  condition: temperatureValid == false
  actions:
    state: FAULT
    fanDuty: safeDuty
    fault: 'true'
  trace:
  - SYS-005
  - HAR-004
- name: highTemperature
  condition: temperatureC >= fanOnThreshold
  actions:
    state: COOLING
    fanDuty: coolingDuty
    fault: 'false'
  trace:
  - SYS-003
  - SYS-006
- name: lowTemperature
  condition: temperatureC <= fanOffThreshold
  actions:
    state: IDLE
    fanDuty: '0'
    fault: 'false'
  trace:
  - SYS-004
  - SYS-006
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
  - generated/ecu_preview/controller.c
  - reports/thermal_fan_normal.md or reports/thermal_fan_fault.md
- requirement: HAR-002
  modelElements:
  - flow:HAL_SPI.read_temperature->ToyThermalFanController.temperatureC
  - harness:ToyThermalFanController
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - generated/ecu_preview/controller.c
  - reports/thermal_fan_normal.md or reports/thermal_fan_fault.md
- requirement: HAR-004
  modelElements:
  - flow:ToyThermalFanController.fault->ScenarioReport.observedBehavior
  - control:sensorFault
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - generated/ecu_preview/controller.c
  - reports/thermal_fan_normal.md or reports/thermal_fan_fault.md
- requirement: HAR-005
  modelElements:
  - component:ToyThermalFanController
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - generated/ecu_preview/controller.c
  - reports/thermal_fan_normal.md or reports/thermal_fan_fault.md
- requirement: STK-001
  modelElements:
  - component:ToyThermalFanController
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - generated/ecu_preview/controller.c
  - reports/thermal_fan_normal.md or reports/thermal_fan_fault.md
- requirement: SWE-001
  modelElements:
  - component:ToyThermalFanController
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - generated/ecu_preview/controller.c
  - reports/thermal_fan_normal.md or reports/thermal_fan_fault.md
- requirement: SWE-004
  modelElements:
  - flow:HAL_SPI.read_temperature->ToyThermalFanController.temperatureC
  - flow:ToyThermalFanController.fanDuty->HAL_PWM.set_fan_duty
  - harness:ToyThermalFanController
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - generated/ecu_preview/controller.c
  - reports/thermal_fan_normal.md or reports/thermal_fan_fault.md
- requirement: SYS-001
  modelElements:
  - component:ToyThermalFanController
  - flow:ToyTempSensorIC.temperatureC->HAL_SPI.read_temperature
  - harness:ToyTempSensorIC
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - generated/ecu_preview/controller.c
  - reports/thermal_fan_normal.md or reports/thermal_fan_fault.md
- requirement: SYS-002
  modelElements:
  - component:ToyThermalFanController
  - flow:ToyThermalFanController.fanDuty->HAL_PWM.set_fan_duty
  - flow:HAL_PWM.set_fan_duty->ToyFanDriverIC.dutyCommand
  - harness:ToyFanDriverIC
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - generated/ecu_preview/controller.c
  - reports/thermal_fan_normal.md or reports/thermal_fan_fault.md
- requirement: SYS-003
  modelElements:
  - component:ToyThermalFanController
  - control:highTemperature
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - generated/ecu_preview/controller.c
  - reports/thermal_fan_normal.md or reports/thermal_fan_fault.md
- requirement: SYS-004
  modelElements:
  - component:ToyThermalFanController
  - control:lowTemperature
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - generated/ecu_preview/controller.c
  - reports/thermal_fan_normal.md or reports/thermal_fan_fault.md
- requirement: SYS-005
  modelElements:
  - component:ToyThermalFanController
  - control:sensorFault
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - generated/ecu_preview/controller.c
  - reports/thermal_fan_normal.md or reports/thermal_fan_fault.md
- requirement: SYS-006
  modelElements:
  - component:ToyThermalFanController
  - flow:ToyThermalFanController.fault->ScenarioReport.observedBehavior
  - control:highTemperature
  - control:lowTemperature
  evidence:
  - examples/toy_thermal_fan_control.mbd.md
  - generated/toy_thermal_fan_control.mmd
  - generated/ecu_preview/controller.c
  - reports/thermal_fan_normal.md or reports/thermal_fan_fault.md
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
    ToyTempSensorIC.temperatureC: 82
    ToyTempSensorIC.temperatureValid: true
  controlRuleEvaluations:
  - rule: sensorFault
    condition: temperatureValid == false
    matched: false
    actionsIfMatched:
      state: FAULT
      fanDuty: safeDuty
      fault: 'true'
    trace:
    - SYS-005
    - HAR-004
  - rule: highTemperature
    condition: temperatureC >= fanOnThreshold
    matched: true
    actionsIfMatched:
      state: COOLING
      fanDuty: coolingDuty
      fault: 'false'
    trace:
    - SYS-003
    - SYS-006
  - rule: lowTemperature
    condition: temperatureC <= fanOffThreshold
    matched: false
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      fault: 'false'
    trace:
    - SYS-004
    - SYS-006
  appliedRule: highTemperature
  generatedEcuCommandOutputs:
    fanDuty: 80
    fault: false
    halCalls:
    - api: hal_spi_read_temperature_c
      direction: virtual IC to controller
      source: ToyTempSensorIC
    - api: hal_pwm_set_fan_duty
      direction: controller to virtual IC
      target: ToyFanDriverIC
      value: 80
    controllerSource: generated/ecu_preview/controller.c
  after:
    state: COOLING
    inputs:
      temperatureC: 82
      temperatureValid: true
    outputs:
      fanDuty: 80
      fault: false
  requirementRefs:
  - HAR-001
  - HAR-002
  - HAR-004
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
    ToyTempSensorIC.temperatureC: 82
    ToyTempSensorIC.temperatureValid: false
  controlRuleEvaluations:
  - rule: sensorFault
    condition: temperatureValid == false
    matched: true
    actionsIfMatched:
      state: FAULT
      fanDuty: safeDuty
      fault: 'true'
    trace:
    - SYS-005
    - HAR-004
  - rule: highTemperature
    condition: temperatureC >= fanOnThreshold
    matched: true
    actionsIfMatched:
      state: COOLING
      fanDuty: coolingDuty
      fault: 'false'
    trace:
    - SYS-003
    - SYS-006
  - rule: lowTemperature
    condition: temperatureC <= fanOffThreshold
    matched: false
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      fault: 'false'
    trace:
    - SYS-004
    - SYS-006
  appliedRule: sensorFault
  generatedEcuCommandOutputs:
    fanDuty: 35
    fault: true
    halCalls:
    - api: hal_spi_read_temperature_c
      direction: virtual IC to controller
      source: ToyTempSensorIC
    - api: hal_pwm_set_fan_duty
      direction: controller to virtual IC
      target: ToyFanDriverIC
      value: 35
    controllerSource: generated/ecu_preview/controller.c
  after:
    state: FAULT
    inputs:
      temperatureC: 82
      temperatureValid: false
    outputs:
      fanDuty: 35
      fault: true
  requirementRefs:
  - HAR-001
  - HAR-002
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
stepEvidence:
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
    ToyTempSensorIC.temperatureC: 82
    ToyTempSensorIC.temperatureValid: true
  controlRuleEvaluations:
  - rule: sensorFault
    condition: temperatureValid == false
    matched: false
    actionsIfMatched:
      state: FAULT
      fanDuty: safeDuty
      fault: 'true'
    trace:
    - SYS-005
    - HAR-004
  - rule: highTemperature
    condition: temperatureC >= fanOnThreshold
    matched: true
    actionsIfMatched:
      state: COOLING
      fanDuty: coolingDuty
      fault: 'false'
    trace:
    - SYS-003
    - SYS-006
  - rule: lowTemperature
    condition: temperatureC <= fanOffThreshold
    matched: false
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      fault: 'false'
    trace:
    - SYS-004
    - SYS-006
  appliedRule: highTemperature
  generatedEcuCommandOutputs:
    fanDuty: 80
    fault: false
    halCalls:
    - api: hal_spi_read_temperature_c
      direction: virtual IC to controller
      source: ToyTempSensorIC
    - api: hal_pwm_set_fan_duty
      direction: controller to virtual IC
      target: ToyFanDriverIC
      value: 80
    controllerSource: generated/ecu_preview/controller.c
  after:
    state: COOLING
    inputs:
      temperatureC: 82
      temperatureValid: true
    outputs:
      fanDuty: 80
      fault: false
  requirementRefs:
  - HAR-001
  - HAR-002
  - HAR-004
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
    ToyTempSensorIC.temperatureC: 82
    ToyTempSensorIC.temperatureValid: false
  controlRuleEvaluations:
  - rule: sensorFault
    condition: temperatureValid == false
    matched: true
    actionsIfMatched:
      state: FAULT
      fanDuty: safeDuty
      fault: 'true'
    trace:
    - SYS-005
    - HAR-004
  - rule: highTemperature
    condition: temperatureC >= fanOnThreshold
    matched: true
    actionsIfMatched:
      state: COOLING
      fanDuty: coolingDuty
      fault: 'false'
    trace:
    - SYS-003
    - SYS-006
  - rule: lowTemperature
    condition: temperatureC <= fanOffThreshold
    matched: false
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      fault: 'false'
    trace:
    - SYS-004
    - SYS-006
  appliedRule: sensorFault
  generatedEcuCommandOutputs:
    fanDuty: 35
    fault: true
    halCalls:
    - api: hal_spi_read_temperature_c
      direction: virtual IC to controller
      source: ToyTempSensorIC
    - api: hal_pwm_set_fan_duty
      direction: controller to virtual IC
      target: ToyFanDriverIC
      value: 35
    controllerSource: generated/ecu_preview/controller.c
  after:
    state: FAULT
    inputs:
      temperatureC: 82
      temperatureValid: false
    outputs:
      fanDuty: 35
      fault: true
  requirementRefs:
  - HAR-001
  - HAR-002
  - HAR-004
  - SYS-005
```

## Generated ECU Command Outputs

```yaml
fanDuty: 35
fault: true
halCalls:
- api: hal_spi_read_temperature_c
  direction: virtual IC to controller
  source: ToyTempSensorIC
- api: hal_pwm_set_fan_duty
  direction: controller to virtual IC
  target: ToyFanDriverIC
  value: 35
controllerSource: generated/ecu_preview/controller.c
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
