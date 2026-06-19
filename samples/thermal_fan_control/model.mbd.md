# Toy Thermal Fan Control

Fictional requirements-traceable MBD authoring example. This document is
synthetic and does not describe a real IC, datasheet, ECU, company, production
project, safety case, or certified code generator.

```mbd-component
component ToyThermalFanController
trace STK-001 SYS-001 SYS-002 SYS-003 SYS-004 SYS-005 SYS-006 SWE-001 HAR-005
bus virtual mode=preview wordBits=16
parameter fanOnThreshold: degC = 75
parameter fanOffThreshold: degC = 65
parameter coolingDuty: percent = 80
parameter safeDuty: percent = 35

port in temperatureC: degC = 25
port in temperatureValid: bool = true
port out fanDuty: percent = 0
port out fault: bool = false
```

```mbd-registers
TEMP_STATUS 0x10 ro 16
  bit 15 valid reset=1
  bits 14..0 temperatureRaw reset=25

FAN_COMMAND 0x20 rw 16
  bits 7..0 dutyCommand reset=0
  bit 15 commandValid reset=0

FAULT_STATUS 0x30 ro 8
  bit 0 sensorInvalid reset=0
```

```mbd-state
RESET --> IDLE: powerOn
IDLE --> COOLING: temperatureC >= fanOnThreshold
COOLING --> IDLE: temperatureC <= fanOffThreshold
IDLE --> FAULT: temperatureValid == false
COOLING --> FAULT: temperatureValid == false
FAULT --> IDLE: temperatureValid == true
```

```mbd-flow
ToyTempSensorIC.temperatureC -> HAL_SPI.read_temperature: virtual sensor sample trace SYS-001 HAR-001
HAL_SPI.read_temperature -> ToyThermalFanController.temperatureC: HAL input trace SWE-004 HAR-002
ToyThermalFanController.fanDuty -> HAL_PWM.set_fan_duty: generated ECU command trace SYS-002 SWE-004
HAL_PWM.set_fan_duty -> ToyFanDriverIC.dutyCommand: virtual actuator command trace SYS-002 HAR-001
ToyThermalFanController.fault -> ScenarioReport.observedBehavior: fault observation trace SYS-006 HAR-004
```

```mbd-control
rule sensorFault: when temperatureValid == false then state=FAULT, fanDuty=safeDuty, fault=true trace SYS-005 HAR-004
rule highTemperature: when temperatureC >= fanOnThreshold then state=COOLING, fanDuty=coolingDuty, fault=false trace SYS-003 SYS-006
rule lowTemperature: when temperatureC <= fanOffThreshold then state=IDLE, fanDuty=0, fault=false trace SYS-004 SYS-006
```

```mbd-harness
device ToyTempSensorIC role=sensor boundary=virtual_ic trace HAR-001 SYS-001
device ToyFanDriverIC role=actuator boundary=virtual_ic trace HAR-001 SYS-002
ecu ToyThermalFanController role=controller boundary=hal trace HAR-002 SWE-004
```
