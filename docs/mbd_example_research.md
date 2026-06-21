# MBD Example Research Notes

This note records public design patterns used to choose small fictional samples
for this repository. It is not a claim of MathWorks compatibility,
certification, or tool qualification.

## Sources Reviewed

- MathWorks Simulink Relay block documentation:
  <https://www.mathworks.com/help/simulink/slref/relay.html>
- MathWorks Stateflow state transition table documentation:
  <https://www.mathworks.com/help/stateflow/ug/state-transition-tables-in-stateflow.html>
- MathWorks state transition table inspection example:
  <https://www.mathworks.com/help/stateflow/ug/inspect-state-transition-table.html>
- MathWorks requirements traceability overview:
  <https://www.mathworks.com/discovery/requirements-traceability.html>

## Extracted Patterns

- Relay/hysteresis is a small but useful next step after a simple Switch:
  behavior depends on two thresholds and the previous state.
- State transition tables are a compact review form for modal logic: state,
  condition, action/effect, and destination should be visible together.
- Requirements traceability should connect requirements to model elements,
  tests, and test results. This repository keeps that as a lightweight preview
  trace, not a commercial-tool trace database.

## Selected Repo Slice

`samples/simple_relay_hysteresis/` implements the selected slice:

- fictional numeric input: `level`
- fictional parameters: `onThreshold`, `offThreshold`
- explicit states: `OFF`, `ON`
- explicit transitions: `OFF -> ON` and `ON -> OFF`
- explicit output: `active`
- one preview Harness scenario proving ON, hold, and OFF behavior

The sample deliberately avoids physical plant modeling, real hardware details,
timing solvers, and certified code generation.
