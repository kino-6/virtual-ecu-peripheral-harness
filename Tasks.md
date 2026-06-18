# Tasks

This is the active human/LLM progress ledger. Keep it concise; if it grows
beyond 200 lines, move completed or historical detail into `docs/archive/` and
leave links here.

Archived task history:

- [Thermal Fan Validation Task Archive](docs/archive/thermal_fan_validation_tasks.md)

## Current Goal

Introduce requirements-to-spec and requirements-to-MBD support so AI can propose
reviewable scaffolds without inventing behavior that is not present in approved
requirements or specification text.

## Quality Gates

- [x] User-visible expectation: `Requirements.md` shall explicitly require
      Req-to-Spec and Req-to-MBD support before implementation.
- [x] Unknowns: actual generator implementation is not started in this step.
- [x] Acceptance check: new requirements shall force open questions instead of
      silent behavior invention.
- [x] Acceptance check: high-class requirements shall require explicit spec,
      MBD, harness, scenario, and expected-behavior coverage.

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
