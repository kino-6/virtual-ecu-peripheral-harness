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
halCalls:
- hal_spi_read_temperature_c
- hal_pwm_set_fan_duty
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
