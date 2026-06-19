from pathlib import Path

from veph.requirements_support import (
    extract_requirements,
    generate_mbd_scaffold,
    generate_spec_scaffold,
    render_requirements_json,
    validate_traceability,
)
from veph.samples.requirements_scaffolds import generate_sample_mbd_scaffold


ROOT = Path(__file__).resolve().parents[1]


def test_extract_requirements_captures_ids_classes_sections_and_evidence():
    extracted = extract_requirements(ROOT / "Requirements.md")

    by_id = {item.id: item for item in extracted.requirements}

    assert by_id["SYS-006"].classification == "DSC-C"
    assert by_id["SYS-006"].section == "System Requirements"
    assert "safe fictional command" in by_id["SYS-006"].statement
    assert "Markup components" in by_id["SYS-006"].planned_evidence
    assert by_id["REQ2MBD-007"].section == "Requirements-To-MBD Support Requirements"
    assert "Open Questions" not in render_requirements_json(extracted)
    assert '"REQ2SPEC-001"' in render_requirements_json(extracted)


def test_generate_spec_scaffold_preserves_trace_and_open_questions():
    extracted = extract_requirements(ROOT / "Requirements.md")
    scaffold = generate_spec_scaffold(extracted)

    assert "# Specification Scaffold" in scaffold
    assert "Source requirements: `Requirements.md`" in scaffold
    assert "## Review Status" in scaffold
    assert "Behavior approval: **PENDING**" in scaffold
    assert "This scaffold is not an approved specification." in scaffold
    assert "## Requirement Trace Appendix" in scaffold
    assert "| `SYS-006` | `DSC-C` | System Requirements |" in scaffold
    assert "## Open Questions" in scaffold
    assert "`SYS-007`" in scaffold
    assert "Do not invent missing thresholds, timings, recovery rules, or fault semantics." in scaffold


def test_generate_mbd_scaffold_preserves_trace_and_refuses_to_invent_behavior():
    extracted = extract_requirements(ROOT / "Requirements.md")
    scaffold = generate_mbd_scaffold(extracted)

    assert "# MBD Scaffold" in scaffold
    assert "component TODO_ComponentName" in scaffold
    assert "trace SYS-001 SYS-002" in scaffold
    assert "```mbd-control" in scaffold
    assert "Behavior approval: **PENDING**" in scaffold
    assert "TODO values are explicit placeholders, not accepted demo answers." in scaffold
    assert "does not choose a controller, IC, signal set, threshold, or scenario" in scaffold
    assert "open-question SYS-007" in scaffold
    assert "Do not treat this scaffold as approved behavior" in scaffold
    assert "ToyThermalProtectionController" not in scaffold
    assert "ToyTempSensorIC" not in scaffold


def test_thermal_protection_mbd_scaffold_requires_explicit_sample_selection():
    extracted = extract_requirements(ROOT / "Requirements.md")
    scaffold = generate_sample_mbd_scaffold("thermal-protection", extracted)

    assert "component ToyThermalProtectionController" in scaffold
    assert "ToyTempSensorIC.temperatureC -> HAL_SPI.read_temperature" in scaffold
    assert "rule TODO_sensorFault" in scaffold
    assert "open-question SYS-007" in scaffold


def test_validate_traceability_reports_missing_and_untraced_behavior():
    extracted = extract_requirements(ROOT / "Requirements.md")
    spec = generate_spec_scaffold(extracted)
    mbd = generate_mbd_scaffold(extracted) + "\n```mbd-control\nrule stray: when x == true then y=1\n```\n"

    report = validate_traceability(extracted, spec, mbd)

    assert report.passed is False
    assert any("untraced MBD behavior" in item for item in report.findings)
    rendered = report.to_markdown()
    assert "## Missing Spec Coverage" in rendered
    assert "## Missing MBD Coverage" in rendered
    assert "## Untraced MBD Behavior" in rendered
    assert "Behavior approval" in rendered


def test_validate_traceability_passes_coverage_but_keeps_behavior_pending():
    extracted = extract_requirements(ROOT / "Requirements.md")
    report = validate_traceability(
        extracted,
        generate_spec_scaffold(extracted),
        generate_mbd_scaffold(extracted),
    )

    assert report.passed is True
    rendered = report.to_markdown()
    assert "Coverage result: **PASS**" in rendered
    assert "Behavior approval: **PENDING**" in rendered
    assert "open question" in rendered
