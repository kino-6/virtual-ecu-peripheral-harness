# Scenario Report

- Scenario: `spi_timeout`
- Result: **PASS**
- Final state: `INIT`

## Model Inputs

```yaml
canonicalModel: specs/toy_power_monitor.tmbd.yml
name: ToyPowerMonitorIC
kind: PeripheralModel
schemaVersion: '0.1'
bus:
  type: spi
  mode: 0
  wordBits: 8
initialState: RESET
parameters:
  undervoltageThreshold: 7.0
inputSignals:
  voltage:
    default: 12.0
    unit: V
```

## Scenario Steps

```yaml
- atMs: 0
  event: powerOn
- atMs: 5
  injectFault: spiTimeout
- atMs: 10
  readRegister:
    name: STATUS
```

## Observed Behavior

```yaml
finalState: INIT
signals:
  voltage: 12.0
reads:
- register: STATUS
  response: timeout
registerFields:
  STATUS:
    ready: 0
    undervoltageFault: 0
  CONTROL:
    enableMonitoring: 0
  FAULT:
    undervoltage: 0
    spiTimeout: 1
  VOLTAGE:
    volts: 12
  RESET_CAUSE:
    powerOnReset: 1
```

## Expected Behavior

```yaml
finalState: INIT
registers:
  FAULT.spiTimeout: 1
reads:
- register: STATUS
  response: timeout
```

## Pass/Fail Result

- PASS finalState: actual INIT, expected INIT
- PASS FAULT.spiTimeout: actual 1, expected 1
- PASS read[0]: actual {'register': 'STATUS', 'response': 'timeout'}, expected {'register': 'STATUS', 'response': 'timeout'}

## Runtime Trace

- event powerOn
- state RESET->INIT on powerOn
- fault injected spiTimeout
- read STATUS: timeout

## Register Reads

- STATUS: timeout
