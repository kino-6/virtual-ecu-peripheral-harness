from pathlib import Path

import yaml

from veph.cli import main
from veph.exporters.demo_html import export_demo_html
from veph.exporters.fmi_metadata import export_fmi_metadata
from veph.exporters.markdown import export_markdown
from veph.exporters.mermaid import export_mermaid
from veph.exporters.modelica import export_modelica
from veph.exporters.plantuml import export_plantuml
from veph.exporters.scxml import export_scxml
from veph.exporters.simulink_m import export_simulink_m
from veph.markup_parser import parse_markup, parse_markup_file
from veph.preview_runtime import run_preview_file
from veph.report import render_report
from veph.sample_catalog import load_sample
from veph.spec_mbd_alignment import compare_spec_to_mbd_model
from veph.spec_mbd_conversion import generate_mbd_from_spec


ROOT = Path(__file__).resolve().parents[1]


def test_simple_relay_hysteresis_sample_is_intentionally_small():
    sample = load_sample("simple_relay_hysteresis", ROOT)
    model = parse_markup_file(sample.paths.model)

    assert model.component.name == "ToyRelayHysteresis"
    assert set(model.component.parameters) == {"onThreshold", "offThreshold"}
    assert set(model.ports) == {"level", "active"}
    assert [(transition.source, transition.target) for transition in model.transitions] == [
        ("OFF", "ON"),
        ("ON", "OFF"),
    ]
    assert [transition.condition for transition in model.transitions] == [
        "level >= onThreshold",
        "level <= offThreshold",
    ]
    assert [control.state_scope for control in model.controls] == ["OFF", "ON"]
    assert model.controls[0].actions == {"state": "ON", "active": "true"}
    assert model.controls[1].actions == {"state": "OFF", "active": "false"}


def test_simple_relay_hysteresis_preview_proves_state_memory():
    sample = load_sample("simple_relay_hysteresis", ROOT)
    scenario = yaml.safe_load(sample.paths.scenarios["hysteresis_cycle"].read_text(encoding="utf-8"))

    assert scenario["expect"]["finalState"] == "OFF"

    result = run_preview_file(sample.paths.model, sample.paths.scenarios["hysteresis_cycle"])

    assert result.passed is True
    assert result.final_state == "OFF"
    assert result.observed_behavior["appliedRules"] == ["off_to_on", "on_to_off"]
    assert result.observed_behavior["stepEvidence"][1]["appliedRule"] is None
    assert result.observed_behavior["stepEvidence"][1]["after"]["state"] == "ON"
    assert result.observed_behavior["stepEvidence"][1]["after"]["outputs"]["active"] is True


def test_simple_relay_hysteresis_generated_artifacts_are_deterministic(tmp_path):
    sample = load_sample("simple_relay_hysteresis", ROOT)
    model = parse_markup_file(sample.paths.model)
    relative_model = Path("samples/simple_relay_hysteresis/model.mbd.md")
    relative_scenario = Path("samples/simple_relay_hysteresis/scenarios/hysteresis_cycle.yml")
    result = run_preview_file(relative_model, relative_scenario)
    expected_outputs = {
        sample.paths.generated["docs"]: export_markdown(model),
        sample.paths.generated["demo"]: export_demo_html(model),
        sample.paths.generated["mermaid"]: export_mermaid(model),
        sample.paths.generated["plantuml"]: export_plantuml(model),
        sample.paths.generated["scxml"]: export_scxml(model),
        sample.paths.generated["modelica"]: export_modelica(model),
        sample.paths.generated["simulink"]: export_simulink_m(model),
        sample.paths.generated["fmi"]: export_fmi_metadata(model),
        sample.paths.reports["hysteresis_cycle"]: render_report(result),
    }
    converted_mbd = generate_mbd_from_spec(
        sample.paths.spec,
        component_name=sample.spec_mbd["component"],
        parameter_defaults=sample.spec_mbd["parameterDefaults"],
        input_defaults=sample.spec_mbd["inputDefaults"],
        output_defaults=sample.spec_mbd["outputDefaults"],
        scenario=sample.spec_mbd["scenario"],
    )
    converted_model = parse_markup(converted_mbd, sample.paths.generated["convertedMbd"])
    expected_outputs[sample.paths.generated["convertedMbd"]] = converted_mbd
    expected_outputs[sample.paths.generated["convertedReviewHtml"]] = export_demo_html(converted_model)

    for path, regenerated in expected_outputs.items():
        assert path.read_text(encoding="utf-8") == regenerated

    report_path = tmp_path / "hysteresis_cycle.md"
    assert run_preview_file(relative_model, relative_scenario, report_path).passed
    assert report_path.read_text(encoding="utf-8") == sample.paths.reports["hysteresis_cycle"].read_text(
        encoding="utf-8"
    )


def test_simple_relay_hysteresis_spec_generates_reviewable_mbd():
    sample = load_sample("simple_relay_hysteresis", ROOT)

    generated = generate_mbd_from_spec(
        sample.paths.spec,
        component_name=sample.spec_mbd["component"],
        parameter_defaults=sample.spec_mbd["parameterDefaults"],
        input_defaults=sample.spec_mbd["inputDefaults"],
        output_defaults=sample.spec_mbd["outputDefaults"],
        scenario=sample.spec_mbd["scenario"],
    )
    model = parse_markup(generated, sample.paths.generated["convertedMbd"])
    alignment = compare_spec_to_mbd_model(
        sample.paths.spec,
        model,
        sample.paths.generated["convertedMbd"],
    )
    review_html = export_demo_html(model)

    assert alignment.passed
    assert "parameter onThreshold: count = 70" in generated
    assert "port in level: count = 0" in generated
    assert "仕様 vs 生成MBD" in review_html
    assert "1分レビュー" in review_html
    assert "状態図レビュー" in review_html
    assert review_html.index("状態図レビュー") < review_html.index("Harness検証結果")
    assert review_html.index("状態図レビュー") < review_html.index("要求ごとの確認")
    assert "Harness検証結果" in review_html
    assert "<strong>PASS</strong>" in review_html
    assert "最終状態=OFF, active=False" in review_html
    assert "OFF -&gt; ON" in review_html
    assert "ON -&gt; OFF" in review_html
    assert "ガードが偽の場合" in review_html
    assert "off_to_on" in review_html
    assert "機能:" not in review_html
    assert "信号線:" not in review_html
    assert "Harness:" not in review_html


def test_simple_relay_hysteresis_export_sample_cli_succeeds():
    assert main(["export-sample", "simple_relay_hysteresis"]) == 0
