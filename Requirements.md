# Requirements: Toy Thermal Fan Control Validation

This document defines the fictional validation target for the next project goal.
It is a requirements baseline, not a hardware datasheet, safety case, or ASPICE
compliance claim.

## Objective

Build a fictional thermal fan control example that proves the repository can
move from readable Mermaid-like MBD markup to generated MBD handoff artifacts,
a virtual IC harness preview, preview-only ECU C scaffolding, scenario reports,
and deterministic tests.

The business-shaped workflow is:

```text
requirements
  -> markup specification
  -> parser and internal IR
  -> MBD handoff artifacts
  -> virtual IC harness preview
  -> preview-only ECU C scaffold
  -> scenario reports and regression tests
```

## Process Stance

- Use a requirements-first PDCA/TDD loop: write or revise requirements, add
  failing tests or acceptance checks, implement the smallest matching slice,
  regenerate artifacts, then review reports.
- Use ASPICE-aware habits where they help: stable requirement IDs,
  bidirectional traceability, reviewable work products, verification evidence,
  and explicit separation of system, software, harness, and tool artifacts.
- Do not claim ASPICE compliance, safety certification, production readiness,
  or tool qualification from this MVP.

## Fictional Scope

The example system is the `Toy Thermal Fan Control System`.

Fictional components:

- `ToyTempSensorIC`
- `ToyFanDriverIC`
- `ToyThermalFanController`

The components, registers, signals, thresholds, and scenarios must remain
invented. They must not resemble a real IC datasheet, production ECU
requirement, confidential product, or vendor-specific implementation.

## Non-Goals

- Replacing Simulink, Stateflow, Modelica, FMI tooling, or commercial MBD tools.
- Building a certified code generator or verifier.
- Building a physics solver or high-fidelity thermal plant model.
- Modeling real hardware registers, electrical behavior, or timing guarantees.
- Deriving ECU logic from production code.

## Stakeholder Needs

- `STK-001`: A reviewer can read one textual source and understand the control
  intent without opening a commercial MBD tool.
- `STK-002`: An MBD engineer can regenerate handoff artifacts for external MBD
  tool review from the same textual source.
- `STK-003`: A software engineer can inspect product-like ECU control logic that
  uses HAL-style boundaries and is not production-derived.
- `STK-004`: A test engineer can run preview scenarios and see inputs,
  scenario steps, observed behavior, expected behavior, and pass/fail results
  separated in the report.
- `STK-005`: A process reviewer can trace requirements to markup sections,
  generated artifacts, preview scenarios, and tests.

## System Requirements

- `SYS-001`: The system shall read a fictional temperature value from
  `ToyTempSensorIC`.
- `SYS-002`: The system shall command a fictional fan duty output through
  `ToyFanDriverIC`.
- `SYS-003`: The system shall increase fan duty when temperature exceeds a
  fictional high threshold.
- `SYS-004`: The system shall reduce or disable fan duty when temperature falls
  below a fictional low threshold.
- `SYS-005`: The system shall enter a safe fictional duty command when the
  temperature input is marked invalid.
- `SYS-006`: The system shall expose normal and fault scenario behavior through
  generated review reports.

## Software Requirements

- `SWE-001`: The controller shall be described in `examples/*.mbd.md` using
  Mermaid-like MBD markup as the public source.
- `SWE-002`: The parser shall convert the markup into an internal IR snapshot
  without requiring YAML as an input.
- `SWE-003`: The IR shall retain enough trace information to connect
  requirements, components, ports, states, flows, control rules, and tests.
- `SWE-004`: Generated preview C shall use HAL-style headers for sensor and fan
  interactions rather than Python internals.
- `SWE-005`: Generated preview C and Python preview behavior shall be labeled
  preview-only and non-certified.

## MBD Handoff Requirements

- `MBD-001`: The tool shall generate a Markdown review document from the markup.
- `MBD-002`: The tool shall generate Mermaid and PlantUML preview diagrams from
  the markup.
- `MBD-003`: The tool shall generate a Simulink model-generation `.m` script
  from the markup.
- `MBD-004`: The tool shall generate a Modelica `.mo` text artifact from the
  markup.
- `MBD-005`: The tool shall generate SCXML or Stateflow-oriented handoff content
  when state behavior is present.
- `MBD-006`: The tool shall generate FMI-oriented metadata while clearly stating
  that no FMU is produced by this repository.
- `MBD-007`: Generated artifacts shall be deterministic for unchanged markup.

## Harness Requirements

- `HAR-001`: The preview harness shall simulate only fictional virtual IC
  boundaries needed by the scenario.
- `HAR-002`: The harness shall not modify ECU controller logic for simulation
  convenience.
- `HAR-003`: Preview scenarios shall be discrete steps, not a full plant or
  physics model.
- `HAR-004`: Reports shall separate model inputs, scenario steps, observed
  behavior, expected behavior, and pass/fail result.
- `HAR-005`: Scenario YAML, if used, shall be test input only and shall not be
  treated as the MBD source of truth.

## Process Requirements

- `PROC-001`: `Requirements.md` shall be updated before substantial changes to
  the validation example.
- `PROC-002`: `Tasks.md` shall break requirements into checked task-list items
  with explicit verification steps.
- `PROC-003`: Tests shall prove deterministic regeneration of generated
  artifacts.
- `PROC-004`: Documentation shall keep the commercial-tool-free MVP boundary
  clear while preserving the future path to Simulink, Modelica, and FMI export.

## Traceability Seed

| Requirement | Planned evidence |
| --- | --- |
| `SYS-001` - `SYS-006` | Markup components, control rules, scenarios, reports |
| `SWE-001` - `SWE-005` | Parser tests, IR snapshot tests, preview C export tests |
| `MBD-001` - `MBD-007` | Exporter tests and deterministic regeneration tests |
| `HAR-001` - `HAR-005` | Preview runtime tests and scenario report checks |
| `PROC-001` - `PROC-004` | `Tasks.md`, docs updates, project philosophy tests |

## Review Gates

- Requirements baseline reviewed before implementing the validation example.
- Markup reviewed before expanding parser and exporter behavior.
- Generated artifacts reviewed before preview harness work.
- Preview reports reviewed before considering the goal complete.
