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


def test_simple_state_machine_sample_is_intentionally_small():
    sample = load_sample("simple_state_machine", ROOT)
    model = parse_markup_file(sample.paths.model)

    assert model.component.name == "ToyStateMachine"
    assert set(model.ports) == {
        "startCommand",
        "finishCommand",
        "resetCommand",
        "busy",
        "complete",
    }
    assert set(transition.source for transition in model.transitions) == {
        "IDLE",
        "RUNNING",
        "DONE",
    }
    assert [(transition.source, transition.target) for transition in model.transitions] == [
        ("IDLE", "RUNNING"),
        ("RUNNING", "DONE"),
        ("DONE", "IDLE"),
    ]
    assert len(model.controls) == 3
    assert [control.state_scope for control in model.controls] == ["IDLE", "RUNNING", "DONE"]
    assert len(model.functions) == 1
    assert model.functions[0].name == "ToyStateController"
    assert len(model.harness_devices) == 2


def test_simple_state_machine_generated_artifacts_are_deterministic(tmp_path):
    sample = load_sample("simple_state_machine", ROOT)
    model = parse_markup_file(sample.paths.model)
    relative_model = Path("samples/simple_state_machine/model.mbd.md")
    relative_scenario = Path("samples/simple_state_machine/scenarios/full_cycle.yml")
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
        sample.paths.reports["full_cycle"]: render_report(result),
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

    report_path = tmp_path / "full_cycle.md"
    assert run_preview_file(relative_model, relative_scenario, report_path).passed
    assert report_path.read_text(encoding="utf-8") == sample.paths.reports["full_cycle"].read_text(
        encoding="utf-8"
    )


def test_simple_state_machine_preview_scenario_passes_with_report_sections():
    sample = load_sample("simple_state_machine", ROOT)

    result = run_preview_file(sample.paths.model, sample.paths.scenarios["full_cycle"])

    assert result.passed is True
    assert result.final_state == "IDLE"
    assert result.generated_ecu_command_outputs["busy"] is False
    assert result.generated_ecu_command_outputs["complete"] is False
    assert result.observed_behavior["appliedRules"] == [
        "start_running",
        "finish_done",
        "reset_idle",
    ]
    report = sample.paths.reports["full_cycle"].read_text(encoding="utf-8")
    assert "## Model Inputs" in report
    assert "## Scenario Steps" in report
    assert "## Observed Behavior" in report
    assert "## Expected Behavior" in report
    assert "## Pass/Fail Result" in report


def test_simple_state_machine_generated_visuals_show_state_behavior():
    sample = load_sample("simple_state_machine", ROOT)
    mermaid = sample.paths.generated["mermaid"].read_text(encoding="utf-8")
    scxml = sample.paths.generated["scxml"].read_text(encoding="utf-8")
    html = sample.paths.generated["demo"].read_text(encoding="utf-8")

    assert 'decision_start_running{"startCommand == true?"}' in mermaid
    assert 'action_finish_done["State DONE<br/>Output busy = false<br/>Output complete = true"]' in mermaid
    assert 'rule_reset_idle{"priority 30<br/>rule reset_idle<br/>owner ToyStateController<br/>from DONE"}' in mermaid
    assert '<scxml xmlns="http://www.w3.org/2005/07/scxml" version="1.0" initial="IDLE">' in scxml
    assert '<transition event="finishCommand == true" target="DONE" />' in scxml
    assert "MBD Review Artifact" in html
    assert "Human Review Question" in html
    assert "Review Evidence Map" in html
    assert "Spec-Oriented Model Review Diagram" in html
    assert "ToyCommandSource" in html
    assert "ToyStateController" in html
    assert "Input Port" in html
    assert "Output busy" in html
    assert "Output complete" in html
    assert "ScenarioReport.observedBehavior" in html
    assert "State Machine Transition Review" in html
    assert "Review basis" in html
    assert "Current outputs" in html
    assert "State Inventory" in html
    assert "Transition Table" in html
    assert "Transition Matrix" in html
    assert "Guard Diagnostics" in html
    assert "Action Semantics" in html
    assert "Scenario Walk-Through" in html
    assert "Report evidence" in html
    assert "reports/full_cycle.md" in html
    assert "Single guarded outgoing transition; false case is implicit self-hold." in html
    assert "Entry / during / exit action" in html
    assert "Unsupported in this slice" in html
    assert "State Machine Diagram" in html
    assert "State Machine Review Package" in html
    assert "start_running (priority 10, owner ToyStateController)" in html
    assert "state=RUNNING, busy=true, complete=false" in html
    assert "full_cycle" in html
    assert "IDLE" in html
    assert "RUNNING" in html
    assert "DONE" in html
    assert "Control Decision Table" in html


def test_simple_state_machine_spec_generates_reviewable_mbd():
    sample = load_sample("simple_state_machine", ROOT)

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
    assert [(transition.source, transition.target) for transition in model.transitions] == [
        ("IDLE", "RUNNING"),
        ("RUNNING", "DONE"),
        ("DONE", "IDLE"),
    ]
    assert [control.state_scope for control in model.controls] == ["IDLE", "RUNNING", "DONE"]
    assert model.controls[0].actions == {
        "state": "RUNNING",
        "busy": "true",
        "complete": "false",
    }
    assert "仕様 vs 生成MBD" in review_html
    assert "1分レビュー" in review_html
    assert "Harness検証結果" in review_html
    assert "<strong>PASS</strong>" in review_html
    assert "<td>IDLE</td><td>3</td>" in review_html
    assert "最終状態=IDLE, busy=False, complete=False" in review_html
    assert "要求ごとの確認" in review_html
    assert "状態図の比較" in review_html
    assert "仕様の状態図" in review_html
    assert "生成MBDの状態図" in review_html
    assert "[*] -> IDLE" in review_html
    assert "生成初期状態" in review_html
    assert "未解決QA" in review_html
    assert "ガードが偽の場合" in review_html
    assert "State Machine Review Package" not in review_html
    assert "State Machine Transition Review" not in review_html
    assert "遷移ごとの確認" in review_html
    assert "対象外" in review_html
    assert "シナリオ" in review_html
    assert "reports/full_cycle.md" in review_html
    assert "idle_to_running" in review_html
    assert "SM-001, SM-004" in review_html
    assert "機能:" not in review_html
    assert "信号線:" not in review_html
    assert "Harness:" not in review_html
    assert "Review Evidence Map" not in review_html
    assert "Functional Decomposition" not in review_html
    assert "Virtual Sensor" not in review_html
    assert "Virtual Actuator" not in review_html


def test_simple_state_machine_export_sample_cli_succeeds():
    assert main(["export-sample", "simple_state_machine"]) == 0
