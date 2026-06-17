# Project Operating Rules

This file is the project-level guidance for agents working in this repository.
It captures the direction established during the early MVP work and the later
pivot away from a custom YAML runtime.

## North Star

Author in text. Verify in MBD tools.

This repository is a Mermaid-like Markup-to-MBD bridge for virtual ECU and
peripheral model authoring. The public authoring source should be readable
Markdown, not a custom YAML modeling language.

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

## What This Project Is

- A lightweight authoring and review layer for virtual ECU/peripheral models.
- A bridge from LLM-readable Markdown markup to MBD-oriented artifacts.
- A way to draft fictional IC/peripheral/control-system specs and hand them off
  to existing MBD tools.
- A commercial-tool-free authoring workflow that can export to commercial MBD
  environments when those tools are available.

## What This Project Is Not

- Not a new MBD language.
- Not a custom MBD runtime.
- Not a Simulink, Stateflow, Modelica, FMI, or certified workflow replacement.
- Not a production ECU simulator.
- Not a physical electrical solver.
- Not a certification claim.

## Source-Of-Truth Policy

Public source is `examples/*.mbd.md`.

YAML is not the public source of truth. Existing YAML support may remain only as
legacy preview input, optional expanded machine-readable form, or implementation
detail. Do not center new work around `*.tmbd.yml`.

The internal IR is a tooling snapshot, not a public standard. It should stay
small, pragmatic, and exporter-oriented.

## Verification Policy

Existing MBD tools are the intended verification backends.

Python may parse markup, generate artifacts, run smoke tests, and provide local
previews. Python must not be described as the main verification path or as a
custom MBD semantic universe.

When adding local preview behavior or local C generation, label it explicitly:

```text
preview-only; not a certified code generation or verification backend
```

## Fictional-Only Safety Policy

Use only fictional components, synthetic examples, and invented register maps.

Do not use:

- real IC names
- real datasheets
- real ECU specifications
- real register maps
- real company names
- production-derived code
- confidential project names or details

Sample ECU code may look product-like, but it must remain synthetic and must
communicate through HAL-style boundaries rather than Python internals.

## Target Validation Story

The next major validation should demonstrate a complete fictional control
system:

```text
fictional IC spec
  -> Mermaid-like markup spec
  -> internal IR
  -> MBD handoff artifacts
  -> virtual IC harness preview
  -> preview ECU C code generation
  -> scenario smoke verification
```

The preferred fictional example is a thermal fan control system with:

- `ToyTempSensorIC`
- `ToyFanDriverIC`
- a virtual ECU controller
- normal and fault scenarios
- generated Simulink/Modelica/FMI handoff artifacts
- preview-only generated C scaffold

## Code Generation Boundary

There are two separate routes:

1. Tool-backed MBD code generation route:
   - Markup generates Simulink `.m`, Modelica `.mo`, SCXML/Stateflow-oriented
     tables, and FMI metadata.
   - Existing tools perform real verification/code generation outside this repo.

2. Local preview code generation route:
   - IR may generate simple C scaffold for smoke testing.
   - This is not certified and not the project’s main verification path.

Never blur these two routes.

## Implementation Preferences

- Keep dependencies minimal.
- Prefer explicit parser/IR/exporter tests for new syntax.
- Keep generated artifacts reproducible from markup.
- Avoid over-engineering physics or runtime semantics.
- When adding a feature, update README, `docs/design_principles.md`, generated
  artifacts, and tests together.

