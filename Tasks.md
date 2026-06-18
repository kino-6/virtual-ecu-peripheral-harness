# Tasks

This is the active human/LLM progress ledger. Keep it concise; if it grows
beyond 200 lines, move completed or historical detail into `docs/archive/` and
leave links here.

Archived task history:

- [Thermal Fan Validation Task Archive](docs/archive/thermal_fan_validation_tasks.md)

## Current Goal

Revise the requirements-to-spec and requirements-to-MBD demo scaffolds so the
business-process demo is reviewable without pretending unresolved behavior has
been approved.

## Quality Gates

- [x] User-visible expectation: `Requirements.md` shall explicitly require
      Req-to-Spec and Req-to-MBD support before implementation.
- [x] Unknowns: actual generator implementation is not started in this step.
- [x] Acceptance check: new requirements shall force open questions instead of
      silent behavior invention.
- [x] Acceptance check: high-class requirements shall require explicit spec,
      MBD, harness, scenario, and expected-behavior coverage.
- [x] Acceptance check: generated spec clearly separates machine extraction,
      demo assumptions, unresolved decisions, and behavior outline.
- [x] Acceptance check: trace report must not present scaffold coverage as
      approved behavior when open questions remain.
- [x] Acceptance check: generated MBD scaffold must keep TODO/open-question
      placeholders visible instead of convenient threshold/timing answers.

## Phase 0: Requirements Update

- [x] Add `REQ2SPEC-*` requirements.
- [x] Add `REQ2MBD-*` requirements.
- [x] Update traceability seed for Req-to-Spec and Req-to-MBD evidence.
- [x] Add review gates before accepting generated spec or MBD scaffold.

Verification:

- [x] `Requirements.md` includes deterministic scaffold requirements.
- [x] `Requirements.md` includes no silent invention requirements.
- [x] `git diff --check` passes.

## Phase 1: Next Implementation Plan

- [x] Define extractor output shape for requirement IDs, DSC tags, statements,
      source section, and planned evidence.
- [x] Define `Spec.md` scaffold template sections.
- [x] Define Mermaid-like MBD scaffold template sections.
- [x] Define trace validator checks for missing spec coverage, missing MBD
      coverage, and untraced MBD behavior.
- [x] Treat the user's "Tasks.md完遂" Goal request as approval to implement the
      conservative scaffold template implied by the reviewed requirements.

## Phase 2: Minimal Vertical Slice

- [x] Add requirements extractor.
- [x] Add deterministic requirements JSON rendering.
- [x] Add `Spec.md` scaffold generator.
- [x] Add Mermaid-like MBD scaffold generator.
- [x] Add traceability validator.
- [x] Add CLI commands:
      `extract-requirements`, `scaffold-spec`, `scaffold-mbd`,
      `validate-trace`.
- [x] Generate review artifacts:
      `generated/requirements.ir.json`,
      `specs/ai_assisted_mbd_workflow.scaffold.md`,
      `examples/ai_assisted_mbd_workflow.scaffold.mbd.md`,
      `reports/requirements_traceability.md`.

Verification:

- [x] Unit tests cover extraction, scaffolds, open questions, and trace
      validation.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.
- [x] Commit the Req-to-Spec/MBD support update.

## Phase 3: Demo Quality Correction

- [x] Update scaffold tests to require review-status and approval-pending
      wording.
- [x] Update spec scaffold generation for human review order.
- [x] Update traceability report wording to distinguish scaffold coverage from
      approved behavior.
- [x] Regenerate affected artifacts.

Verification:

- [x] Unit tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 4: Complete Business-Process Demo Slice

- [x] Add approved demo assumptions for a fictional `Toy Thermal Protection
      Controller` without claiming product or safety approval.
- [x] Add a human-readable specification that links requirements, Mermaid
      diagrams, MBD source, harness boundary, generated C, and reports.
- [x] Add Mermaid-like MBD source as the public source for the demo.
- [x] Add preview scenarios for normal cooling, derating, fault latch, and
      recovery.
- [x] Extend preview runtime evidence so reports show model inputs, scenario
      steps, observed behavior, expected behavior, and pass/fail for the
      protection demo.
- [x] Extend preview C generation to produce HAL-style product-like synthetic
      controller code for the protection demo.
- [x] Regenerate IR, Markdown, Mermaid, PlantUML, SCXML, Modelica, Simulink
      `.m`, FMI metadata, demo HTML, preview C, and reports from the MBD source.
- [x] Add tests proving deterministic regeneration and scenario pass/fail
      evidence for the protection demo.

Verification:

- [x] Protection demo reports pass and separate required report sections.
- [x] Generated artifacts are deterministic from the `.mbd.md` source.
- [x] Preview C syntax-checks when `cc` is available.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 5: Reviewable MBD Visualization

- [x] Add SVG-based process visualization for the MBD review pipeline.
- [x] Add SVG-based data-flow visualization from virtual ICs through HAL,
      controller, actuators, and reports.
- [x] Add SVG-based state-machine visualization from `mbd-state`.
- [x] Add SVG-based control-rule visualization from `mbd-control`.
- [x] Add SVG-based harness-boundary visualization from `mbd-harness`.
- [x] Regenerate `generated/toy_thermal_protection_controller_demo.html`.

Verification:

- [x] Exporter tests require visual review sections.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 6: Reject-Driven Retake

- [x] Fix specification mismatch: recovery from `FAULT_LATCHED` shall require
      `temperatureValid == true`, `invalidDebounced == false`, and
      `recoveryRequest == true` in MBD control, state handoff, preview runtime,
      generated C, and reports.
- [x] Remove broad component-level trace that makes every requirement look
      covered by the component instead of concrete model elements.
- [x] Add a small spec-to-MBD compliance view that maps each `SYS-*`
      requirement to the exact MBD rule/flow/harness/scenario evidence.
- [x] Simplify the HTML review page so the first review path is specification
      compliance, not a pile of diagrams.
- [x] Regenerate MBD IR, handoff artifacts, preview C, reports, and demo HTML.

Verification:

- [x] Tests fail if recovery omits `invalidDebounced == false`.
- [x] Tests fail if component trace contains broad `SYS-*` coverage.
- [x] Tests fail if the demo HTML lacks the spec-to-MBD compliance view.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 7: Pre-Human Reject Loop Rule

- [x] Add project rule requiring agent-side reject review before presenting
      demos, reports, MBD visualizations, generated code, or trace artifacts as
      complete.
- [x] Add quality-gate skill guidance for rejecting spec mismatches, broad
      trace, hidden assumptions, unclear review paths, and needless complexity.

Verification:

- [x] `AGENTS.md` includes the pre-human reject loop.
- [x] `quality-gate-expectation-control` includes the pre-human reject loop.

## Phase 8: MBD Review Practice Intake

- [x] Research MBD review practices from MathWorks and NASA references.
- [x] Add `docs/mbd_review_principles.md`.
- [x] Add MBD review checklist guidance to AGENTS and quality-gate skill.
- [x] Add the checklist to generated protection demo HTML.

Verification:

- [x] Exporter tests require the checklist.
- [x] Regenerated demo HTML includes the checklist.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 9: MBD Review Skill

- [x] Add `mbd-review-quality-gate` project skill.
- [x] Define five parallel review lanes: spec, traceability, readability,
      scenario evidence, and generated artifact boundary.
- [x] Register the skill in `AGENTS.md`.

Verification:

- [x] Skill metadata and `agents/openai.yaml` exist.
- [x] `AGENTS.md` remains near the 200-line target.
- [x] `git diff --check` passes.
