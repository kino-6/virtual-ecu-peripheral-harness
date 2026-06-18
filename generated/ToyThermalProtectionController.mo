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
  // Control rule handoff summary:
  // priority 10 recoverFromLatch: from FAULT_LATCHED when temperatureValid == true and invalidDebounced == false and recoveryRequest == true then state=IDLE, fanDuty=0, deratingCommand=0, diagnosticFault=false, safeCommandActive=false trace SYS-008, HAR-006 scenarios thermal_protection_recovery
  // priority 20 faultLatch: from * when invalidDebounced == true then state=FAULT_LATCHED, fanDuty=safeDuty, deratingCommand=0, diagnosticFault=true, safeCommandActive=true trace SYS-007, SYS-006, HAR-004 scenarios thermal_protection_fault_latch, thermal_protection_recovery
  // priority 30 holdLatchedFault: from FAULT_LATCHED when always then state=FAULT_LATCHED, fanDuty=safeDuty, deratingCommand=0, diagnosticFault=true, safeCommandActive=true trace SYS-007, HAR-004 scenarios thermal_protection_fault_latch, thermal_protection_recovery
  // priority 40 sensorInvalid: from * when temperatureValid == false then state=SENSOR_FAULT, fanDuty=safeDuty, deratingCommand=0, diagnosticFault=true, safeCommandActive=true trace SYS-006, HAR-004 scenarios thermal_protection_fault_latch, thermal_protection_recovery
  // priority 50 derating: from * when temperatureC >= deratingEntryThreshold then state=DERATING, fanDuty=deratingFanDuty, deratingCommand=deratingLimit, diagnosticFault=false, safeCommandActive=false trace SYS-005, SYS-002, HAR-004 scenarios thermal_protection_derating, thermal_protection_recovery
  // priority 60 highCooling: from * when temperatureC >= coolingOnThreshold then state=COOLING, fanDuty=coolingDuty, deratingCommand=0, diagnosticFault=false, safeCommandActive=false trace SYS-003, SYS-002, HAR-004 scenarios thermal_protection_normal
  // priority 70 lowCooling: from * when temperatureC <= coolingOffThreshold then state=IDLE, fanDuty=0, deratingCommand=0, diagnosticFault=false, safeCommandActive=false trace SYS-004, HAR-004 scenarios thermal_protection_boundary
end ToyThermalProtectionController;
