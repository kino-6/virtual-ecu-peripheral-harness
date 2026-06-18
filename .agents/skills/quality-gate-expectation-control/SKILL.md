---
name: quality-gate-expectation-control
description: Project-local workflow for expectation alignment, human QA, and quality gates before substantial or ambiguous validation work. Use when Codex is asked to build demos, MBD validation flows, harnesses, generated code, reports, agent rules, or any high-blast-radius task where the user's quality target is unclear, subjective, or likely stricter than a smoke-test implementation.
---

# Quality Gate Expectation Control

Use this skill before implementation when the requested outcome may be judged by
fitness, evidence quality, reviewability, or professional realism rather than by
"tests pass" alone.

## Trigger Signals

- The user says the current output is "not what I imagined", "too rough",
  "is this really MBD?", "quality", "expectation", "gate", or "ask me first".
- The task asks for a demo, report, validation story, harness, generated code,
  or MBD artifact whose acceptable quality is not objectively defined.
- The agent is about to mark a large `Tasks.md` scope complete without an
  explicit user-facing acceptance gate.

## Required Loop

1. Restate the expected outcome in concrete review terms.
2. List assumptions that affect quality, not only implementation.
3. Ask the user about unclear quality targets before coding.
4. Write acceptance gates into `Tasks.md` before substantial implementation.
5. Build the smallest vertical slice that can be reviewed.
6. Show evidence and residual gaps before declaring completion.

## Ask-Back Questions

Ask concise questions when any answer would change the artifact shape:

- What should a human reviewer be convinced of after opening the report or demo?
- Is the target a smoke-test proof, a reviewable engineering artifact, or a
  product-like validation story?
- Which evidence is mandatory: trace matrix, step-by-step execution, generated
  code linkage, MBD handoff shape, or harness boundary proof?
- What would make this unacceptable even if tests pass?

Prefer 1-3 questions. Do not bury the user in a survey.

## Quality Gate Template

Add gates like these to `Tasks.md` before implementation:

- [ ] User-visible expectation is stated in one paragraph.
- [ ] Unknowns that affect artifact quality are asked or explicitly assumed.
- [ ] Report/demo acceptance checks are listed before generation.
- [ ] Evidence links requirements, model elements, generated code, scenario
      steps, observed behavior, expected behavior, and pass/fail.
- [ ] Final response names what is still preview-only or weak.

## Stop Conditions

Pause and ask the user before coding when:

- "MBD", "production-like", "ASPICE-aware", or "validation" is used but the
  expected rigor is not defined.
- The implementation could be merely a toy while the user expects a convincing
  engineering artifact.
- The agent cannot explain what the user will inspect to decide whether the
  work is good.

## Completion Rule

Do not mark a task complete solely because tests pass. Mark it complete only
when the agreed quality gate is met and the final answer points to the evidence.
