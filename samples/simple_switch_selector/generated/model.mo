model ToySwitchSelector
  // Generated from Mermaid-like MBD markup.
  // Readable Modelica handoff artifact; not a complete physical model.
  parameter Real highValue = 100;
  parameter Real lowValue = 25;
  input Boolean selectHigh(start=false);
  output Real selectedValue(start=25);
  discrete Integer state;
equation
  // State placeholders generated from markup:
  // Functional decomposition handoff summary:
  // function SwitchSelector: owns selectedValue trace SWS-001, SWS-002, SWS-003, SWS-004 scenarios select_high
  // Control rule handoff summary:
  // priority 10 select_high_value: owner SwitchSelector from * when selectHigh == true then selectedValue=highValue trace SWS-001, SWS-003, SWS-004 scenarios select_high
  // priority 20 select_low_value: owner SwitchSelector from * when selectHigh != true then selectedValue=lowValue trace SWS-002, SWS-003, SWS-004 scenarios select_high
end ToySwitchSelector;
