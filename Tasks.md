# Tasks

This is the active human/LLM progress ledger. Keep it concise; if it grows
beyond 200 lines, move completed or historical detail into `docs/archive/` and
leave links here.

Archived task history:

- [Thermal Fan Validation Task Archive](docs/archive/thermal_fan_validation_tasks.md)

## Current Goal

Install a project-local quality gate and expectation-control workflow so agents
ask back when the expected artifact quality is unclear, especially for MBD
validation demos, reports, harnesses, generated code, and ASPICE-aware work.

## Phase 0: Calibration From User Feedback

- [x] Capture the issue: tests passing and reports existing were not enough;
      the work did not match the user's expected quality.
- [x] Treat the failure as expectation alignment and quality-gate failure, not
      just a report-format problem.
- [x] Preserve the prior completed thermal fan task history in `docs/archive/`.

## Phase 1: Quality Gate Skill

- [x] Add `.agents/skills/quality-gate-expectation-control/`.
- [x] Define when the skill must trigger.
- [x] Define ask-back questions for unclear quality expectations.
- [x] Define quality gate items that must be added to `Tasks.md` before large
      implementation.
- [x] Define stop conditions where the agent should ask the user before coding.

Verification:

- [x] Skill validates with the skill validator.
- [x] `agents/openai.yaml` references `$quality-gate-expectation-control`.

## Phase 2: Agent Rules

- [x] Update `AGENTS.md` to require expectation alignment before substantial or
      ambiguous validation work.
- [x] Add the new skill to the Project Skills list.
- [x] Clarify that agents should ask the user when "quality", "MBD",
      "validation", "product-like", or "ASPICE-aware" expectations are unclear.

Verification:

- [x] `AGENTS.md` remains under 200 lines.
- [x] The new rule is concise and actionable.

## Phase 3: Final Checkpoint

- [x] Run the relevant documentation/skill validation checks.
- [x] Review `git diff --check`.
- [x] Commit the quality gate workflow update.
