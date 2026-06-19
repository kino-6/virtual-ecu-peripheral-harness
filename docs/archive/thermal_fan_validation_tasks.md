# Thermal Fan Validation Task Archive

Archived from `Tasks.md` after completing the first Toy Thermal Fan validation
goal on branch `codex/thermal-fan-validation`.

Related commits:

- `3de5cd6 Add requirements traced thermal fan validation`
- `c7e14f8 Improve thermal fan preview evidence`

Completed scope:

- Requirements-first baseline in `Requirements.md`.
- Human-readable specification in `samples/thermal_fan_control/spec.md`.
- Traceable MBD markup in `samples/thermal_fan_control/model.mbd.md`.
- Parser and IR support for requirement refs, control rules, and harness
  devices.
- Generated Markdown, Mermaid, PlantUML, SCXML, Simulink `.m`, Modelica, FMI
  metadata, demo HTML, and preview ECU C scaffold.
- Preview normal and fault scenarios with reports.
- Deterministic regeneration tests and preview runtime/codegen tests.

Post-goal lesson:

The first pass satisfied commands and tests but did not sufficiently align with
the user's expected artifact quality. Future substantial validation work must
start with expectation alignment, human QA, and explicit quality gates before
implementation.
