# Scenario Report

- Scenario: `thermal_protection_boundary`
- Result: **PASS**
- Final state: `IDLE`
- Boundary: preview-only; not a certified code generation or verification backend.

## Model Inputs

```yaml
source: examples/toy_thermal_protection_controller.mbd.md
sourceFormat: mbd-markdown
component: ToyThermalProtectionController
parameters:
  coolingOnThreshold: '78'
  coolingOffThreshold: '68'
  deratingEntryThreshold: '94'
  coolingDuty: '70'
  deratingFanDuty: '95'
  deratingLimit: '45'
  safeDuty: '30'
ports:
  temperatureC:
    direction: in
    type: degC
    default: '25'
  temperatureValid:
    direction: in
    type: bool
    default: 'true'
  invalidDebounced:
    direction: in
    type: bool
    default: 'false'
  recoveryRequest:
    direction: in
    type: bool
    default: 'false'
  fanDuty:
    direction: out
    type: percent
    default: '0'
  deratingCommand:
    direction: out
    type: percent
    default: '0'
  diagnosticFault:
    direction: out
    type: bool
    default: 'false'
  safeCommandActive:
    direction: out
    type: bool
    default: 'false'
controlRules:
- name: recoverFromLatch
  condition: state == FAULT_LATCHED and temperatureValid == true and invalidDebounced
    == false and recoveryRequest == true
  actions:
    state: IDLE
    fanDuty: '0'
    deratingCommand: '0'
    diagnosticFault: 'false'
    safeCommandActive: 'false'
  trace:
  - SYS-008
  - HAR-006
- name: faultLatch
  condition: invalidDebounced == true
  actions:
    state: FAULT_LATCHED
    fanDuty: safeDuty
    deratingCommand: '0'
    diagnosticFault: 'true'
    safeCommandActive: 'true'
  trace:
  - SYS-007
  - SYS-006
  - HAR-004
- name: holdLatchedFault
  condition: state == FAULT_LATCHED
  actions:
    state: FAULT_LATCHED
    fanDuty: safeDuty
    deratingCommand: '0'
    diagnosticFault: 'true'
    safeCommandActive: 'true'
  trace:
  - SYS-007
  - HAR-004
- name: sensorInvalid
  condition: temperatureValid == false
  actions:
    state: SENSOR_FAULT
    fanDuty: safeDuty
    deratingCommand: '0'
    diagnosticFault: 'true'
    safeCommandActive: 'true'
  trace:
  - SYS-006
  - HAR-004
- name: derating
  condition: temperatureC >= deratingEntryThreshold
  actions:
    state: DERATING
    fanDuty: deratingFanDuty
    deratingCommand: deratingLimit
    diagnosticFault: 'false'
    safeCommandActive: 'false'
  trace:
  - SYS-005
  - SYS-002
  - HAR-004
- name: highCooling
  condition: temperatureC >= coolingOnThreshold
  actions:
    state: COOLING
    fanDuty: coolingDuty
    deratingCommand: '0'
    diagnosticFault: 'false'
    safeCommandActive: 'false'
  trace:
  - SYS-003
  - SYS-002
  - HAR-004
- name: lowCooling
  condition: temperatureC <= coolingOffThreshold
  actions:
    state: IDLE
    fanDuty: '0'
    deratingCommand: '0'
    diagnosticFault: 'false'
    safeCommandActive: 'false'
  trace:
  - SYS-004
  - HAR-004
requirementRefs:
- CGEN-003
- ENG-002
- HAR-001
- HAR-002
- HAR-003
- HAR-004
- HAR-006
- SWE-001
- SWE-002
- SWE-003
- SWE-004
- SYS-001
- SYS-002
- SYS-003
- SYS-004
- SYS-005
- SYS-006
- SYS-007
- SYS-008
- SYS-009
previewSubsetAssumption: 'Preview subset assumption: discrete scenario steps represent
  the Simulink-compatible subset. Timing behavior such as sensor invalid debounce
  is represented by explicit scenario inputs and must be verified by external MBD/product-test
  infrastructure.'
```

## Traceability Matrix

```yaml
- requirement: CGEN-003
  modelElements:
  - flow:ToyThermalProtectionController.fanDuty->HAL_PWM.set_fan_duty
  - flow:ToyThermalProtectionController.deratingCommand->HAL_LIMITER.set_derating
  - harness:ToyThermalProtectionController
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: ENG-002
  modelElements:
  - flow:ToyTempSensorIC.invalidDebounced->ToyThermalProtectionController.invalidDebounced
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: HAR-001
  modelElements:
  - flow:ToyTempSensorIC.temperatureC->HAL_SPI.read_temperature
  - flow:ToyTempSensorIC.temperatureValid->HAL_SPI.read_temperature
  - flow:HAL_PWM.set_fan_duty->ToyFanDriverIC.dutyCommand
  - harness:ToyTempSensorIC
  - harness:ToyFanDriverIC
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: HAR-002
  modelElements:
  - flow:HAL_SPI.read_temperature->ToyThermalProtectionController.temperatureC
  - harness:ToyThermalProtectionController
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: HAR-003
  modelElements:
  - flow:ToyTempSensorIC.invalidDebounced->ToyThermalProtectionController.invalidDebounced
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: HAR-004
  modelElements:
  - flow:ToyThermalProtectionController.diagnosticFault->ScenarioReport.observedBehavior
  - flow:ToyThermalProtectionController.safeCommandActive->ScenarioReport.passFailResult
  - control:faultLatch
  - control:holdLatchedFault
  - control:sensorInvalid
  - control:derating
  - control:highCooling
  - control:lowCooling
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: HAR-006
  modelElements:
  - flow:HAL_LIMITER.set_derating->ToyLoadLimiterIC.limitCommand
  - control:recoverFromLatch
  - harness:ToyLoadLimiterIC
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: SWE-001
  modelElements:
  - component:ToyThermalProtectionController
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: SWE-002
  modelElements:
  - component:ToyThermalProtectionController
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: SWE-003
  modelElements:
  - component:ToyThermalProtectionController
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: SWE-004
  modelElements:
  - flow:HAL_SPI.read_temperature->ToyThermalProtectionController.temperatureC
  - flow:ToyThermalProtectionController.fanDuty->HAL_PWM.set_fan_duty
  - flow:ToyThermalProtectionController.deratingCommand->HAL_LIMITER.set_derating
  - harness:ToyThermalProtectionController
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: SYS-001
  modelElements:
  - flow:ToyTempSensorIC.temperatureC->HAL_SPI.read_temperature
  - flow:ToyTempSensorIC.temperatureValid->HAL_SPI.read_temperature
  - harness:ToyTempSensorIC
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: SYS-002
  modelElements:
  - flow:ToyThermalProtectionController.fanDuty->HAL_PWM.set_fan_duty
  - flow:HAL_PWM.set_fan_duty->ToyFanDriverIC.dutyCommand
  - control:derating
  - control:highCooling
  - harness:ToyFanDriverIC
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: SYS-003
  modelElements:
  - control:highCooling
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: SYS-004
  modelElements:
  - control:lowCooling
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: SYS-005
  modelElements:
  - flow:ToyThermalProtectionController.deratingCommand->HAL_LIMITER.set_derating
  - flow:HAL_LIMITER.set_derating->ToyLoadLimiterIC.limitCommand
  - control:derating
  - harness:ToyLoadLimiterIC
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: SYS-006
  modelElements:
  - flow:ToyTempSensorIC.temperatureValid->HAL_SPI.read_temperature
  - flow:ToyThermalProtectionController.diagnosticFault->ScenarioReport.observedBehavior
  - control:faultLatch
  - control:sensorInvalid
  - harness:ToyTempSensorIC
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: SYS-007
  modelElements:
  - flow:ToyTempSensorIC.invalidDebounced->ToyThermalProtectionController.invalidDebounced
  - flow:ToyThermalProtectionController.diagnosticFault->ScenarioReport.observedBehavior
  - control:faultLatch
  - control:holdLatchedFault
  - harness:ToyTempSensorIC
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: SYS-008
  modelElements:
  - control:recoverFromLatch
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
- requirement: SYS-009
  modelElements:
  - flow:ToyThermalProtectionController.safeCommandActive->ScenarioReport.passFailResult
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - generated/protection_ecu_preview/controller.c
  - reports/thermal_protection_normal.md
  - reports/thermal_protection_boundary.md
  - reports/thermal_protection_derating.md
  - reports/thermal_protection_fault_latch.md
  - reports/thermal_protection_recovery.md
```

## Scenario Steps

```yaml
- atMs: 0
  setInput:
    name: temperatureValid
    value: true
- atMs: 20
  setInput:
    name: temperatureC
    value: 82
- atMs: 80
  setInput:
    name: temperatureC
    value: 66
```

## Harness Boundary Evidence

```yaml
- name: ToyTempSensorIC
  role: sensor
  boundary: virtual_ic
  trace:
  - HAR-001
  - SYS-001
  - SYS-006
  - SYS-007
- name: ToyFanDriverIC
  role: actuator
  boundary: virtual_ic
  trace:
  - HAR-001
  - SYS-002
- name: ToyLoadLimiterIC
  role: actuator
  boundary: virtual_ic
  trace:
  - HAR-006
  - SYS-005
- name: ToyThermalProtectionController
  role: controller
  boundary: hal
  trace:
  - HAR-002
  - SWE-004
  - CGEN-003
```

## Per-Step Preview Execution

```yaml
- stepIndex: 0
  atMs: 0
  scenarioInput:
    name: temperatureValid
    value: true
  before:
    state: RESET
    inputs:
      temperatureC: 25
      temperatureValid: true
      invalidDebounced: false
      recoveryRequest: false
    outputs:
      fanDuty: 0
      deratingCommand: 0
      diagnosticFault: false
      safeCommandActive: false
  virtualIcObservation:
    ToyTempSensorIC.temperatureC: 25
    ToyTempSensorIC.temperatureValid: true
  controlRuleEvaluations:
  - rule: recoverFromLatch
    condition: state == FAULT_LATCHED and temperatureValid == true and invalidDebounced
      == false and recoveryRequest == true
    matched: false
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-008
    - HAR-006
  - rule: faultLatch
    condition: invalidDebounced == true
    matched: false
    actionsIfMatched:
      state: FAULT_LATCHED
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-007
    - SYS-006
    - HAR-004
  - rule: holdLatchedFault
    condition: state == FAULT_LATCHED
    matched: false
    actionsIfMatched:
      state: FAULT_LATCHED
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-007
    - HAR-004
  - rule: sensorInvalid
    condition: temperatureValid == false
    matched: false
    actionsIfMatched:
      state: SENSOR_FAULT
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-006
    - HAR-004
  - rule: derating
    condition: temperatureC >= deratingEntryThreshold
    matched: false
    actionsIfMatched:
      state: DERATING
      fanDuty: deratingFanDuty
      deratingCommand: deratingLimit
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-005
    - SYS-002
    - HAR-004
  - rule: highCooling
    condition: temperatureC >= coolingOnThreshold
    matched: false
    actionsIfMatched:
      state: COOLING
      fanDuty: coolingDuty
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-003
    - SYS-002
    - HAR-004
  - rule: lowCooling
    condition: temperatureC <= coolingOffThreshold
    matched: true
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-004
    - HAR-004
  appliedRule: lowCooling
  generatedEcuCommandOutputs:
    fanDuty: 0
    deratingCommand: 0
    diagnosticFault: false
    safeCommandActive: false
    halCalls:
    - api: hal_spi_read_temperature_c
      direction: virtual IC to controller
      source: ToyTempSensorIC
    - api: hal_pwm_set_fan_duty
      direction: controller to virtual IC
      target: ToyFanDriverIC
      value: 0
    - api: hal_load_limiter_set_derating
      direction: controller to virtual IC
      target: ToyLoadLimiterIC
      value: 0
    controllerSource: generated/protection_ecu_preview/controller.c
  after:
    state: IDLE
    inputs:
      temperatureC: 25
      temperatureValid: true
      invalidDebounced: false
      recoveryRequest: false
    outputs:
      fanDuty: 0
      deratingCommand: 0
      diagnosticFault: false
      safeCommandActive: false
  requirementRefs:
  - HAR-001
  - HAR-002
  - HAR-004
  - SYS-004
- stepIndex: 1
  atMs: 20
  scenarioInput:
    name: temperatureC
    value: 82
  before:
    state: IDLE
    inputs:
      temperatureC: 25
      temperatureValid: true
      invalidDebounced: false
      recoveryRequest: false
    outputs:
      fanDuty: 0
      deratingCommand: 0
      diagnosticFault: false
      safeCommandActive: false
  virtualIcObservation:
    ToyTempSensorIC.temperatureC: 82
    ToyTempSensorIC.temperatureValid: true
  controlRuleEvaluations:
  - rule: recoverFromLatch
    condition: state == FAULT_LATCHED and temperatureValid == true and invalidDebounced
      == false and recoveryRequest == true
    matched: false
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-008
    - HAR-006
  - rule: faultLatch
    condition: invalidDebounced == true
    matched: false
    actionsIfMatched:
      state: FAULT_LATCHED
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-007
    - SYS-006
    - HAR-004
  - rule: holdLatchedFault
    condition: state == FAULT_LATCHED
    matched: false
    actionsIfMatched:
      state: FAULT_LATCHED
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-007
    - HAR-004
  - rule: sensorInvalid
    condition: temperatureValid == false
    matched: false
    actionsIfMatched:
      state: SENSOR_FAULT
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-006
    - HAR-004
  - rule: derating
    condition: temperatureC >= deratingEntryThreshold
    matched: false
    actionsIfMatched:
      state: DERATING
      fanDuty: deratingFanDuty
      deratingCommand: deratingLimit
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-005
    - SYS-002
    - HAR-004
  - rule: highCooling
    condition: temperatureC >= coolingOnThreshold
    matched: true
    actionsIfMatched:
      state: COOLING
      fanDuty: coolingDuty
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-003
    - SYS-002
    - HAR-004
  - rule: lowCooling
    condition: temperatureC <= coolingOffThreshold
    matched: false
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-004
    - HAR-004
  appliedRule: highCooling
  generatedEcuCommandOutputs:
    fanDuty: 70
    deratingCommand: 0
    diagnosticFault: false
    safeCommandActive: false
    halCalls:
    - api: hal_spi_read_temperature_c
      direction: virtual IC to controller
      source: ToyTempSensorIC
    - api: hal_pwm_set_fan_duty
      direction: controller to virtual IC
      target: ToyFanDriverIC
      value: 70
    - api: hal_load_limiter_set_derating
      direction: controller to virtual IC
      target: ToyLoadLimiterIC
      value: 0
    controllerSource: generated/protection_ecu_preview/controller.c
  after:
    state: COOLING
    inputs:
      temperatureC: 82
      temperatureValid: true
      invalidDebounced: false
      recoveryRequest: false
    outputs:
      fanDuty: 70
      deratingCommand: 0
      diagnosticFault: false
      safeCommandActive: false
  requirementRefs:
  - HAR-001
  - HAR-002
  - HAR-004
  - SYS-002
  - SYS-003
- stepIndex: 2
  atMs: 80
  scenarioInput:
    name: temperatureC
    value: 66
  before:
    state: COOLING
    inputs:
      temperatureC: 82
      temperatureValid: true
      invalidDebounced: false
      recoveryRequest: false
    outputs:
      fanDuty: 70
      deratingCommand: 0
      diagnosticFault: false
      safeCommandActive: false
  virtualIcObservation:
    ToyTempSensorIC.temperatureC: 66
    ToyTempSensorIC.temperatureValid: true
  controlRuleEvaluations:
  - rule: recoverFromLatch
    condition: state == FAULT_LATCHED and temperatureValid == true and invalidDebounced
      == false and recoveryRequest == true
    matched: false
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-008
    - HAR-006
  - rule: faultLatch
    condition: invalidDebounced == true
    matched: false
    actionsIfMatched:
      state: FAULT_LATCHED
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-007
    - SYS-006
    - HAR-004
  - rule: holdLatchedFault
    condition: state == FAULT_LATCHED
    matched: false
    actionsIfMatched:
      state: FAULT_LATCHED
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-007
    - HAR-004
  - rule: sensorInvalid
    condition: temperatureValid == false
    matched: false
    actionsIfMatched:
      state: SENSOR_FAULT
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-006
    - HAR-004
  - rule: derating
    condition: temperatureC >= deratingEntryThreshold
    matched: false
    actionsIfMatched:
      state: DERATING
      fanDuty: deratingFanDuty
      deratingCommand: deratingLimit
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-005
    - SYS-002
    - HAR-004
  - rule: highCooling
    condition: temperatureC >= coolingOnThreshold
    matched: false
    actionsIfMatched:
      state: COOLING
      fanDuty: coolingDuty
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-003
    - SYS-002
    - HAR-004
  - rule: lowCooling
    condition: temperatureC <= coolingOffThreshold
    matched: true
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-004
    - HAR-004
  appliedRule: lowCooling
  generatedEcuCommandOutputs:
    fanDuty: 0
    deratingCommand: 0
    diagnosticFault: false
    safeCommandActive: false
    halCalls:
    - api: hal_spi_read_temperature_c
      direction: virtual IC to controller
      source: ToyTempSensorIC
    - api: hal_pwm_set_fan_duty
      direction: controller to virtual IC
      target: ToyFanDriverIC
      value: 0
    - api: hal_load_limiter_set_derating
      direction: controller to virtual IC
      target: ToyLoadLimiterIC
      value: 0
    controllerSource: generated/protection_ecu_preview/controller.c
  after:
    state: IDLE
    inputs:
      temperatureC: 66
      temperatureValid: true
      invalidDebounced: false
      recoveryRequest: false
    outputs:
      fanDuty: 0
      deratingCommand: 0
      diagnosticFault: false
      safeCommandActive: false
  requirementRefs:
  - HAR-001
  - HAR-002
  - HAR-004
  - SYS-004
```

## Observed Behavior

```yaml
finalState: IDLE
inputs:
  temperatureC: 66
  temperatureValid: true
  invalidDebounced: false
  recoveryRequest: false
outputs:
  fanDuty: 0
  deratingCommand: 0
  diagnosticFault: false
  safeCommandActive: false
appliedRules:
- lowCooling
- highCooling
- lowCooling
harnessDevices:
- name: ToyTempSensorIC
  role: sensor
  boundary: virtual_ic
- name: ToyFanDriverIC
  role: actuator
  boundary: virtual_ic
- name: ToyLoadLimiterIC
  role: actuator
  boundary: virtual_ic
- name: ToyThermalProtectionController
  role: controller
  boundary: hal
stepEvidence:
- stepIndex: 0
  atMs: 0
  scenarioInput:
    name: temperatureValid
    value: true
  before:
    state: RESET
    inputs:
      temperatureC: 25
      temperatureValid: true
      invalidDebounced: false
      recoveryRequest: false
    outputs:
      fanDuty: 0
      deratingCommand: 0
      diagnosticFault: false
      safeCommandActive: false
  virtualIcObservation:
    ToyTempSensorIC.temperatureC: 25
    ToyTempSensorIC.temperatureValid: true
  controlRuleEvaluations:
  - rule: recoverFromLatch
    condition: state == FAULT_LATCHED and temperatureValid == true and invalidDebounced
      == false and recoveryRequest == true
    matched: false
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-008
    - HAR-006
  - rule: faultLatch
    condition: invalidDebounced == true
    matched: false
    actionsIfMatched:
      state: FAULT_LATCHED
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-007
    - SYS-006
    - HAR-004
  - rule: holdLatchedFault
    condition: state == FAULT_LATCHED
    matched: false
    actionsIfMatched:
      state: FAULT_LATCHED
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-007
    - HAR-004
  - rule: sensorInvalid
    condition: temperatureValid == false
    matched: false
    actionsIfMatched:
      state: SENSOR_FAULT
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-006
    - HAR-004
  - rule: derating
    condition: temperatureC >= deratingEntryThreshold
    matched: false
    actionsIfMatched:
      state: DERATING
      fanDuty: deratingFanDuty
      deratingCommand: deratingLimit
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-005
    - SYS-002
    - HAR-004
  - rule: highCooling
    condition: temperatureC >= coolingOnThreshold
    matched: false
    actionsIfMatched:
      state: COOLING
      fanDuty: coolingDuty
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-003
    - SYS-002
    - HAR-004
  - rule: lowCooling
    condition: temperatureC <= coolingOffThreshold
    matched: true
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-004
    - HAR-004
  appliedRule: lowCooling
  generatedEcuCommandOutputs:
    fanDuty: 0
    deratingCommand: 0
    diagnosticFault: false
    safeCommandActive: false
    halCalls:
    - api: hal_spi_read_temperature_c
      direction: virtual IC to controller
      source: ToyTempSensorIC
    - api: hal_pwm_set_fan_duty
      direction: controller to virtual IC
      target: ToyFanDriverIC
      value: 0
    - api: hal_load_limiter_set_derating
      direction: controller to virtual IC
      target: ToyLoadLimiterIC
      value: 0
    controllerSource: generated/protection_ecu_preview/controller.c
  after:
    state: IDLE
    inputs:
      temperatureC: 25
      temperatureValid: true
      invalidDebounced: false
      recoveryRequest: false
    outputs:
      fanDuty: 0
      deratingCommand: 0
      diagnosticFault: false
      safeCommandActive: false
  requirementRefs:
  - HAR-001
  - HAR-002
  - HAR-004
  - SYS-004
- stepIndex: 1
  atMs: 20
  scenarioInput:
    name: temperatureC
    value: 82
  before:
    state: IDLE
    inputs:
      temperatureC: 25
      temperatureValid: true
      invalidDebounced: false
      recoveryRequest: false
    outputs:
      fanDuty: 0
      deratingCommand: 0
      diagnosticFault: false
      safeCommandActive: false
  virtualIcObservation:
    ToyTempSensorIC.temperatureC: 82
    ToyTempSensorIC.temperatureValid: true
  controlRuleEvaluations:
  - rule: recoverFromLatch
    condition: state == FAULT_LATCHED and temperatureValid == true and invalidDebounced
      == false and recoveryRequest == true
    matched: false
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-008
    - HAR-006
  - rule: faultLatch
    condition: invalidDebounced == true
    matched: false
    actionsIfMatched:
      state: FAULT_LATCHED
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-007
    - SYS-006
    - HAR-004
  - rule: holdLatchedFault
    condition: state == FAULT_LATCHED
    matched: false
    actionsIfMatched:
      state: FAULT_LATCHED
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-007
    - HAR-004
  - rule: sensorInvalid
    condition: temperatureValid == false
    matched: false
    actionsIfMatched:
      state: SENSOR_FAULT
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-006
    - HAR-004
  - rule: derating
    condition: temperatureC >= deratingEntryThreshold
    matched: false
    actionsIfMatched:
      state: DERATING
      fanDuty: deratingFanDuty
      deratingCommand: deratingLimit
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-005
    - SYS-002
    - HAR-004
  - rule: highCooling
    condition: temperatureC >= coolingOnThreshold
    matched: true
    actionsIfMatched:
      state: COOLING
      fanDuty: coolingDuty
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-003
    - SYS-002
    - HAR-004
  - rule: lowCooling
    condition: temperatureC <= coolingOffThreshold
    matched: false
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-004
    - HAR-004
  appliedRule: highCooling
  generatedEcuCommandOutputs:
    fanDuty: 70
    deratingCommand: 0
    diagnosticFault: false
    safeCommandActive: false
    halCalls:
    - api: hal_spi_read_temperature_c
      direction: virtual IC to controller
      source: ToyTempSensorIC
    - api: hal_pwm_set_fan_duty
      direction: controller to virtual IC
      target: ToyFanDriverIC
      value: 70
    - api: hal_load_limiter_set_derating
      direction: controller to virtual IC
      target: ToyLoadLimiterIC
      value: 0
    controllerSource: generated/protection_ecu_preview/controller.c
  after:
    state: COOLING
    inputs:
      temperatureC: 82
      temperatureValid: true
      invalidDebounced: false
      recoveryRequest: false
    outputs:
      fanDuty: 70
      deratingCommand: 0
      diagnosticFault: false
      safeCommandActive: false
  requirementRefs:
  - HAR-001
  - HAR-002
  - HAR-004
  - SYS-002
  - SYS-003
- stepIndex: 2
  atMs: 80
  scenarioInput:
    name: temperatureC
    value: 66
  before:
    state: COOLING
    inputs:
      temperatureC: 82
      temperatureValid: true
      invalidDebounced: false
      recoveryRequest: false
    outputs:
      fanDuty: 70
      deratingCommand: 0
      diagnosticFault: false
      safeCommandActive: false
  virtualIcObservation:
    ToyTempSensorIC.temperatureC: 66
    ToyTempSensorIC.temperatureValid: true
  controlRuleEvaluations:
  - rule: recoverFromLatch
    condition: state == FAULT_LATCHED and temperatureValid == true and invalidDebounced
      == false and recoveryRequest == true
    matched: false
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-008
    - HAR-006
  - rule: faultLatch
    condition: invalidDebounced == true
    matched: false
    actionsIfMatched:
      state: FAULT_LATCHED
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-007
    - SYS-006
    - HAR-004
  - rule: holdLatchedFault
    condition: state == FAULT_LATCHED
    matched: false
    actionsIfMatched:
      state: FAULT_LATCHED
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-007
    - HAR-004
  - rule: sensorInvalid
    condition: temperatureValid == false
    matched: false
    actionsIfMatched:
      state: SENSOR_FAULT
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-006
    - HAR-004
  - rule: derating
    condition: temperatureC >= deratingEntryThreshold
    matched: false
    actionsIfMatched:
      state: DERATING
      fanDuty: deratingFanDuty
      deratingCommand: deratingLimit
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-005
    - SYS-002
    - HAR-004
  - rule: highCooling
    condition: temperatureC >= coolingOnThreshold
    matched: false
    actionsIfMatched:
      state: COOLING
      fanDuty: coolingDuty
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-003
    - SYS-002
    - HAR-004
  - rule: lowCooling
    condition: temperatureC <= coolingOffThreshold
    matched: true
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-004
    - HAR-004
  appliedRule: lowCooling
  generatedEcuCommandOutputs:
    fanDuty: 0
    deratingCommand: 0
    diagnosticFault: false
    safeCommandActive: false
    halCalls:
    - api: hal_spi_read_temperature_c
      direction: virtual IC to controller
      source: ToyTempSensorIC
    - api: hal_pwm_set_fan_duty
      direction: controller to virtual IC
      target: ToyFanDriverIC
      value: 0
    - api: hal_load_limiter_set_derating
      direction: controller to virtual IC
      target: ToyLoadLimiterIC
      value: 0
    controllerSource: generated/protection_ecu_preview/controller.c
  after:
    state: IDLE
    inputs:
      temperatureC: 66
      temperatureValid: true
      invalidDebounced: false
      recoveryRequest: false
    outputs:
      fanDuty: 0
      deratingCommand: 0
      diagnosticFault: false
      safeCommandActive: false
  requirementRefs:
  - HAR-001
  - HAR-002
  - HAR-004
  - SYS-004
```

## Generated ECU Command Outputs

```yaml
fanDuty: 0
deratingCommand: 0
diagnosticFault: false
safeCommandActive: false
halCalls:
- api: hal_spi_read_temperature_c
  direction: virtual IC to controller
  source: ToyTempSensorIC
- api: hal_pwm_set_fan_duty
  direction: controller to virtual IC
  target: ToyFanDriverIC
  value: 0
- api: hal_load_limiter_set_derating
  direction: controller to virtual IC
  target: ToyLoadLimiterIC
  value: 0
controllerSource: generated/protection_ecu_preview/controller.c
```

## Expected Behavior

```yaml
finalState: IDLE
outputs:
  fanDuty: 0
  deratingCommand: 0
  diagnosticFault: false
  safeCommandActive: false
```

## Pass/Fail Result

- PASS finalState: actual IDLE, expected IDLE
- PASS outputs.fanDuty: actual 0, expected 0
- PASS outputs.deratingCommand: actual 0, expected 0
- PASS outputs.diagnosticFault: actual False, expected False
- PASS outputs.safeCommandActive: actual False, expected False

## Runtime Trace

- preview-only runtime started
- input temperatureValid=True
- rule lowCooling applied
- input temperatureC=82
- rule highCooling applied
- input temperatureC=66
- rule lowCooling applied

## Register Reads

- No register reads recorded.
