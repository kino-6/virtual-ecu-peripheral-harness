# Tasks

This is the active human/LLM progress ledger. Keep it concise; if it grows
beyond 200 lines, move completed or historical detail into `docs/archive/` and
leave links here.

Archived task history:

- [Thermal Fan Validation Task Archive](docs/archive/thermal_fan_validation_tasks.md)
- [Requirements To MBD Demo Task Archive](docs/archive/requirements_to_mbd_demo_tasks.md)

## Current Goal

Improve the thermal protection specification and MBD so the artifact passes the
decomposition review gate: system context, functional components,
responsibility allocation, signal ownership, control ownership, and scenario
evidence are reviewable before detailed control rules.

## Quality Gates

- [x] Specification describes the system context and functional decomposition
      before detailed behavior.
- [x] MBD source includes decomposed functional components with responsibility,
      signal ownership, trace, and scenario evidence.
- [x] Control rules identify their owning function.
- [x] Generated review artifacts show decomposition before control tables.
- [x] Preview reports include decomposition and control ownership evidence.
- [x] Tests reject missing decomposition/control ownership for the protection
      demo.

## Phase 14: Thermal Protection Decomposition

- [x] Add parser/IR support for `mbd-decomposition`.
- [x] Add control-rule owner support.
- [x] Rewrite the protection specification around system context,
      functional responsibilities, and allocations.
- [x] Rewrite the protection MBD source to include functional decomposition.
- [x] Update Markdown/HTML/Mermaid/Modelica/Simulink/SCXML/report exports.
- [x] Regenerate generated artifacts and preview reports.

Verification:

- [x] Focused parser/exporter/runtime/codegen tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.
