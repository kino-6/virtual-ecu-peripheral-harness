# Requirements Traceability Report

- Coverage result: **PASS**
- Behavior approval: **PENDING**
- Scope: scaffold trace coverage only; not a safety case, tool qualification, or production approval.

## Findings

- PASS scaffold trace coverage exists for extracted requirements
- PENDING behavior approval: 20 open question or TODO item(s) remain

## Missing Spec Coverage

- None

## Missing MBD Coverage

- None

## Untraced MBD Behavior

- None

## Approval Pending Items

- `SYS-005`: confirm threshold/timing/recovery/fault semantics and required scenario evidence.
- `SYS-006`: confirm threshold/timing/recovery/fault semantics and required scenario evidence.
- `SYS-007`: confirm threshold/timing/recovery/fault semantics and required scenario evidence.
- `SYS-008`: confirm threshold/timing/recovery/fault semantics and required scenario evidence.
- parameter TODO_highThreshold: degC = 0
- parameter TODO_lowThreshold: degC = 0
- parameter TODO_deratingLimit: percent = 0
- parameter TODO_safeCommand: percent = 0
- RESET --> NOMINAL: open-question SYS-008 trace SYS-008
- NOMINAL --> COOLING: open-question threshold-high trace SYS-003
- COOLING --> DERATING: open-question derating-entry trace SYS-005
- DERATING --> FAULT_LATCHED: open-question persistent-invalid-sensor trace SYS-007
- FAULT_LATCHED --> NOMINAL: open-question recovery-conditions trace SYS-008
- rule TODO_sensorFault: when temperatureValid == false then diagnosticFault=true trace SYS-006 SYS-007
- rule TODO_highTemperature: when temperatureC >= TODO_highThreshold then coolingCommand=TODO trace SYS-003
- rule TODO_derating: when temperatureC >= TODO_deratingEntry then deratingCommand=TODO trace SYS-005
- open-question SYS-005: define explicit state/control/harness/scenario/expected behavior coverage.
- open-question SYS-006: define explicit state/control/harness/scenario/expected behavior coverage.
- open-question SYS-007: define explicit state/control/harness/scenario/expected behavior coverage.
- open-question SYS-008: define explicit state/control/harness/scenario/expected behavior coverage.
