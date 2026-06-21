model ToyRelayHysteresis
  // Generated from Mermaid-like MBD markup.
  // Readable Modelica handoff artifact; not a complete physical model.
  parameter Real onThreshold = 70;
  parameter Real offThreshold = 30;
  input Real level(start=0);
  output Boolean active(start=false);
  discrete Integer state;
equation
  // State placeholders generated from markup:
  // 0: OFF
  // 1: ON
  // Functional decomposition handoff summary:
  // function ToyRelayController: owns OFF, ON, active trace RLY-001, RLY-002, RLY-003, RLY-004, RLY-005 scenarios hysteresis_cycle
  // Control rule handoff summary:
  // priority 10 off_to_on: owner ToyRelayController from OFF when level >= onThreshold then state=ON, active=true trace RLY-001, RLY-003, RLY-005 scenarios hysteresis_cycle
  // priority 20 on_to_off: owner ToyRelayController from ON when level <= offThreshold then state=OFF, active=false trace RLY-002, RLY-003, RLY-005 scenarios hysteresis_cycle
end ToyRelayHysteresis;
