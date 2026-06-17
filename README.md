# Virtual ECU Peripheral Harness

Textual MBD as the source of truth, with optional exports to Simulink,
Modelica, and FMI.

This repository is a Python-based MVP for building executable virtual peripheral
models from human-readable and LLM-readable text files. It is not a Simulink replacement, a full ECU simulator, or a physical electrical solver.

## What This Project Is

The harness keeps model intent in plain text, then generates useful artifacts
from that source:

- executable virtual peripheral behavior
- MBD-style functional block and signal-flow views
- Markdown documentation
- PlantUML state diagrams
- SCXML state machines
- readable Modelica text models
- best-effort MATLAB/Simulink `.m` generation scripts

The first sample peripheral is `ToyPowerMonitorIC`, a fictional SPI power monitor
with `STATUS`, `CONTROL`, `FAULT`, `VOLTAGE`, and `RESET_CAUSE` registers.

This repository uses fictional components and synthetic examples only. It does
not contain proprietary data, real IC specifications, production ECU code, or
confidential project information.

## What This Project Is Not

This MVP does not implement a commercial MBD workflow, a Simulink-compatible
runtime, a complete ECU simulator, a physics engine, an FMI toolchain, or a
production embedded test bench. Commercial MBD tools are optional export targets, not runtime dependencies.

## Why Textual MBD

The canonical model is the YAML file under `specs/`, not a generated binary or a
tool-owned project file. Textual MBD keeps the model:

- readable in code review
- editable without commercial licenses
- friendly to LLM-assisted inspection and generation
- easy to diff, test, and regenerate
- portable across documentation and MBD-compatible export formats

Generated Markdown, PlantUML, SCXML, Modelica, and Simulink `.m` files are
reproducible from the same YAML. If a generated file is wrong, update the YAML
or exporter and regenerate it; do not treat generated artifacts as source.

For the demo, the YAML also contains `blocks` and `connections`. These describe
functional blocks, typed ports, and signal lines so the HTML view looks like an
MBD block diagram rather than a hand-authored picture.

For the full policy, see [docs/design_principles.md](docs/design_principles.md).

## ECU Boundary Rule

Product-like ECU code stays unchanged. Only the hardware boundary is replaced by
virtual peripherals.

The sample C code in `ecu_app/` talks through HAL-like SPI and GPIO interfaces:

- `ecu_app/app.c`
- `ecu_app/diagnostics.c`
- `ecu_app/hal_spi.h`
- `ecu_app/hal_gpio.h`

The Python harness simulates the peripheral boundary rather than asking the
sample ECU logic to know about Python internals.

## Repository Layout

```text
specs/       Textual MBD YAML and synthetic manual docs
scenarios/   Scenario YAML files used by the interpreter
src/veph/    Python package, CLI, runtime, and exporters
ecu_app/     Tiny product-like C sample using HAL boundaries
generated/   Generated docs and MBD-compatible artifacts
reports/     Scenario run reports
tests/       Pytest coverage for loader, runtime, scenarios, exporters
```

## Run The MVP

The repo uses Python 3.11+ and `PyYAML`. For a local editable install:

```bash
python -m pip install -e ".[dev]"
```

From the repository root, these commands validate the model, run scenarios, and
generate artifacts:

```bash
python -m veph validate specs/toy_power_monitor.tmbd.yml
python -m veph run --model specs/toy_power_monitor.tmbd.yml --scenario scenarios/normal_startup.yml --report reports/normal_startup.md
python -m veph run --model specs/toy_power_monitor.tmbd.yml --scenario scenarios/undervoltage_fault.yml --report reports/undervoltage_fault.md
python -m veph run --model specs/toy_power_monitor.tmbd.yml --scenario scenarios/spi_timeout.yml --report reports/spi_timeout.md
python -m veph export-docs --model specs/toy_power_monitor.tmbd.yml --out generated/toy_power_monitor.md
python -m veph export-demo --model specs/toy_power_monitor.tmbd.yml --out generated/demo.html
python -m veph export-plantuml --model specs/toy_power_monitor.tmbd.yml --out generated/toy_power_monitor.puml
python -m veph export-scxml --model specs/toy_power_monitor.tmbd.yml --out generated/toy_power_monitor.scxml
python -m veph export-modelica --model specs/toy_power_monitor.tmbd.yml --out generated/ToyPowerMonitor.mo
python -m veph export-simulink-m --model specs/toy_power_monitor.tmbd.yml --out generated/create_toy_power_monitor_model.m
pytest
```

The included root-level `veph` shim also makes `python -m veph` work directly
from a source checkout when running from the repo root.

## Generated Artifacts

- `reports/*.md`: scenario execution reports separated into model inputs, scenario steps, observed behavior, expected behavior, and pass/fail result
- `generated/toy_power_monitor.md`: human-readable peripheral documentation
- `generated/demo.html`: static MBD visualization demo with state-machine and data-flow views
- `generated/toy_power_monitor.puml`: PlantUML state diagram
- `generated/toy_power_monitor.scxml`: minimal SCXML state-machine export
- `generated/ToyPowerMonitor.mo`: readable Modelica-compatible text artifact
- `generated/create_toy_power_monitor_model.m`: best-effort MATLAB/Simulink script

These files are generated from `specs/toy_power_monitor.tmbd.yml`. They are not
the canonical model source.

## Current Limitations

- The YAML schema is intentionally small and validated with lightweight Python checks.
- State transition expressions support only simple comparisons such as `voltage < undervoltageThreshold`.
- The runtime is discrete-step only and does not solve continuous physics.
- SPI behavior is modeled at register transaction level, not waveform level.
- Modelica and Simulink outputs are readable compatibility artifacts, not verified tool projects.
- No MATLAB, Simulink, OpenModelica, FMI tooling, Docker, or external service is required.

## Roadmap

- Add schema versioning and stricter diagnostics.
- Add richer register field semantics and access policies.
- Generate Mermaid diagrams alongside PlantUML.
- Add FMI-oriented text metadata and optional exporter stubs.
- Add C HAL adapter examples that bind the sample ECU code to the Python runtime.
- Add more fictional peripherals and multi-peripheral scenarios.
