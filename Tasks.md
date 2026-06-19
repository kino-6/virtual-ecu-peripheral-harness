# Tasks

This is the active human/LLM progress ledger. Keep it concise; if it grows
beyond 200 lines, move completed or historical detail into `docs/archive/` and
leave links here.

Archived task history:

- [Thermal Fan Validation Task Archive](docs/archive/thermal_fan_validation_tasks.md)
- [Requirements To MBD Demo Task Archive](docs/archive/requirements_to_mbd_demo_tasks.md)

## Current Goal

Create a semantic MBD export quality contract and improve the Simulink handoff
exporter so supported thermal protection control rules are structurally
represented, not only preserved as comments.

## Quality Gates

- [x] Contract distinguishes review-only artifact, semantic handoff artifact,
      and executable preview subset.
- [x] Control rules carry a parsed expression AST, not only raw condition
      strings.
- [x] Simulink exporter fails with actionable diagnostics for unsupported
      control expressions.
- [x] Thermal protection Simulink handoff includes typed ports, constants,
      compare blocks, logical blocks, and switch structures for supported
      priority-ordered rules.
- [x] Tests prevent rule semantics from regressing to comments only.

## Phase 15: Semantic MBD Export Quality Gate

- [x] Add `docs/mbd_semantic_export_contract.md`.
- [x] Add minimal expression AST and parser support.
- [x] Add Simulink semantic subset validation.
- [x] Improve `export_simulink_m` for supported thermal protection rules.
- [x] Add golden/regression/unsupported-expression tests.
- [x] Regenerate `generated/create_toy_thermal_protection_controller_model.m`.

Verification:

- [x] Focused semantic export tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.
