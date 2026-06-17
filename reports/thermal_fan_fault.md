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
halCalls:
- hal_spi_read_temperature_c
- hal_pwm_set_fan_duty
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
