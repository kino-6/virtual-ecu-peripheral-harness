---
name: mbd-control-semantics
description: Project-local workflow for integrating competing MBD state and control descriptions into one reviewable control semantics. Use when mbd-state and mbd-control overlap, when control-rule priority or exclusivity is unclear, or when MBD artifacts need to become human-reviewable before export.
---

# MBD Control Semantics

Use this skill when MBD behavior is split across state diagrams, control rules,
preview runtime, and generated code.

## Core Policy

There must be one semantic owner for executable control behavior.

- `mbd-control` owns control semantics: priority, guard, state scope, actions,
  trace, and scenario evidence.
- `mbd-state` is a lifecycle/topology view unless it is generated from the same
  control semantics.
- Generated Mermaid, SCXML, Simulink `.m`, Modelica, FMI metadata, preview C,
  reports, and HTML are derived views.
- If two views disagree, fix the public `.mbd.md` source and regenerate.

## Reviewable Control Row

Each control row should make simultaneous conditions reviewable:

```text
priority <number> rule <name>:
  from <state-or-*>
  when <guard>
  then state=<state>, outputs...
  trace <requirements>
  scenarios <scenario names>
```

Required fields:

- priority: lower number wins, with no hidden fallback ordering
- state scope: `from FAULT_LATCHED`, `from *`, or equivalent
- guard: boolean condition using model inputs and parameters
- actions: next state and externally observable outputs
- trace: concrete requirement IDs
- scenario evidence: one or more scenario names or an explicit open question

## Integration Rules

- Do not encode the same behavior independently in `mbd-state` and
  `mbd-control`.
- Prefer a decision-table style control section when faults, latches, recovery,
  or derating can overlap.
- Add an explicit `default hold` or `default safe` behavior.
- Reject behavior that only works because the preview runtime happens to test
  rules in list order.
- Keep unsupported timing, debounce, plant physics, and tool-specific execution
  semantics explicit as assumptions or external verification needs.

## Best-Practice Basis

Apply `docs/mbd_review_principles.md`: requirements traceability, interface and
data-flow clarity, state/control behavior in one place, requirements-based
scenario evidence, readability, and generated-artifact boundaries.

## Completion Gate

Before presenting an MBD artifact as reviewable, answer:

1. Which table owns state and output decisions?
2. What happens when multiple guards are true?
3. Which requirement and scenario prove each high-risk row?
4. Which generated artifacts are derived from this source?

If any answer is missing, the artifact is not ready for human review.
