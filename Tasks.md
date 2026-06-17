# Tasks

This is the proposed breakdown for the next Goal. Review and adjust this file
before asking an agent to execute it end to end.

Maintenance rule: if this file grows beyond 200 lines, move completed or
historical detail into `docs/archive/` and leave only a short summary plus links
here.

## Goal

Build a fictional, requirements-first validation case proving this repository
can go from a written intent to a human-readable specification, readable MBD
markup, generated MBD handoff artifacts, virtual IC harness preview,
preview-only ECU C scaffolding, scenario reports, and deterministic tests.

Working example: `Toy Thermal Fan Control System`

Primary requirements baseline: `Requirements.md`

## Done Criteria

The work is complete when these commands pass:

```bash
python -m veph parse examples/toy_thermal_fan_control.mbd.md --out generated/toy_thermal_fan_control.ir.json
python -m veph export-docs examples/toy_thermal_fan_control.mbd.md --out generated/toy_thermal_fan_control.md
python -m veph export-mermaid examples/toy_thermal_fan_control.mbd.md --out generated/toy_thermal_fan_control.mmd
python -m veph export-plantuml examples/toy_thermal_fan_control.mbd.md --out generated/toy_thermal_fan_control.puml
python -m veph export-simulink-m examples/toy_thermal_fan_control.mbd.md --out generated/create_toy_thermal_fan_control_model.m
python -m veph export-modelica examples/toy_thermal_fan_control.mbd.md --out generated/ToyThermalFanControl.mo
python -m veph export-fmi-metadata examples/toy_thermal_fan_control.mbd.md --out generated/toy_thermal_fan_control.fmi.json
python -m veph export-code-preview examples/toy_thermal_fan_control.mbd.md --out generated/ecu_preview/
python -m veph run-preview --model examples/toy_thermal_fan_control.mbd.md --scenario scenarios/thermal_fan_normal.yml --report reports/thermal_fan_normal.md
python -m veph run-preview --model examples/toy_thermal_fan_control.mbd.md --scenario scenarios/thermal_fan_fault.yml --report reports/thermal_fan_fault.md
pytest
```

## Phase 0: Requirements Baseline

Requirement coverage: `PROC-001`, `PROC-002`

- [x] Add `Requirements.md` with the fictional control-system intent.
- [x] Add explicit ASPICE-aware but non-compliance process language.
- [x] Add scenario YAML boundary: test input only, not MBD source of truth.
- [x] Review `Requirements.md` with the user and adjust the fictional control
      intent if needed.
- [x] Confirm requirement IDs cover stakeholder, system, software, MBD handoff,
      harness, and process needs.
- [x] Confirm the example remains fictional and does not resemble a real IC
      datasheet or production ECU specification.
- [x] Confirm ASPICE is treated as process inspiration only, with no compliance,
      certification, or tool qualification claim.

Verification:

- [x] `Requirements.md` has stable requirement IDs.
- [x] `Requirements.md` defines review gates and planned evidence.
- [x] `Tasks.md` maps implementation phases back to requirements.

## Phase 1: Human-Readable Specification

Requirement coverage: `STK-001`, `STK-005`, `SYS-001` - `SYS-006`

- [x] Add `specs/toy_thermal_fan_control.md` as a specification derived from
      `Requirements.md`.
- [x] Describe the fictional IC-facing behavior without real datasheet details.
- [x] Include trace links from specification sections back to requirement IDs.
- [x] Define the PDCA/TDD review path from specification to MBD artifacts and
      harness reports.

Verification:

- [x] Specification has no untraced system behavior.
- [x] Specification preserves the fictional-only and preview-only boundaries.

## Phase 2: Markup From Specification

Requirement coverage: `STK-001`, `SWE-001`

- [x] Add `examples/toy_thermal_fan_control.mbd.md`.
- [x] Use `Requirements.md` IDs and specification anchors in markup comments or
      trace fields.
- [x] Include fictional `ToyTempSensorIC`, `ToyFanDriverIC`, and
      `ToyThermalFanController` only.
- [x] Define component, register, state, flow, control, and optional harness
      sections only where they support stated requirements.
- [x] Define `temperatureC`, `fanDuty`, `fault`, `fanOnThreshold`,
      `fanOffThreshold`, and `safeDuty`.

Verification:

- [x] Parser reads the new markup file.
- [x] IR contains traceable components, ports, registers, states, flows, and
      control rules.
- [x] No YAML source is required for the example.

## Phase 3: Parser And IR Traceability

Requirement coverage: `SWE-002`, `SWE-003`, `PROC-003`

- [x] Add or refine IR structures for multiple components, control rules,
      harness devices, and requirement references.
- [x] Parse deterministic rule blocks from markup.
- [x] Keep IR documented as an internal tooling snapshot, not a public standard.

Verification:

- [x] Parser tests cover valid and malformed control/trace blocks.
- [x] IR snapshot tests prove stable ordering and requirement references.

## Phase 4: MBD Handoff Artifact Exporters

Requirement coverage: `STK-002`, `MBD-001` - `MBD-007`

- [x] Update Markdown exporter to show requirements, control logic, and harness
      boundaries.
- [x] Update Mermaid and PlantUML exporters to show control/data flow and
      controller states.
- [x] Update Simulink `.m` exporter with model, block, line, parameter, compare,
      switch, and subsystem generation where appropriate.
- [x] Update Modelica, SCXML/Stateflow-oriented, and FMI metadata exporters with
      ports, parameters, states, signal names, and preview variables.

Verification:

- [x] Each generated artifact is non-empty and deterministic from markup.
- [x] Simulink script contains `new_system`, `open_system`, `add_block`,
      `add_line`, and `set_param`.
- [x] FMI metadata clearly says no FMU is generated.

## Phase 5: Preview Harness And Scenarios

Requirement coverage: `STK-004`, `HAR-001` - `HAR-005`

- [x] Add preview-only harness modules under `src/veph/preview_runtime/`.
- [x] Implement minimal fictional `ToyTempSensorIC` and `ToyFanDriverIC`
      behavior at virtual IC boundaries.
- [x] Keep ECU logic behind HAL-style boundaries; do not call Python internals
      from product-like controller logic.
- [x] Add normal and fault scenario YAML files as test inputs only, with
      discrete steps only.

Verification:

- [x] Normal scenario reads temperature and commands fan duty.
- [x] Fault scenario triggers safe duty.
- [x] Reports separate model inputs, scenario steps, observed behavior,
      expected behavior, and pass/fail result.

## Phase 6: Preview C Code Generation

Requirement coverage: `STK-003`, `SWE-004`, `SWE-005`

- [x] Add `export-code-preview`.
- [x] Generate `controller.c`, `controller.h`, `hal_spi.h`, `hal_pwm.h`, and a
      preview README under `generated/ecu_preview/`.
- [x] Mark generated C as preview-only, synthetic, and non-certified.

Verification:

- [x] Generated C contains controller states and threshold logic.
- [x] Generated C includes HAL headers rather than Python bindings.
- [x] If a local C compiler is available, syntax-check the generated scaffold.

## Phase 7: PDCA/TDD Closure

Requirement coverage: `STK-005`, `PROC-003`, `PROC-004`

- [x] Add deterministic regeneration tests for all generated artifacts.
- [x] Update README with the requirements-first thermal fan validation path.
- [x] Update `docs/design_principles.md` if policy language changes.
- [x] Keep project-local skills under `.agents/skills/` aligned with the
      implementation.
- [x] Refactor after tests are green, keeping behavior-preserving changes
      separate where practical.

Verification:

- [x] `pytest` passes.
- [x] Project philosophy tests confirm markup is public source, YAML is not the
      public source of truth, MBD tools are verification backends, and preview
      code generation is not certified.

## Risks To Watch

- [x] Skipping requirements and jumping straight into markup or runtime work.
- [x] Accidentally turning Python preview into the main verifier.
- [x] Accidentally making YAML central again.
- [x] Over-designing a new modeling language instead of staying Mermaid-like.
- [x] Making fictional hardware too realistic.
- [x] Mixing preview C generation with certified code generation claims.
