# Tasks

This is the active human/LLM progress ledger. Keep it concise; if it grows
beyond 200 lines, move completed or historical detail into `docs/archive/` and
leave links here.

Archived task history:

- [Thermal Fan Validation Task Archive](docs/archive/thermal_fan_validation_tasks.md)
- [Requirements To MBD Demo Task Archive](docs/archive/requirements_to_mbd_demo_tasks.md)

## Current Goal

Separate sample-specific assumptions from the common MBD authoring, export, and
preview layers so future small-start samples do not inherit thermal-control
behavior implicitly.

## Quality Gates

- [x] Common HTML review output has no hardcoded thermal-protection
      requirement expectations.
- [x] Common preview reports derive observations, command outputs, trace
      evidence, and artifact evidence from the parsed model instead of thermal
      sample names.
- [x] Preview C generation uses explicit sample-specific generators and fails
      for unsupported components instead of falling back to a thermal template.
- [x] Requirements-to-MBD scaffold generation is sample-neutral by default;
      thermal scaffold output requires explicit sample selection.
- [x] Tests prove unsupported preview codegen does not silently use the thermal
      fan scaffold.

## Phase 16: Sample Isolation Boundary

- [x] Remove thermal-specific requirement and scenario tables from the common
      HTML exporter.
- [x] Remove thermal-specific observations, HAL calls, report paths, and
      controller paths from the common preview runtime.
- [x] Add an explicit preview-code generator registry.
- [x] Add explicit sample scaffold selection for thermal-protection and keep the
      default scaffold sample-neutral.
- [x] Update tests to assert generic behavior and explicit unsupported-sample
      diagnostics.

Verification:

- [x] Focused exporter/runtime/codegen tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.
