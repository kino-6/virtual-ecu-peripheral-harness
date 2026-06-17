model ToyPowerMonitor
  // Generated from fictional Textual MBD model ToyPowerMonitorIC.
  // Canonical source: Textual MBD YAML. Regenerate instead of editing as source.
  parameter Real undervoltageThreshold = 7.0;
  input Real voltage(start=12.0) "V";
  output Boolean ready;
  discrete Integer state;
equation
  // State encoding:
  // 0: RESET
  // 1: INIT
  // 2: NORMAL
  // 3: FAULT_LATCHED
  ready = state == 2;
end ToyPowerMonitor;
