# ToyPowerMonitorIC

> Generated artifact. This component is fictional and is provided for synthetic examples only.
> Canonical source: Textual MBD YAML. Regenerate this file instead of editing it by hand.

## Overview

Fictional power monitor IC for virtual ECU harness demos.

## Bus Interface

- Type: `spi`
- Mode: `0`
- Word bits: `8`

## Register Map

| Register | Address | Width | Access | Description |
| --- | ---: | ---: | --- | --- |
| STATUS | 0x01 | 8 | ro | Read-only status flags. |
| CONTROL | 0x02 | 8 | rw | Control bits for starting monitoring. |
| FAULT | 0x03 | 8 | ro | Latched fault flags. |
| VOLTAGE | 0x04 | 8 | ro | Quantized voltage in volts for demo purposes. |
| RESET_CAUSE | 0x05 | 8 | ro | Reset cause flags. |

## Fields

### STATUS

| Field | Bits | Reset |
| --- | --- | ---: |
| ready | 7 | 0 |
| undervoltageFault | 0 | 0 |

### CONTROL

| Field | Bits | Reset |
| --- | --- | ---: |
| enableMonitoring | 0 | 0 |

### FAULT

| Field | Bits | Reset |
| --- | --- | ---: |
| undervoltage | 0 | 0 |
| spiTimeout | 1 | 0 |

### VOLTAGE

| Field | Bits | Reset |
| --- | --- | ---: |
| volts | 7, 6, 5, 4, 3, 2, 1, 0 | 12 |

### RESET_CAUSE

| Field | Bits | Reset |
| --- | --- | ---: |
| powerOnReset | 0 | 1 |

## States And Transitions

- Initial: `RESET`
- State: `RESET`
- State: `INIT`
- State: `NORMAL`
- State: `FAULT_LATCHED`

- `RESET` -> `INIT` when `powerOn`
- `INIT` -> `NORMAL` when `initSequenceOk`
- `NORMAL` -> `FAULT_LATCHED` when `voltage < undervoltageThreshold`

## Signals

- Input `voltage` (V), default `12.0`
- Output `ready` (bool)

## Functional Blocks

### `VoltageInput`

- Kind: `signalSource`
- Description: Scenario-controlled input signal source.
- Outputs: `voltage: real` (voltage)

### `ThresholdParameter`

- Kind: `parameter`
- Description: Textual threshold parameter from the YAML model.
- Outputs: `threshold: real` (undervoltageThreshold)

### `UndervoltageComparator`

- Kind: `comparator`
- Description: Compares voltage against the undervoltage threshold.
- Inputs: `voltage: real` (voltage), `threshold: real` (undervoltageThreshold)
- Outputs: `undervoltageDetected: bool` (undervoltageDetected)

### `FaultLatch`

- Kind: `latch`
- Description: Latches undervoltage into the fault state.
- Inputs: `set: bool` (undervoltageDetected)
- Outputs: `faultLatched: bool` (faultLatched)

### `ReadyLogic`

- Kind: `logic`
- Description: Produces ready when initialization is complete and no stuck-ready fault is active.
- Inputs: `stateNormal: bool` (state == NORMAL), `stuckReady: bool` (stuckReadyBit)
- Outputs: `ready: bool` (ready)

### `RegisterMap`

- Kind: `registerMap`
- Description: Maps internal signals to externally readable registers.
- Inputs: `ready: bool` (ready), `undervoltageFault: bool` (faultLatched), `voltage: real` (voltage)
- Outputs: `STATUS.ready: bit` (STATUS.ready), `STATUS.undervoltageFault: bit` (STATUS.undervoltageFault), `VOLTAGE.volts: uint8` (VOLTAGE.volts)

## Connections

- `VoltageInput.voltage` -> `UndervoltageComparator.voltage` via `voltage`
- `ThresholdParameter.threshold` -> `UndervoltageComparator.threshold` via `undervoltageThreshold`
- `UndervoltageComparator.undervoltageDetected` -> `FaultLatch.set` via `undervoltageDetected`
- `FaultLatch.faultLatched` -> `RegisterMap.undervoltageFault` via `faultLatched`
- `ReadyLogic.ready` -> `RegisterMap.ready` via `ready`
- `VoltageInput.voltage` -> `RegisterMap.voltage` via `voltage`

## Faults

- `undervoltage`: set STATUS.undervoltageFault and transition to FAULT_LATCHED
- `spiTimeout`: return no response for SPI transaction
- `stuckReadyBit`: keep STATUS.ready fixed at 0

## Timing

- `tickMs`: `1`
