model ToyThresholdIndicator
  // Generated from Mermaid-like MBD markup.
  // Readable Modelica handoff artifact; not a complete physical model.
  parameter Real limit = 10;
  input Real sampleValue(start=0);
  output Boolean active(start=false);
  discrete Integer state;
equation
  // State placeholders generated from markup:
  // 0: IDLE
  // 1: ACTIVE
  // Functional decomposition handoff summary:
  // Control rule handoff summary:
  // priority 1000 activate: from * when sampleValue >= limit then state=ACTIVE, active=true trace SIMPLE-001, SIMPLE-003 scenarios above_limit
  // priority 1001 clear: from * when sampleValue < limit then state=IDLE, active=false trace SIMPLE-002, SIMPLE-003
end ToyThresholdIndicator;
