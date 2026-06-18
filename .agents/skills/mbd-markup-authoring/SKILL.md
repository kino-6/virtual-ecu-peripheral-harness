---
name: mbd-markup-authoring
description: Project-local workflow for editing or extending Mermaid-like MBD Markdown authoring files under examples/*.mbd.md, including mbd-component, mbd-registers, mbd-state, mbd-flow, mbd-control, parser/IR changes, and source-to-artifact traceability. Use when Codex works on markup syntax, example specs, parser behavior, or IR fields for this repository.
---

# MBD Markup Authoring

Use this skill when changing `Requirements.md`, `specs/*.md`,
`examples/*.mbd.md`, `src/veph/markup_parser.py`, or `src/veph/ir.py`.

## Rules

- Keep `examples/*.mbd.md` as the public authoring source.
- For substantial examples, start from `Requirements.md` and a human-readable
  specification before editing markup.
- Do not promote YAML to public source of truth.
- Keep the syntax compact and Mermaid-like.
- Use only fictional components, registers, buses, and project names.
- Treat IR JSON as an internal snapshot, not a user-facing standard.
- When `mbd-state` and `mbd-control` overlap, use
  `mbd-control-semantics` before changing syntax or examples.

## Workflow

1. Update `Tasks.md` before substantial syntax or IR work.
2. Confirm requirement IDs and specification anchors exist for new behavior.
3. Add or update parser tests first.
4. Parse from Markdown fenced blocks into IR dataclasses.
5. Preserve section traceability in `MarkupSectionIR` and requirement refs in
   parsed structures.
6. Regenerate IR snapshots with:

```bash
python -m veph parse examples/toy_power_monitor.mbd.md --out generated/toy_power_monitor.ir.json
```

7. Run:

```bash
pytest tests/test_markup_parser.py tests/test_markup_exports.py
```

## Design Checks

- New syntax should be readable without tool-specific knowledge.
- Parser errors should name the malformed section or line.
- Generated artifacts must remain reproducible from the `.mbd.md` source.
- State diagrams and control rules must not define competing executable
  behavior. Prefer one reviewable control semantics and derive views from it.
- If a feature starts requiring deep semantics, prefer a handoff artifact over a
  Python runtime interpretation.
