model ToyDualSignalCoordinator
  // Generated from Mermaid-like MBD markup.
  // Readable Modelica handoff artifact; not a complete physical model.
  input Boolean sideRequest(start=false);
  input Boolean mainWarningExpired(start=false);
  input Boolean clearanceExpired(start=false);
  input Boolean sideServed(start=false);
  input Boolean sideWarningExpired(start=false);
  output Boolean mainGreen(start=true);
  output Boolean mainYellow(start=false);
  output Boolean mainRed(start=false);
  output Boolean sideGreen(start=false);
  output Boolean sideYellow(start=false);
  output Boolean sideRed(start=true);
  discrete Integer state;
equation
  // State placeholders generated from markup:
  // 0: MAIN_GO_SIDE_STOP
  // 1: MAIN_WARN_SIDE_STOP
  // 2: ALL_STOP_BEFORE_SIDE
  // 3: MAIN_STOP_SIDE_GO
  // 4: MAIN_STOP_SIDE_WARN
  // 5: ALL_STOP_BEFORE_MAIN
  // Functional decomposition handoff summary:
  // function ToyCrossingCoordinator: owns MAIN_GO_SIDE_STOP, MAIN_WARN_SIDE_STOP, ALL_STOP_BEFORE_SIDE, MAIN_STOP_SIDE_GO, MAIN_STOP_SIDE_WARN, ALL_STOP_BEFORE_MAIN trace DSC-001, DSC-002, DSC-003, DSC-004, DSC-005, DSC-PRE-001, DSC-PRE-002 scenarios side_request_cycle
  // function MainSignalStateMachine: owns mainGreen, mainYellow, mainRed trace DSC-001, DSC-002, DSC-003, DSC-004, DSC-006, DSC-007 scenarios side_request_cycle
  // function SideSignalStateMachine: owns sideGreen, sideYellow, sideRed trace DSC-003, DSC-004, DSC-005, DSC-006, DSC-007 scenarios side_request_cycle
  // function InterlockMonitor: owns mainGreen, sideGreen trace DSC-006, DSC-PRE-001 scenarios side_request_cycle
  // Control rule handoff summary:
  // priority 10 request_side_prepare_main: owner ToyCrossingCoordinator from MAIN_GO_SIDE_STOP when sideRequest == true then state=MAIN_WARN_SIDE_STOP, mainGreen=false, mainYellow=true, mainRed=false, sideGreen=false, sideYellow=false, sideRed=true trace DSC-002, DSC-006, DSC-007 scenarios side_request_cycle
  // priority 20 main_warning_to_all_stop: owner ToyCrossingCoordinator from MAIN_WARN_SIDE_STOP when mainWarningExpired == true then state=ALL_STOP_BEFORE_SIDE, mainGreen=false, mainYellow=false, mainRed=true, sideGreen=false, sideYellow=false, sideRed=true trace DSC-003, DSC-006, DSC-007 scenarios side_request_cycle
  // priority 30 clearance_to_side_go: owner ToyCrossingCoordinator from ALL_STOP_BEFORE_SIDE when clearanceExpired == true then state=MAIN_STOP_SIDE_GO, mainGreen=false, mainYellow=false, mainRed=true, sideGreen=true, sideYellow=false, sideRed=false trace DSC-004, DSC-006, DSC-007 scenarios side_request_cycle
  // priority 40 side_service_prepare_main: owner ToyCrossingCoordinator from MAIN_STOP_SIDE_GO when sideServed == true then state=MAIN_STOP_SIDE_WARN, mainGreen=false, mainYellow=false, mainRed=true, sideGreen=false, sideYellow=true, sideRed=false trace DSC-005, DSC-006, DSC-007 scenarios side_request_cycle
  // priority 50 side_warning_to_all_stop: owner ToyCrossingCoordinator from MAIN_STOP_SIDE_WARN when sideWarningExpired == true then state=ALL_STOP_BEFORE_MAIN, mainGreen=false, mainYellow=false, mainRed=true, sideGreen=false, sideYellow=false, sideRed=true trace DSC-003, DSC-005, DSC-006, DSC-007 scenarios side_request_cycle
  // priority 60 clearance_to_main_go: owner ToyCrossingCoordinator from ALL_STOP_BEFORE_MAIN when clearanceExpired == true then state=MAIN_GO_SIDE_STOP, mainGreen=true, mainYellow=false, mainRed=false, sideGreen=false, sideYellow=false, sideRed=true trace DSC-001, DSC-005, DSC-006, DSC-007 scenarios side_request_cycle
end ToyDualSignalCoordinator;
