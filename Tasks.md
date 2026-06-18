# Tasks

This is the active human/LLM progress ledger. Keep it concise; if it grows
beyond 200 lines, move completed or historical detail into `docs/archive/` and
leave links here.

Archived task history:

- [Thermal Fan Validation Task Archive](docs/archive/thermal_fan_validation_tasks.md)
- [Requirements To MBD Demo Task Archive](docs/archive/requirements_to_mbd_demo_tasks.md)

## Current Goal

Improve the agent workflow so MBD artifacts can be reviewed in Japanese with a
clear, low-noise technical review style.

## Quality Gates

- [x] Keep `Tasks.md` below 200 lines by archiving completed phases.
- [x] Add a project-local Japanese technical review skill.
- [x] Register the skill in `AGENTS.md`.
- [x] The skill must support MBD review comments that state finding, evidence,
      impact, and required correction without vague praise or LLM filler.

## Phase 10: Japanese Technical Review Skill

- [x] Add `japanese-technical-review` project skill.
- [x] Include rules for concise Japanese review comments, paragraph structure,
      evidence-first findings, and strict uncertainty handling.
- [x] Link the skill to MBD review use cases without copying the external gist.
- [x] Add `agents/openai.yaml`.

Verification:

- [x] Skill metadata and `agents/openai.yaml` exist.
- [x] `AGENTS.md` remains near the 200-line target.
- [x] `git diff --check` passes.
