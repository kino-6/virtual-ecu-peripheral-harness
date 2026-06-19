from pathlib import Path

from veph.exporters.demo_html import export_demo_html
from veph.exporters.fmi_metadata import export_fmi_metadata
from veph.exporters.markdown import export_markdown
from veph.exporters.mermaid import export_mermaid
from veph.exporters.modelica import export_modelica
from veph.exporters.plantuml import export_plantuml
from veph.exporters.scxml import export_scxml
from veph.exporters.simulink_m import export_simulink_m
from veph.markup_parser import parse_markup_file
from veph.preview_runtime import run_preview_file
from veph.sample_catalog import load_sample
from veph.spec_mbd_alignment import compare_spec_to_mbd


ROOT = Path(__file__).resolve().parents[1]


def test_simple_threshold_sample_is_intentionally_small():
    sample = load_sample("simple_threshold_indicator", ROOT)
    model = parse_markup_file(sample.paths.model)

    assert model.component.name == "ToyThresholdIndicator"
    assert set(model.ports) == {"sampleValue", "active"}
    assert set(model.component.parameters) == {"limit"}
    assert len(model.transitions) == 2
    assert len(model.controls) == 2
    assert len(model.functions) == 1
    assert model.functions[0].name == "ThresholdCompare"
    assert len(model.flows) == 4
    assert len(model.harness_devices) == 2


def test_simple_threshold_generated_artifacts_are_deterministic():
    sample = load_sample("simple_threshold_indicator", ROOT)
    model = parse_markup_file(sample.paths.model)
    expected_outputs = {
        sample.paths.generated["docs"]: export_markdown(model),
        sample.paths.generated["demo"]: export_demo_html(model),
        sample.paths.generated["mermaid"]: export_mermaid(model),
        sample.paths.generated["plantuml"]: export_plantuml(model),
        sample.paths.generated["scxml"]: export_scxml(model),
        sample.paths.generated["modelica"]: export_modelica(model),
        sample.paths.generated["simulink"]: export_simulink_m(model),
        sample.paths.generated["fmi"]: export_fmi_metadata(model),
        sample.paths.generated["specMbdAlignment"]: compare_spec_to_mbd(
            sample.paths.spec,
            sample.paths.model,
        ).to_markdown(),
    }

    for path, regenerated in expected_outputs.items():
        assert path.read_text(encoding="utf-8") == regenerated


def test_simple_threshold_generated_visuals_match_spec_design():
    sample = load_sample("simple_threshold_indicator", ROOT)
    mermaid = sample.paths.generated["mermaid"].read_text(encoding="utf-8")
    html = sample.paths.generated["demo"].read_text(encoding="utf-8")

    assert "%% Semantic MBD Block Diagram" in mermaid
    assert 'source_ToyInputSource["ToyInputSource"]' in mermaid
    assert 'input_sampleValue["Input Port: sampleValue"]' in mermaid
    assert 'parameter_limit["Parameter: limit"]' in mermaid
    assert 'decision_activate_clear{"sampleValue >= limit?"}' in mermaid
    assert 'action_activate["Output active = true"]' in mermaid
    assert 'action_clear["Output active = false"]' in mermaid
    assert 'decision_activate_clear -->|"true"| action_activate' in mermaid
    assert 'decision_activate_clear -->|"false"| action_clear' in mermaid
    assert "ToyInputSource_sampleValue -->|\"scenario input\"| ThresholdCompare_sampleValue" in mermaid
    assert "ToyThresholdIndicator_limit -->|\"threshold parameter\"| ThresholdCompare_limit" in mermaid
    assert "ThresholdCompare_active -->|\"comparison result\"| ToyThresholdIndicator_active" in mermaid
    assert "owner ThresholdCompare" in mermaid
    assert "sampleValue >= limit" in mermaid
    assert "sampleValue < limit" in mermaid

    assert "Semantic MBD Block Diagram" in html
    assert "ToyInputSource.sampleValue" in html
    assert "Virtual Source" in html
    assert "Input Port" in html
    assert "sampleValue" in html
    assert "ToyThresholdIndicator.limit" in html
    assert "Parameter" in html
    assert "sampleValue &gt;= limit?" in html
    assert "Output active = true" in html
    assert "Output active = false" in html
    assert "true" in html
    assert "false" in html
    assert "ThresholdCompare.sampleValue" in html
    assert "ThresholdCompare.limit" in html
    assert "ThresholdCompare.active" in html
    assert "comparison result" in html


def test_simple_threshold_preview_scenario_passes_with_report_sections(tmp_path):
    sample = load_sample("simple_threshold_indicator", ROOT)
    report_path = tmp_path / "above_limit.md"

    result = run_preview_file(
        sample.paths.model,
        sample.paths.scenarios["above_limit"],
        report_path=report_path,
    )

    assert result.passed is True
    assert result.final_state == "ACTIVE"
    assert result.generated_ecu_command_outputs["active"] is True
    report = report_path.read_text(encoding="utf-8")
    assert "## Model Inputs" in report
    assert "## Scenario Steps" in report
    assert "## Observed Behavior" in report
    assert "## Expected Behavior" in report
    assert "## Pass/Fail Result" in report
