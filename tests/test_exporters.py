from pathlib import Path

from veph.cli import EXPORT_COMMANDS
from veph.exporters.demo_html import export_demo_html
from veph.exporters.fmi_metadata import export_fmi_metadata
from veph.exporters.markdown import export_markdown
from veph.exporters.mermaid import export_mermaid
from veph.exporters.modelica import export_modelica
from veph.exporters.plantuml import export_plantuml
from veph.exporters.scxml import export_scxml
from veph.exporters.simulink_m import export_simulink_m
from veph.markup_parser import parse_markup_file
from veph.model_loader import load_model


ROOT = Path(__file__).resolve().parents[1]


def test_each_exporter_creates_non_empty_output():
    model = load_model(ROOT / "specs" / "toy_power_monitor.tmbd.yml")

    outputs = [
        export_markdown(model),
        export_demo_html(model),
        export_plantuml(model),
        export_scxml(model),
        export_modelica(model),
        export_simulink_m(model),
    ]

    for output in outputs:
        assert output.strip()
        assert "ToyPowerMonitor" in output


def test_generated_artifacts_are_deterministic_from_markup_source():
    model = parse_markup_file(ROOT / "examples" / "toy_power_monitor.mbd.md")

    expected_outputs = {
        "generated/toy_power_monitor.md": export_markdown(model),
        "generated/toy_power_monitor.mmd": export_mermaid(model),
        "generated/toy_power_monitor.puml": export_plantuml(model),
        "generated/toy_power_monitor.scxml": export_scxml(model),
        "generated/ToyPowerMonitor.mo": export_modelica(model),
        "generated/create_toy_power_monitor_model.m": export_simulink_m(model),
        "generated/toy_power_monitor.fmi.json": export_fmi_metadata(model),
    }

    for relative_path, regenerated in expected_outputs.items():
        assert (ROOT / relative_path).read_text(encoding="utf-8") == regenerated


def test_cli_export_commands_use_only_model_and_output_arguments():
    assert set(EXPORT_COMMANDS) == {
        "export-docs",
        "export-demo",
        "export-mermaid",
        "export-plantuml",
        "export-scxml",
        "export-modelica",
        "export-simulink-m",
        "export-fmi-metadata",
    }

    for command in EXPORT_COMMANDS.values():
        assert command.source_required is True
        assert command.out_required is True


def test_thermal_generated_artifacts_are_deterministic_from_markup_source():
    model = parse_markup_file(ROOT / "examples" / "toy_thermal_fan_control.mbd.md")

    expected_outputs = {
        "generated/toy_thermal_fan_control.md": export_markdown(model),
        "generated/toy_thermal_fan_control.mmd": export_mermaid(model),
        "generated/toy_thermal_fan_control.puml": export_plantuml(model),
        "generated/toy_thermal_fan_control.scxml": export_scxml(model),
        "generated/ToyThermalFanControl.mo": export_modelica(model),
        "generated/create_toy_thermal_fan_control_model.m": export_simulink_m(model),
        "generated/toy_thermal_fan_control.fmi.json": export_fmi_metadata(model),
    }

    for relative_path, regenerated in expected_outputs.items():
        assert (ROOT / relative_path).read_text(encoding="utf-8") == regenerated


def test_thermal_protection_generated_artifacts_are_deterministic_from_markup_source():
    model = parse_markup_file(ROOT / "examples" / "toy_thermal_protection_controller.mbd.md")

    expected_outputs = {
        "generated/toy_thermal_protection_controller.md": export_markdown(model),
        "generated/toy_thermal_protection_controller_demo.html": export_demo_html(model),
        "generated/toy_thermal_protection_controller.mmd": export_mermaid(model),
        "generated/toy_thermal_protection_controller.puml": export_plantuml(model),
        "generated/toy_thermal_protection_controller.scxml": export_scxml(model),
        "generated/ToyThermalProtectionController.mo": export_modelica(model),
        "generated/create_toy_thermal_protection_controller_model.m": export_simulink_m(model),
        "generated/toy_thermal_protection_controller.fmi.json": export_fmi_metadata(model),
    }

    for relative_path, regenerated in expected_outputs.items():
        assert (ROOT / relative_path).read_text(encoding="utf-8") == regenerated


def test_demo_html_visualizes_mbd_and_data_flow_from_yaml():
    model = load_model(ROOT / "specs" / "toy_power_monitor.tmbd.yml")

    html = export_demo_html(model)

    assert "<svg" in html
    assert "Textual MBD YAML" in html
    assert "MBD Block Diagram" in html
    assert "Scenario YAML" in html
    assert "Virtual SPI/HAL Boundary" in html
    assert "Product-like ECU code" in html
    assert "UndervoltageComparator" in html
    assert "FaultLatch" in html
    assert "RegisterMap" in html
    assert "voltage" in html
    assert "undervoltageDetected" in html
    assert "RESET -> INIT" in html
    assert "STATUS.ready" in html


def test_thermal_demo_html_visualizes_trace_control_and_harness():
    model = parse_markup_file(ROOT / "examples" / "toy_thermal_fan_control.mbd.md")

    html = export_demo_html(model)

    assert "Requirements Trace Matrix" in html
    assert "Control Rules" in html
    assert "Harness Boundary" in html
    assert "ToyTempSensorIC" in html
    assert "sensorFault" in html
    assert "SYS-005" in html
    assert "generated Simulink, Modelica, SCXML" in html


def test_thermal_protection_demo_html_visualizes_complete_process_slice():
    model = parse_markup_file(ROOT / "examples" / "toy_thermal_protection_controller.mbd.md")

    html = export_demo_html(model)

    assert "<svg" in html
    assert "ToyThermalProtectionController" in html
    assert "Spec-To-MBD Compliance Review" in html
    assert "MBD Review Checklist" in html
    assert "Requirements traceability" in html
    assert "Interface and data-flow review" in html
    assert "Requirements-based scenario evidence" in html
    assert "Modeling standards and readability" in html
    assert "SYS-008" in html
    assert "recoverFromLatch" in html
    assert "thermal_protection_recovery" in html
    assert "MBD Data Flow Diagram" in html
    assert "State Machine Diagram" in html
    assert "Harness Boundary Diagram" in html
    assert "ToyTempSensorIC.temperatureC" in html
    assert "HAL_LIMITER.set_derating" in html
    assert "faultLatch" in html
    assert "ToyLoadLimiterIC" in html


def test_markdown_documents_mbd_blocks_and_connections():
    model = load_model(ROOT / "specs" / "toy_power_monitor.tmbd.yml")

    markdown = export_markdown(model)

    assert "## Functional Blocks" in markdown
    assert "`UndervoltageComparator`" in markdown
    assert "`VoltageInput.voltage` -> `UndervoltageComparator.voltage`" in markdown
