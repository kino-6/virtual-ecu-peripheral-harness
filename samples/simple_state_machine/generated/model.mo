model ToyStateMachine
  // Generated from Mermaid-like MBD markup.
  // Readable Modelica handoff artifact; not a complete physical model.
  input Boolean startCommand(start=false);
  input Boolean finishCommand(start=false);
  input Boolean resetCommand(start=false);
  output Boolean busy(start=false);
  output Boolean complete(start=false);
  discrete Integer state;
equation
  // State placeholders generated from markup:
  // 0: IDLE
  // 1: RUNNING
  // 2: DONE
  // Functional decomposition handoff summary:
  // function ToyStateController: owns IDLE, RUNNING, DONE, busy, complete trace SM-001, SM-002, SM-003, SM-004 scenarios full_cycle
  // Control rule handoff summary:
  // priority 10 start_running: owner ToyStateController from IDLE when startCommand == true then state=RUNNING, busy=true, complete=false trace SM-001, SM-004 scenarios full_cycle
  // priority 20 finish_done: owner ToyStateController from RUNNING when finishCommand == true then state=DONE, busy=false, complete=true trace SM-002, SM-004 scenarios full_cycle
  // priority 30 reset_idle: owner ToyStateController from DONE when resetCommand == true then state=IDLE, busy=false, complete=false trace SM-003, SM-004 scenarios full_cycle
end ToyStateMachine;
