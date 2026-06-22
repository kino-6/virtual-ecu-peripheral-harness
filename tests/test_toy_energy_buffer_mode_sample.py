from pathlib import Path

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


def test_toy_energy_buffer_mode_sample_is_source_informed_and_fictional():
    sample = load_sample("toy_energy_buffer_mode", ROOT)
    model = parse_markup_file(sample.paths.model)
    spec = sample.paths.spec.read_text(encoding="utf-8")

    assert model.component.name == "ToyEnergyBufferMode"
    assert set(model.ports) == {
        "externalPowerAvailable",
        "emptyDetected",
        "supplyEnabled",
        "chargeIndicator",
    }
    assert [(transition.source, transition.target) for transition in model.transitions] == [
        ("CHARGE", "DISCHARGE"),
        ("DISCHARGE", "EMPTY"),
        ("EMPTY", "CHARGE"),
        ("DISCHARGE", "CHARGE"),
    ]
    assert [control.state_scope for control in model.controls] == [
        "CHARGE",
        "DISCHARGE",
        "EMPTY",
        "DISCHARGE",
    ]
    assert model.controls[0].actions == {
        "state": "DISCHARGE",
        "supplyEnabled": "true",
        "chargeIndicator": "false",
    }
    assert len(model.harness_devices) == 3
    assert "www.mathworks.com/help/stateflow/gs/get-started-create-table.html" in spec
    assert "real battery" in spec


def test_toy_energy_buffer_mode_preview_scenario_passes_with_harness_evidence():
    sample = load_sample("toy_energy_buffer_mode", ROOT)

    result = run_preview_file(sample.paths.model, sample.paths.scenarios["source_loss_recovery"])

    assert result.passed is True
    assert result.final_state == "CHARGE"
    assert result.generated_ecu_command_outputs["supplyEnabled"] is False
    assert result.generated_ecu_command_outputs["chargeIndicator"] is True
    assert result.observed_behavior["appliedRules"] == [
        "power_removed_discharge",
        "discharge_empty",
        "empty_reconnect_charge",
    ]
    report = sample.paths.reports["source_loss_recovery"].read_text(encoding="utf-8")
    assert "## Harness Boundary Evidence" in report
    assert "preview-only; not a certified code generation or verification backend" in report
    assert "ToyPowerSource" in report
    assert "ToyEmptyMonitor" in report
    assert "PASS finalState: actual CHARGE, expected CHARGE" in report


def test_toy_energy_buffer_mode_spec_generates_reviewable_mbd():
    sample = load_sample("toy_energy_buffer_mode", ROOT)

    generated = generate_mbd_from_spec(
        sample.paths.spec,
        component_name=sample.spec_mbd["component"],
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
    assert "Generated from Spec Data Flow View and Control Semantics View" in generated
    assert "sequenceDiagram" not in generated
    assert "port in externalPowerAvailable: bool = true" in generated
    assert "port out chargeIndicator: bool = true" in generated
    assert [control.name for control in model.controls] == [
        "charge_to_discharge",
        "discharge_to_empty",
        "empty_to_charge",
        "discharge_to_charge",
    ]
    assert model.controls[0].actions == {
        "state": "DISCHARGE",
        "supplyEnabled": "true",
        "chargeIndicator": "false",
    }
    assert "仕様 vs 生成MBD" not in review_html
    assert "1分レビュー" in review_html
    assert "状態図レビュー" in review_html
    assert review_html.index("状態図レビュー") < review_html.index("Harnessテスト要約")
    assert review_html.index("状態図レビュー") < review_html.index("要求ごとの確認")
    assert "Harnessテスト要約" in review_html
    assert "<strong>PASS</strong>" in review_html
    assert "状態遷移" in review_html
    assert "externalPowerAvailable=false</td><td>CHARGE-&gt;DISCHARGE; supplyEnabled=true, chargeIndicator=false" in review_html
    assert "emptyDetected=true</td><td>DISCHARGE-&gt;EMPTY; supplyEnabled=false, chargeIndicator=false" in review_html
    assert "externalPowerAvailable=true</td><td>EMPTY-&gt;CHARGE; supplyEnabled=false, chargeIndicator=true" in review_html
    assert "機能:" not in review_html
    assert "信号線:" not in review_html
    assert "Harness:" not in review_html


def test_toy_energy_buffer_mode_generated_artifacts_are_deterministic(tmp_path):
    sample = load_sample("toy_energy_buffer_mode", ROOT)
    model = parse_markup_file(sample.paths.model)
    relative_model = Path("samples/toy_energy_buffer_mode/model.mbd.md")
    relative_scenario = Path("samples/toy_energy_buffer_mode/scenarios/source_loss_recovery.yml")
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
        sample.paths.reports["source_loss_recovery"]: render_report(result),
    }
    converted_mbd = generate_mbd_from_spec(
        sample.paths.spec,
        component_name=sample.spec_mbd["component"],
        input_defaults=sample.spec_mbd["inputDefaults"],
        output_defaults=sample.spec_mbd["outputDefaults"],
        scenario=sample.spec_mbd["scenario"],
    )
    converted_model = parse_markup(converted_mbd, sample.paths.generated["convertedMbd"])
    expected_outputs[sample.paths.generated["convertedMbd"]] = converted_mbd
    expected_outputs[sample.paths.generated["convertedReviewHtml"]] = export_demo_html(converted_model)

    for path, regenerated in expected_outputs.items():
        assert path.read_text(encoding="utf-8") == regenerated

    report_path = tmp_path / "source_loss_recovery.md"
    assert run_preview_file(relative_model, relative_scenario, report_path).passed
    assert report_path.read_text(encoding="utf-8") == sample.paths.reports[
        "source_loss_recovery"
    ].read_text(encoding="utf-8")


def test_toy_energy_buffer_mode_export_sample_cli_succeeds():
    assert main(["export-sample", "toy_energy_buffer_mode"]) == 0
