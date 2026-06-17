from pathlib import Path

from veph.cli import EXPORT_COMMANDS
from veph.exporters.demo_html import export_demo_html
from veph.exporters.markdown import export_markdown
from veph.exporters.modelica import export_modelica
from veph.exporters.plantuml import export_plantuml
from veph.exporters.scxml import export_scxml
from veph.exporters.simulink_m import export_simulink_m
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


def test_generated_artifacts_are_deterministic_from_canonical_yaml():
    model = load_model(ROOT / "specs" / "toy_power_monitor.tmbd.yml")

    expected_outputs = {
        "generated/toy_power_monitor.md": export_markdown(model),
        "generated/demo.html": export_demo_html(model),
        "generated/toy_power_monitor.puml": export_plantuml(model),
        "generated/toy_power_monitor.scxml": export_scxml(model),
        "generated/ToyPowerMonitor.mo": export_modelica(model),
        "generated/create_toy_power_monitor_model.m": export_simulink_m(model),
    }

    for relative_path, regenerated in expected_outputs.items():
        assert (ROOT / relative_path).read_text(encoding="utf-8") == regenerated


def test_cli_export_commands_use_only_model_and_output_arguments():
    assert set(EXPORT_COMMANDS) == {
        "export-docs",
        "export-demo",
        "export-plantuml",
        "export-scxml",
        "export-modelica",
        "export-simulink-m",
    }

    for command in EXPORT_COMMANDS.values():
        assert command.model_required is True
        assert command.out_required is True


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


def test_markdown_documents_mbd_blocks_and_connections():
    model = load_model(ROOT / "specs" / "toy_power_monitor.tmbd.yml")

    markdown = export_markdown(model)

    assert "## Functional Blocks" in markdown
    assert "`UndervoltageComparator`" in markdown
    assert "`VoltageInput.voltage` -> `UndervoltageComparator.voltage`" in markdown
