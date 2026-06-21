# Design Principles

Author in text. Verify in MBD tools.

This project is a Markup-to-MBD bridge. The authoring experience should feel
closer to Mermaid than to inventing a full modeling language or runtime.

## Mermaid-Like Markup

The public authoring source is Markdown containing compact fenced blocks such as
`mbd-component`, `mbd-registers`, `mbd-state`, and `mbd-flow`.

The markup should be easy for humans and LLMs to read, diff, review, and edit.
It is intentionally small and fictional-example friendly.

## Authoring Source Policy

`samples/<sample-id>/model.mbd.md` is the public source for each sample.
Generated files are review or handoff artifacts. The internal IR JSON exists to
connect parser and exporters; it is not advertised as a user-facing standard.

YAML is not the public source of truth. Existing YAML files may remain as legacy
preview inputs, optional expanded machine-readable forms, or temporary
implementation details.

For substantial validation examples, begin with `Requirements.md`, derive a
human-readable sample specification under `samples/<sample-id>/spec.md`, then
write the `.mbd.md` source. Do not jump directly from a vague idea into runtime
or generated artifacts.

## ASPICE-Aware Process Boundary

MBD examples are treated as stricter product-development work products than a
casual demo. Use stable requirement IDs, trace links, review gates,
deterministic regeneration tests, and explicit evidence files.

This is process inspiration only. The repository does not claim ASPICE
compliance, safety certification, production readiness, or tool qualification.

## Existing MBD Tools As Verification Backends

The project does not try to replace Simulink, Stateflow, Modelica, FMI tools, or
certified MBD workflows. Existing MBD tools are the intended verification
backends.

Generated Simulink `.m`, Modelica `.mo`, SCXML, Mermaid, PlantUML, and FMI
metadata are handoff artifacts. They should make it easier to inspect or import
the model in existing environments.

## Generated Artifact Policy

Generated artifacts must be reproducible from the Markdown markup source. Manual
edits to generated artifacts are not the model-change workflow.

If a generated artifact is wrong, fix the markup or exporter and regenerate it.

## Python Preview Boundary

Python preview is only a preview/smoke-test helper. It may parse markup, emit
artifacts, and run lightweight sanity checks, but it must not be presented as
the main verification path or a custom MBD semantic universe.

Scenario YAML, if used, is test input only. It is not the MBD source of truth.

## Harness Evidence Boundary

Harness is a preview evidence layer. It exists to expose scenario stimulus,
fictional virtual IC boundaries, HAL boundaries, observed behavior, expected
behavior, and pass/fail report evidence before external MBD/product-test
handoff.

Control decisions, state transitions, and output decisions belong to MBD source,
`mbd-control`, and functional decomposition. Scenario YAML, Python preview
helpers, and virtual IC fixtures must not add missing thresholds, recovery
rules, or state behavior for convenience. Missing behavior should become an
open review question or a preview limitation, not hidden Harness logic.

## YAML And IR Policy

The internal IR should stay pragmatic and tool-facing. It is a snapshot that
helps exporters share parsed structure. It is not a public modeling standard.

YAML support must not become the central user-facing format.

## Certification Boundary

This repository does not claim certification. It uses fictional components and
synthetic examples only. It must not include real IC names, real datasheets,
real ECU specifications, production-derived code, confidential project names, or
company-specific details.
