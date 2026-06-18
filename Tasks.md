# Tasks

This is the active human/LLM progress ledger. Keep it concise; if it grows
beyond 200 lines, move completed or historical detail into `docs/archive/` and
leave links here.

Archived task history:

- [Thermal Fan Validation Task Archive](docs/archive/thermal_fan_validation_tasks.md)
- [Requirements To MBD Demo Task Archive](docs/archive/requirements_to_mbd_demo_tasks.md)

## Current Goal

Capture the MBD control-semantics lesson so future work integrates competing
state/control views before claiming review readiness.

## Quality Gates

- [x] Add a project-local control-semantics skill.
- [x] Register the skill in `AGENTS.md`.
- [x] Existing MBD authoring/review skills route state/control conflicts to the
      new skill.
- [x] The skill encodes the best-practice lesson: one behavior owner, explicit
      priority/exclusivity, concrete trace, scenario evidence, and generated
      artifact boundaries.

## Phase 11: MBD Control Semantics Skill

- [x] Add `mbd-control-semantics` project skill.
- [x] Define `mbd-control` as the semantic owner when executable behavior and
      state topology overlap.
- [x] Require priority, state scope, guard, actions, trace, and scenario evidence
      for reviewable control rows.
- [x] Require generated views to be derived from the public `.mbd.md` source.
- [x] Add `agents/openai.yaml`.

Verification:

- [x] Skill metadata and `agents/openai.yaml` exist.
- [x] `AGENTS.md` remains near the 200-line target.
- [x] `git diff --check` passes.
