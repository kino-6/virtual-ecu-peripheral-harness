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
from veph.sample_catalog import load_sample
from veph.spec_mbd_alignment import compare_spec_to_mbd, compare_spec_to_mbd_model
from veph.spec_mbd_conversion import generate_mbd_from_spec
from veph.spec_mbd_viewer import export_spec_mbd_viewer


ROOT = Path(__file__).resolve().parents[1]


def test_simple_switch_sample_is_intentionally_small_and_switch_style():
    sample = load_sample("simple_switch_selector", ROOT)
    model = parse_markup_file(sample.paths.model)

    assert model.component.name == "ToySwitchSelector"
    assert set(model.ports) == {"selectHigh", "selectedValue"}
    assert set(model.component.parameters) == {"highValue", "lowValue"}
    assert len(model.functions) == 1
    assert model.functions[0].name == "SwitchSelector"
    assert [(control.condition, control.actions["selectedValue"]) for control in model.controls] == [
        ("selectHigh == true", "highValue"),
        ("selectHigh != true", "lowValue"),
    ]


def test_simple_switch_generated_artifacts_are_deterministic():
    sample = load_sample("simple_switch_selector", ROOT)
    model = parse_markup_file(sample.paths.model)
    converted_mbd = generate_mbd_from_spec(
        sample.paths.spec,
        component_name=sample.spec_mbd["component"],
        parameter_defaults=sample.spec_mbd["parameterDefaults"],
        input_defaults=sample.spec_mbd["inputDefaults"],
        output_defaults=sample.spec_mbd["outputDefaults"],
        scenario=sample.spec_mbd["scenario"],
    )
    converted_model = parse_markup(converted_mbd, sample.paths.generated["convertedMbd"])
    converted_report = compare_spec_to_mbd_model(
        sample.paths.spec,
        converted_model,
        sample.paths.generated["convertedMbd"],
    )
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
        sample.paths.generated["convertedMbd"]: converted_mbd,
        sample.paths.generated["specMbdViewer"]: export_spec_mbd_viewer(
            sample.paths.spec,
            converted_model,
            converted_report,
        ),
    }

    assert converted_report.passed
    assert "Constant: highValue = 100" in converted_report.matched_nodes
    assert "Constant: lowValue = 25" in converted_report.matched_nodes
    for path, regenerated in expected_outputs.items():
        assert path.read_text(encoding="utf-8") == regenerated


def test_simple_switch_preview_scenario_passes_with_report_sections():
    sample = load_sample("simple_switch_selector", ROOT)

    result = run_preview_file(sample.paths.model, sample.paths.scenarios["select_high"])

    assert result.passed is True
    assert result.generated_ecu_command_outputs["selectedValue"] == 100
    report = sample.paths.reports["select_high"].read_text(encoding="utf-8")
    assert "## Model Inputs" in report
    assert "## Scenario Steps" in report
    assert "## Observed Behavior" in report
    assert "## Expected Behavior" in report
    assert "## Pass/Fail Result" in report


def test_simple_switch_review_artifacts_show_compare_switch_semantics():
    sample = load_sample("simple_switch_selector", ROOT)
    html = sample.paths.generated["demo"].read_text(encoding="utf-8")
    mermaid = sample.paths.generated["mermaid"].read_text(encoding="utf-8")
    simulink = sample.paths.generated["simulink"].read_text(encoding="utf-8")
    viewer = sample.paths.generated["specMbdViewer"].read_text(encoding="utf-8")

    assert "Semantic MBD Block Diagram" in html
    assert "selectHigh == true?" in html
    assert "selectedValue=highValue" in html
    assert "selectedValue=lowValue" in html
    assert 'decision_select_high_value_select_low_value{"selectHigh == true?"}' in mermaid
    assert "Rule_select_high_value_selectedValue_Switch" in simulink
    assert "Spec Mermaid To MBD Review" in viewer
    assert "Interactive Review" in viewer
    assert "Constant: highValue = 100" in viewer
    assert "Constant: lowValue = 25" in viewer


def test_simple_switch_export_sample_cli_succeeds():
    assert main(["export-sample", "simple_switch_selector"]) == 0
