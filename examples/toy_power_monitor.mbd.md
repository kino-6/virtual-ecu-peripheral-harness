# Toy Power Monitor IC

Fictional virtual ECU peripheral authoring example. This document is synthetic
and does not describe a real IC, datasheet, ECU, company, or production project.

```mbd-component
component ToyPowerMonitorIC
bus spi mode=0 wordBits=8
parameter undervoltageThreshold: V = 7.0

port in voltage: V = 12.0
port out ready: bool
port out fault: bool
```

```mbd-registers
STATUS 0x01 ro 8
  bit 7 ready reset=0
  bit 0 undervoltageFault reset=0

CONTROL 0x02 rw 8
  bit 0 enable reset=0

FAULT 0x03 ro 8
  bit 0 undervoltage reset=0
  bit 1 spiTimeout reset=0

VOLTAGE 0x04 ro 8
  bits 7..0 volts reset=12
```

```mbd-state
RESET --> INIT: powerOn
INIT --> NORMAL: initSequenceOk
NORMAL --> FAULT_LATCHED: voltage < undervoltageThreshold
FAULT_LATCHED --> RESET: clearFault
```

```mbd-flow
ECU_App.control_task -> HAL_SPI: write CONTROL.enable
HAL_SPI -> ToyPowerMonitorIC.CONTROL: spi write
ToyPowerMonitorIC.STATUS -> HAL_SPI: spi read
HAL_SPI -> ECU_App.diagnostics: STATUS.ready, STATUS.undervoltageFault
ToyPowerMonitorIC.ready -> ECU_App.diagnostics: ready signal
ToyPowerMonitorIC.fault -> ECU_App.diagnostics: fault signal
```
