---
name: mbd-review-quality-gate
description: Project-local workflow for reviewing MBD demos, markup, visualizations, handoff artifacts, generated preview C, harness scenarios, and reports before showing them as complete. Use when Codex works on MBD review quality, traceability, requirements-based scenario evidence, Stateflow/Simulink-style handoff, or when the user says the MBD output is unclear or rejectable.
---

# MBD Review Quality Gate

Use this skill before declaring an MBD demo, visualization, trace report, or
generated handoff artifact ready for human review.

## Source Checklist

Use `docs/mbd_review_principles.md` as the project checklist. Apply it in the
commercial-tool-free MVP context; do not claim tool qualification, ISO 26262,
ASPICE, Simulink, Stateflow, Modelica, or FMI compliance.

## Parallel Review Lanes

Review in independent lanes before merging the result:

1. **Spec compliance lane**
   - Compare `Requirements.md`, `specs/*.md`, and `examples/*.mbd.md`.
   - Reject spec mismatches, missing assumptions, and behavior invented only for
     preview convenience.

2. **Traceability lane**
   - Confirm every claimed requirement maps to concrete MBD elements, scenarios,
     report checks, generated artifacts, or tests.
   - Reject broad component-level trace as proof.

3. **Model readability lane**
   - Review ports, parameters, states, guard conditions, actions, and data flow.
   - Reject visuals that are more complex than the behavior being reviewed.

4. **Scenario evidence lane**
   - Confirm reports separate model inputs, scenario steps, observed behavior,
     expected behavior, and pass/fail.
   - Reject pass/fail without expected behavior or requirement linkage.

5. **Generated artifact boundary lane**
   - Confirm Simulink `.m`, Modelica `.mo`, SCXML, Mermaid, PlantUML, FMI
     metadata, and preview C are regenerated outputs from `.mbd.md`.
   - Reject manual synchronization or production/certification wording.

## Workflow

1. Add or update `Tasks.md` gates for the five lanes.
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
