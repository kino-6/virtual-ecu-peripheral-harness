---
name: mbd-artifact-export
description: Project-local workflow for generating, updating, and validating MBD handoff artifacts from the internal IR, including Markdown review docs, Mermaid, PlantUML, Simulink .m, Modelica .mo, SCXML, and FMI metadata. Use when Codex modifies exporters, generated artifacts, or source-to-artifact determinism tests.
---

# MBD Artifact Export

Use this skill when changing files under `src/veph/exporters/` or generated MBD
handoff artifacts under `generated/`.

## Rules

- Exporters consume IR from Mermaid-like Markdown markup.
- Generated artifacts are handoff/review outputs, not source.
- Existing MBD tools are the verification backends.
- Simulink, Modelica, SCXML, Mermaid, PlantUML, and FMI outputs must not imply
  certification.
- FMI export is metadata only; do not generate FMUs.

## Workflow

1. Add or update exporter tests first.
2. Keep each exporter deterministic.
3. Regenerate affected artifacts from the `.mbd.md` source.
4. Check generated files include source/preview/handoff wording where relevant.
5. Run:

```bash
pytest tests/test_exporters.py tests/test_markup_exports.py
```

## Regeneration Commands

```bash
python -m veph export-docs examples/toy_power_monitor.mbd.md --out generated/toy_power_monitor.md
python -m veph export-mermaid examples/toy_power_monitor.mbd.md --out generated/toy_power_monitor.mmd
python -m veph export-plantuml examples/toy_power_monitor.mbd.md --out generated/toy_power_monitor.puml
python -m veph export-simulink-m examples/toy_power_monitor.mbd.md --out generated/create_toy_power_monitor_model.m
python -m veph export-modelica examples/toy_power_monitor.mbd.md --out generated/ToyPowerMonitor.mo
python -m veph export-fmi-metadata examples/toy_power_monitor.mbd.md --out generated/toy_power_monitor.fmi.json
```

## Design Checks

- Simulink scripts should contain plausible `new_system`, `open_system`,
  `add_block`, `add_line`, and `set_param` operations.
- Modelica should preserve component, ports, parameters, states, and signals.
- Preview diagrams should be readable and traceable to source sections.
