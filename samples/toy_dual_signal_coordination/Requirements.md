# Toy Dual Signal Coordination Requirements

This fictional sample exists to review a multi-component, multi-state-machine
MBD handoff shape. It does not describe a real intersection, IC, ECU, vehicle,
traffic product, certification artifact, or production design.

## Functional Requirements

- `DSC-001`: The model shall start with the main signal granted and the side
  signal stopped.
- `DSC-002`: When a side request arrives, the coordinator shall move the main
  signal from go to warning before granting the side signal.
- `DSC-003`: The model shall require an all-stop clearance mode between
  opposing grants.
- `DSC-004`: After clearance, the side signal shall be granted while the main
  signal remains stopped.
- `DSC-005`: After the side service completes, the side signal shall warn, then
  the model shall return through all-stop clearance to the main grant.
- `DSC-006`: Main and side green outputs shall never be true at the same
  preview step.
- `DSC-007`: The review artifact shall separate the coordinator, the main
  signal state-machine role, the side signal state-machine role, data flow, and
  harness boundary.

## Preview Boundary

- `DSC-PRE-001`: The local Python preview validates the discrete coordinated
  mode path and observable output interlock.
- `DSC-PRE-002`: External MBD tools must verify chart/message semantics,
  parallel activity, timing, and Stateflow/Simulink execution ordering.
