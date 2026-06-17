---
name: preview-harness-codegen
description: Project-local workflow for preview-only virtual IC harnesses, scenario smoke tests, and generated C scaffolds. Use when Codex adds preview_runtime modules, run-preview, export-code-preview, HAL-style generated C, or scenarios for fictional control-system validation.
---

# Preview Harness Codegen

Use this skill when adding preview runtime, scenarios, or local generated C
scaffolds.

## Rules

- Preview runtime is not the main verifier.
- Generated C is preview-only and non-certified.
- Product-like ECU logic must communicate through HAL-style boundaries.
- Do not let generated C call Python internals.
- Use fictional ICs, fictional registers, and synthetic scenarios only.
- Scenario YAML is test input only, not MBD source of truth.

## Workflow

1. Update `Tasks.md` and mark items only after verification.
2. Confirm the scenario maps back to requirement IDs and specification behavior.
3. Add tests for normal and fault scenarios before implementation.
4. Keep preview runtime discrete-step and simple.
5. Generate C into `generated/ecu_preview/`.
6. Include a `README.md` in generated C output stating preview-only status.
7. If a local C compiler is available, syntax-check the generated scaffold.
8. Run the relevant preview tests and `pytest`.

## Expected Commands

These commands may not exist yet; add them when implementing the thermal fan
validation goal:

```bash
python -m veph export-code-preview examples/toy_thermal_fan_control.mbd.md --out generated/ecu_preview/
python -m veph run-preview --model examples/toy_thermal_fan_control.mbd.md --scenario scenarios/thermal_fan_normal.yml --report reports/thermal_fan_normal.md
python -m veph run-preview --model examples/toy_thermal_fan_control.mbd.md --scenario scenarios/thermal_fan_fault.yml --report reports/thermal_fan_fault.md
```

## Report Checks

Preview reports should separate:

- markup source
- scenario inputs
- virtual IC observations
- generated ECU command outputs
- expected behavior
- pass/fail result
- preview-only disclaimer
