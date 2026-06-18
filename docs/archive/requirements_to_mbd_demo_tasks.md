# Requirements To MBD Demo Task Archive

Archived from `Tasks.md` after completing the requirements-to-MBD process demo
and review-gate setup on branch `codex/thermal-fan-validation`.

Completed phases:

- Phase 0: Added `REQ2SPEC-*` and `REQ2MBD-*` requirements and review gates.
- Phase 1: Defined extractor, spec scaffold, MBD scaffold, and trace validator
  plan.
- Phase 2: Implemented requirements extractor, deterministic JSON,
  spec/MBD scaffolds, trace validator, CLI commands, generated review
  artifacts, and tests.
- Phase 3: Corrected scaffold/report wording so trace coverage was not shown as
  approved behavior.
- Phase 4: Added the `ToyThermalProtectionController` process-demo slice:
  specification, MBD source, scenarios, generated artifacts, preview C, reports,
  and deterministic tests.
- Phase 5: Added MBD visualization sections for process, data flow, state
  machine, control rules, and harness boundary.
- Phase 6: Retook the demo after review rejection by fixing `SYS-008`, removing
  broad component-level trace, adding boundary scenario evidence, and adding a
  spec-to-MBD compliance view.
- Phase 7: Added pre-human reject loop rules to project guidance and quality
  gate skill.
- Phase 8: Added MBD review principles from MathWorks/NASA-inspired review
  practice and surfaced a checklist in the generated demo.
- Phase 9: Added `mbd-review-quality-gate` with five parallel review lanes.

Verification completed across the archived phases:

- Full `pytest` passed.
- `git diff --check` passed.
- Generated artifacts were refreshed from `.mbd.md` sources.
- Relevant commits were created at green checkpoints.
