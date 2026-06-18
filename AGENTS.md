# Project Operating Rules

Project-level guidance for agents working in this repository.

## North Star

Author in text. Verify in MBD tools.

This repository is a Mermaid-like Markup-to-MBD bridge for virtual ECU and
peripheral model authoring. Public authoring source is readable Markdown, not a
custom YAML modeling language.

The intended pipeline is:

```text
examples/*.mbd.md
  -> markup parser
  -> internal IR snapshot
  -> exporters
      -> Markdown review document
      -> Mermaid / PlantUML preview diagrams
      -> Simulink model-generation .m script
      -> SCXML or Stateflow-oriented handoff
      -> Modelica .mo text artifact
      -> FMI-oriented metadata stub
  -> optional Python preview only
```

## Project Boundary

This is a lightweight authoring/review layer and handoff bridge to existing MBD
tools. It is not a new MBD language, custom runtime, Simulink/Stateflow/Modelica
/FMI replacement, production ECU simulator, physics solver, or certification
claim.

## Source-Of-Truth Policy

Public source is `examples/*.mbd.md`. YAML is not the public source of truth;
keep YAML only as legacy preview input, optional expanded machine-readable form,
or implementation detail. Internal IR is a tooling snapshot, not a public
standard.

## Requirements And Process Policy

Start substantial validation work from `Requirements.md`, then move to markup,
parser/IR, generated artifacts, preview harness, preview C, and reports. Keep
requirements fictional, ID-based, and traceable to markup, generated artifacts,
preview scenarios, and tests. Use ASPICE-aware practices as process inspiration:
requirements traceability, reviewable work products, verification evidence, and
clear artifact boundaries. Do not claim ASPICE compliance, safety
certification, production readiness, or tool qualification from this MVP.

Recent direction decisions:

- Do not jump from an idea directly into MBD markup or harness implementation.
  First write the fictional intent in `Requirements.md`.
- Derive a human-readable specification from requirements before expanding MBD
  markup, generated artifacts, or preview runtime behavior.
- Treat MBD usage as a stricter product-development context than an ordinary
  demo. Favor traceability, review gates, and reproducible evidence.
- Run the loop as PDCA/TDD: requirements, specification, failing checks, markup
  and exporters, harness preview, reports, then task/status updates.
- If expected artifact quality is unclear, ask the user before implementation.
  Do not silently downgrade a validation goal into a smoke-test demo.

## Quality Gate And Expectation Control

Before substantial or ambiguous validation work, state the expected human-facing
artifact quality and add acceptance gates to `Tasks.md`. Ask back when words
like "MBD", "validation", "product-like", "ASPICE-aware", "demo", or "report"
could imply different rigor levels. Tests passing is necessary evidence, not a
complete definition of done.

Before calling a demo, report, MBD visualization, generated code, or trace
artifact complete, run an agent-side reject loop. Compare it against the
human-readable spec, reject broad trace coverage, hidden assumptions,
over-complex visuals, and demo-convenient behavior absent from the spec. A
reviewer should see the path in about 30 seconds: requirement, expected
behavior, MBD element, harness/scenario, observed behavior, expected behavior,
and pass/fail. If not, update `Tasks.md` with the failed gate and iterate.

## Verification Policy

Existing MBD tools are the intended verification backends. Python may parse
markup, generate artifacts, run smoke tests, and provide previews, but must not
be described as the main verification path. Label local preview behavior and C
generation: `preview-only; not a certified code generation or verification backend`.

## Fictional-Only Safety Policy

Use only fictional components, synthetic examples, and invented register maps.
Do not use real IC names, datasheets, ECU specs, register maps, company names,
production-derived code, or confidential project details. Sample ECU code may
look product-like, but must remain synthetic and communicate through HAL-style
boundaries rather than Python internals.

## Target Validation Story

The next major validation should demonstrate a complete fictional control system:

```text
fictional IC spec
  -> Mermaid-like markup spec
  -> internal IR
  -> MBD handoff artifacts
  -> virtual IC harness preview
  -> preview ECU C code generation
  -> scenario smoke verification
```

Preferred example: thermal fan control with `ToyTempSensorIC`,
`ToyFanDriverIC`, a virtual ECU controller, normal/fault scenarios,
Simulink/Modelica/FMI handoff artifacts, and preview-only C scaffold.

## Code Generation Boundary

Never blur the two code generation routes. Tool-backed route: markup generates
Simulink `.m`, Modelica `.mo`, SCXML/Stateflow-oriented tables, and FMI metadata
for existing tools to verify outside this repo. Local preview route: IR may
generate simple C scaffold for smoke testing, but it is not certified and not
the main verification path.

## Implementation Preferences

- Keep dependencies minimal.
- Prefer explicit parser/IR/exporter tests for new syntax.
- Keep generated artifacts reproducible from markup.
- Avoid over-engineering physics or runtime semantics.
- When adding a feature, update README, `docs/design_principles.md`, generated
  artifacts, and tests together.
- Refactor regularly after tests are green. Keep refactors scoped, behavior
  preserving, and separated from feature changes when practical.

## Project Skills

Project-local skills live under `.agents/skills/`:

- `mbd-markup-authoring`: use for `examples/*.mbd.md`, markup grammar,
  `markup_parser.py`, and `ir.py` work.
- `mbd-artifact-export`: use for exporter changes, generated artifacts, and
  source-to-artifact determinism.
- `preview-harness-codegen`: use for preview runtime, `run-preview`,
  `export-code-preview`, scenarios, and preview-only generated C scaffolds.
- `quality-gate-expectation-control`: use before substantial or ambiguous work
  when user-visible artifact quality, review evidence, or acceptance gates are
  unclear.

Keep skills concise; move details into one-level `references/` files when needed.

## Git Workflow Policy

Use Git checkpoints to keep larger goals recoverable and reviewable.

- Create a topic branch for substantial/risky multi-checkpoint work, e.g.
  `codex/thermal-fan-preview`.
- Stay on the current branch for tiny documentation edits unless a branch is expected.
- Commit at meaningful green checkpoints: parser/IR, exporters, preview runtime,
  code generation, scenario runner, and documentation updates.
- Run the relevant tests before committing. Do not knowingly commit broken
  generated artifacts or stale regenerated files.
- Push regularly only when the user asks or the active goal includes remote
  checkpointing. Before push, review `git status` and staged diff.
- Prefer small, descriptive commits over one large opaque commit for multi-phase
  work.

## Agent And Claude Operating Practices

Keep instructions concise, concrete, and actionable. Long background belongs in
linked docs.

- For Claude Code compatibility, keep a root `CLAUDE.md` that imports
  `AGENTS.md` instead of duplicating instructions.
- Prefer plan-first work for ambiguous or high-blast-radius changes. Write or
  update `Tasks.md` before editing substantial code.
- Use the loop: gather context, make a small change, verify it, then repeat.
- For long-running goals, leave a clean handoff: tests run, generated files
  refreshed, `Tasks.md` updated, Git checkpointed when appropriate.
- Keep instruction files below roughly 200 lines when possible; move large or
  historical detail to `docs/archive/` or focused docs and link it.
- Keep references one level deep when practical. If a referenced file grows past
  about 100 lines, add a short table of contents near the top.
- Make instructions specific and testable. Prefer "run `pytest` after parser or
  exporter changes" over vague instructions such as "test thoroughly."
- Treat hooks, external services, credentials, pushes, and destructive commands
  as explicit-boundary actions requiring approval/sandbox compliance.

## Task Tracking Policy

Use `Tasks.md` as the shared human/LLM progress ledger for larger goals.

- Write implementation steps and acceptance checks as Markdown task-list items.
- Use unchecked boxes (`- [ ]`) for pending work.
- Mark items complete with checked boxes (`- [x]`) only after the work is
  implemented and verified.
- Keep task items small enough that progress is visible in code review.
- When scope changes, update `Tasks.md` before continuing substantial work.
- Keep `Tasks.md` concise. If it grows beyond 200 lines, move completed or
  historical task detail into `docs/archive/` and leave only a short summary plus
  links in `Tasks.md`.
