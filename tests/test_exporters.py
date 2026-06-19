from pathlib import Path

from veph.cli import EXPORT_COMMANDS
from veph.exporters.demo_html import export_demo_html
from veph.exporters.fmi_metadata import export_fmi_metadata
from veph.exporters.markdown import export_markdown
from veph.exporters.mermaid import export_mermaid
from veph.exporters.modelica import export_modelica
from veph.exporters.plantuml import export_plantuml
from veph.exporters.scxml import export_scxml
from veph.exporters.simulink_m import SimulinkSemanticExportError, export_simulink_m
from veph.markup_parser import parse_markup, parse_markup_file
from veph.model_loader import load_model
import pytest


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


def test_thermal_protection_simulink_handoff_structures_high_cooling_rule():
    model = parse_markup_file(ROOT / "examples" / "toy_thermal_protection_controller.mbd.md")

    script = export_simulink_m(model)
    semantic_lines = _without_comment_lines(script)

    assert "add_block('simulink/Sources/In1', [model '/In_temperatureC'])" in script
    assert "set_param([model '/In_temperatureC'], 'OutDataTypeStr', 'double')" in script
    assert "add_block('simulink/Sources/Constant', [model '/Param_coolingOnThreshold'])" in script
    assert "add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_highCooling_Compare'])" in semantic_lines
    assert "set_param([model '/Rule_highCooling_Compare'], 'relop', '>=')" in semantic_lines
    assert "set_param([model '/Rule_highCooling_Compare'], 'const', 'coolingOnThreshold')" in semantic_lines
    assert "add_block('simulink/Signal Routing/Switch', [model '/Rule_highCooling_fanDuty_Switch'])" in semantic_lines
    assert "add_line(model, 'Param_coolingDuty/1', 'Rule_highCooling_fanDuty_Switch/1'" in semantic_lines
    assert "add_line(model, 'Rule_highCooling_fanDuty_Switch/1', 'Out_fanDuty/1'" in semantic_lines


def test_thermal_protection_simulink_handoff_structures_fault_latch_rule():
    model = parse_markup_file(ROOT / "examples" / "toy_thermal_protection_controller.mbd.md")

    script = export_simulink_m(model)
    semantic_lines = _without_comment_lines(script)

    assert "add_block('simulink/Sources/In1', [model '/In_invalidDebounced'])" in script
    assert "add_block('simulink/Logic and Bit Operations/Compare To Constant', [model '/Rule_faultLatch_Compare'])" in semantic_lines
    assert "set_param([model '/Rule_faultLatch_Compare'], 'relop', '==')" in semantic_lines
    assert "set_param([model '/Rule_faultLatch_Compare'], 'const', 'true')" in semantic_lines
    assert "add_block('simulink/Signal Routing/Switch', [model '/Rule_faultLatch_safeCommandActive_Switch'])" in semantic_lines
    assert "add_block('simulink/Sources/Constant', [model '/Rule_faultLatch_safeCommandActive_true_Const'])" in semantic_lines
    assert "add_line(model, 'Rule_faultLatch_Compare/1', 'Rule_faultLatch_safeCommandActive_Switch/2'" in semantic_lines


def test_simulink_rule_semantics_are_not_comment_only():
    model = parse_markup_file(ROOT / "examples" / "toy_thermal_protection_controller.mbd.md")

    semantic_lines = _without_comment_lines(export_simulink_m(model))

    assert "Rule_highCooling_Compare" in semantic_lines
    assert "Rule_faultLatch_Compare" in semantic_lines
    assert "Rule_derating_fanDuty_Switch" in semantic_lines
    assert "Rule_sensorInvalid_diagnosticFault_Switch" in semantic_lines


def test_simulink_export_reports_unsupported_expression_diagnostics():
    source = (ROOT / "examples" / "toy_thermal_protection_controller.mbd.md").read_text(encoding="utf-8")
    source = source.replace(
        "when temperatureC >= coolingOnThreshold then state=COOLING",
        "when temperatureC + 1 >= coolingOnThreshold then state=COOLING",
    )
    model = parse_markup(source, ROOT / "examples" / "unsupported_expression.mbd.md")

    with pytest.raises(SimulinkSemanticExportError, match="highCooling.*unsupported condition.*\\+"):
        export_simulink_m(model)


def _without_comment_lines(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.startswith("%"))


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
    assert "Control Decision Table" in html
    assert "Harness Boundary" in html
    assert "ToyTempSensorIC" in html
    assert "sensorFault" in html
    assert "SYS-005" in html
    assert "generated Simulink, Modelica, SCXML" in html


def test_thermal_protection_demo_html_visualizes_complete_process_slice():
    model = parse_markup_file(ROOT / "examples" / "toy_thermal_protection_controller.mbd.md")

    html = export_demo_html(model)
    mermaid = export_mermaid(model)
    fmi = export_fmi_metadata(model)

    assert "<svg" in html
    assert "ToyThermalProtectionController" in html
    assert "Functional Architecture" in html
    assert "Functional Decomposition" in html
    assert "SensorInterface" in html
    assert "FaultLatchRecoveryManager" in html
    assert "function:FaultLatchRecoveryManager" in html
    assert "Spec-To-MBD Compliance Review" in html
    assert "MBD Review Checklist" in html
    assert "Requirements traceability" in html
    assert "Interface and data-flow review" in html
    assert "Requirements-based scenario evidence" in html
    assert "Modeling standards and readability" in html
    assert "SYS-008" in html
    assert "Control Decision Table" in html
    assert "Selection policy" in html
    assert "Priority" in html
    assert "Owner" in html
    assert "State scope" in html
    assert "recoverFromLatch" in html
    assert "thermal_protection_recovery" in html
    assert "thermal_protection_boundary" in html
    assert "MBD Data Flow Diagram" in html
    assert "State Machine Diagram" in html
    assert "Harness Boundary Diagram" in html
    assert "ToyTempSensorIC.temperatureC" in html
    assert "HAL_LIMITER.set_derating" in html
    assert "faultLatch" in html
    assert "ToyLoadLimiterIC" in html
    assert "SensorInterface<br/>Acquire fictional temperature" in mermaid
    assert "owner FaultLatchRecoveryManager" in mermaid
    assert '"functionalDecomposition"' in fmi
    assert '"owner": "FaultLatchRecoveryManager"' in fmi


def test_markdown_documents_mbd_blocks_and_connections():
    model = load_model(ROOT / "specs" / "toy_power_monitor.tmbd.yml")

    markdown = export_markdown(model)

    assert "## Functional Blocks" in markdown
    assert "`UndervoltageComparator`" in markdown
    assert "`VoltageInput.voltage` -> `UndervoltageComparator.voltage`" in markdown
