model ToyThermalProtectionController
  // Generated from Mermaid-like MBD markup.
  // Readable Modelica handoff artifact; not a complete physical model.
  parameter Real coolingOnThreshold = 78;
  parameter Real coolingOffThreshold = 68;
  parameter Real deratingEntryThreshold = 94;
  parameter Real coolingDuty = 70;
  parameter Real deratingFanDuty = 95;
  parameter Real deratingLimit = 45;
  parameter Real safeDuty = 30;
  input Real temperatureC(start=25);
  input Boolean temperatureValid(start=true);
  input Boolean invalidDebounced(start=false);
  input Boolean recoveryRequest(start=false);
  output Real fanDuty(start=0);
  output Real deratingCommand(start=0);
  output Boolean diagnosticFault(start=false);
  output Boolean safeCommandActive(start=false);
  discrete Integer state;
equation
  // State placeholders generated from markup:
  // 0: RESET
  // 1: IDLE
  // 2: COOLING
  // 3: DERATING
  // 4: SENSOR_FAULT
  // 5: FAULT_LATCHED
  // Functional decomposition handoff summary:
  // function SensorInterface: owns temperatureC, temperatureValid trace SYS-001, HAR-001, HAR-002 scenarios thermal_protection_normal, thermal_protection_derating, thermal_protection_fault_latch, thermal_protection_recovery
  // function ValidityDebounceManager: owns invalidDebounced trace SYS-006, SYS-007, ENG-002, HAR-003 scenarios thermal_protection_fault_latch, thermal_protection_recovery
  // function ThermalStateManager: owns IDLE, COOLING, DERATING trace SYS-003, SYS-004, SYS-005 scenarios thermal_protection_normal, thermal_protection_boundary, thermal_protection_derating
  // function CoolingCommandManager: owns fanDuty trace SYS-002, SYS-003, SYS-004 scenarios thermal_protection_normal, thermal_protection_boundary
  // function DeratingCommandManager: owns deratingCommand trace SYS-005 scenarios thermal_protection_derating
  // function FaultLatchRecoveryManager: owns SENSOR_FAULT, FAULT_LATCHED, recoveryRequest trace SYS-006, SYS-007, SYS-008 scenarios thermal_protection_fault_latch, thermal_protection_recovery
  // function OutputMappingDiagnostics: owns safeCommandActive, diagnosticFault trace SYS-002, SYS-006, SYS-009, CGEN-003, HAR-004 scenarios thermal_protection_normal, thermal_protection_boundary, thermal_protection_derating, thermal_protection_fault_latch, thermal_protection_recovery
  // Control rule handoff summary:
  // priority 10 recoverFromLatch: owner FaultLatchRecoveryManager from FAULT_LATCHED when temperatureValid == true and invalidDebounced == false and recoveryRequest == true then state=IDLE, fanDuty=0, deratingCommand=0, diagnosticFault=false, safeCommandActive=false trace SYS-008, HAR-006 scenarios thermal_protection_recovery
  // priority 20 faultLatch: owner FaultLatchRecoveryManager from * when invalidDebounced == true then state=FAULT_LATCHED, fanDuty=safeDuty, deratingCommand=0, diagnosticFault=true, safeCommandActive=true trace SYS-007, SYS-006, HAR-004 scenarios thermal_protection_fault_latch, thermal_protection_recovery
  // priority 30 holdLatchedFault: owner FaultLatchRecoveryManager from FAULT_LATCHED when always then state=FAULT_LATCHED, fanDuty=safeDuty, deratingCommand=0, diagnosticFault=true, safeCommandActive=true trace SYS-007, HAR-004 scenarios thermal_protection_fault_latch, thermal_protection_recovery
  // priority 40 sensorInvalid: owner FaultLatchRecoveryManager from * when temperatureValid == false then state=SENSOR_FAULT, fanDuty=safeDuty, deratingCommand=0, diagnosticFault=true, safeCommandActive=true trace SYS-006, HAR-004 scenarios thermal_protection_fault_latch, thermal_protection_recovery
  // priority 50 derating: owner DeratingCommandManager from * when temperatureC >= deratingEntryThreshold then state=DERATING, fanDuty=deratingFanDuty, deratingCommand=deratingLimit, diagnosticFault=false, safeCommandActive=false trace SYS-005, SYS-002, HAR-004 scenarios thermal_protection_derating, thermal_protection_recovery
  // priority 60 highCooling: owner CoolingCommandManager from * when temperatureC >= coolingOnThreshold then state=COOLING, fanDuty=coolingDuty, deratingCommand=0, diagnosticFault=false, safeCommandActive=false trace SYS-003, SYS-002, HAR-004 scenarios thermal_protection_normal
  // priority 70 lowCooling: owner CoolingCommandManager from * when temperatureC <= coolingOffThreshold then state=IDLE, fanDuty=0, deratingCommand=0, diagnosticFault=false, safeCommandActive=false trace SYS-004, HAR-004 scenarios thermal_protection_boundary
end ToyThermalProtectionController;
