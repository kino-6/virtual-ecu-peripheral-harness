# Tasks

This is the proposed breakdown for the next Goal. Review and adjust this file
before asking an agent to execute it end to end.

Maintenance rule: if this file grows beyond 200 lines, move completed or
historical detail into `docs/archive/` and leave only a short summary plus links
here.

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

- [ ] Add `examples/toy_thermal_fan_control.mbd.md`.
- [ ] Include fictional component descriptions only.
- [ ] Extend markup usage with `mbd-component`.
- [ ] Extend markup usage with `mbd-registers`.
- [ ] Extend markup usage with `mbd-state`.
- [ ] Extend markup usage with `mbd-flow`.
- [ ] Extend markup usage with `mbd-control`.
- [ ] Decide whether `mbd-harness` is needed and add it only if it helps the
      preview harness.
- [ ] Define input `temperatureC`.
- [ ] Define output `fanDuty`.
- [ ] Define output `fault`.
- [ ] Define parameter `fanOnThreshold`.
- [ ] Define parameter `fanOffThreshold`.
- [ ] Define parameter `safeDuty`.
- [ ] Add fictional registers for `ToyTempSensorIC`.
- [ ] Add fictional registers for `ToyFanDriverIC`.
- [ ] Add normal and fault controller states.

Acceptance tests:

- [ ] Parser reads the new markup file.
- [ ] IR contains components, ports, registers, states, transitions, flows, and
      control rules.
- [ ] No YAML source is required for the example.

## Phase 2: Parser And IR

- [ ] Add IR structures for multiple components/peripherals.
- [ ] Add IR structures for control rules.
- [ ] Add IR structures for harness devices.
- [ ] Add scenario or scenario-binding IR only if needed.
- [ ] Parse `mbd-control` into simple control-rule IR.
- [ ] Keep the IR internal and exporter-oriented.

Acceptance tests:

- [ ] `mbd-control` parses deterministic rule blocks.
- [ ] Parser errors are clear for malformed blocks.
- [ ] IR JSON says it is an internal snapshot, not a public standard.

## Phase 3: MBD Artifact Exporters

- [ ] Update Markdown exporter to include control logic and harness boundaries.
- [ ] Update Mermaid exporter to show control/data flow.
- [ ] Update PlantUML or SCXML exporter to show controller mode states.
- [ ] Update Simulink `.m` exporter to include `new_system`.
- [ ] Update Simulink `.m` exporter to include `open_system`.
- [ ] Update Simulink `.m` exporter to include `add_block`.
- [ ] Update Simulink `.m` exporter to include `add_line`.
- [ ] Update Simulink `.m` exporter to include `set_param`.
- [ ] Update Simulink `.m` exporter to include threshold compare / switch /
      subsystem blocks.
- [ ] Update Modelica exporter with ports, parameters, states, and signal names.
- [ ] Update FMI metadata exporter with inputs, outputs, parameters, states, and
      preview variables.

Acceptance tests:

- [ ] Each generated artifact is non-empty.
- [ ] Each generated artifact is deterministic from markup.
- [ ] Simulink script contains block and line creation commands.
- [ ] Modelica contains expected component and signal names.
- [ ] FMI metadata clearly says no FMU is generated.

## Phase 4: Virtual IC Harness Preview

- [ ] Add preview-only harness modules under `src/veph/preview_runtime/`.
- [ ] Implement minimal fictional device `ToyTempSensorIC`.
- [ ] Implement minimal fictional device `ToyFanDriverIC`.
- [ ] Add virtual bus/HAL boundary helpers.
- [ ] Keep runtime simple: discrete scenario steps only, no physics solver.
- [ ] Label all preview runtime docs and reports as preview-only.

Acceptance tests:

- [ ] Normal scenario reads temperature and commands fan duty.
- [ ] Fault scenario triggers safe duty.
- [ ] Product-like ECU logic does not call Python internals directly.

## Phase 5: Preview C Code Generation

- [ ] Add `export-code-preview`.
- [ ] Generate `generated/ecu_preview/controller.c`.
- [ ] Generate `generated/ecu_preview/controller.h`.
- [ ] Generate `generated/ecu_preview/hal_spi.h`.
- [ ] Generate `generated/ecu_preview/hal_pwm.h`.
- [ ] Generate `generated/ecu_preview/README.md`.
- [ ] Generated C must use HAL-style boundaries.
- [ ] Generated C must be explicitly marked preview-only and non-certified.

Acceptance tests:

- [ ] Generated C contains controller states and threshold logic.
- [ ] Generated C includes HAL headers rather than Python bindings.
- [ ] If a local C compiler is available, syntax-check the generated scaffold.

## Phase 6: Preview Scenario Runner

- [ ] Add `run-preview`.
- [ ] Add `scenarios/thermal_fan_normal.yml`.
- [ ] Add `scenarios/thermal_fan_fault.yml`.
- [ ] Reports separate markup source.
- [ ] Reports separate scenario inputs.
- [ ] Reports separate virtual IC observations.
- [ ] Reports separate generated ECU command outputs.
- [ ] Reports separate expected behavior.
- [ ] Reports separate pass/fail result.

Acceptance tests:

- [ ] Normal scenario passes.
- [ ] Fault scenario passes.
- [ ] Reports state that Python is preview-only.

## Phase 7: Documentation And Guardrails

- [ ] Update README with the new thermal fan validation path.
- [ ] Update `docs/design_principles.md` if any policy changes are needed.
- [ ] Keep `AGENTS.md` aligned with the implementation.
- [ ] Keep project-local skills under `.agents/skills/` aligned with the
      implementation.
- [ ] Add a short note explaining the MBD tool-backed code generation route.
- [ ] Add a short note explaining the local preview-only code generation route.

Acceptance tests:

- [ ] Project philosophy tests confirm `examples/*.mbd.md` is public source.
- [ ] Project philosophy tests confirm YAML is not public source of truth.
- [ ] Project philosophy tests confirm existing MBD tools are verification
      backends.
- [ ] Project philosophy tests confirm preview code generation is not certified.

## Risks To Watch

- [ ] Accidentally turning Python preview into the main verifier.
- [ ] Accidentally making YAML central again.
- [ ] Over-designing a new modeling language instead of staying Mermaid-like.
- [ ] Making fake hardware too realistic or resembling a real datasheet.
- [ ] Mixing preview C generation with certified/codegen claims.
