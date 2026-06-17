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
  -> specs/*.md
examples/*.mbd.md
  -> markup parser
  -> internal IR snapshot
  -> exporters
      -> Markdown review document
      -> Mermaid / PlantUML preview diagrams
      -> Simulink model-generation .m script
      -> SCXML state-machine handoff
      -> Modelica .mo text artifact
      -> FMI-oriented metadata stub
  -> optional Python preview only
```

The public authoring source is Markdown with Mermaid-like fenced blocks, such as
[examples/toy_power_monitor.mbd.md](examples/toy_power_monitor.mbd.md). The IR
JSON is an internal snapshot for tooling. YAML files, where present, are legacy
or optional machine-readable forms, not the public source of truth.

For larger validation examples, start from [Requirements.md](Requirements.md),
derive a human-readable specification under `specs/`, then author the MBD markup.
The project uses ASPICE-aware habits such as requirement IDs, traceability,
review gates, and reproducible evidence, but it does not claim ASPICE
compliance, safety certification, or tool qualification.

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

The requirements-traceable validation example is `ToyThermalFanController`,
with fictional `ToyTempSensorIC` and `ToyFanDriverIC` harness boundaries. It
demonstrates readable requirements, a human-readable specification, MBD markup,
generated handoff artifacts, preview-only generated C, and scenario reports.

The sample C files under `ecu_app/` are product-like but synthetic. They use
HAL-style boundaries and are not production-derived.

## Commands

```bash
python -m veph parse examples/toy_power_monitor.mbd.md --out generated/toy_power_monitor.ir.json
python -m veph export-docs examples/toy_power_monitor.mbd.md --out generated/toy_power_monitor.md
python -m veph export-mermaid examples/toy_power_monitor.mbd.md --out generated/toy_power_monitor.mmd
python -m veph export-plantuml examples/toy_power_monitor.mbd.md --out generated/toy_power_monitor.puml
python -m veph export-simulink-m examples/toy_power_monitor.mbd.md --out generated/create_toy_power_monitor_model.m
python -m veph export-modelica examples/toy_power_monitor.mbd.md --out generated/ToyPowerMonitor.mo
python -m veph export-fmi-metadata examples/toy_power_monitor.mbd.md --out generated/toy_power_monitor.fmi.json
pytest
```

Thermal fan validation commands:

```bash
python -m veph parse examples/toy_thermal_fan_control.mbd.md --out generated/toy_thermal_fan_control.ir.json
python -m veph export-mermaid examples/toy_thermal_fan_control.mbd.md --out generated/toy_thermal_fan_control.mmd
python -m veph export-simulink-m examples/toy_thermal_fan_control.mbd.md --out generated/create_toy_thermal_fan_control_model.m
python -m veph export-code-preview examples/toy_thermal_fan_control.mbd.md --out generated/ecu_preview/
python -m veph run-preview --model examples/toy_thermal_fan_control.mbd.md --scenario scenarios/thermal_fan_normal.yml --report reports/thermal_fan_normal.md
python -m veph run-preview --model examples/toy_thermal_fan_control.mbd.md --scenario scenarios/thermal_fan_fault.yml --report reports/thermal_fan_fault.md
pytest
```

Legacy YAML preview commands may still exist while the project transitions, but
new examples and public documentation should use `examples/*.mbd.md`.

## Generated Artifacts

- `generated/toy_power_monitor.ir.json`: internal IR snapshot, not a public standard
- `generated/toy_power_monitor.md`: review document with source-section traceability
- `generated/toy_power_monitor.mmd`: Mermaid preview diagram
- `generated/toy_power_monitor.puml`: PlantUML state preview
- `generated/create_toy_power_monitor_model.m`: plausible Simulink API handoff script
- `generated/ToyPowerMonitor.mo`: readable Modelica text artifact
- `generated/toy_power_monitor.fmi.json`: FMI-oriented metadata stub
- `generated/toy_thermal_fan_control.mmd`: requirements-traceable Mermaid data-flow preview
- `generated/ecu_preview/`: preview-only synthetic ECU C scaffold
- `reports/thermal_fan_normal.md`: preview report with separated inputs, steps,
  observed behavior, generated ECU command outputs, expected behavior, and result

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
