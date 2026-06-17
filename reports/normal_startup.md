# Scenario Report

- Scenario: `normal_startup`
- Result: **PASS**
- Final state: `NORMAL`

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
- atMs: 10
  writeRegister:
    name: CONTROL
    value: 1
- atMs: 15
  readRegister:
    name: STATUS
```

## Observed Behavior

```yaml
finalState: NORMAL
signals:
  voltage: 12.0
reads:
- register: STATUS
  response: 128
registerFields:
  STATUS:
    ready: 1
    undervoltageFault: 0
  CONTROL:
    enableMonitoring: 1
  FAULT:
    undervoltage: 0
    spiTimeout: 0
  VOLTAGE:
    volts: 12
  RESET_CAUSE:
    powerOnReset: 1
```

## Expected Behavior

```yaml
finalState: NORMAL
registers:
  STATUS.ready: 1
  STATUS.undervoltageFault: 0
reads:
- register: STATUS
  response: 128
```

## Pass/Fail Result

- PASS finalState: actual NORMAL, expected NORMAL
- PASS STATUS.ready: actual 1, expected 1
- PASS STATUS.undervoltageFault: actual 0, expected 0
- PASS read[0]: actual {'register': 'STATUS', 'response': 128}, expected {'register': 'STATUS', 'response': 128}

## Runtime Trace

- event powerOn
- state RESET->INIT on powerOn
- write CONTROL: 0x01
- event initSequenceOk
- state INIT->NORMAL on initSequenceOk
- read STATUS: 0x80

## Register Reads

- STATUS: 128
