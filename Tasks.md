# Tasks

This is the active human/LLM progress ledger. Keep it concise; if it grows
beyond 200 lines, move completed or historical detail into `docs/archive/` and
leave links here.

Archived task history:

- [Thermal Fan Validation Task Archive](docs/archive/thermal_fan_validation_tasks.md)
- [Requirements To MBD Demo Task Archive](docs/archive/requirements_to_mbd_demo_tasks.md)
- [Simple Sample And Spec Converter Task Archive](docs/archive/simple_sample_and_spec_converter_tasks.md)

## Current Goal

Reach 34/34 coverage for the repository-defined Mermaid-to-MBD MVP catalog, with
tests and generated artifacts proving each item is script-supported.

## Quality Gates

- [x] New state-machine sample is fictional, sample-local, and independent of
      thermal-control assumptions.
- [x] Spec documents the intended state behavior with Mermaid stateDiagram and
      a simple review-oriented Design Overview.
- [x] MBD authoring source has explicit states, state-scoped control rules,
      functional allocation, flows, harness boundary, and requirement trace.
- [x] Generated PlantUML, SCXML, Mermaid, Modelica, Simulink `.m`, HTML review
      artifact, IR, FMI metadata, and preview report are reproducible from sample source.
- [x] HTML review artifact leads with the human question: whether the MBD
      implements the specification as written.
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
- [x] Canonical tests and docs use `samples/<sample-id>/...` paths for
      sample-specific source, scenarios, artifacts, reports, and preview C output.
- [x] Root-level `examples/`, `scenarios/`, `generated/`, and `reports/` are no
      longer the required place for new samples.
- [x] New simple sample has one clear input, one threshold parameter, one output,
      two states, and one preview scenario.
- [x] New simple sample is registered by `list-samples` and regenerated through
      `export-sample`.

## Archived Completed Phases

- [x] Phases 16 and 21-25 are complete; details live in the archive links at
      the top of this file and in Git history.

## Phase 26: State Machine Review Material

- [x] Add state-machine review practice to the local MBD review Skill.
- [x] Make the generated review artifact transition-table first, not
      diagram-first.
- [x] Add state inventory, transition matrix, guard diagnostics, action
      semantics, and scenario walk-through sections.
- [x] Regenerate `simple_state_machine` review artifacts from source.
- [x] Add tests proving the generated review material exposes those sections.
- [x] Add self-review hard rejects for spec-diff burden, invented concepts,
      weak initial-state evidence, buried assumptions, and generated-dump pages.
- [x] Retake `from_spec_review.html` as a Spec-first state-machine review sheet.
- [x] Add the 30-60 second initial judgment rule to self-review gates.
- [x] Retake `from_spec_review.html` again because the current Japanese review
      sheet is still too text-heavy for the new time-boxed review gate.

Verification:

- [x] Focused state-machine/exporter tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 27: Mermaid-To-MBD Item Expansion

- [x] Keep Relay/Hysteresis as a state-machine conversion sample, not the main
      definition of item expansion.
- [x] Add `Constant: <name> = <value>` as a supported Mermaid flowchart item.
- [x] Regenerate `simple_switch_selector` from Spec using Constant items instead
      of treating fixed values only as Parameters.
- [x] Document the supported Mermaid-to-MBD item subset.
- [x] Add/adjust tests proving Constant items are parsed, aligned, regenerated,
      and shown in review artifacts.

Verification:

- [x] `python -m veph export-sample simple_relay_hysteresis` succeeds.
- [x] Preview scenario produces a PASS report with separated report sections.
- [x] Focused relay-hysteresis tests pass.
- [x] `python -m veph export-sample simple_switch_selector` succeeds with
      Constant Mermaid items.
- [x] Focused Mermaid-to-MBD conversion tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 28: Logical Expression Coverage

- [x] Add unary `not` to the MBD expression parser.
- [x] Evaluate parsed expression IR in the preview Harness so `and`, `or`, and
      `not` are runtime-supported consistently.
- [x] Keep Simulink semantic export structural for `and`, `or`, and `not`.
- [x] Add tests proving Mermaid decision guards with logical expressions convert
      to MBD, preview correctly, and generate structural handoff artifacts.
- [x] Update the supported-items coverage table and revised coverage numbers.

Verification:

- [x] Focused expression/conversion/exporter tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 29: Coverage Contract Lock

- [x] Assign stable IDs to all 34 MVP catalog items in
      `docs/mermaid_to_mbd_supported_items.md`.
- [x] Add a coverage matrix showing supported, partial, and unsupported status per item.
- [x] Add tests that fail if the documented coverage count and implemented
      support drift apart.

Verification:

- [x] Coverage matrix reports 23/34 before new implementation phases.
- [x] Focused coverage-doc tests pass.

## Phase 30: Arithmetic Dataflow Coverage

- [x] Add Mermaid syntax for arithmetic blocks: `Gain`, `Sum`, and `Product`.
- [x] Extend conversion, alignment, preview, and review artifacts for arithmetic.
- [x] Add one small review fixture proving `input -> Gain -> Sum/Product ->
      Output` converts deterministically.

Verification:

- [x] Arithmetic expression item becomes supported.
- [x] Focused conversion/runtime/exporter tests pass.

## Phase 31: Limit And Lookup Coverage

- [x] Add Mermaid syntax for `Saturation` or `MinMax` limit blocks.
- [x] Add Mermaid syntax for a 1-D lookup table with explicit fictional points.
- [x] Extend preview/runtime and review output so limit and lookup behavior is inspectable.

Verification:

- [x] `saturation/min/max` item becomes supported.
- [x] `lookup table` item becomes supported.
- [x] Focused conversion/runtime/exporter tests pass.

## Phase 32: Structural Composition Coverage

- [x] Support multiple controller/function nodes in one Design Overview.
- [x] Support one-level subsystem hierarchy with explicit Mermaid grouping or
      naming convention.
- [x] Support bus/vector signal notation in Mermaid and generated MBD review.

Verification:

- [x] `multiple functions`, `subsystem hierarchy`, and `bus/vector signal`
      items become supported.
- [x] Review artifact shows function ownership and grouped signal paths clearly.
- [x] Focused alignment/exporter tests pass.

## Phase 33: State Action Coverage

- [x] Add syntax for entry, during, and exit actions in state-machine Specs.
- [x] Convert those actions into explicit MBD control/action semantics instead
      of burying them as notes.
- [x] Update state-machine review HTML to separate transition actions from
      entry/during/exit actions.

Verification:

- [x] `entry/during/exit action` item becomes supported.
- [x] State-machine review artifact stays understandable in 30-60 seconds.
- [x] Focused state-machine tests pass.

## Phase 34: Advanced State Semantics Coverage

- [x] Add a deliberately tiny hierarchy subset for nested states.
- [x] Add a deliberately tiny parallel-state subset with explicit unsupported
      conflict diagnostics where semantics exceed the MVP.
- [x] Add shallow history and temporal-event syntax with explicit preview
      semantics and handoff boundaries.

Verification:

- [x] `hierarchy`, `parallel state`, `history`, and `temporal event` items
      become supported or explicitly handled by the MVP contract.
- [x] Coverage matrix reports 34/34 for the repository-defined MVP catalog.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.
