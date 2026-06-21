# Tasks

This is the active human/LLM progress ledger. Keep it concise; if it grows
beyond 200 lines, move completed or historical detail into `docs/archive/` and
leave links here.

Archived task history:

- [Thermal Fan Validation Task Archive](docs/archive/thermal_fan_validation_tasks.md)
- [Requirements To MBD Demo Task Archive](docs/archive/requirements_to_mbd_demo_tasks.md)

## Current Goal

Add a very small state-machine sample that demonstrates reviewable MBD state
behavior without thermal-control complexity.

## Quality Gates

- [x] New state-machine sample is fictional, sample-local, and independent of
      thermal-control assumptions.
- [x] Spec documents the intended state behavior with Mermaid stateDiagram and
      a simple review-oriented Design Overview.
- [x] MBD authoring source has explicit states, state-scoped control rules,
      functional allocation, flows, harness boundary, and requirement trace.
- [x] Generated PlantUML, SCXML, Mermaid, Modelica, Simulink `.m`, HTML demo,
      IR, FMI metadata, and preview report are reproducible from sample source.
- [x] Demo HTML includes a design-overview diagram that matches the
      specification-level Mermaid Design Overview before detailed rule tables.
- [x] Preview scenario proves the full state cycle and report sections separate
      model inputs, scenario steps, observed behavior, expected behavior, and
      pass/fail result.
- [x] Tests prove the sample remains small and deterministic.
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

## Phase 21: Minimal State Machine Sample

- [x] Add `samples/simple_state_machine/` with `sample.yml`, `spec.md`,
      `model.mbd.md`, one scenario, one preview report, and generated artifacts.
- [x] Model exactly three states: `IDLE`, `RUNNING`, and `DONE`.
- [x] Model exactly three state-scoped transitions: start, finish, and reset.
- [x] Generate sample-local Markdown, Mermaid, PlantUML, SCXML, Modelica,
      Simulink `.m`, FMI metadata, demo HTML, IR, and preview report.
- [x] Align demo HTML with `spec.md` by showing `ToyCommandSource` inputs,
      `ToyStateController`, `busy`/`complete` outputs, and
      `ScenarioReport.observedBehavior` at the top-level design view.
- [x] Add tests proving the state-machine sample is intentionally small,
      deterministic, and preview-executable.

Verification:

- [x] `python -m veph list-samples` includes `simple_state_machine`.
- [x] `python -m veph export-sample simple_state_machine` succeeds.
- [x] `python -m veph run-preview --model samples/simple_state_machine/model.mbd.md --scenario samples/simple_state_machine/scenarios/full_cycle.yml --report samples/simple_state_machine/reports/full_cycle.md` succeeds.
- [x] Focused state-machine sample tests pass.
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

## Phase 20: Generic Spec Mermaid To MBD Converter And Viewer

- [x] Add a generic converter for the supported Spec Mermaid flowchart subset:
      source nodes, `Input Port: ...`, `Parameter: ...`, decision nodes,
      `Output ... = ...`, report nodes, and labeled true/false branches.
- [x] Parse the adjacent simple `stateDiagram-v2` subset when present and carry
      it into generated `mbd-state`.
- [x] Generate MBD authoring Markdown from Mermaid semantics without
      hardcoding `simple_threshold_indicator` names or values; require explicit
      metadata such as component name when Mermaid cannot express it.
- [x] Add a CLI command that converts `Spec.md` Mermaid to MBD authoring source
      and fails with actionable diagnostics for unsupported Mermaid syntax.
- [x] Add a review viewer that shows the original Spec Mermaid semantics and
      converted MBD semantics side-by-side with node/edge alignment evidence.
- [x] Add an interactive review panel for the supported simple threshold subset
      so reviewers can vary model inputs/parameters and see the active branch,
      state, and output.
- [x] Wire the simple sample to generate a converted MBD artifact and viewer
      from `spec.md`.
- [x] Add tests proving conversion output is deterministic, parseable, and
      semantically aligned with the Spec Mermaid.

Verification:

- [x] Focused converter/viewer tests pass.
- [x] `python -m veph export-sample simple_threshold_indicator` succeeds.
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
