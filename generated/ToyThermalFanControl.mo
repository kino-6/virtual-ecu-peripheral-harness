model ToyThermalFanController
  // Generated from Mermaid-like MBD markup.
  // Readable Modelica handoff artifact; not a complete physical model.
  parameter Real fanOnThreshold = 75;
  parameter Real fanOffThreshold = 65;
  parameter Real coolingDuty = 80;
  parameter Real safeDuty = 35;
  input Real temperatureC(start=25);
  input Boolean temperatureValid(start=true);
  output Real fanDuty(start=0);
  output Boolean fault(start=false);
  discrete Integer state;
equation
  // State placeholders generated from markup:
  // 0: RESET
  // 1: IDLE
  // 2: COOLING
  // 3: FAULT
  // Control rule handoff summary:
  // priority 1000 sensorFault: from * when temperatureValid == false then state=FAULT, fanDuty=safeDuty, fault=true trace SYS-005, HAR-004
  // priority 1001 highTemperature: from * when temperatureC >= fanOnThreshold then state=COOLING, fanDuty=coolingDuty, fault=false trace SYS-003, SYS-006
  // priority 1002 lowTemperature: from * when temperatureC <= fanOffThreshold then state=IDLE, fanDuty=0, fault=false trace SYS-004, SYS-006
end ToyThermalFanController;
