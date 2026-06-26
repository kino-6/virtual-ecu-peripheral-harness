# Toy Dual Signal Coordination

Fictional multi-component MBD authoring sample for reviewing coordination
between two signal state-machine roles. The local preview uses one coordinated
mode state; external MBD tools must verify separated chart/message semantics.

```mbd-component
component ToyDualSignalCoordinator
trace DSC-001 DSC-002 DSC-003 DSC-004 DSC-005 DSC-006 DSC-007 DSC-PRE-001 DSC-PRE-002
bus virtual mode=preview wordBits=16

port in sideRequest: bool = false
port in mainWarningExpired: bool = false
port in clearanceExpired: bool = false
port in sideServed: bool = false
port in sideWarningExpired: bool = false
port out mainGreen: bool = true
port out mainYellow: bool = false
port out mainRed: bool = false
port out sideGreen: bool = false
port out sideYellow: bool = false
port out sideRed: bool = true
```

```mbd-registers
INPUT_STATUS 0x01 ro 8
  bit 0 sideRequest reset=0
  bit 1 mainWarningExpired reset=0
  bit 2 clearanceExpired reset=0
  bit 3 sideServed reset=0
  bit 4 sideWarningExpired reset=0

SIGNAL_COMMAND 0x10 rw 16
  bit 0 mainGreen reset=1
  bit 1 mainYellow reset=0
  bit 2 mainRed reset=0
  bit 8 sideGreen reset=0
  bit 9 sideYellow reset=0
  bit 10 sideRed reset=1
```

```mbd-state
MAIN_GO_SIDE_STOP --> MAIN_WARN_SIDE_STOP: sideRequest == true
MAIN_WARN_SIDE_STOP --> ALL_STOP_BEFORE_SIDE: mainWarningExpired == true
ALL_STOP_BEFORE_SIDE --> MAIN_STOP_SIDE_GO: clearanceExpired == true
MAIN_STOP_SIDE_GO --> MAIN_STOP_SIDE_WARN: sideServed == true
MAIN_STOP_SIDE_WARN --> ALL_STOP_BEFORE_MAIN: sideWarningExpired == true
ALL_STOP_BEFORE_MAIN --> MAIN_GO_SIDE_STOP: clearanceExpired == true
```

```mbd-decomposition
system ToyDualSignalCoordination: note=Review as coordinator plus two signal state-machine roles; preview state is the coordinated mode projection.
function ToyCrossingCoordinator: responsibility=Own request arbitration and all-stop clearance before changing directional grants; owns=MAIN_GO_SIDE_STOP,MAIN_WARN_SIDE_STOP,ALL_STOP_BEFORE_SIDE,MAIN_STOP_SIDE_GO,MAIN_STOP_SIDE_WARN,ALL_STOP_BEFORE_MAIN; inputs=sideRequest,mainWarningExpired,clearanceExpired,sideServed,sideWarningExpired; outputs=state; trace=DSC-001,DSC-002,DSC-003,DSC-004,DSC-005,DSC-PRE-001,DSC-PRE-002; scenarios=side_request_cycle
function MainSignalStateMachine: responsibility=Map coordinated modes to the main signal go warn stop outputs; owns=mainGreen,mainYellow,mainRed; inputs=state; outputs=mainGreen,mainYellow,mainRed; trace=DSC-001,DSC-002,DSC-003,DSC-004,DSC-006,DSC-007; scenarios=side_request_cycle
function SideSignalStateMachine: responsibility=Map coordinated modes to the side signal stop go warn outputs; owns=sideGreen,sideYellow,sideRed; inputs=state; outputs=sideGreen,sideYellow,sideRed; trace=DSC-003,DSC-004,DSC-005,DSC-006,DSC-007; scenarios=side_request_cycle
function InterlockMonitor: responsibility=Expose the no-both-green invariant as preview evidence; owns=mainGreen,sideGreen; inputs=mainGreen,sideGreen; outputs=ScenarioReport.passFailResult; trace=DSC-006,DSC-PRE-001; scenarios=side_request_cycle
```

```mbd-flow
ToySideRequestSource.sideRequest -> ToyCrossingCoordinator.sideRequest: side grant request trace DSC-002 DSC-004
ToyMainWarningTimer.expired -> ToyCrossingCoordinator.mainWarningExpired: main warning completion trace DSC-002 DSC-003
ToyClearanceTimer.expired -> ToyCrossingCoordinator.clearanceExpired: all-stop clearance completion trace DSC-003 DSC-004 DSC-005
ToySideServiceSource.sideServed -> ToyCrossingCoordinator.sideServed: side service completion trace DSC-005
ToySideWarningTimer.expired -> ToyCrossingCoordinator.sideWarningExpired: side warning completion trace DSC-005
ToyCrossingCoordinator.state -> MainSignalStateMachine.state: coordinated mode projection trace DSC-001 DSC-002 DSC-003 DSC-004 DSC-007
ToyCrossingCoordinator.state -> SideSignalStateMachine.state: coordinated mode projection trace DSC-003 DSC-004 DSC-005 DSC-007
ToyDualSignalCoordinator.mainGreen -> ScenarioReport.observedBehavior: main green evidence trace DSC-001 DSC-006
ToyDualSignalCoordinator.mainYellow -> ScenarioReport.observedBehavior: main warning evidence trace DSC-002
ToyDualSignalCoordinator.mainRed -> ScenarioReport.observedBehavior: main stop evidence trace DSC-003 DSC-004
ToyDualSignalCoordinator.sideGreen -> ScenarioReport.observedBehavior: side green evidence trace DSC-004 DSC-006
ToyDualSignalCoordinator.sideYellow -> ScenarioReport.observedBehavior: side warning evidence trace DSC-005
ToyDualSignalCoordinator.sideRed -> ScenarioReport.observedBehavior: side stop evidence trace DSC-001 DSC-002 DSC-003
```

```mbd-control
priority 10 rule request_side_prepare_main: owner ToyCrossingCoordinator from MAIN_GO_SIDE_STOP when sideRequest == true then state=MAIN_WARN_SIDE_STOP, mainGreen=false, mainYellow=true, mainRed=false, sideGreen=false, sideYellow=false, sideRed=true trace DSC-002 DSC-006 DSC-007 scenarios side_request_cycle
priority 20 rule main_warning_to_all_stop: owner ToyCrossingCoordinator from MAIN_WARN_SIDE_STOP when mainWarningExpired == true then state=ALL_STOP_BEFORE_SIDE, mainGreen=false, mainYellow=false, mainRed=true, sideGreen=false, sideYellow=false, sideRed=true trace DSC-003 DSC-006 DSC-007 scenarios side_request_cycle
priority 30 rule clearance_to_side_go: owner ToyCrossingCoordinator from ALL_STOP_BEFORE_SIDE when clearanceExpired == true then state=MAIN_STOP_SIDE_GO, mainGreen=false, mainYellow=false, mainRed=true, sideGreen=true, sideYellow=false, sideRed=false trace DSC-004 DSC-006 DSC-007 scenarios side_request_cycle
priority 40 rule side_service_prepare_main: owner ToyCrossingCoordinator from MAIN_STOP_SIDE_GO when sideServed == true then state=MAIN_STOP_SIDE_WARN, mainGreen=false, mainYellow=false, mainRed=true, sideGreen=false, sideYellow=true, sideRed=false trace DSC-005 DSC-006 DSC-007 scenarios side_request_cycle
priority 50 rule side_warning_to_all_stop: owner ToyCrossingCoordinator from MAIN_STOP_SIDE_WARN when sideWarningExpired == true then state=ALL_STOP_BEFORE_MAIN, mainGreen=false, mainYellow=false, mainRed=true, sideGreen=false, sideYellow=false, sideRed=true trace DSC-003 DSC-005 DSC-006 DSC-007 scenarios side_request_cycle
priority 60 rule clearance_to_main_go: owner ToyCrossingCoordinator from ALL_STOP_BEFORE_MAIN when clearanceExpired == true then state=MAIN_GO_SIDE_STOP, mainGreen=true, mainYellow=false, mainRed=false, sideGreen=false, sideYellow=false, sideRed=true trace DSC-001 DSC-005 DSC-006 DSC-007 scenarios side_request_cycle
```

```mbd-harness
device ToySideRequestSource role=stimulus boundary=virtual_ic trace DSC-002 DSC-004 DSC-PRE-001
device ToyMainWarningTimer role=timer boundary=virtual_ic trace DSC-002 DSC-003 DSC-PRE-001
device ToyClearanceTimer role=timer boundary=virtual_ic trace DSC-003 DSC-004 DSC-005 DSC-PRE-001
device ToySideServiceSource role=stimulus boundary=virtual_ic trace DSC-005 DSC-PRE-001
device ToySideWarningTimer role=timer boundary=virtual_ic trace DSC-005 DSC-PRE-001
ecu ToyDualSignalCoordinator role=controller boundary=hal trace DSC-001 DSC-002 DSC-003 DSC-004 DSC-005 DSC-006 DSC-007
```
