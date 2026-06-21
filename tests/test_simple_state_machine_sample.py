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
from veph.markup_parser import parse_markup_file
from veph.preview_runtime import run_preview_file
from veph.report import render_report
from veph.sample_catalog import load_sample


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
    assert "Design Overview Diagram" in html
    assert "ToyCommandSource" in html
    assert "ToyStateController" in html
    assert "Input Port" in html
    assert "Output busy" in html
    assert "Output complete" in html
    assert "ScenarioReport.observedBehavior" in html
    assert "State Machine Diagram" in html
    assert "IDLE" in html
    assert "RUNNING" in html
    assert "DONE" in html
    assert "Control Decision Table" in html


def test_simple_state_machine_export_sample_cli_succeeds():
    assert main(["export-sample", "simple_state_machine"]) == 0
