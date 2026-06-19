# Tasks

This is the active human/LLM progress ledger. Keep it concise; if it grows
beyond 200 lines, move completed or historical detail into `docs/archive/` and
leave links here.

Archived task history:

- [Thermal Fan Validation Task Archive](docs/archive/thermal_fan_validation_tasks.md)
- [Requirements To MBD Demo Task Archive](docs/archive/requirements_to_mbd_demo_tasks.md)

## Current Goal

Add a very small sample that produces an intentionally simple MBD artifact for
reviewing the sample-workspace workflow without thermal-control complexity.

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
- [x] Canonical tests and documentation use `samples/<sample-id>/...` paths for
      sample-specific source, scenarios, generated artifacts, reports, and
      preview C output.
- [x] Root-level `examples/`, `scenarios/`, `generated/`, and `reports/` are no
      longer the required place for new samples.
- [x] New simple sample has one clear input, one threshold parameter, one output,
      two states, and one preview scenario.
- [x] New simple sample is registered by `list-samples` and regenerated through
      `export-sample`.

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

## Phase 18: Minimal MBD Sample

- [x] Add `samples/simple_threshold_indicator/` with `sample.yml`, `spec.md`,
      `model.mbd.md`, and one scenario.
- [x] Generate sample-local Markdown, Mermaid, PlantUML, SCXML, Modelica,
      Simulink `.m`, FMI metadata, demo HTML, IR, and report artifacts.
- [x] Add tests proving the simple sample stays intentionally small and
      deterministic.

Verification:

- [x] `python -m veph list-samples` includes `simple_threshold_indicator`.
- [x] `python -m veph export-sample simple_threshold_indicator` succeeds.
- [x] Focused simple-sample tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 19: Spec Mermaid To MBD Script Gate

- [x] Document that `model.mbd.md` is an authoring source for generated MBD
      review artifacts, not itself the visual MBD deliverable.
- [x] Add a small parser for the supported `Spec.md` Mermaid Design Overview
      subset: labeled nodes, decision nodes, labeled edges, input ports,
      parameters, output actions, and report endpoints.
- [x] Add a script/CLI gate that compares the parsed Spec Mermaid semantic graph
      against the semantic MBD graph derived from `model.mbd.md`.
- [x] Make mismatch diagnostics actionable: missing nodes, extra nodes, missing
      edges, and extra edges.
- [x] Add tests proving the simple threshold sample passes and an intentional
      mismatch fails.
- [x] Wire the gate into sample validation without adding large dependencies.

Verification:

- [x] Focused spec-to-MBD script tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 17: Sample Workspace Repository Structure

- [x] Add a sample catalog/manifest abstraction for sample-local paths.
- [x] Move or mirror canonical sample source and generated evidence under
      `samples/<sample-id>/`.
- [x] Update tests to resolve sample paths through the catalog instead of
      hardcoded root-level sample directories.
- [x] Update README and project rules to document the sample workspace layout.
- [x] Keep legacy root-level artifacts clearly compatibility-only or remove the
      dependency from tests and docs.

Verification:

- [x] Sample catalog tests pass.
- [x] Focused exporter/runtime/scenario tests pass with sample workspace paths.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.
