from pathlib import Path

from veph.cli import main
from veph.markup_parser import parse_markup, parse_markup_file
from veph.sample_catalog import load_sample
from veph.spec_mbd_alignment import compare_spec_to_mbd, compare_spec_to_mbd_model
from veph.spec_mbd_conversion import generate_mbd_from_spec
from veph.spec_mbd_viewer import export_spec_mbd_viewer


ROOT = Path(__file__).resolve().parents[1]


def test_generate_mbd_from_spec_mermaid_is_parseable_and_aligned():
    sample = load_sample("simple_threshold_indicator", ROOT)

    mbd_text = generate_mbd_from_spec(
        sample.paths.spec,
        component_name="ToyThresholdIndicator",
        parameter_defaults={"limit": "10"},
        scenario="above_limit",
    )
    model = parse_markup(mbd_text, sample.paths.generated_dir / "from_spec.model.mbd.md")
    report = compare_spec_to_mbd_model(sample.paths.spec, model, model.source_path)

    assert model.component.name == "ToyThresholdIndicator"
    assert set(model.ports) == {"sampleValue", "active"}
    assert set(model.component.parameters) == {"limit"}
    assert len(model.controls) == 2
    assert report.passed is True
    assert "Generated from Spec Mermaid Design Overview" in mbd_text
    assert "priority 10 rule active_true" in mbd_text
    assert "priority 20 rule active_false" in mbd_text


def test_generate_mbd_from_spec_cli_writes_authoring_source(tmp_path):
    sample = load_sample("simple_threshold_indicator", ROOT)
    out = tmp_path / "from_spec.model.mbd.md"

    exit_code = main(
        [
            "generate-mbd-from-spec",
            "--spec",
            str(sample.paths.spec),
            "--component",
            "ToyThresholdIndicator",
            "--parameter-default",
            "limit=10",
            "--scenario",
            "above_limit",
            "--out",
            str(out),
        ]
    )

    assert exit_code == 0
    generated = parse_markup_file(out)
    assert generated.component.name == "ToyThresholdIndicator"
    assert compare_spec_to_mbd_model(sample.paths.spec, generated, out).passed is True


def test_render_spec_mbd_cli_uses_sample_metadata_from_spec_path(tmp_path):
    sample = load_sample("simple_threshold_indicator", ROOT)
    viewer = tmp_path / "viewer.html"
    converted = tmp_path / "from_spec.model.mbd.md"

    exit_code = main(
        [
            "render-spec-mbd",
            str(sample.paths.spec),
            "--out",
            str(viewer),
            "--mbd-out",
            str(converted),
        ]
    )

    assert exit_code == 0
    assert viewer.exists()
    assert converted.exists()
    assert parse_markup_file(converted).component.name == "ToyThresholdIndicator"
    assert "Alignment: PASS" in viewer.read_text(encoding="utf-8")


def test_export_sample_writes_converted_mbd_and_review_viewer():
    sample = load_sample("simple_threshold_indicator", ROOT)

    assert main(["export-sample", "simple_threshold_indicator"]) == 0

    converted = sample.paths.generated["convertedMbd"]
    viewer = sample.paths.generated["specMbdViewer"]
    assert converted.exists()
    assert viewer.exists()
    assert parse_markup_file(converted).component.name == "ToyThresholdIndicator"
    assert compare_spec_to_mbd(sample.paths.spec, converted).passed is True
    html = viewer.read_text(encoding="utf-8")
    assert "Spec Mermaid To MBD Review" in html
    assert "Alignment: PASS" in html
    assert "Spec Mermaid Semantic Graph" in html
    assert "Converted MBD Semantic Graph" in html
    assert "Output active = true" in html


def test_spec_mbd_viewer_renders_alignment_evidence():
    sample = load_sample("simple_threshold_indicator", ROOT)
    mbd_text = generate_mbd_from_spec(
        sample.paths.spec,
        component_name="ToyThresholdIndicator",
        parameter_defaults={"limit": "10"},
        scenario="above_limit",
    )
    model = parse_markup(mbd_text, sample.paths.generated_dir / "from_spec.model.mbd.md")
    report = compare_spec_to_mbd_model(sample.paths.spec, model, model.source_path)

    html = export_spec_mbd_viewer(sample.paths.spec, model, report)

    assert "<svg" in html
    assert "ToyInputSource" in html
    assert "sampleValue &gt;= limit?" in html
    assert "Missing MBD nodes" in html
    assert "None" in html
