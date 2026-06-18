# Tasks

This is the active human/LLM progress ledger. Keep it concise; if it grows
beyond 200 lines, move completed or historical detail into `docs/archive/` and
leave links here.

Archived task history:

- [Thermal Fan Validation Task Archive](docs/archive/thermal_fan_validation_tasks.md)
- [Requirements To MBD Demo Task Archive](docs/archive/requirements_to_mbd_demo_tasks.md)

## Current Goal

Improve the thermal protection MBD so state/control behavior has one reviewable
control semantics instead of competing `mbd-state`, `mbd-control`, preview
runtime, and generated C behavior.

## Quality Gates

- [x] `mbd-control` rows expose priority, state scope, guard, actions, trace,
      and scenario evidence.
- [x] `mbd-state` is documented as a lifecycle/topology view derived from the
      same control semantics, not a competing executable source.
- [x] Preview runtime selects rules by explicit priority and state scope, not
      hidden list ordering.
- [x] Generated Markdown, HTML, Mermaid, SCXML, Modelica, Simulink `.m`, FMI
      metadata, preview C, and reports are regenerated from `.mbd.md`.
- [x] Tests prove deterministic regeneration and reject missing control
      semantics.

## Phase 12: Thermal Protection Control Semantics

- [x] Add parser/IR fields for control priority, state scope, and scenario
      evidence while keeping older examples compatible.
- [x] Update the thermal protection `.mbd.md` source to use priority-based
      control rows.
- [x] Update exporters and demo HTML to show the control decision table as the
      first behavior review view.
- [x] Update preview runtime and generated preview C to follow the same
      priority order.
- [x] Align `SYS-009` scenario coverage between requirements, spec, demo HTML,
      and reports.
- [x] Regenerate generated artifacts and reports.

Verification:

- [x] Focused parser/exporter/runtime/codegen tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.
