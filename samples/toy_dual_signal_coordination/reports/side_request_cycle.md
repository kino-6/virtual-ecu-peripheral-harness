# Scenario Report

- Scenario: `toy_dual_signal_side_request_cycle`
- Result: **PASS**
- Final state: `MAIN_GO_SIDE_STOP`
- Boundary: preview-only; not a certified code generation or verification backend.

## Model Inputs

```yaml
source: samples/toy_dual_signal_coordination/model.mbd.md
sourceFormat: mbd-markdown
component: ToyDualSignalCoordinator
parameters: {}
ports:
  sideRequest:
    direction: in
    type: bool
    default: 'false'
  mainWarningExpired:
    direction: in
    type: bool
    default: 'false'
  clearanceExpired:
    direction: in
    type: bool
    default: 'false'
  sideServed:
    direction: in
    type: bool
    default: 'false'
  sideWarningExpired:
    direction: in
    type: bool
    default: 'false'
  mainGreen:
    direction: out
    type: bool
    default: 'true'
  mainYellow:
    direction: out
    type: bool
    default: 'false'
  mainRed:
    direction: out
    type: bool
    default: 'false'
  sideGreen:
    direction: out
    type: bool
    default: 'false'
  sideYellow:
    direction: out
    type: bool
    default: 'false'
  sideRed:
    direction: out
    type: bool
    default: 'true'
controlRules:
- name: request_side_prepare_main
  owner: ToyCrossingCoordinator
  priority: 10
  stateScope: MAIN_GO_SIDE_STOP
  condition: sideRequest == true
  actions:
    state: MAIN_WARN_SIDE_STOP
    mainGreen: 'false'
    mainYellow: 'true'
    mainRed: 'false'
    sideGreen: 'false'
    sideYellow: 'false'
    sideRed: 'true'
  trace:
  - DSC-002
  - DSC-006
  - DSC-007
  scenarios:
  - side_request_cycle
- name: main_warning_to_all_stop
  owner: ToyCrossingCoordinator
  priority: 20
  stateScope: MAIN_WARN_SIDE_STOP
  condition: mainWarningExpired == true
  actions:
    state: ALL_STOP_BEFORE_SIDE
    mainGreen: 'false'
    mainYellow: 'false'
    mainRed: 'true'
    sideGreen: 'false'
    sideYellow: 'false'
    sideRed: 'true'
  trace:
  - DSC-003
  - DSC-006
  - DSC-007
  scenarios:
  - side_request_cycle
- name: clearance_to_side_go
  owner: ToyCrossingCoordinator
  priority: 30
  stateScope: ALL_STOP_BEFORE_SIDE
  condition: clearanceExpired == true
  actions:
    state: MAIN_STOP_SIDE_GO
    mainGreen: 'false'
    mainYellow: 'false'
    mainRed: 'true'
    sideGreen: 'true'
    sideYellow: 'false'
    sideRed: 'false'
  trace:
  - DSC-004
  - DSC-006
  - DSC-007
  scenarios:
  - side_request_cycle
- name: side_service_prepare_main
  owner: ToyCrossingCoordinator
  priority: 40
  stateScope: MAIN_STOP_SIDE_GO
  condition: sideServed == true
  actions:
    state: MAIN_STOP_SIDE_WARN
    mainGreen: 'false'
    mainYellow: 'false'
    mainRed: 'true'
    sideGreen: 'false'
    sideYellow: 'true'
    sideRed: 'false'
  trace:
  - DSC-005
  - DSC-006
  - DSC-007
  scenarios:
  - side_request_cycle
- name: side_warning_to_all_stop
  owner: ToyCrossingCoordinator
  priority: 50
  stateScope: MAIN_STOP_SIDE_WARN
  condition: sideWarningExpired == true
  actions:
    state: ALL_STOP_BEFORE_MAIN
    mainGreen: 'false'
    mainYellow: 'false'
    mainRed: 'true'
    sideGreen: 'false'
    sideYellow: 'false'
    sideRed: 'true'
  trace:
  - DSC-003
  - DSC-005
  - DSC-006
  - DSC-007
  scenarios:
  - side_request_cycle
- name: clearance_to_main_go
  owner: ToyCrossingCoordinator
  priority: 60
  stateScope: ALL_STOP_BEFORE_MAIN
  condition: clearanceExpired == true
  actions:
    state: MAIN_GO_SIDE_STOP
    mainGreen: 'true'
    mainYellow: 'false'
    mainRed: 'false'
    sideGreen: 'false'
    sideYellow: 'false'
    sideRed: 'true'
  trace:
  - DSC-001
  - DSC-005
  - DSC-006
  - DSC-007
  scenarios:
  - side_request_cycle
controlSelectionPolicy: lowest numeric priority wins after state scope and guard match
requirementRefs:
- DSC-001
- DSC-002
- DSC-003
- DSC-004
- DSC-005
- DSC-006
- DSC-007
- DSC-PRE-001
- DSC-PRE-002
previewSubsetAssumption: 'Preview subset assumption: discrete scenario steps represent
  the Simulink-compatible subset. Timing behavior such as sensor invalid debounce
  is represented by explicit scenario inputs and must be verified by external MBD/product-test
  infrastructure.'
```

## Functional Decomposition Evidence

```yaml
- name: ToyCrossingCoordinator
  responsibility: Own request arbitration and all-stop clearance before changing directional
    grants
  owns:
  - MAIN_GO_SIDE_STOP
  - MAIN_WARN_SIDE_STOP
  - ALL_STOP_BEFORE_SIDE
  - MAIN_STOP_SIDE_GO
  - MAIN_STOP_SIDE_WARN
  - ALL_STOP_BEFORE_MAIN
  inputs:
  - sideRequest
  - mainWarningExpired
  - clearanceExpired
  - sideServed
  - sideWarningExpired
  outputs:
  - state
  trace:
  - DSC-001
  - DSC-002
  - DSC-003
  - DSC-004
  - DSC-005
  - DSC-PRE-001
  - DSC-PRE-002
  scenarios:
  - side_request_cycle
- name: MainSignalStateMachine
  responsibility: Map coordinated modes to the main signal go warn stop outputs
  owns:
  - mainGreen
  - mainYellow
  - mainRed
  inputs:
  - state
  outputs:
  - mainGreen
  - mainYellow
  - mainRed
  trace:
  - DSC-001
  - DSC-002
  - DSC-003
  - DSC-004
  - DSC-006
  - DSC-007
  scenarios:
  - side_request_cycle
- name: SideSignalStateMachine
  responsibility: Map coordinated modes to the side signal stop go warn outputs
  owns:
  - sideGreen
  - sideYellow
  - sideRed
  inputs:
  - state
  outputs:
  - sideGreen
  - sideYellow
  - sideRed
  trace:
  - DSC-003
  - DSC-004
  - DSC-005
  - DSC-006
  - DSC-007
  scenarios:
  - side_request_cycle
- name: InterlockMonitor
  responsibility: Expose the no-both-green invariant as preview evidence
  owns:
  - mainGreen
  - sideGreen
  inputs:
  - mainGreen
  - sideGreen
  outputs:
  - ScenarioReport.passFailResult
  trace:
  - DSC-006
  - DSC-PRE-001
  scenarios:
  - side_request_cycle
```

## Traceability Matrix

```yaml
- requirement: DSC-001
  modelElements:
  - component:ToyDualSignalCoordinator
  - function:ToyCrossingCoordinator
  - function:MainSignalStateMachine
  - flow:ToyCrossingCoordinator.state->MainSignalStateMachine.state
  - flow:ToyDualSignalCoordinator.mainGreen->ScenarioReport.observedBehavior
  - flow:ToyDualSignalCoordinator.sideRed->ScenarioReport.observedBehavior
  - control:clearance_to_main_go
  - harness:ToyDualSignalCoordinator
  evidence:
  - samples/toy_dual_signal_coordination/model.mbd.md
  - samples/toy_dual_signal_coordination/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: DSC-002
  modelElements:
  - component:ToyDualSignalCoordinator
  - function:ToyCrossingCoordinator
  - function:MainSignalStateMachine
  - flow:ToySideRequestSource.sideRequest->ToyCrossingCoordinator.sideRequest
  - flow:ToyMainWarningTimer.expired->ToyCrossingCoordinator.mainWarningExpired
  - flow:ToyCrossingCoordinator.state->MainSignalStateMachine.state
  - flow:ToyDualSignalCoordinator.mainYellow->ScenarioReport.observedBehavior
  - flow:ToyDualSignalCoordinator.sideRed->ScenarioReport.observedBehavior
  - control:request_side_prepare_main
  - harness:ToySideRequestSource
  - harness:ToyMainWarningTimer
  - harness:ToyDualSignalCoordinator
  evidence:
  - samples/toy_dual_signal_coordination/model.mbd.md
  - samples/toy_dual_signal_coordination/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: DSC-003
  modelElements:
  - component:ToyDualSignalCoordinator
  - function:ToyCrossingCoordinator
  - function:MainSignalStateMachine
  - function:SideSignalStateMachine
  - flow:ToyMainWarningTimer.expired->ToyCrossingCoordinator.mainWarningExpired
  - flow:ToyClearanceTimer.expired->ToyCrossingCoordinator.clearanceExpired
  - flow:ToyCrossingCoordinator.state->MainSignalStateMachine.state
  - flow:ToyCrossingCoordinator.state->SideSignalStateMachine.state
  - flow:ToyDualSignalCoordinator.mainRed->ScenarioReport.observedBehavior
  - flow:ToyDualSignalCoordinator.sideRed->ScenarioReport.observedBehavior
  - control:main_warning_to_all_stop
  - control:side_warning_to_all_stop
  - harness:ToyMainWarningTimer
  - harness:ToyClearanceTimer
  - harness:ToyDualSignalCoordinator
  evidence:
  - samples/toy_dual_signal_coordination/model.mbd.md
  - samples/toy_dual_signal_coordination/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: DSC-004
  modelElements:
  - component:ToyDualSignalCoordinator
  - function:ToyCrossingCoordinator
  - function:MainSignalStateMachine
  - function:SideSignalStateMachine
  - flow:ToySideRequestSource.sideRequest->ToyCrossingCoordinator.sideRequest
  - flow:ToyClearanceTimer.expired->ToyCrossingCoordinator.clearanceExpired
  - flow:ToyCrossingCoordinator.state->MainSignalStateMachine.state
  - flow:ToyCrossingCoordinator.state->SideSignalStateMachine.state
  - flow:ToyDualSignalCoordinator.mainRed->ScenarioReport.observedBehavior
  - flow:ToyDualSignalCoordinator.sideGreen->ScenarioReport.observedBehavior
  - control:clearance_to_side_go
  - harness:ToySideRequestSource
  - harness:ToyClearanceTimer
  - harness:ToyDualSignalCoordinator
  evidence:
  - samples/toy_dual_signal_coordination/model.mbd.md
  - samples/toy_dual_signal_coordination/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: DSC-005
  modelElements:
  - component:ToyDualSignalCoordinator
  - function:ToyCrossingCoordinator
  - function:SideSignalStateMachine
  - flow:ToyClearanceTimer.expired->ToyCrossingCoordinator.clearanceExpired
  - flow:ToySideServiceSource.sideServed->ToyCrossingCoordinator.sideServed
  - flow:ToySideWarningTimer.expired->ToyCrossingCoordinator.sideWarningExpired
  - flow:ToyCrossingCoordinator.state->SideSignalStateMachine.state
  - flow:ToyDualSignalCoordinator.sideYellow->ScenarioReport.observedBehavior
  - control:side_service_prepare_main
  - control:side_warning_to_all_stop
  - control:clearance_to_main_go
  - harness:ToyClearanceTimer
  - harness:ToySideServiceSource
  - harness:ToySideWarningTimer
  - harness:ToyDualSignalCoordinator
  evidence:
  - samples/toy_dual_signal_coordination/model.mbd.md
  - samples/toy_dual_signal_coordination/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: DSC-006
  modelElements:
  - component:ToyDualSignalCoordinator
  - function:MainSignalStateMachine
  - function:SideSignalStateMachine
  - function:InterlockMonitor
  - flow:ToyDualSignalCoordinator.mainGreen->ScenarioReport.observedBehavior
  - flow:ToyDualSignalCoordinator.sideGreen->ScenarioReport.observedBehavior
  - control:request_side_prepare_main
  - control:main_warning_to_all_stop
  - control:clearance_to_side_go
  - control:side_service_prepare_main
  - control:side_warning_to_all_stop
  - control:clearance_to_main_go
  - harness:ToyDualSignalCoordinator
  evidence:
  - samples/toy_dual_signal_coordination/model.mbd.md
  - samples/toy_dual_signal_coordination/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: DSC-007
  modelElements:
  - component:ToyDualSignalCoordinator
  - function:MainSignalStateMachine
  - function:SideSignalStateMachine
  - flow:ToyCrossingCoordinator.state->MainSignalStateMachine.state
  - flow:ToyCrossingCoordinator.state->SideSignalStateMachine.state
  - control:request_side_prepare_main
  - control:main_warning_to_all_stop
  - control:clearance_to_side_go
  - control:side_service_prepare_main
  - control:side_warning_to_all_stop
  - control:clearance_to_main_go
  - harness:ToyDualSignalCoordinator
  evidence:
  - samples/toy_dual_signal_coordination/model.mbd.md
  - samples/toy_dual_signal_coordination/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: DSC-PRE-001
  modelElements:
  - component:ToyDualSignalCoordinator
  - function:ToyCrossingCoordinator
  - function:InterlockMonitor
  - harness:ToySideRequestSource
  - harness:ToyMainWarningTimer
  - harness:ToyClearanceTimer
  - harness:ToySideServiceSource
  - harness:ToySideWarningTimer
  evidence:
  - samples/toy_dual_signal_coordination/model.mbd.md
  - samples/toy_dual_signal_coordination/generated/diagram.mmd
  - preview report path supplied by run-preview
- requirement: DSC-PRE-002
  modelElements:
  - component:ToyDualSignalCoordinator
  - function:ToyCrossingCoordinator
  evidence:
  - samples/toy_dual_signal_coordination/model.mbd.md
  - samples/toy_dual_signal_coordination/generated/diagram.mmd
  - preview report path supplied by run-preview
```

## Scenario Steps

```yaml
- atMs: 0
  setInput:
    name: sideRequest
    value: true
- atMs: 10
  setInput:
    name: mainWarningExpired
    value: true
- atMs: 20
  setInput:
    name: clearanceExpired
    value: true
- atMs: 30
  setInput:
    name: sideServed
    value: true
- atMs: 40
  setInput:
    name: sideWarningExpired
    value: true
- atMs: 50
  setInput:
    name: clearanceExpired
    value: true
```

## Harness Boundary Evidence

```yaml
- name: ToySideRequestSource
  role: stimulus
  boundary: virtual_ic
  trace:
  - DSC-002
  - DSC-004
  - DSC-PRE-001
- name: ToyMainWarningTimer
  role: timer
  boundary: virtual_ic
  trace:
  - DSC-002
  - DSC-003
  - DSC-PRE-001
- name: ToyClearanceTimer
  role: timer
  boundary: virtual_ic
  trace:
  - DSC-003
  - DSC-004
  - DSC-005
  - DSC-PRE-001
- name: ToySideServiceSource
  role: stimulus
  boundary: virtual_ic
  trace:
  - DSC-005
  - DSC-PRE-001
- name: ToySideWarningTimer
  role: timer
  boundary: virtual_ic
  trace:
  - DSC-005
  - DSC-PRE-001
- name: ToyDualSignalCoordinator
  role: controller
  boundary: hal
  trace:
  - DSC-001
  - DSC-002
  - DSC-003
  - DSC-004
  - DSC-005
  - DSC-006
  - DSC-007
```

## Per-Step Preview Execution

```yaml
- stepIndex: 0
  atMs: 0
  scenarioInput:
    name: sideRequest
    value: true
  before:
    state: MAIN_GO_SIDE_STOP
    inputs:
      sideRequest: false
      mainWarningExpired: false
      clearanceExpired: false
      sideServed: false
      sideWarningExpired: false
    outputs:
      mainGreen: true
      mainYellow: false
      mainRed: false
      sideGreen: false
      sideYellow: false
      sideRed: true
  virtualIcObservation:
    ToyDualSignalCoordinator.sideRequest: true
    ToyDualSignalCoordinator.mainWarningExpired: false
    ToyDualSignalCoordinator.clearanceExpired: false
    ToyDualSignalCoordinator.sideServed: false
    ToyDualSignalCoordinator.sideWarningExpired: false
  controlRuleEvaluations:
  - rule: request_side_prepare_main
    owner: ToyCrossingCoordinator
    priority: 10
    stateScope: MAIN_GO_SIDE_STOP
    stateScopeMatched: true
    condition: sideRequest == true
    matched: true
    selectable: true
    actionsIfMatched:
      state: MAIN_WARN_SIDE_STOP
      mainGreen: 'false'
      mainYellow: 'true'
      mainRed: 'false'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-002
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: main_warning_to_all_stop
    owner: ToyCrossingCoordinator
    priority: 20
    stateScope: MAIN_WARN_SIDE_STOP
    stateScopeMatched: false
    condition: mainWarningExpired == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: ALL_STOP_BEFORE_SIDE
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-003
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: clearance_to_side_go
    owner: ToyCrossingCoordinator
    priority: 30
    stateScope: ALL_STOP_BEFORE_SIDE
    stateScopeMatched: false
    condition: clearanceExpired == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: MAIN_STOP_SIDE_GO
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'true'
      sideYellow: 'false'
      sideRed: 'false'
    trace:
    - DSC-004
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: side_service_prepare_main
    owner: ToyCrossingCoordinator
    priority: 40
    stateScope: MAIN_STOP_SIDE_GO
    stateScopeMatched: false
    condition: sideServed == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: MAIN_STOP_SIDE_WARN
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'false'
      sideYellow: 'true'
      sideRed: 'false'
    trace:
    - DSC-005
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: side_warning_to_all_stop
    owner: ToyCrossingCoordinator
    priority: 50
    stateScope: MAIN_STOP_SIDE_WARN
    stateScopeMatched: false
    condition: sideWarningExpired == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: ALL_STOP_BEFORE_MAIN
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-003
    - DSC-005
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: clearance_to_main_go
    owner: ToyCrossingCoordinator
    priority: 60
    stateScope: ALL_STOP_BEFORE_MAIN
    stateScopeMatched: false
    condition: clearanceExpired == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: MAIN_GO_SIDE_STOP
      mainGreen: 'true'
      mainYellow: 'false'
      mainRed: 'false'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-001
    - DSC-005
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: request_side_prepare_main
  appliedOwner: ToyCrossingCoordinator
  generatedEcuCommandOutputs:
    mainGreen: false
    mainYellow: true
    mainRed: false
    sideGreen: false
    sideYellow: false
    sideRed: true
    commandFlows:
    - source: ToyDualSignalCoordinator.mainGreen
      target: ScenarioReport.observedBehavior
      label: main green evidence
      value: false
      trace:
      - DSC-001
      - DSC-006
    - source: ToyDualSignalCoordinator.mainYellow
      target: ScenarioReport.observedBehavior
      label: main warning evidence
      value: true
      trace:
      - DSC-002
    - source: ToyDualSignalCoordinator.mainRed
      target: ScenarioReport.observedBehavior
      label: main stop evidence
      value: false
      trace:
      - DSC-003
      - DSC-004
    - source: ToyDualSignalCoordinator.sideGreen
      target: ScenarioReport.observedBehavior
      label: side green evidence
      value: false
      trace:
      - DSC-004
      - DSC-006
    - source: ToyDualSignalCoordinator.sideYellow
      target: ScenarioReport.observedBehavior
      label: side warning evidence
      value: false
      trace:
      - DSC-005
    - source: ToyDualSignalCoordinator.sideRed
      target: ScenarioReport.observedBehavior
      label: side stop evidence
      value: true
      trace:
      - DSC-001
      - DSC-002
      - DSC-003
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: MAIN_WARN_SIDE_STOP
    inputs:
      sideRequest: true
      mainWarningExpired: false
      clearanceExpired: false
      sideServed: false
      sideWarningExpired: false
    outputs:
      mainGreen: false
      mainYellow: true
      mainRed: false
      sideGreen: false
      sideYellow: false
      sideRed: true
  requirementRefs:
  - DSC-002
  - DSC-006
  - DSC-007
- stepIndex: 1
  atMs: 10
  scenarioInput:
    name: mainWarningExpired
    value: true
  before:
    state: MAIN_WARN_SIDE_STOP
    inputs:
      sideRequest: true
      mainWarningExpired: false
      clearanceExpired: false
      sideServed: false
      sideWarningExpired: false
    outputs:
      mainGreen: false
      mainYellow: true
      mainRed: false
      sideGreen: false
      sideYellow: false
      sideRed: true
  virtualIcObservation:
    ToyDualSignalCoordinator.sideRequest: true
    ToyDualSignalCoordinator.mainWarningExpired: true
    ToyDualSignalCoordinator.clearanceExpired: false
    ToyDualSignalCoordinator.sideServed: false
    ToyDualSignalCoordinator.sideWarningExpired: false
  controlRuleEvaluations:
  - rule: request_side_prepare_main
    owner: ToyCrossingCoordinator
    priority: 10
    stateScope: MAIN_GO_SIDE_STOP
    stateScopeMatched: false
    condition: sideRequest == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: MAIN_WARN_SIDE_STOP
      mainGreen: 'false'
      mainYellow: 'true'
      mainRed: 'false'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-002
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: main_warning_to_all_stop
    owner: ToyCrossingCoordinator
    priority: 20
    stateScope: MAIN_WARN_SIDE_STOP
    stateScopeMatched: true
    condition: mainWarningExpired == true
    matched: true
    selectable: true
    actionsIfMatched:
      state: ALL_STOP_BEFORE_SIDE
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-003
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: clearance_to_side_go
    owner: ToyCrossingCoordinator
    priority: 30
    stateScope: ALL_STOP_BEFORE_SIDE
    stateScopeMatched: false
    condition: clearanceExpired == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: MAIN_STOP_SIDE_GO
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'true'
      sideYellow: 'false'
      sideRed: 'false'
    trace:
    - DSC-004
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: side_service_prepare_main
    owner: ToyCrossingCoordinator
    priority: 40
    stateScope: MAIN_STOP_SIDE_GO
    stateScopeMatched: false
    condition: sideServed == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: MAIN_STOP_SIDE_WARN
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'false'
      sideYellow: 'true'
      sideRed: 'false'
    trace:
    - DSC-005
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: side_warning_to_all_stop
    owner: ToyCrossingCoordinator
    priority: 50
    stateScope: MAIN_STOP_SIDE_WARN
    stateScopeMatched: false
    condition: sideWarningExpired == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: ALL_STOP_BEFORE_MAIN
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-003
    - DSC-005
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: clearance_to_main_go
    owner: ToyCrossingCoordinator
    priority: 60
    stateScope: ALL_STOP_BEFORE_MAIN
    stateScopeMatched: false
    condition: clearanceExpired == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: MAIN_GO_SIDE_STOP
      mainGreen: 'true'
      mainYellow: 'false'
      mainRed: 'false'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-001
    - DSC-005
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: main_warning_to_all_stop
  appliedOwner: ToyCrossingCoordinator
  generatedEcuCommandOutputs:
    mainGreen: false
    mainYellow: false
    mainRed: true
    sideGreen: false
    sideYellow: false
    sideRed: true
    commandFlows:
    - source: ToyDualSignalCoordinator.mainGreen
      target: ScenarioReport.observedBehavior
      label: main green evidence
      value: false
      trace:
      - DSC-001
      - DSC-006
    - source: ToyDualSignalCoordinator.mainYellow
      target: ScenarioReport.observedBehavior
      label: main warning evidence
      value: false
      trace:
      - DSC-002
    - source: ToyDualSignalCoordinator.mainRed
      target: ScenarioReport.observedBehavior
      label: main stop evidence
      value: true
      trace:
      - DSC-003
      - DSC-004
    - source: ToyDualSignalCoordinator.sideGreen
      target: ScenarioReport.observedBehavior
      label: side green evidence
      value: false
      trace:
      - DSC-004
      - DSC-006
    - source: ToyDualSignalCoordinator.sideYellow
      target: ScenarioReport.observedBehavior
      label: side warning evidence
      value: false
      trace:
      - DSC-005
    - source: ToyDualSignalCoordinator.sideRed
      target: ScenarioReport.observedBehavior
      label: side stop evidence
      value: true
      trace:
      - DSC-001
      - DSC-002
      - DSC-003
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: ALL_STOP_BEFORE_SIDE
    inputs:
      sideRequest: true
      mainWarningExpired: true
      clearanceExpired: false
      sideServed: false
      sideWarningExpired: false
    outputs:
      mainGreen: false
      mainYellow: false
      mainRed: true
      sideGreen: false
      sideYellow: false
      sideRed: true
  requirementRefs:
  - DSC-003
  - DSC-006
  - DSC-007
- stepIndex: 2
  atMs: 20
  scenarioInput:
    name: clearanceExpired
    value: true
  before:
    state: ALL_STOP_BEFORE_SIDE
    inputs:
      sideRequest: true
      mainWarningExpired: true
      clearanceExpired: false
      sideServed: false
      sideWarningExpired: false
    outputs:
      mainGreen: false
      mainYellow: false
      mainRed: true
      sideGreen: false
      sideYellow: false
      sideRed: true
  virtualIcObservation:
    ToyDualSignalCoordinator.sideRequest: true
    ToyDualSignalCoordinator.mainWarningExpired: true
    ToyDualSignalCoordinator.clearanceExpired: true
    ToyDualSignalCoordinator.sideServed: false
    ToyDualSignalCoordinator.sideWarningExpired: false
  controlRuleEvaluations:
  - rule: request_side_prepare_main
    owner: ToyCrossingCoordinator
    priority: 10
    stateScope: MAIN_GO_SIDE_STOP
    stateScopeMatched: false
    condition: sideRequest == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: MAIN_WARN_SIDE_STOP
      mainGreen: 'false'
      mainYellow: 'true'
      mainRed: 'false'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-002
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: main_warning_to_all_stop
    owner: ToyCrossingCoordinator
    priority: 20
    stateScope: MAIN_WARN_SIDE_STOP
    stateScopeMatched: false
    condition: mainWarningExpired == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: ALL_STOP_BEFORE_SIDE
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-003
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: clearance_to_side_go
    owner: ToyCrossingCoordinator
    priority: 30
    stateScope: ALL_STOP_BEFORE_SIDE
    stateScopeMatched: true
    condition: clearanceExpired == true
    matched: true
    selectable: true
    actionsIfMatched:
      state: MAIN_STOP_SIDE_GO
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'true'
      sideYellow: 'false'
      sideRed: 'false'
    trace:
    - DSC-004
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: side_service_prepare_main
    owner: ToyCrossingCoordinator
    priority: 40
    stateScope: MAIN_STOP_SIDE_GO
    stateScopeMatched: false
    condition: sideServed == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: MAIN_STOP_SIDE_WARN
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'false'
      sideYellow: 'true'
      sideRed: 'false'
    trace:
    - DSC-005
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: side_warning_to_all_stop
    owner: ToyCrossingCoordinator
    priority: 50
    stateScope: MAIN_STOP_SIDE_WARN
    stateScopeMatched: false
    condition: sideWarningExpired == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: ALL_STOP_BEFORE_MAIN
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-003
    - DSC-005
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: clearance_to_main_go
    owner: ToyCrossingCoordinator
    priority: 60
    stateScope: ALL_STOP_BEFORE_MAIN
    stateScopeMatched: false
    condition: clearanceExpired == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: MAIN_GO_SIDE_STOP
      mainGreen: 'true'
      mainYellow: 'false'
      mainRed: 'false'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-001
    - DSC-005
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: clearance_to_side_go
  appliedOwner: ToyCrossingCoordinator
  generatedEcuCommandOutputs:
    mainGreen: false
    mainYellow: false
    mainRed: true
    sideGreen: true
    sideYellow: false
    sideRed: false
    commandFlows:
    - source: ToyDualSignalCoordinator.mainGreen
      target: ScenarioReport.observedBehavior
      label: main green evidence
      value: false
      trace:
      - DSC-001
      - DSC-006
    - source: ToyDualSignalCoordinator.mainYellow
      target: ScenarioReport.observedBehavior
      label: main warning evidence
      value: false
      trace:
      - DSC-002
    - source: ToyDualSignalCoordinator.mainRed
      target: ScenarioReport.observedBehavior
      label: main stop evidence
      value: true
      trace:
      - DSC-003
      - DSC-004
    - source: ToyDualSignalCoordinator.sideGreen
      target: ScenarioReport.observedBehavior
      label: side green evidence
      value: true
      trace:
      - DSC-004
      - DSC-006
    - source: ToyDualSignalCoordinator.sideYellow
      target: ScenarioReport.observedBehavior
      label: side warning evidence
      value: false
      trace:
      - DSC-005
    - source: ToyDualSignalCoordinator.sideRed
      target: ScenarioReport.observedBehavior
      label: side stop evidence
      value: false
      trace:
      - DSC-001
      - DSC-002
      - DSC-003
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: MAIN_STOP_SIDE_GO
    inputs:
      sideRequest: true
      mainWarningExpired: true
      clearanceExpired: true
      sideServed: false
      sideWarningExpired: false
    outputs:
      mainGreen: false
      mainYellow: false
      mainRed: true
      sideGreen: true
      sideYellow: false
      sideRed: false
  requirementRefs:
  - DSC-004
  - DSC-006
  - DSC-007
- stepIndex: 3
  atMs: 30
  scenarioInput:
    name: sideServed
    value: true
  before:
    state: MAIN_STOP_SIDE_GO
    inputs:
      sideRequest: true
      mainWarningExpired: true
      clearanceExpired: true
      sideServed: false
      sideWarningExpired: false
    outputs:
      mainGreen: false
      mainYellow: false
      mainRed: true
      sideGreen: true
      sideYellow: false
      sideRed: false
  virtualIcObservation:
    ToyDualSignalCoordinator.sideRequest: true
    ToyDualSignalCoordinator.mainWarningExpired: true
    ToyDualSignalCoordinator.clearanceExpired: true
    ToyDualSignalCoordinator.sideServed: true
    ToyDualSignalCoordinator.sideWarningExpired: false
  controlRuleEvaluations:
  - rule: request_side_prepare_main
    owner: ToyCrossingCoordinator
    priority: 10
    stateScope: MAIN_GO_SIDE_STOP
    stateScopeMatched: false
    condition: sideRequest == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: MAIN_WARN_SIDE_STOP
      mainGreen: 'false'
      mainYellow: 'true'
      mainRed: 'false'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-002
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: main_warning_to_all_stop
    owner: ToyCrossingCoordinator
    priority: 20
    stateScope: MAIN_WARN_SIDE_STOP
    stateScopeMatched: false
    condition: mainWarningExpired == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: ALL_STOP_BEFORE_SIDE
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-003
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: clearance_to_side_go
    owner: ToyCrossingCoordinator
    priority: 30
    stateScope: ALL_STOP_BEFORE_SIDE
    stateScopeMatched: false
    condition: clearanceExpired == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: MAIN_STOP_SIDE_GO
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'true'
      sideYellow: 'false'
      sideRed: 'false'
    trace:
    - DSC-004
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: side_service_prepare_main
    owner: ToyCrossingCoordinator
    priority: 40
    stateScope: MAIN_STOP_SIDE_GO
    stateScopeMatched: true
    condition: sideServed == true
    matched: true
    selectable: true
    actionsIfMatched:
      state: MAIN_STOP_SIDE_WARN
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'false'
      sideYellow: 'true'
      sideRed: 'false'
    trace:
    - DSC-005
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: side_warning_to_all_stop
    owner: ToyCrossingCoordinator
    priority: 50
    stateScope: MAIN_STOP_SIDE_WARN
    stateScopeMatched: false
    condition: sideWarningExpired == true
    matched: false
    selectable: false
    actionsIfMatched:
      state: ALL_STOP_BEFORE_MAIN
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-003
    - DSC-005
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: clearance_to_main_go
    owner: ToyCrossingCoordinator
    priority: 60
    stateScope: ALL_STOP_BEFORE_MAIN
    stateScopeMatched: false
    condition: clearanceExpired == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: MAIN_GO_SIDE_STOP
      mainGreen: 'true'
      mainYellow: 'false'
      mainRed: 'false'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-001
    - DSC-005
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: side_service_prepare_main
  appliedOwner: ToyCrossingCoordinator
  generatedEcuCommandOutputs:
    mainGreen: false
    mainYellow: false
    mainRed: true
    sideGreen: false
    sideYellow: true
    sideRed: false
    commandFlows:
    - source: ToyDualSignalCoordinator.mainGreen
      target: ScenarioReport.observedBehavior
      label: main green evidence
      value: false
      trace:
      - DSC-001
      - DSC-006
    - source: ToyDualSignalCoordinator.mainYellow
      target: ScenarioReport.observedBehavior
      label: main warning evidence
      value: false
      trace:
      - DSC-002
    - source: ToyDualSignalCoordinator.mainRed
      target: ScenarioReport.observedBehavior
      label: main stop evidence
      value: true
      trace:
      - DSC-003
      - DSC-004
    - source: ToyDualSignalCoordinator.sideGreen
      target: ScenarioReport.observedBehavior
      label: side green evidence
      value: false
      trace:
      - DSC-004
      - DSC-006
    - source: ToyDualSignalCoordinator.sideYellow
      target: ScenarioReport.observedBehavior
      label: side warning evidence
      value: true
      trace:
      - DSC-005
    - source: ToyDualSignalCoordinator.sideRed
      target: ScenarioReport.observedBehavior
      label: side stop evidence
      value: false
      trace:
      - DSC-001
      - DSC-002
      - DSC-003
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: MAIN_STOP_SIDE_WARN
    inputs:
      sideRequest: true
      mainWarningExpired: true
      clearanceExpired: true
      sideServed: true
      sideWarningExpired: false
    outputs:
      mainGreen: false
      mainYellow: false
      mainRed: true
      sideGreen: false
      sideYellow: true
      sideRed: false
  requirementRefs:
  - DSC-005
  - DSC-006
  - DSC-007
- stepIndex: 4
  atMs: 40
  scenarioInput:
    name: sideWarningExpired
    value: true
  before:
    state: MAIN_STOP_SIDE_WARN
    inputs:
      sideRequest: true
      mainWarningExpired: true
      clearanceExpired: true
      sideServed: true
      sideWarningExpired: false
    outputs:
      mainGreen: false
      mainYellow: false
      mainRed: true
      sideGreen: false
      sideYellow: true
      sideRed: false
  virtualIcObservation:
    ToyDualSignalCoordinator.sideRequest: true
    ToyDualSignalCoordinator.mainWarningExpired: true
    ToyDualSignalCoordinator.clearanceExpired: true
    ToyDualSignalCoordinator.sideServed: true
    ToyDualSignalCoordinator.sideWarningExpired: true
  controlRuleEvaluations:
  - rule: request_side_prepare_main
    owner: ToyCrossingCoordinator
    priority: 10
    stateScope: MAIN_GO_SIDE_STOP
    stateScopeMatched: false
    condition: sideRequest == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: MAIN_WARN_SIDE_STOP
      mainGreen: 'false'
      mainYellow: 'true'
      mainRed: 'false'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-002
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: main_warning_to_all_stop
    owner: ToyCrossingCoordinator
    priority: 20
    stateScope: MAIN_WARN_SIDE_STOP
    stateScopeMatched: false
    condition: mainWarningExpired == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: ALL_STOP_BEFORE_SIDE
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-003
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: clearance_to_side_go
    owner: ToyCrossingCoordinator
    priority: 30
    stateScope: ALL_STOP_BEFORE_SIDE
    stateScopeMatched: false
    condition: clearanceExpired == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: MAIN_STOP_SIDE_GO
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'true'
      sideYellow: 'false'
      sideRed: 'false'
    trace:
    - DSC-004
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: side_service_prepare_main
    owner: ToyCrossingCoordinator
    priority: 40
    stateScope: MAIN_STOP_SIDE_GO
    stateScopeMatched: false
    condition: sideServed == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: MAIN_STOP_SIDE_WARN
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'false'
      sideYellow: 'true'
      sideRed: 'false'
    trace:
    - DSC-005
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: side_warning_to_all_stop
    owner: ToyCrossingCoordinator
    priority: 50
    stateScope: MAIN_STOP_SIDE_WARN
    stateScopeMatched: true
    condition: sideWarningExpired == true
    matched: true
    selectable: true
    actionsIfMatched:
      state: ALL_STOP_BEFORE_MAIN
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-003
    - DSC-005
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: clearance_to_main_go
    owner: ToyCrossingCoordinator
    priority: 60
    stateScope: ALL_STOP_BEFORE_MAIN
    stateScopeMatched: false
    condition: clearanceExpired == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: MAIN_GO_SIDE_STOP
      mainGreen: 'true'
      mainYellow: 'false'
      mainRed: 'false'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-001
    - DSC-005
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: side_warning_to_all_stop
  appliedOwner: ToyCrossingCoordinator
  generatedEcuCommandOutputs:
    mainGreen: false
    mainYellow: false
    mainRed: true
    sideGreen: false
    sideYellow: false
    sideRed: true
    commandFlows:
    - source: ToyDualSignalCoordinator.mainGreen
      target: ScenarioReport.observedBehavior
      label: main green evidence
      value: false
      trace:
      - DSC-001
      - DSC-006
    - source: ToyDualSignalCoordinator.mainYellow
      target: ScenarioReport.observedBehavior
      label: main warning evidence
      value: false
      trace:
      - DSC-002
    - source: ToyDualSignalCoordinator.mainRed
      target: ScenarioReport.observedBehavior
      label: main stop evidence
      value: true
      trace:
      - DSC-003
      - DSC-004
    - source: ToyDualSignalCoordinator.sideGreen
      target: ScenarioReport.observedBehavior
      label: side green evidence
      value: false
      trace:
      - DSC-004
      - DSC-006
    - source: ToyDualSignalCoordinator.sideYellow
      target: ScenarioReport.observedBehavior
      label: side warning evidence
      value: false
      trace:
      - DSC-005
    - source: ToyDualSignalCoordinator.sideRed
      target: ScenarioReport.observedBehavior
      label: side stop evidence
      value: true
      trace:
      - DSC-001
      - DSC-002
      - DSC-003
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: ALL_STOP_BEFORE_MAIN
    inputs:
      sideRequest: true
      mainWarningExpired: true
      clearanceExpired: true
      sideServed: true
      sideWarningExpired: true
    outputs:
      mainGreen: false
      mainYellow: false
      mainRed: true
      sideGreen: false
      sideYellow: false
      sideRed: true
  requirementRefs:
  - DSC-003
  - DSC-005
  - DSC-006
  - DSC-007
- stepIndex: 5
  atMs: 50
  scenarioInput:
    name: clearanceExpired
    value: true
  before:
    state: ALL_STOP_BEFORE_MAIN
    inputs:
      sideRequest: true
      mainWarningExpired: true
      clearanceExpired: true
      sideServed: true
      sideWarningExpired: true
    outputs:
      mainGreen: false
      mainYellow: false
      mainRed: true
      sideGreen: false
      sideYellow: false
      sideRed: true
  virtualIcObservation:
    ToyDualSignalCoordinator.sideRequest: true
    ToyDualSignalCoordinator.mainWarningExpired: true
    ToyDualSignalCoordinator.clearanceExpired: true
    ToyDualSignalCoordinator.sideServed: true
    ToyDualSignalCoordinator.sideWarningExpired: true
  controlRuleEvaluations:
  - rule: request_side_prepare_main
    owner: ToyCrossingCoordinator
    priority: 10
    stateScope: MAIN_GO_SIDE_STOP
    stateScopeMatched: false
    condition: sideRequest == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: MAIN_WARN_SIDE_STOP
      mainGreen: 'false'
      mainYellow: 'true'
      mainRed: 'false'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-002
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: main_warning_to_all_stop
    owner: ToyCrossingCoordinator
    priority: 20
    stateScope: MAIN_WARN_SIDE_STOP
    stateScopeMatched: false
    condition: mainWarningExpired == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: ALL_STOP_BEFORE_SIDE
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-003
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: clearance_to_side_go
    owner: ToyCrossingCoordinator
    priority: 30
    stateScope: ALL_STOP_BEFORE_SIDE
    stateScopeMatched: false
    condition: clearanceExpired == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: MAIN_STOP_SIDE_GO
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'true'
      sideYellow: 'false'
      sideRed: 'false'
    trace:
    - DSC-004
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: side_service_prepare_main
    owner: ToyCrossingCoordinator
    priority: 40
    stateScope: MAIN_STOP_SIDE_GO
    stateScopeMatched: false
    condition: sideServed == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: MAIN_STOP_SIDE_WARN
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'false'
      sideYellow: 'true'
      sideRed: 'false'
    trace:
    - DSC-005
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: side_warning_to_all_stop
    owner: ToyCrossingCoordinator
    priority: 50
    stateScope: MAIN_STOP_SIDE_WARN
    stateScopeMatched: false
    condition: sideWarningExpired == true
    matched: true
    selectable: false
    actionsIfMatched:
      state: ALL_STOP_BEFORE_MAIN
      mainGreen: 'false'
      mainYellow: 'false'
      mainRed: 'true'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-003
    - DSC-005
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  - rule: clearance_to_main_go
    owner: ToyCrossingCoordinator
    priority: 60
    stateScope: ALL_STOP_BEFORE_MAIN
    stateScopeMatched: true
    condition: clearanceExpired == true
    matched: true
    selectable: true
    actionsIfMatched:
      state: MAIN_GO_SIDE_STOP
      mainGreen: 'true'
      mainYellow: 'false'
      mainRed: 'false'
      sideGreen: 'false'
      sideYellow: 'false'
      sideRed: 'true'
    trace:
    - DSC-001
    - DSC-005
    - DSC-006
    - DSC-007
    scenarios:
    - side_request_cycle
  selectionPolicy: lowest numeric priority wins after state scope and guard match
  appliedRule: clearance_to_main_go
  appliedOwner: ToyCrossingCoordinator
  generatedEcuCommandOutputs:
    mainGreen: true
    mainYellow: false
    mainRed: false
    sideGreen: false
    sideYellow: false
    sideRed: true
    commandFlows:
    - source: ToyDualSignalCoordinator.mainGreen
      target: ScenarioReport.observedBehavior
      label: main green evidence
      value: true
      trace:
      - DSC-001
      - DSC-006
    - source: ToyDualSignalCoordinator.mainYellow
      target: ScenarioReport.observedBehavior
      label: main warning evidence
      value: false
      trace:
      - DSC-002
    - source: ToyDualSignalCoordinator.mainRed
      target: ScenarioReport.observedBehavior
      label: main stop evidence
      value: false
      trace:
      - DSC-003
      - DSC-004
    - source: ToyDualSignalCoordinator.sideGreen
      target: ScenarioReport.observedBehavior
      label: side green evidence
      value: false
      trace:
      - DSC-004
      - DSC-006
    - source: ToyDualSignalCoordinator.sideYellow
      target: ScenarioReport.observedBehavior
      label: side warning evidence
      value: false
      trace:
      - DSC-005
    - source: ToyDualSignalCoordinator.sideRed
      target: ScenarioReport.observedBehavior
      label: side stop evidence
      value: true
      trace:
      - DSC-001
      - DSC-002
      - DSC-003
    previewCodeSource: sample-specific preview C export, if available
  after:
    state: MAIN_GO_SIDE_STOP
    inputs:
      sideRequest: true
      mainWarningExpired: true
      clearanceExpired: true
      sideServed: true
      sideWarningExpired: true
    outputs:
      mainGreen: true
      mainYellow: false
      mainRed: false
      sideGreen: false
      sideYellow: false
      sideRed: true
  requirementRefs:
  - DSC-001
  - DSC-005
  - DSC-006
  - DSC-007
```

## Observed Behavior

```yaml
finalState: MAIN_GO_SIDE_STOP
inputs:
  sideRequest: true
  mainWarningExpired: true
  clearanceExpired: true
  sideServed: true
  sideWarningExpired: true
outputs:
  mainGreen: true
  mainYellow: false
  mainRed: false
  sideGreen: false
  sideYellow: false
  sideRed: true
appliedRules:
- request_side_prepare_main
- main_warning_to_all_stop
- clearance_to_side_go
- side_service_prepare_main
- side_warning_to_all_stop
- clearance_to_main_go
harnessDevices:
- name: ToySideRequestSource
  role: stimulus
  boundary: virtual_ic
- name: ToyMainWarningTimer
  role: timer
  boundary: virtual_ic
- name: ToyClearanceTimer
  role: timer
  boundary: virtual_ic
- name: ToySideServiceSource
  role: stimulus
  boundary: virtual_ic
- name: ToySideWarningTimer
  role: timer
  boundary: virtual_ic
- name: ToyDualSignalCoordinator
  role: controller
  boundary: hal
```

## Generated ECU Command Outputs

```yaml
mainGreen: true
mainYellow: false
mainRed: false
sideGreen: false
sideYellow: false
sideRed: true
commandFlows:
- source: ToyDualSignalCoordinator.mainGreen
  target: ScenarioReport.observedBehavior
  label: main green evidence
  value: true
  trace:
  - DSC-001
  - DSC-006
- source: ToyDualSignalCoordinator.mainYellow
  target: ScenarioReport.observedBehavior
  label: main warning evidence
  value: false
  trace:
  - DSC-002
- source: ToyDualSignalCoordinator.mainRed
  target: ScenarioReport.observedBehavior
  label: main stop evidence
  value: false
  trace:
  - DSC-003
  - DSC-004
- source: ToyDualSignalCoordinator.sideGreen
  target: ScenarioReport.observedBehavior
  label: side green evidence
  value: false
  trace:
  - DSC-004
  - DSC-006
- source: ToyDualSignalCoordinator.sideYellow
  target: ScenarioReport.observedBehavior
  label: side warning evidence
  value: false
  trace:
  - DSC-005
- source: ToyDualSignalCoordinator.sideRed
  target: ScenarioReport.observedBehavior
  label: side stop evidence
  value: true
  trace:
  - DSC-001
  - DSC-002
  - DSC-003
previewCodeSource: sample-specific preview C export, if available
```

## Expected Behavior

```yaml
finalState: MAIN_GO_SIDE_STOP
outputs:
  mainGreen: true
  mainYellow: false
  mainRed: false
  sideGreen: false
  sideYellow: false
  sideRed: true
neverBothTrue:
- - mainGreen
  - sideGreen
```

## Pass/Fail Result

- PASS finalState: actual MAIN_GO_SIDE_STOP, expected MAIN_GO_SIDE_STOP
- PASS outputs.mainGreen: actual True, expected True
- PASS outputs.mainYellow: actual False, expected False
- PASS outputs.mainRed: actual False, expected False
- PASS outputs.sideGreen: actual False, expected False
- PASS outputs.sideYellow: actual False, expected False
- PASS outputs.sideRed: actual True, expected True
- PASS neverBothTrue.mainGreen.sideGreen: no preview step had both true

## Runtime Trace

- preview-only runtime started
- input sideRequest=True
- rule request_side_prepare_main applied
- input mainWarningExpired=True
- rule main_warning_to_all_stop applied
- input clearanceExpired=True
- rule clearance_to_side_go applied
- input sideServed=True
- rule side_service_prepare_main applied
- input sideWarningExpired=True
- rule side_warning_to_all_stop applied
- input clearanceExpired=True
- rule clearance_to_main_go applied

## Register Reads

- No register reads recorded.
