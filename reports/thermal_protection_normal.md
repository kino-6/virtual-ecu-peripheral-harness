# Scenario Report

- Scenario: `thermal_protection_normal`
- Result: **PASS**
- Final state: `COOLING`
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
  owner: FaultLatchRecoveryManager
  priority: 10
  stateScope: FAULT_LATCHED
  condition: temperatureValid == true and invalidDebounced == false and recoveryRequest
    == true
  actions:
    state: IDLE
    fanDuty: '0'
    deratingCommand: '0'
    diagnosticFault: 'false'
    safeCommandActive: 'false'
  trace:
  - SYS-008
  - HAR-006
  scenarios:
  - thermal_protection_recovery
- name: faultLatch
  owner: FaultLatchRecoveryManager
  priority: 20
  stateScope: '*'
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
  scenarios:
  - thermal_protection_fault_latch
  - thermal_protection_recovery
- name: holdLatchedFault
  owner: FaultLatchRecoveryManager
  priority: 30
  stateScope: FAULT_LATCHED
  condition: always
  actions:
    state: FAULT_LATCHED
    fanDuty: safeDuty
    deratingCommand: '0'
    diagnosticFault: 'true'
    safeCommandActive: 'true'
  trace:
  - SYS-007
  - HAR-004
  scenarios:
  - thermal_protection_fault_latch
  - thermal_protection_recovery
- name: sensorInvalid
  owner: FaultLatchRecoveryManager
  priority: 40
  stateScope: '*'
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
  scenarios:
  - thermal_protection_fault_latch
  - thermal_protection_recovery
- name: derating
  owner: DeratingCommandManager
  priority: 50
  stateScope: '*'
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
  scenarios:
  - thermal_protection_derating
  - thermal_protection_recovery
- name: highCooling
  owner: CoolingCommandManager
  priority: 60
  stateScope: '*'
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
  scenarios:
  - thermal_protection_normal
- name: lowCooling
  owner: CoolingCommandManager
  priority: 70
  stateScope: '*'
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
  scenarios:
  - thermal_protection_boundary
controlSelectionPolicy: lowest numeric priority wins after state scope and guard match
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

## Functional Decomposition Evidence

```yaml
- name: SensorInterface
  responsibility: Acquire fictional temperature and validity through the HAL boundary
  owns:
  - temperatureC
  - temperatureValid
  inputs:
  - ToyTempSensorIC.temperatureC
  - ToyTempSensorIC.temperatureValid
  outputs:
  - temperatureC
  - temperatureValid
  trace:
  - SYS-001
  - HAR-001
  - HAR-002
  scenarios:
  - thermal_protection_normal
  - thermal_protection_derating
  - thermal_protection_fault_latch
  - thermal_protection_recovery
- name: ValidityDebounceManager
  responsibility: Represent invalid sensor input and preview debounce status without
    timing physics
  owns:
  - invalidDebounced
  inputs:
  - temperatureValid
  - ToyTempSensorIC.invalidDebounced
  outputs:
  - invalidDebounced
  trace:
  - SYS-006
  - SYS-007
  - ENG-002
  - HAR-003
  scenarios:
  - thermal_protection_fault_latch
  - thermal_protection_recovery
- name: ThermalStateManager
  responsibility: Own IDLE COOLING and DERATING state decisions for valid temperature
    inputs
  owns:
  - IDLE
  - COOLING
  - DERATING
  inputs:
  - temperatureC
  - temperatureValid
  outputs:
  - state
  trace:
  - SYS-003
  - SYS-004
  - SYS-005
  scenarios:
  - thermal_protection_normal
  - thermal_protection_boundary
  - thermal_protection_derating
- name: CoolingCommandManager
  responsibility: Calculate nominal fan command for cooling and hysteresis behavior
  owns:
  - fanDuty
  inputs:
  - state
  - temperatureC
  outputs:
  - fanDuty
  trace:
  - SYS-002
  - SYS-003
  - SYS-004
  scenarios:
  - thermal_protection_normal
  - thermal_protection_boundary
- name: DeratingCommandManager
  responsibility: Calculate high-temperature fan and fictional load-limit commands
  owns:
  - deratingCommand
  inputs:
  - state
  - temperatureC
  outputs:
  - fanDuty
  - deratingCommand
  trace:
  - SYS-005
  scenarios:
  - thermal_protection_derating
- name: FaultLatchRecoveryManager
  responsibility: Own sensor fault latch hold and explicit recovery behavior
  owns:
  - SENSOR_FAULT
  - FAULT_LATCHED
  - recoveryRequest
  inputs:
  - temperatureValid
  - invalidDebounced
  - recoveryRequest
  outputs:
  - state
  - safeCommandActive
  - diagnosticFault
  trace:
  - SYS-006
  - SYS-007
  - SYS-008
  scenarios:
  - thermal_protection_fault_latch
  - thermal_protection_recovery
- name: OutputMappingDiagnostics
  responsibility: Map selected commands to HAL outputs and report-observable diagnostics
  owns:
  - safeCommandActive
  - diagnosticFault
  inputs:
  - fanDuty
  - deratingCommand
  - state
  outputs:
  - HAL_PWM.set_fan_duty
  - HAL_LIMITER.set_derating
  - ScenarioReport.observedBehavior
  - ScenarioReport.passFailResult
  trace:
  - SYS-002
  - SYS-006
  - SYS-009
  - CGEN-003
  - HAR-004
  scenarios:
  - thermal_protection_normal
  - thermal_protection_boundary
  - thermal_protection_derating
  - thermal_protection_fault_latch
  - thermal_protection_recovery
```

## Traceability Matrix

```yaml
- requirement: CGEN-003
  modelElements:
  - function:OutputMappingDiagnostics
  - flow:ToyThermalProtectionController.fanDuty->HAL_PWM.set_fan_duty
  - flow:ToyThermalProtectionController.deratingCommand->HAL_LIMITER.set_derating
  - harness:ToyThermalProtectionController
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
- requirement: ENG-002
  modelElements:
  - function:ValidityDebounceManager
  - flow:ToyTempSensorIC.invalidDebounced->ToyThermalProtectionController.invalidDebounced
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
- requirement: HAR-001
  modelElements:
  - function:SensorInterface
  - flow:ToyTempSensorIC.temperatureC->HAL_SPI.read_temperature
  - flow:ToyTempSensorIC.temperatureValid->HAL_SPI.read_temperature
  - flow:HAL_PWM.set_fan_duty->ToyFanDriverIC.dutyCommand
  - harness:ToyTempSensorIC
  - harness:ToyFanDriverIC
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
- requirement: HAR-002
  modelElements:
  - function:SensorInterface
  - flow:HAL_SPI.read_temperature->ToyThermalProtectionController.temperatureC
  - harness:ToyThermalProtectionController
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
- requirement: HAR-003
  modelElements:
  - function:ValidityDebounceManager
  - flow:ToyTempSensorIC.invalidDebounced->ToyThermalProtectionController.invalidDebounced
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
- requirement: HAR-004
  modelElements:
  - function:OutputMappingDiagnostics
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
  - preview report path supplied by run-preview
- requirement: HAR-006
  modelElements:
  - flow:HAL_LIMITER.set_derating->ToyLoadLimiterIC.limitCommand
  - control:recoverFromLatch
  - harness:ToyLoadLimiterIC
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
- requirement: SWE-001
  modelElements:
  - component:ToyThermalProtectionController
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
- requirement: SWE-002
  modelElements:
  - component:ToyThermalProtectionController
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
- requirement: SWE-003
  modelElements:
  - component:ToyThermalProtectionController
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
- requirement: SWE-004
  modelElements:
  - flow:HAL_SPI.read_temperature->ToyThermalProtectionController.temperatureC
  - flow:ToyThermalProtectionController.fanDuty->HAL_PWM.set_fan_duty
  - flow:ToyThermalProtectionController.deratingCommand->HAL_LIMITER.set_derating
  - harness:ToyThermalProtectionController
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
- requirement: SYS-001
  modelElements:
  - function:SensorInterface
  - flow:ToyTempSensorIC.temperatureC->HAL_SPI.read_temperature
  - flow:ToyTempSensorIC.temperatureValid->HAL_SPI.read_temperature
  - harness:ToyTempSensorIC
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
- requirement: SYS-002
  modelElements:
  - function:CoolingCommandManager
  - function:OutputMappingDiagnostics
  - flow:ToyThermalProtectionController.fanDuty->HAL_PWM.set_fan_duty
  - flow:HAL_PWM.set_fan_duty->ToyFanDriverIC.dutyCommand
  - control:derating
  - control:highCooling
  - harness:ToyFanDriverIC
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
- requirement: SYS-003
  modelElements:
  - function:ThermalStateManager
  - function:CoolingCommandManager
  - control:highCooling
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
- requirement: SYS-004
  modelElements:
  - function:ThermalStateManager
  - function:CoolingCommandManager
  - control:lowCooling
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
- requirement: SYS-005
  modelElements:
  - function:ThermalStateManager
  - function:DeratingCommandManager
  - flow:ToyThermalProtectionController.deratingCommand->HAL_LIMITER.set_derating
  - flow:HAL_LIMITER.set_derating->ToyLoadLimiterIC.limitCommand
  - control:derating
  - harness:ToyLoadLimiterIC
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
- requirement: SYS-006
  modelElements:
  - function:ValidityDebounceManager
  - function:FaultLatchRecoveryManager
  - function:OutputMappingDiagnostics
  - flow:ToyTempSensorIC.temperatureValid->HAL_SPI.read_temperature
  - flow:ToyThermalProtectionController.diagnosticFault->ScenarioReport.observedBehavior
  - control:faultLatch
  - control:sensorInvalid
  - harness:ToyTempSensorIC
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
- requirement: SYS-007
  modelElements:
  - function:ValidityDebounceManager
  - function:FaultLatchRecoveryManager
  - flow:ToyTempSensorIC.invalidDebounced->ToyThermalProtectionController.invalidDebounced
  - flow:ToyThermalProtectionController.diagnosticFault->ScenarioReport.observedBehavior
  - control:faultLatch
  - control:holdLatchedFault
  - harness:ToyTempSensorIC
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
- requirement: SYS-008
  modelElements:
  - function:FaultLatchRecoveryManager
  - control:recoverFromLatch
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
- requirement: SYS-009
  modelElements:
  - function:OutputMappingDiagnostics
  - flow:ToyThermalProtectionController.safeCommandActive->ScenarioReport.passFailResult
  evidence:
  - examples/toy_thermal_protection_controller.mbd.md
  - generated/toy_thermal_protection_controller.mmd
  - preview report path supplied by run-preview
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
    ToyThermalProtectionController.temperatureC: 25
    ToyThermalProtectionController.temperatureValid: true
    ToyThermalProtectionController.invalidDebounced: false
    ToyThermalProtectionController.recoveryRequest: false
  controlRuleEvaluations:
  - rule: recoverFromLatch
    owner: FaultLatchRecoveryManager
    priority: 10
    stateScope: FAULT_LATCHED
    stateScopeMatched: false
    condition: temperatureValid == true and invalidDebounced == false and recoveryRequest
      == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-008
    - HAR-006
    scenarios:
    - thermal_protection_recovery
  - rule: faultLatch
    owner: FaultLatchRecoveryManager
    priority: 20
    stateScope: '*'
    stateScopeMatched: true
    condition: invalidDebounced == true
    matched: false
    selectable: false
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
    scenarios:
    - thermal_protection_fault_latch
    - thermal_protection_recovery
  - rule: holdLatchedFault
    owner: FaultLatchRecoveryManager
    priority: 30
    stateScope: FAULT_LATCHED
    stateScopeMatched: false
    condition: always
    matched: true
    selectable: false
    actionsIfMatched:
      state: FAULT_LATCHED
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-007
    - HAR-004
    scenarios:
    - thermal_protection_fault_latch
    - thermal_protection_recovery
  - rule: sensorInvalid
    owner: FaultLatchRecoveryManager
    priority: 40
    stateScope: '*'
    stateScopeMatched: true
    condition: temperatureValid == false
    matched: false
    selectable: false
    actionsIfMatched:
      state: SENSOR_FAULT
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-006
    - HAR-004
    scenarios:
    - thermal_protection_fault_latch
    - thermal_protection_recovery
  - rule: derating
    owner: DeratingCommandManager
    priority: 50
    stateScope: '*'
    stateScopeMatched: true
    condition: temperatureC >= deratingEntryThreshold
    matched: false
    selectable: false
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
    scenarios:
    - thermal_protection_derating
    - thermal_protection_recovery
  - rule: highCooling
    owner: CoolingCommandManager
    priority: 60
    stateScope: '*'
    stateScopeMatched: true
    condition: temperatureC >= coolingOnThreshold
    matched: false
    selectable: false
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
    scenarios:
    - thermal_protection_normal
  - rule: lowCooling
    owner: CoolingCommandManager
    priority: 70
    stateScope: '*'
    stateScopeMatched: true
    condition: temperatureC <= coolingOffThreshold
    matched: true
    selectable: true
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-004
    - HAR-004
    scenarios:
    - thermal_protection_boundary
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: lowCooling
  appliedOwner: CoolingCommandManager
  generatedEcuCommandOutputs:
    fanDuty: 0
    deratingCommand: 0
    diagnosticFault: false
    safeCommandActive: false
    commandFlows:
    - source: ToyThermalProtectionController.fanDuty
      target: HAL_PWM.set_fan_duty
      label: generated ECU fan command
      value: 0
      trace:
      - SYS-002
      - SWE-004
      - CGEN-003
    - source: ToyThermalProtectionController.deratingCommand
      target: HAL_LIMITER.set_derating
      label: generated ECU derating command
      value: 0
      trace:
      - SYS-005
      - SWE-004
      - CGEN-003
    - source: ToyThermalProtectionController.diagnosticFault
      target: ScenarioReport.observedBehavior
      label: diagnostic observation
      value: false
      trace:
      - SYS-006
      - SYS-007
      - HAR-004
    - source: ToyThermalProtectionController.safeCommandActive
      target: ScenarioReport.passFailResult
      label: scenario pass/fail evidence
      value: false
      trace:
      - SYS-009
      - HAR-004
    previewCodeSource: sample-specific preview C export, if available
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
    ToyThermalProtectionController.temperatureC: 82
    ToyThermalProtectionController.temperatureValid: true
    ToyThermalProtectionController.invalidDebounced: false
    ToyThermalProtectionController.recoveryRequest: false
  controlRuleEvaluations:
  - rule: recoverFromLatch
    owner: FaultLatchRecoveryManager
    priority: 10
    stateScope: FAULT_LATCHED
    stateScopeMatched: false
    condition: temperatureValid == true and invalidDebounced == false and recoveryRequest
      == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-008
    - HAR-006
    scenarios:
    - thermal_protection_recovery
  - rule: faultLatch
    owner: FaultLatchRecoveryManager
    priority: 20
    stateScope: '*'
    stateScopeMatched: true
    condition: invalidDebounced == true
    matched: false
    selectable: false
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
    scenarios:
    - thermal_protection_fault_latch
    - thermal_protection_recovery
  - rule: holdLatchedFault
    owner: FaultLatchRecoveryManager
    priority: 30
    stateScope: FAULT_LATCHED
    stateScopeMatched: false
    condition: always
    matched: true
    selectable: false
    actionsIfMatched:
      state: FAULT_LATCHED
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-007
    - HAR-004
    scenarios:
    - thermal_protection_fault_latch
    - thermal_protection_recovery
  - rule: sensorInvalid
    owner: FaultLatchRecoveryManager
    priority: 40
    stateScope: '*'
    stateScopeMatched: true
    condition: temperatureValid == false
    matched: false
    selectable: false
    actionsIfMatched:
      state: SENSOR_FAULT
      fanDuty: safeDuty
      deratingCommand: '0'
      diagnosticFault: 'true'
      safeCommandActive: 'true'
    trace:
    - SYS-006
    - HAR-004
    scenarios:
    - thermal_protection_fault_latch
    - thermal_protection_recovery
  - rule: derating
    owner: DeratingCommandManager
    priority: 50
    stateScope: '*'
    stateScopeMatched: true
    condition: temperatureC >= deratingEntryThreshold
    matched: false
    selectable: false
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
    scenarios:
    - thermal_protection_derating
    - thermal_protection_recovery
  - rule: highCooling
    owner: CoolingCommandManager
    priority: 60
    stateScope: '*'
    stateScopeMatched: true
    condition: temperatureC >= coolingOnThreshold
    matched: true
    selectable: true
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
    scenarios:
    - thermal_protection_normal
  - rule: lowCooling
    owner: CoolingCommandManager
    priority: 70
    stateScope: '*'
    stateScopeMatched: true
    condition: temperatureC <= coolingOffThreshold
    matched: false
    selectable: false
    actionsIfMatched:
      state: IDLE
      fanDuty: '0'
      deratingCommand: '0'
      diagnosticFault: 'false'
      safeCommandActive: 'false'
    trace:
    - SYS-004
    - HAR-004
    scenarios:
    - thermal_protection_boundary
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: highCooling
  appliedOwner: CoolingCommandManager
  generatedEcuCommandOutputs:
    fanDuty: 70
    deratingCommand: 0
    diagnosticFault: false
    safeCommandActive: false
    commandFlows:
    - source: ToyThermalProtectionController.fanDuty
      target: HAL_PWM.set_fan_duty
      label: generated ECU fan command
      value: 70
      trace:
      - SYS-002
      - SWE-004
      - CGEN-003
    - source: ToyThermalProtectionController.deratingCommand
      target: HAL_LIMITER.set_derating
      label: generated ECU derating command
      value: 0
      trace:
      - SYS-005
      - SWE-004
      - CGEN-003
    - source: ToyThermalProtectionController.diagnosticFault
      target: ScenarioReport.observedBehavior
      label: diagnostic observation
      value: false
      trace:
      - SYS-006
      - SYS-007
      - HAR-004
    - source: ToyThermalProtectionController.safeCommandActive
      target: ScenarioReport.passFailResult
      label: scenario pass/fail evidence
      value: false
      trace:
      - SYS-009
      - HAR-004
    previewCodeSource: sample-specific preview C export, if available
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
  - HAR-004
  - SYS-002
  - SYS-003
```

## Observed Behavior

```yaml
finalState: COOLING
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
appliedRules:
- lowCooling
- highCooling
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
```

## Generated ECU Command Outputs

```yaml
fanDuty: 70
deratingCommand: 0
diagnosticFault: false
safeCommandActive: false
commandFlows:
- source: ToyThermalProtectionController.fanDuty
  target: HAL_PWM.set_fan_duty
  label: generated ECU fan command
  value: 70
  trace:
  - SYS-002
  - SWE-004
  - CGEN-003
- source: ToyThermalProtectionController.deratingCommand
  target: HAL_LIMITER.set_derating
  label: generated ECU derating command
  value: 0
  trace:
  - SYS-005
  - SWE-004
  - CGEN-003
- source: ToyThermalProtectionController.diagnosticFault
  target: ScenarioReport.observedBehavior
  label: diagnostic observation
  value: false
  trace:
  - SYS-006
  - SYS-007
  - HAR-004
- source: ToyThermalProtectionController.safeCommandActive
  target: ScenarioReport.passFailResult
  label: scenario pass/fail evidence
  value: false
  trace:
  - SYS-009
  - HAR-004
previewCodeSource: sample-specific preview C export, if available
```

## Expected Behavior

```yaml
finalState: COOLING
outputs:
  fanDuty: 70
  deratingCommand: 0
  diagnosticFault: false
  safeCommandActive: false
```

## Pass/Fail Result

- PASS finalState: actual COOLING, expected COOLING
- PASS outputs.fanDuty: actual 70, expected 70
- PASS outputs.deratingCommand: actual 0, expected 0
- PASS outputs.diagnosticFault: actual False, expected False
- PASS outputs.safeCommandActive: actual False, expected False

## Runtime Trace

- preview-only runtime started
- input temperatureValid=True
- rule lowCooling applied
- input temperatureC=82
- rule highCooling applied

## Register Reads

- No register reads recorded.
