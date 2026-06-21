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

Reduce long Python implementation modules while preserving behavior, generated
artifact determinism, and the 34/34 repository-defined Mermaid-to-MBD MVP
coverage contract.

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

- [ ] Split decision/control-rule generation out of `spec_mbd_conversion.py`.
- [x] Split state-machine MBD generation out of `spec_mbd_conversion.py`.
- [ ] Split arithmetic/dataflow MBD generation out of `spec_mbd_conversion.py`
      while keeping parser helpers in `spec_dataflow.py`.
- [x] Keep `generate_mbd_from_spec()` as the stable public entry point.

Verification:

- [x] `tests/test_spec_mbd_conversion.py` passes.
- [x] Spec/MBD alignment tests pass.
- [ ] `spec_mbd_conversion.py` becomes an orchestration layer rather than the
      owner of every generation detail.

## Phase 38: Parser And Alignment Cleanup

- [ ] Split expression parsing out of `markup_parser.py` only if it reduces
      cognitive load without weakening parser diagnostics.
- [ ] Split semantic graph builders in `spec_mbd_alignment.py` by concern:
      decision graphs, generic flow graphs, and state/dataflow graph support.
- [ ] Add narrow tests for any extracted parser/alignment helper if existing
      tests do not already cover it directly.

Verification:

- [ ] Parser tests pass.
- [ ] Spec/MBD alignment tests pass.
- [ ] Unsupported syntax diagnostics remain actionable.

## Phase 39: Final Refactor Verification And Checkpoint

- [ ] Regenerate affected sample artifacts only through existing CLI commands.
- [ ] Run focused tests for exporters, preview runtime, parser, conversion, and
      sample determinism.
- [ ] Run full `pytest`.
- [ ] Run `git diff --check`.
- [ ] Review module sizes and record the new baseline in this file.
- [ ] Commit, push, and merge after the refactor is green.
