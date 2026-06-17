# Tasks

This is the proposed breakdown for the next Goal. Review and adjust this file
before asking an agent to execute it end to end.

## Goal

Build a fictional end-to-end validation case proving this repository can go from
Mermaid-like markup to MBD handoff artifacts, virtual IC harness preview, and
preview-only ECU C code generation.

Working example:

```text
Toy Thermal Fan Control System
```

Fictional components:

- `ToyTempSensorIC`
- `ToyFanDriverIC`
- `ToyThermalFanController`

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

## Phase 1: Markup Spec

- Add `examples/toy_thermal_fan_control.mbd.md`.
- Include fictional component descriptions only.
- Extend markup usage with sections for:
  - `mbd-component`
  - `mbd-registers`
  - `mbd-state`
  - `mbd-flow`
  - `mbd-control`
  - optional `mbd-harness`
- Define at least:
  - input `temperatureC`
  - output `fanDuty`
  - output `fault`
  - parameter `fanOnThreshold`
  - parameter `fanOffThreshold`
  - parameter `safeDuty`
- Add fictional registers for `ToyTempSensorIC` and `ToyFanDriverIC`.
- Add normal and fault controller states.

Acceptance tests:

- Parser reads the new markup file.
- IR contains components, ports, registers, states, transitions, flows, and
  control rules.
- No YAML source is required for the example.

## Phase 2: Parser And IR

- Add IR structures for:
  - multiple components/peripherals
  - control rules
  - harness devices
  - scenarios or scenario bindings, if needed
- Parse `mbd-control` into simple control-rule IR.
- Keep the IR internal and exporter-oriented.

Acceptance tests:

- `mbd-control` parses deterministic rule blocks.
- Parser errors are clear for malformed blocks.
- IR JSON says it is an internal snapshot, not a public standard.

## Phase 3: MBD Artifact Exporters

- Update Markdown exporter to include control logic and harness boundaries.
- Update Mermaid exporter to show control/data flow.
- Update PlantUML or SCXML exporter to show controller mode states.
- Update Simulink `.m` exporter to include plausible:
  - `new_system`
  - `open_system`
  - `add_block`
  - `add_line`
  - `set_param`
  - threshold compare / switch / subsystem blocks
- Update Modelica exporter with ports, parameters, states, and signal names.
- Update FMI metadata exporter with inputs, outputs, parameters, states, and
  preview variables.

Acceptance tests:

- Each generated artifact is non-empty.
- Each generated artifact is deterministic from markup.
- Simulink script contains block and line creation commands.
- Modelica contains expected component and signal names.
- FMI metadata clearly says no FMU is generated.

## Phase 4: Virtual IC Harness Preview

- Add preview-only harness modules under `src/veph/preview_runtime/`.
- Implement minimal fictional devices:
  - `ToyTempSensorIC`
  - `ToyFanDriverIC`
- Add virtual bus/HAL boundary helpers.
- Keep runtime simple: discrete scenario steps only, no physics solver.
- Label all preview runtime docs and reports as preview-only.

Acceptance tests:

- Normal scenario reads temperature and commands fan duty.
- Fault scenario triggers safe duty.
- Product-like ECU logic does not call Python internals directly.

## Phase 5: Preview C Code Generation

- Add `export-code-preview`.
- Generate files under `generated/ecu_preview/`, for example:
  - `controller.c`
  - `controller.h`
  - `hal_spi.h`
  - `hal_pwm.h`
  - `README.md`
- Generated C must use HAL-style boundaries.
- Generated C must be explicitly marked preview-only and non-certified.

Acceptance tests:

- Generated C contains controller states and threshold logic.
- Generated C includes HAL headers rather than Python bindings.
- If a local C compiler is available, syntax-check the generated scaffold.

## Phase 6: Preview Scenario Runner

- Add `run-preview`.
- Add scenarios:
  - `scenarios/thermal_fan_normal.yml`
  - `scenarios/thermal_fan_fault.yml`
- Reports should separate:
  - markup source
  - scenario inputs
  - virtual IC observations
  - generated ECU command outputs
  - expected behavior
  - pass/fail result

Acceptance tests:

- Normal scenario passes.
- Fault scenario passes.
- Reports state that Python is preview-only.

## Phase 7: Documentation And Guardrails

- Update README with the new thermal fan validation path.
- Update `docs/design_principles.md` if any policy changes are needed.
- Keep `AGENTS.md` aligned with the implementation.
- Add a short note explaining the two code generation routes:
  - MBD tool-backed route
  - local preview-only route

Acceptance tests:

- Project philosophy tests confirm:
  - `examples/*.mbd.md` is public source
  - YAML is not public source of truth
  - existing MBD tools are verification backends
  - preview code generation is not certified

## Risks To Watch

- Accidentally turning Python preview into the main verifier.
- Accidentally making YAML central again.
- Over-designing a new modeling language instead of staying Mermaid-like.
- Making fake hardware too realistic or resembling a real datasheet.
- Mixing preview C generation with certified/codegen claims.

