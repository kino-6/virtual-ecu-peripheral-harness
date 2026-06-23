---
name: mbd-review-quality-gate
description: Project-local workflow for reviewing MBD demos, markup, visualizations, handoff artifacts, generated preview C, harness scenarios, and reports before showing them as complete. Use when Codex works on MBD review quality, traceability, requirements-based scenario evidence, Stateflow/Simulink-style handoff, or when the user says the MBD output is unclear or rejectable.
---

# MBD Review Quality Gate

Use this skill before declaring an MBD demo, visualization, trace report, or
generated handoff artifact ready for human review.

In this repository, `demo.html` is an MBD review artifact compatibility name,
not a casual visual demo.

## Source Checklist

Use `docs/mbd_review_principles.md` as the project checklist. Apply it in the
commercial-tool-free MVP context; do not claim tool qualification, ISO 26262,
ASPICE, Simulink, Stateflow, Modelica, or FMI compliance.
When reducing noisy generated HTML, follow that document's Compact Review
Tables guidance before inventing a new table shape.

## Parallel Review Lanes

Review in independent lanes before merging the result:

1. **Spec compliance lane**
   - Compare `Requirements.md`, `specs/*.md`, and `examples/*.mbd.md`.
   - Reject spec mismatches, missing assumptions, and behavior invented only for
     preview convenience.

2. **System decomposition lane**
   - Check whether the review target is a system/architecture artifact or a
     single controller logic table.
   - Confirm the spec and MBD identify system context, functional components,
     responsibility allocation, owned signals, and interfaces before detailed
     control rules.
   - Reject flat controller-only models when the requirement expects a
     decomposed system, component architecture, or MBD handoff.
   - Reject decomposition that exists only as decorative boxes without allocated
     requirements, signals, scenarios, or reports.

3. **Traceability lane**
   - Confirm every claimed requirement maps to concrete MBD elements, scenarios,
     report checks, generated artifacts, or tests.
   - Reject broad component-level trace as proof.

4. **Model readability lane**
   - Review ports, parameters, states, guard conditions, actions, and data flow.
   - Use `mbd-control-semantics` when states and control rules can compete.
   - Reject visuals that are more complex than the behavior being reviewed.
   - Reject behavior that depends on hidden rule ordering.

5. **State-machine transition-system lane**
   - Treat state-machine review as transition-system review, not diagram review.
   - Lead with state inventory, initial/default state, transition table, trigger
     or guard, effect/action, priority, trace, and scenario evidence.
   - Add a transition matrix for source-state to target-state coverage.
   - Check determinism and completeness: multiple enabled outgoing transitions,
     missing else/self-hold assumptions, unreachable states, and terminal states.
   - State action semantics explicitly: entry/during/exit actions, transition
     actions, condition actions, and Mealy/Moore-like output timing. Reject
     artifacts that hide this in a diagram label.
   - Scenario walk-through must show expected source state, input/event, selected
     transition, expected target state, output effect, trace, and report link.
   - Reject if the artifact asks "does this match the Spec?" but does not show
     the Spec intent, Spec state diagram, generated MBD state diagram, and
     generated transition table close enough for direct comparison.

6. **Scenario evidence lane**
   - Confirm reports separate model inputs, scenario steps, observed behavior,
     expected behavior, and pass/fail.
   - Reject pass/fail without expected behavior or requirement linkage.

7. **Harness evidence lane**
   - Treat Harness as a preview evidence layer, not an MBD verification backend.
   - Confirm Harness evidence shows scenario stimulus, virtual IC boundaries,
     HAL boundaries, observed behavior, expected behavior, report evidence, and
     pass/fail.
   - Confirm control decisions, state transitions, output decisions, thresholds,
     recovery rules, and product behavior are owned by the spec, MBD source,
     `mbd-control`, and functional decomposition.
   - Reject harness shortcuts where scenario YAML, Python preview code, virtual
     IC fixtures, or generated preview C compensate for missing MBD semantics.
   - Separate what Harness preview observed from what external MBD/product-test
     infrastructure must still verify.

8. **Generated artifact boundary lane**
   - Confirm Simulink `.m`, Modelica `.mo`, SCXML, Mermaid, PlantUML, FMI
     metadata, and preview C are regenerated outputs from `.mbd.md`.
   - Reject manual synchronization or production/certification wording.

## Self-Review Hard Rejects

Reject the artifact before showing it to the user when any of these are true:

- The reviewer must open `Spec.md` separately and do a mental diff to decide
  whether the MBD follows the spec.
- The page is mostly a generated dump of pipelines, markup sections, or generic
  tables instead of a curated review surface for the user's question.
- A generated diagram introduces concepts not present in the spec, such as
  generic sensors, actuators, plants, or harness nodes, without labeling them as
  derived assumptions or open questions.
- A state-machine spec has an initial/default state, but the review artifact
  does not show it structurally in both the state review table and visual view.
- Missing else/self-hold, unsupported timing, or other unresolved semantics are
  buried in diagnostics instead of appearing as open review questions.
- The artifact contains duplicate state/transition tables that dilute the main
  review path.
- A reviewer cannot answer the core question in about 30 seconds: spec intent,
  generated MBD element, trace, scenario/report evidence, and unresolved QA.
- A reviewer cannot form an initial accept/reject judgment in 30 seconds to
  1 minute from the first viewport and the immediately following review block.
- The first review block is text-heavy enough that the reviewer must read
  paragraphs, scan long evidence strings, or scroll repeatedly before seeing
  the spec intent, generated behavior, mismatch status, and open questions.
- Dense trace details, generated element lists, or tool-handoff explanations
  appear before the concise review verdict. Put those details behind a
  secondary section or omit them from the human-first review artifact.
- Harness PASS is presented as formal MBD verification, or scenario YAML owns
  control behavior that is missing from the MBD source.

## Workflow

1. Add or update `Tasks.md` gates for the eight lanes.
2. Run each lane independently. Use parallel tool calls for file reads and
   generated artifact checks when possible.
3. Summarize lane findings as PASS/REJECT with file references.
4. Fix rejects before presenting the artifact as complete.
5. Regenerate affected artifacts from `examples/*.mbd.md`.
6. Run focused tests plus full `pytest` and `git diff --check`.
7. Commit only after all lanes pass.

## Completion Gate

The final answer must identify the review entry point and say what remains
preview-only or externally verified. Do not describe the MBD artifact as ready
when any lane still has a reject.
