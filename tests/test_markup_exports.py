from pathlib import Path

from veph.exporters.fmi_metadata import export_fmi_metadata
from veph.exporters.markdown import export_markdown
from veph.exporters.mermaid import export_mermaid
from veph.exporters.modelica import export_modelica
from veph.exporters.plantuml import export_plantuml
from veph.exporters.scxml import export_scxml
from veph.exporters.simulink_m import export_simulink_m
from veph.markup_parser import parse_markup_file
from veph.sample_catalog import load_sample


ROOT = Path(__file__).resolve().parents[1]


def _model():
    return parse_markup_file(load_sample("toy_power_monitor", ROOT).paths.model)


def test_exported_markdown_is_traceable_to_markup_sections():
    output = export_markdown(_model())

    assert "# Toy Power Monitor IC" in output
    assert "Source: `samples/toy_power_monitor/model.mbd.md`" in output
    assert "mbd-component" in output
    assert "mbd-registers" in output
    assert "mbd-state" in output
    assert "mbd-flow" in output
    assert "Python preview" in output


def test_simulink_export_contains_block_and_line_creation_commands():
    output = export_simulink_m(_model())

    assert "new_system" in output
    assert "open_system" in output
    assert "add_block" in output
    assert "add_line" in output
    assert "set_param" in output
    assert "ToyPowerMonitorIC" in output
    assert "HAL_SPI" in output


def test_modelica_export_contains_component_ports_and_signals():
    output = export_modelica(_model())

    assert "model ToyPowerMonitorIC" in output
    assert "input Real voltage" in output
    assert "output Boolean ready" in output
    assert "RESET" in output
    assert "undervoltageThreshold" in output


def test_preview_diagrams_contain_expected_nodes_and_edges():
    mermaid = export_mermaid(_model())
    plantuml = export_plantuml(_model())

    assert "flowchart LR" in mermaid
    assert "ECU_App_control_task --> HAL_SPI" in mermaid
    assert "@startuml" in plantuml
    assert "RESET --> INIT : powerOn" in plantuml


def test_state_and_fmi_exports_are_handoff_stubs_not_full_toolchains():
    scxml = export_scxml(_model())
    fmi = export_fmi_metadata(_model())

    assert "<scxml" in scxml
    assert 'initial="RESET"' in scxml
    assert '"fmiIntent": "metadata stub only; no FMU is generated"' in fmi
    assert '"voltage"' in fmi
    assert '"ready"' in fmi


def test_thermal_exports_include_trace_control_and_harness_boundaries():
    model = parse_markup_file(load_sample("thermal_fan_control", ROOT).paths.model)

    markdown = export_markdown(model)
    mermaid = export_mermaid(model)
    simulink = export_simulink_m(model)
    fmi = export_fmi_metadata(model)

    assert "## Requirements Trace" in markdown
    assert "`SYS-005`" in markdown
    assert "## Control Rules" in markdown
    assert "## Harness Boundary" in markdown
    assert "ToyTempSensorIC" in mermaid
    assert "Trace: SYS-001" in mermaid
    assert "Compare To Constant" in simulink
    assert "Switch" in simulink
    assert '"requirementRefs"' in fmi
    assert '"HAR-005"' in fmi
