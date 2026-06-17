# Design Principles

This document defines the project philosophy for the Virtual ECU Peripheral
Harness MVP. It is intentionally small and practical: the repository should stay
usable without commercial MBD tools, without real hardware data, and without
turning the runtime into a full simulator.

## Textual MBD

Textual MBD means the model is written in a human-readable and LLM-readable text
format. In this MVP, the canonical model is YAML under `specs/`.

The YAML describes the fictional peripheral interface, registers, state machine,
signals, functional blocks, block ports, connections, faults, and timing. The
runtime and exporters consume that same YAML. No generated binary model, `.slx`
file, tool project, or exported script is the source of truth.

## Source-Of-Truth Policy

The Textual MBD YAML file is the canonical source. For the sample peripheral,
that file is `specs/toy_power_monitor.tmbd.yml`.

Changes to model behavior should be made in the YAML first, then validated and
regenerated through the CLI. Generated artifacts must not become canonical source.
They may be checked into the repository for inspection or examples, but they are
not the model change workflow.

## Generated Artifact Policy

Markdown, static HTML demos, PlantUML, SCXML, Modelica, and Simulink `.m` files
are generated outputs. They should be reproducible from the same YAML input.

Generated files may be useful for review, documentation, and handoff to optional
tools, but manual edits to generated files are not the model change workflow. If
a generated artifact is wrong, fix the YAML or exporter and regenerate it.

## Virtual Peripheral Boundary

The harness replaces the hardware boundary with virtual peripherals. It models
fictional register-level behavior well enough for scenario tests, documentation,
and export demonstrations.

The MVP does not model electrical waveforms, analog physics, timing closure, bus
contention, or real device quirks. It intentionally uses fictional components
and synthetic examples only.

## Product-Like ECU Code Boundary

Product-like ECU code stays unchanged. Only the hardware boundary is replaced by
virtual peripherals.

The sample C code under `ecu_app/` uses HAL-style SPI and GPIO interfaces. It is
written to look like embedded application code, but it is not production-derived
and must not include real company code, real project names, real register maps,
or real IC details. The Python harness must not ask the ECU logic to call Python
internals for simulation convenience.

## Commercial-Tool-Free MVP Policy

The MVP must run with Python, pytest, and minimal Python dependencies. MATLAB,
Simulink, Modelica tools, FMI tools, Docker, cloud services, and commercial MBD
licenses are not required to validate, run, test, or regenerate the MVP.

Commercial MBD tools are optional export consumers, not runtime dependencies.

## Future Export Direction

Future Simulink, Modelica, and FMI work should remain export-oriented. The
project may generate richer `.m`, `.mo`, FMU metadata, or FMI-compatible
intermediate files, but the direction stays the same: Textual MBD YAML remains
canonical, and tool-specific artifacts remain generated outputs.
