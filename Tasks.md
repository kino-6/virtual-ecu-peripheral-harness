# Tasks

This is the active human/LLM progress ledger. Keep it concise; if it grows
beyond 200 lines, move completed or historical detail into `docs/archive/` and
leave links here.

Archived task history:

- [Thermal Fan Validation Task Archive](docs/archive/thermal_fan_validation_tasks.md)
- [Requirements To MBD Demo Task Archive](docs/archive/requirements_to_mbd_demo_tasks.md)
- [Simple Sample And Spec Converter Task Archive](docs/archive/simple_sample_and_spec_converter_tasks.md)
- [Mermaid To MBD Coverage Task Archive](docs/archive/mermaid_to_mbd_coverage_tasks.md)

## Current Goal

Make spec-first state-machine review artifacts focus on the state diagram and
transition behavior before Harness evidence or requirement detail.

## Phase 50: Concise Test Summary By Behavior Type

Acceptance gates:

- [x] Harness preview evidence is shown as a concise test summary, not a
      scenario-file/status dump.
- [x] Threshold/hysteresis tests show input values and threshold parameters.
- [x] State-transition tests show stimulus sequence and expected transition
      path.
- [x] Tests reject returning to final-state-only review text.

Verification:

- [x] Regenerate affected sample review HTML.
- [x] Focused review artifact tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 49: Remove Noisy Generated-MBD Review Header

Acceptance gates:

- [x] State-machine `from_spec_review.html` starts with the state diagram review
      question, not a broad "spec vs generated MBD" badge strip.
- [x] PASS and scenario evidence remain available later as support evidence
      instead of leading the first viewport.
- [x] Tests reject reintroducing the old text-heavy generated-MBD header.

Verification:

- [x] Regenerate affected sample review HTML.
- [x] Focused review artifact tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 48: State-Diagram-First Review Entry

Acceptance gates:

- [x] `from_spec_review.html` presents state diagram review before Harness
      evidence and requirement detail for state-machine samples.
- [x] The one-minute review focuses on initial state, transition direction,
      guard conditions, and output effects rather than Harness summary text.
- [x] Requirement rows and QA/unsupported details remain available but are
      moved behind secondary detail sections.
- [x] Tests reject ordering regressions where Harness or requirement detail
      appears before the state diagram review.

Verification:

- [x] Focused state-machine review artifact tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 47: One-Hour Review Quality PDCA Loop

PDCA backlog:

- [x] Cycle 0: push/merge current branch, push `main`, and create a fresh topic
      branch.
- [x] Cycle 1: add automated review artifact quality checks for one-minute
      review paths.
- [x] Cycle 2: connect Sequence View expectations to preview scenarios without
      letting sequence diagrams own control semantics.
- [x] Cycle 3: add a minimal `validate-sample` command for sample-level
      consistency checks.

Acceptance gates:

- [x] Review HTML quality checks reject missing one-minute markers, missing
      PASS/alignment signals, dense first-read evidence, and missing Harness
      evidence where required.
- [x] Sequence View checks detect scenario expectation drift for at least one
      layered sample.
- [x] Sample validation CLI checks generated artifact determinism, spec-to-MBD
      alignment, preview report pass/fail, and review HTML quality for one
      sample.
- [ ] Remaining Budget Decisions are made after each green checkpoint.

Verification:

- [x] Focused review artifact quality tests pass.
- [x] Focused sequence/scenario tests pass.
- [x] Focused sample validation tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 46: Timeboxed PDCA Goal Guardrail

Acceptance gates:

- [x] `AGENTS.md` states that timeboxed Goals use the timebox as work budget,
      not merely as a deadline.
- [x] `AGENTS.md` states that a green checkpoint is not the end of a timeboxed
      Goal when useful follow-up cycles fit the remaining budget.
- [x] A project-local `timeboxed-pdca-goal` Skill exists and triggers on
      "1h Goal", "2h Goal", "時間を余らせるな", "自律的にPlan", and
      "PDCAで回す".
- [x] The Skill requires a Remaining Budget Decision after every green
      checkpoint and defines explicit stop conditions.
- [x] Tests reject removal of the AGENTS rule or Skill trigger language.

Verification:

- [x] Focused project philosophy tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 45: Source-Informed State Transition PDCA Sample

Acceptance gates:

- [x] Use MathWorks official documentation as design inspiration for state
      transition tables, operating modes, and requirements-based harness
      assessment; cite the sources in the sample specification.
- [x] Add a fictional `toy_energy_buffer_mode` sample with requirements,
      Component/Data Flow/Sequence/Control Semantics views, MBD source,
      scenario, report, and generated handoff artifacts.
- [x] Keep the example synthetic: no real battery model, physical plant,
      register map, production ECU behavior, or copied MathWorks model data.
- [x] Preview Harness evidence shows scenario stimulus, observed behavior,
      expected behavior, pass/fail, and boundary evidence without owning
      control semantics.
- [x] Tests cover parser/model shape, spec-to-MBD conversion, deterministic
      generated artifacts, preview scenario pass/fail evidence, and sample
      catalog discovery.
- [x] Agent-side review confirms the first review path can be understood in
      about one minute and that external MBD/product-test verification remains
      explicitly out of scope.

Verification:

- [x] Focused new sample tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 44: Design Layer Separation And Generated-Side Checks

Acceptance gates:

- [x] Review principles state that Component View, Data Flow View, Sequence
      View, and Control Semantics View have separate review roles.
- [x] Spec-to-MBD generation prefers explicit Data Flow View and Control
      Semantics View sections while keeping legacy Design Overview samples
      compatible.
- [x] `simple_relay_hysteresis/spec.md` demonstrates the four-layer structure
      without adding new requirements, thresholds, states, or Harness behavior.
- [x] Tests prove Component/Sequence views do not silently become control
      implementation and that only explicit control semantics drive
      state/control generation.
- [x] Generated relay review artifacts are regenerated from source.
- [x] Agent-side reject loop confirms Harness and preview C are internal
      consistency evidence, not production MBD verification.

Verification:

- [x] Focused spec conversion and simple relay tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 40: Spec-First Demo And Harness Direction

Acceptance gates:

- [x] `AGENTS.md`, README, review principles, and local Skills state that
      "demo" means MBD review artifact, not a casual visual demo.
- [x] Harness guidance says the Harness supplies scenario stimulus, virtual IC
      and HAL boundary evidence, observed behavior, and report evidence only.
- [x] Harness guidance says control decisions, state transitions, and output
      decisions belong to MBD source, `mbd-control`, and functional
      decomposition, not scenario YAML or Harness shortcuts.
- [x] HTML review artifacts expose Harness as preview evidence and separate
      it from external MBD/product-test verification.
- [x] Tests reject regressions that blur demo, Harness, preview-only, and
      external verification boundaries.

Verification:

- [x] Focused philosophy/exporter/sample tests pass.
- [x] Affected generated artifacts are regenerated from sample source.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 41: Simple Relay Process Rehearsal

Acceptance gates:

- [x] Use `simple_relay_hysteresis` as the process rehearsal sample without
      inventing new requirements, thresholds, states, or Harness behavior.
- [x] Confirm spec-to-source alignment from `spec.md` to `model.mbd.md`.
- [x] Regenerate handoff/review artifacts from `model.mbd.md`.
- [x] Run the Harness preview scenario and confirm the report separates model
      inputs, scenario steps, Harness boundary evidence, observed behavior,
      expected behavior, and pass/fail.
- [x] Run the MBD review reject loop: spec compliance, transition-system
      review, traceability, Harness evidence boundary, and generated artifact
      boundary.

Verification:

- [x] `python -m veph validate-spec-mbd --spec samples/simple_relay_hysteresis/spec.md --mbd samples/simple_relay_hysteresis/model.mbd.md --out /tmp/simple_relay_alignment.md` passes.
- [x] `python -m veph export-sample simple_relay_hysteresis` succeeds.
- [x] `python -m veph run-preview --model samples/simple_relay_hysteresis/model.mbd.md --scenario samples/simple_relay_hysteresis/scenarios/hysteresis_cycle.yml --report samples/simple_relay_hysteresis/reports/hysteresis_cycle.md` passes.
- [x] Focused simple relay tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 42: Compact Spec Review HTML

Acceptance gates:

- [x] `from_spec_review.html` starts with a compact one-minute review path,
      not dense evidence text.
- [x] Requirement rows keep requirement, intended behavior, concise MBD/scenario
      evidence, and status, but omit long flow/function/Harness evidence
      strings from the first read.
- [x] Transition rows keep initial state, guard, action, trace, and status in a
      compact table.
- [x] Harness wording stays present but short; detailed Harness evidence remains
      in reports and the full review artifact.
- [x] Tests reject reintroducing long generated evidence summaries into
      spec-first review HTML.

Verification:

- [x] Regenerate affected sample review artifacts from source.
- [x] Focused spec-review sample tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Phase 43: Compact Spec-MBD Viewer HTML

Acceptance gates:

- [x] `spec_mbd_viewer.html` for non-state simple samples starts with a
      one-minute review summary before interactive or graph evidence.
- [x] Semantic graph sections remain visual but no longer duplicate every edge
      as dense tables in the first review path.
- [x] Alignment evidence emphasizes PASS/FAIL, matched counts, and Missing/Extra
      gaps; long matched-edge dumps are omitted from the HTML.
- [x] Constant/value evidence for switch-style samples remains visible enough
      for review.
- [x] Tests reject reintroducing dense matched-edge lists into
      `spec_mbd_viewer.html`.

Verification:

- [x] Regenerate `simple_threshold_indicator` and `simple_switch_selector`
      artifacts from source.
- [x] Focused threshold/switch/spec-MBD viewer tests pass.
- [x] Full `pytest` passes.
- [x] `git diff --check` passes.

## Current Size Baseline

- [x] `src/veph/exporters/demo_html.py`: 2438 lines.
- [x] `src/veph/spec_mbd_conversion.py`: 921 lines after first helper split.
- [x] `src/veph/preview_runtime/generic.py`: 514 lines.
- [x] `src/veph/markup_parser.py`: 480 lines.
- [x] `src/veph/spec_mbd_viewer.py`: 466 lines.
- [x] `src/veph/cli.py`: 463 lines.
- [x] `src/veph/spec_mbd_alignment.py`: 440 lines.
- [x] Generated HTML/reports are long but should be treated as outputs; refactor
      their generators, not the generated files directly.

## Refactor Checkpoint 1 Size Baseline

- [x] `src/veph/exporters/demo_html.py`: 1831 lines after extracting HTML
      helpers, state review rendering, and report evidence rendering.
- [x] `src/veph/preview_runtime/generic.py`: 384 lines after extracting
      expression evaluation.
- [x] `src/veph/spec_mbd_conversion.py`: 613 lines after extracting common text
      helpers, graph helpers, and state-machine MBD generation.
- [x] `src/veph/spec_mbd_conversion.py`: 102 lines after extracting decision
      and arithmetic/dataflow MBD generation.
- [x] `src/veph/spec_mbd_alignment.py`: 252 lines after extracting MBD semantic
      graph builders.

## Refactoring Quality Gates

- [x] Preserve public CLI behavior and sample manifests.
- [x] Preserve generated artifact determinism for all sample tests.
- [x] Preserve the MVP coverage matrix at 34/34.
- [x] Keep generated/review artifacts reviewable; do not hide semantics in
      comments or generic dumps.
- [x] Split by responsibility, not by arbitrary line count.
- [x] Run focused tests after each phase and full `pytest` before commit.
- [x] Run `git diff --check` before commit.

## Phase 35: HTML Review Exporter Decomposition

- [x] Identify high-level sections inside `src/veph/exporters/demo_html.py`:
      common HTML helpers, generic review shell, state-machine review,
      scenario evidence, traceability/evidence sections, and Japanese labels.
- [x] Extract pure formatting helpers into a small module such as
      `src/veph/exporters/html_helpers.py`.
- [x] Extract state-machine review rendering into a focused module such as
      `src/veph/exporters/state_review_html.py`.
- [x] Extract scenario/report evidence rendering into a focused module such as
      `src/veph/exporters/evidence_html.py`.
- [x] Keep `export_demo_html()` as the stable public entry point.

Verification:

- [x] Focused exporter/sample tests pass.
- [x] Generated sample HTML remains deterministic.
- [x] `demo_html.py` drops substantially from 2438 lines without changing
      rendered review semantics.

## Phase 36: Preview Runtime Decomposition

- [x] Extract `ExpressionIR` evaluation and safe arithmetic evaluation into
      `src/veph/preview_runtime/expression_eval.py`.
- [x] Extract scenario step evidence construction into a focused helper module
      or small internal functions.
- [x] Keep `run_preview()` and `run_preview_file()` as stable public entry
      points.

Verification:

- [x] `tests/test_preview_runtime.py` passes.
- [x] Sample preview report tests pass.
- [x] `generic.py` becomes easier to scan, with runtime orchestration separated
      from expression semantics.

## Phase 37: Spec-To-MBD Generator Decomposition

- [x] Split decision/control-rule generation out of `spec_mbd_conversion.py`.
- [x] Split state-machine MBD generation out of `spec_mbd_conversion.py`.
- [x] Split arithmetic/dataflow MBD generation out of `spec_mbd_conversion.py`
      while keeping parser helpers in `spec_dataflow.py`.
- [x] Keep `generate_mbd_from_spec()` as the stable public entry point.

Verification:

- [x] `tests/test_spec_mbd_conversion.py` passes.
- [x] Spec/MBD alignment tests pass.
- [x] `spec_mbd_conversion.py` becomes an orchestration layer rather than the
      owner of every generation detail.

## Phase 38: Parser And Alignment Cleanup

- [x] Reviewed expression parsing in `markup_parser.py` and kept it local
      because splitting it now would add indirection without improving parser
      diagnostics.
- [x] Split semantic graph builders in `spec_mbd_alignment.py` by concern:
      decision graphs, generic flow graphs, and state/dataflow graph support.
- [x] Add narrow tests for any extracted parser/alignment helper if existing
      tests do not already cover it directly.

Verification:

- [x] Parser tests pass.
- [x] Spec/MBD alignment tests pass.
- [x] Unsupported syntax diagnostics remain actionable.

## Phase 39: Final Refactor Verification And Checkpoint

- [x] Confirm no generated sample artifacts required refresh; determinism tests
      stayed green without direct generated-file edits.
- [x] Run focused tests for exporters, preview runtime, parser, conversion, and
      sample determinism.
- [x] Run full `pytest`.
- [x] Run `git diff --check`.
- [x] Review module sizes and record the new baseline in this file.
- [x] Commit, push, and merge after the refactor is green.
