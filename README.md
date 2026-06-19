# Virtual ECU Peripheral Harness

Author in text. Verify in MBD tools.

Mermaid-like Markup for virtual ECU and peripheral model authoring.

This repository is a lightweight Markup-to-MBD bridge. It lets humans and LLMs
author small virtual ECU/peripheral models in readable Markdown, then generates
handoff artifacts for review and existing MBD tools.

It is not a Simulink replacement. It is not a new certified MBD language. It is
not a custom MBD runtime. It does not claim certification.

## Direction

The intended pipeline is:

```text
Requirements.md
  -> samples/<sample-id>/spec.md
samples/<sample-id>/sample.yml
samples/<sample-id>/model.mbd.md
  -> markup parser
  -> internal IR snapshot
  -> samples/<sample-id>/generated/
      -> Markdown review document
      -> Mermaid / PlantUML preview diagrams
      -> Simulink model-generation .m script
      -> SCXML state-machine handoff
      -> Modelica .mo text artifact
      -> FMI-oriented metadata stub
  -> optional Python preview only under samples/<sample-id>/reports/
```

The public authoring source is Markdown with Mermaid-like fenced blocks, such as
[samples/toy_power_monitor/model.mbd.md](samples/toy_power_monitor/model.mbd.md).
Each sample owns a `sample.yml` manifest that declares its source, scenarios,
generated artifacts, reports, and preview C output. The IR JSON is an internal
snapshot for tooling. YAML files, where present, are legacy or optional
machine-readable forms, not the public source of truth.

For larger validation examples, start from [Requirements.md](Requirements.md),
derive a human-readable specification under `samples/<sample-id>/spec.md`, then
author the MBD markup. The project uses ASPICE-aware habits such as requirement
IDs, traceability, review gates, and reproducible evidence, but it does not
claim ASPICE compliance, safety certification, or tool qualification.

## What This Project Is

- A compact text authoring layer for virtual ECU/peripheral models
- A generator for MBD-oriented handoff artifacts
- A review-friendly bridge between LLM-readable markup and existing MBD tools
- A commercial-tool-free authoring workflow that can export to commercial tools
  when available

## What This Project Is Not

- Not a Simulink, Stateflow, Modelica, or FMI replacement
- Not a certified workflow
- Not a production ECU simulator
- Not a physical electrical solver
- Not a real IC, datasheet, ECU, or company-specific model repository

## Python Preview Boundary

Python preview is only a preview/smoke-test helper. Existing MBD tools are the
intended verification backends.

The Python code may parse markup, generate artifacts, and run lightweight smoke
checks, but it must not be presented as the main verification path.

## Fictional Example

The sample component is `ToyPowerMonitorIC`, a fictional SPI peripheral used to
exercise the pipeline. It does not describe a real IC, real datasheet, real ECU
specification, real register map, or production-derived project.

The complete business-process demo is `ToyThermalProtectionController`, with
fictional `ToyTempSensorIC`, `ToyFanDriverIC`, and `ToyLoadLimiterIC` harness
boundaries. It demonstrates readable requirements, a human-readable
specification, Mermaid-like MBD markup, generated handoff artifacts,
preview-only generated C, and scenario reports. Demo threshold values are
explicit assumptions, not real product answers.

The sample C files under `ecu_app/` are product-like but synthetic. They use
HAL-style boundaries and are not production-derived.

## Commands

```bash
python -m veph list-samples
python -m veph export-sample toy_power_monitor
python -m veph export-sample thermal_fan_control
python -m veph export-sample thermal_protection_controller
pytest
```

Preview scenario examples:

```bash
python -m veph run-preview \
  --model samples/thermal_fan_control/model.mbd.md \
  --scenario samples/thermal_fan_control/scenarios/normal.yml \
  --report samples/thermal_fan_control/reports/normal.md

python -m veph run-preview \
  --model samples/thermal_protection_controller/model.mbd.md \
  --scenario samples/thermal_protection_controller/scenarios/derating.yml \
  --report samples/thermal_protection_controller/reports/derating.md
```

Legacy YAML preview commands may still exist, but new samples and public
documentation should use `samples/<sample-id>/model.mbd.md`.

## Sample Workspace Layout

```text
samples/<sample-id>/
  sample.yml        # manifest and local path contract
  model.mbd.md      # public MBD authoring source
  spec.md           # optional human-readable sample specification
  scenarios/        # preview scenario inputs
  generated/        # reproducible handoff/review artifacts
  reports/          # reproducible preview reports
  preview_c/        # preview-only generated C when supported
  legacy/           # optional compatibility YAML, not source of truth
```

## Generated Artifacts

- `samples/toy_power_monitor/generated/`: internal IR, review docs, diagrams,
  Simulink `.m`, Modelica `.mo`, SCXML, and FMI metadata for the compact sample.
- `samples/simple_threshold_indicator/`: intentionally tiny one-input,
  one-threshold, one-output MBD sample for checking the workflow shape.
- `samples/thermal_fan_control/generated/`: MBD handoff artifacts for the small
  thermal control validation sample.
- `samples/thermal_fan_control/preview_c/`: preview-only synthetic ECU C
  scaffold for that sample.
- `samples/thermal_protection_controller/generated/`: reviewable process-demo
  handoff artifacts.
- `samples/thermal_protection_controller/reports/`: preview reports with
  separated inputs, steps, observed behavior, expected behavior, and result.
- `samples/thermal_protection_controller/preview_c/`: preview-only synthetic ECU
  C scaffold for the process demo.

These files are generated from the Markdown markup source. If an artifact is
wrong, update the markup or exporter and regenerate.

## Current Limitations

- The markup syntax is intentionally small and experimental.
- Simulink, Modelica, SCXML, and FMI outputs are handoff artifacts, not certified
  generated models.
- The FMI output is metadata only; no FMU is generated.
- No MATLAB, Simulink, OpenModelica, FMI tools, Docker, or external service is
  required for authoring or tests.

## Roadmap

- Tighten the markup grammar and diagnostics.
- Add stronger source-to-artifact traceability.
- Add Stateflow-oriented tables alongside SCXML.
- Improve Simulink block layout and signal naming.
- Expand FMI metadata toward future FMU generation without making Python the
  verifier.
