# Toy Thermal Protection Controller

Fictional requirements-traceable MBD authoring example. This document is the
public MBD source for the complete business-process demo. It is synthetic and
does not describe a real IC, datasheet, ECU, company, production project, safety
case, or certified code generator.

```mbd-component
component ToyThermalProtectionController
trace STK-001 STK-002 STK-003 STK-004 STK-005 STK-006 STK-007 SYS-001 SYS-002 SYS-003 SYS-004 SYS-005 SYS-006 SYS-007 SYS-008 SYS-009 SWE-001 SWE-002 SWE-003 SWE-004 SWE-005 ENG-001 ENG-002 ENG-003 ENG-004 ENG-005 ENG-006 HAR-001 HAR-002 HAR-003 HAR-004 HAR-006 HAR-007 CGEN-001 CGEN-002 CGEN-003 CGEN-004 CGEN-005
bus virtual mode=preview wordBits=16
parameter coolingOnThreshold: degC = 78
parameter coolingOffThreshold: degC = 68
parameter deratingEntryThreshold: degC = 94
parameter coolingDuty: percent = 70
parameter deratingFanDuty: percent = 95
parameter deratingLimit: percent = 45
parameter safeDuty: percent = 30

port in temperatureC: degC = 25
port in temperatureValid: bool = true
port in invalidDebounced: bool = false
port in recoveryRequest: bool = false
port out fanDuty: percent = 0
port out deratingCommand: percent = 0
port out diagnosticFault: bool = false
port out safeCommandActive: bool = false
```

```mbd-registers
TP_TEMP_STATUS 0x10 ro 16
  bit 15 valid reset=1
  bits 14..0 temperatureCode reset=25

TP_CONTROL_STATUS 0x20 ro 16
  bits 7..0 fanDutyMirror reset=0
  bit 8 deratingActive reset=0
  bit 9 safeCommandActive reset=0
  bit 10 diagnosticFault reset=0

TP_COMMAND 0x30 rw 16
  bits 7..0 fanDutyCommand reset=0
  bits 14..8 deratingCommand reset=0
  bit 15 commandValid reset=0
```

```mbd-state
RESET --> IDLE: temperatureValid == true
IDLE --> COOLING: temperatureC >= coolingOnThreshold
COOLING --> IDLE: temperatureC <= coolingOffThreshold
COOLING --> DERATING: temperatureC >= deratingEntryThreshold
DERATING --> COOLING: temperatureC < deratingEntryThreshold
IDLE --> SENSOR_FAULT: temperatureValid == false
COOLING --> SENSOR_FAULT: temperatureValid == false
DERATING --> SENSOR_FAULT: temperatureValid == false
SENSOR_FAULT --> FAULT_LATCHED: invalidDebounced == true
FAULT_LATCHED --> IDLE: recoveryRequest == true
```

```mbd-flow
ToyTempSensorIC.temperatureC -> HAL_SPI.read_temperature: virtual sensor sample trace SYS-001 HAR-001
ToyTempSensorIC.temperatureValid -> HAL_SPI.read_temperature: virtual validity sample trace SYS-001 SYS-006 HAR-001
ToyTempSensorIC.invalidDebounced -> ToyThermalProtectionController.invalidDebounced: preview debounce input trace SYS-007 ENG-002 HAR-003
HAL_SPI.read_temperature -> ToyThermalProtectionController.temperatureC: HAL temperature input trace SWE-004 HAR-002
ToyThermalProtectionController.fanDuty -> HAL_PWM.set_fan_duty: generated ECU fan command trace SYS-002 SWE-004 CGEN-003
ToyThermalProtectionController.deratingCommand -> HAL_LIMITER.set_derating: generated ECU derating command trace SYS-005 SWE-004 CGEN-003
HAL_PWM.set_fan_duty -> ToyFanDriverIC.dutyCommand: virtual actuator command trace SYS-002 HAR-001
HAL_LIMITER.set_derating -> ToyLoadLimiterIC.limitCommand: virtual load limiter command trace SYS-005 HAR-006
ToyThermalProtectionController.diagnosticFault -> ScenarioReport.observedBehavior: diagnostic observation trace SYS-006 SYS-007 HAR-004
```

```mbd-control
rule recoverFromLatch: when state == FAULT_LATCHED and temperatureValid == true and recoveryRequest == true then state=IDLE, fanDuty=0, deratingCommand=0, diagnosticFault=false, safeCommandActive=false trace SYS-008 HAR-006
rule faultLatch: when invalidDebounced == true then state=FAULT_LATCHED, fanDuty=safeDuty, deratingCommand=0, diagnosticFault=true, safeCommandActive=true trace SYS-007 SYS-006 HAR-004
rule holdLatchedFault: when state == FAULT_LATCHED then state=FAULT_LATCHED, fanDuty=safeDuty, deratingCommand=0, diagnosticFault=true, safeCommandActive=true trace SYS-007 SYS-008 HAR-004
rule sensorInvalid: when temperatureValid == false then state=SENSOR_FAULT, fanDuty=safeDuty, deratingCommand=0, diagnosticFault=true, safeCommandActive=true trace SYS-006 HAR-004
rule derating: when temperatureC >= deratingEntryThreshold then state=DERATING, fanDuty=deratingFanDuty, deratingCommand=deratingLimit, diagnosticFault=false, safeCommandActive=false trace SYS-005 SYS-002 HAR-004
rule highCooling: when temperatureC >= coolingOnThreshold then state=COOLING, fanDuty=coolingDuty, deratingCommand=0, diagnosticFault=false, safeCommandActive=false trace SYS-003 SYS-002 HAR-004
rule lowCooling: when temperatureC <= coolingOffThreshold then state=IDLE, fanDuty=0, deratingCommand=0, diagnosticFault=false, safeCommandActive=false trace SYS-004 HAR-004
```

```mbd-harness
device ToyTempSensorIC role=sensor boundary=virtual_ic trace HAR-001 SYS-001 SYS-006 SYS-007
device ToyFanDriverIC role=actuator boundary=virtual_ic trace HAR-001 SYS-002
device ToyLoadLimiterIC role=actuator boundary=virtual_ic trace HAR-006 SYS-005
ecu ToyThermalProtectionController role=controller boundary=hal trace HAR-002 SWE-004 CGEN-003
```

