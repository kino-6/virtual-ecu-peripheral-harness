from pathlib import Path

from veph.cli import main
from veph.markup_parser import parse_markup_file
from veph.sample_catalog import load_sample
from veph.spec_mbd_alignment import (
    SpecMbdAlignmentError,
    compare_spec_to_mbd,
    parse_spec_design_overview,
    semantic_graph_from_mbd,
)


ROOT = Path(__file__).resolve().parents[1]


def test_parse_spec_design_overview_mermaid_subset():
    sample = load_sample("simple_threshold_indicator", ROOT)

    graph = parse_spec_design_overview(sample.paths.spec)

    assert "ToyInputSource" in graph.nodes
    assert "Input Port: sampleValue" in graph.nodes
    assert "Parameter: limit" in graph.nodes
    assert "sampleValue >= limit?" in graph.nodes
    assert "Output active = true" in graph.nodes
    assert "Output active = false" in graph.nodes
    assert "ScenarioReport.observedBehavior" in graph.nodes
    assert graph.has_edge("ToyInputSource", "sampleValue", "Input Port: sampleValue")
    assert graph.has_edge("Parameter: limit", "", "sampleValue >= limit?")
    assert graph.has_edge("sampleValue >= limit?", "true", "Output active = true")
    assert graph.has_edge("sampleValue >= limit?", "false", "Output active = false")


def test_simple_threshold_spec_mermaid_matches_mbd_semantics():
    sample = load_sample("simple_threshold_indicator", ROOT)

    report = compare_spec_to_mbd(sample.paths.spec, sample.paths.model)

    assert report.passed is True
    rendered = report.to_markdown()
    assert "Spec-to-MBD semantic alignment: **PASS**" in rendered
    assert "Output active = true" in rendered


def test_spec_mermaid_mismatch_reports_actionable_diagnostics(tmp_path):
    sample = load_sample("simple_threshold_indicator", ROOT)
    spec_text = sample.paths.spec.read_text(encoding="utf-8")
    mismatched_spec = tmp_path / "spec.md"
    mismatched_spec.write_text(
        spec_text.replace("Output active = true", "Output active = maybe"),
        encoding="utf-8",
    )

    report = compare_spec_to_mbd(mismatched_spec, sample.paths.model)

    assert report.passed is False
    assert "Output active = maybe" in report.missing_nodes
    assert "Output active = true" in report.extra_nodes
    rendered = report.to_markdown()
    assert "Spec-to-MBD semantic alignment: **FAIL**" in rendered
    assert "Missing MBD nodes" in rendered
    assert "Extra MBD nodes" in rendered


def test_mbd_semantic_graph_is_derived_from_model_not_generated_mermaid():
    sample = load_sample("simple_threshold_indicator", ROOT)
    model = parse_markup_file(sample.paths.model)

    graph = semantic_graph_from_mbd(model)

    assert graph.has_edge("ToyInputSource", "sampleValue", "Input Port: sampleValue")
    assert graph.has_edge("Input Port: sampleValue", "", "sampleValue >= limit?")
    assert graph.has_edge("Parameter: limit", "", "sampleValue >= limit?")
    assert graph.has_edge("sampleValue >= limit?", "true", "Output active = true")
    assert graph.has_edge("sampleValue >= limit?", "false", "Output active = false")


def test_unsupported_spec_mermaid_reports_the_line(tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_text(
        "\n".join(
            [
                "# Spec",
                "## Design Overview",
                "```mermaid",
                "flowchart LR",
                "  A -.-> B",
                "```",
            ]
        ),
        encoding="utf-8",
    )

    try:
        parse_spec_design_overview(spec)
    except SpecMbdAlignmentError as exc:
        assert "unsupported Mermaid line" in str(exc)
        assert "A -.-> B" in str(exc)
    else:
        raise AssertionError("expected SpecMbdAlignmentError")


def test_validate_spec_mbd_cli_writes_report(tmp_path):
    sample = load_sample("simple_threshold_indicator", ROOT)
    report_path = tmp_path / "spec_mbd_alignment.md"

    exit_code = main(
        [
            "validate-spec-mbd",
            "--spec",
            str(sample.paths.spec),
            "--mbd",
            str(sample.paths.model),
            "--out",
            str(report_path),
        ]
    )

    assert exit_code == 0
    report = report_path.read_text(encoding="utf-8")
    assert "Spec-to-MBD semantic alignment: **PASS**" in report
    assert "Missing MBD nodes" in report
