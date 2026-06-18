# Tasks

This is the active human/LLM progress ledger. Keep it concise; if it grows
beyond 200 lines, move completed or historical detail into `docs/archive/` and
leave links here.

Archived task history:

- [Thermal Fan Validation Task Archive](docs/archive/thermal_fan_validation_tasks.md)
- [Requirements To MBD Demo Task Archive](docs/archive/requirements_to_mbd_demo_tasks.md)

## Current Goal

Capture researched MBD/system-decomposition review practice in the project
review and quality-gate skills.

## Quality Gates

- [x] Add source-informed decomposition review principles.
- [x] Update MBD review quality gate to reject flat controller-only artifacts
      when system decomposition is expected.
- [x] Update expectation-control skill to ask/flag decomposition questions
      before substantial MBD demo work.
- [x] Keep the update as process guidance; do not claim commercial tool,
      ASPICE, ISO 26262, or certification compliance.

## Phase 13: MBD Decomposition Review Practice

- [x] Summarize researched decomposition points in
      `docs/mbd_review_principles.md`.
- [x] Add decomposition/allocation lane to `mbd-review-quality-gate`.
- [x] Add flat-spec/flat-MBD reject prompts to
      `quality-gate-expectation-control`.

Verification:

- [x] `git diff --check` passes.
