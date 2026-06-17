# Scenario Report

- Scenario: `undervoltage_fault`
- Result: **PASS**
- Final state: `FAULT_LATCHED`

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
- atMs: 20
  setSignal:
    name: voltage
    value: 6.5
- atMs: 25
  readRegister:
    name: STATUS
```

## Observed Behavior

```yaml
finalState: FAULT_LATCHED
signals:
  voltage: 6.5
reads:
- register: STATUS
  response: 1
registerFields:
  STATUS:
    ready: 0
    undervoltageFault: 1
  CONTROL:
    enableMonitoring: 1
  FAULT:
    undervoltage: 1
    spiTimeout: 0
  VOLTAGE:
    volts: 6
  RESET_CAUSE:
    powerOnReset: 1
```

## Expected Behavior

```yaml
finalState: FAULT_LATCHED
registers:
  STATUS.undervoltageFault: 1
  FAULT.undervoltage: 1
```

## Pass/Fail Result

- PASS finalState: actual FAULT_LATCHED, expected FAULT_LATCHED
- PASS STATUS.undervoltageFault: actual 1, expected 1
- PASS FAULT.undervoltage: actual 1, expected 1

## Runtime Trace

- event powerOn
- state RESET->INIT on powerOn
- write CONTROL: 0x01
- event initSequenceOk
- state INIT->NORMAL on initSequenceOk
- signal voltage=6.5
- state NORMAL->FAULT_LATCHED on voltage < undervoltageThreshold
- read STATUS: 0x01

## Register Reads

- STATUS: 1
