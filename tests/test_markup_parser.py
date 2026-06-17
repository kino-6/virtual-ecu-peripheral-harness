from pathlib import Path

from veph.markup_parser import parse_markup_file


ROOT = Path(__file__).resolve().parents[1]


def test_markup_file_parses_to_internal_ir():
    model = parse_markup_file(ROOT / "examples" / "toy_power_monitor.mbd.md")

    assert model.title == "Toy Power Monitor IC"
    assert model.component.name == "ToyPowerMonitorIC"
    assert model.component.bus["type"] == "spi"
    assert model.ports["voltage"].direction == "in"
    assert model.ports["ready"].type == "bool"
    assert model.registers["STATUS"].fields["ready"].bit == 7
    assert model.registers["CONTROL"].access == "rw"
    assert model.transitions[0].source == "RESET"
    assert model.transitions[0].target == "INIT"
    assert model.flows[0].source == "ECU_App.control_task"
    assert model.flows[0].target == "HAL_SPI"
    assert model.source_path.name == "toy_power_monitor.mbd.md"


def test_internal_ir_json_is_not_public_authoring_format():
    model = parse_markup_file(ROOT / "examples" / "toy_power_monitor.mbd.md")

    data = model.to_dict()

    assert data["metadata"]["sourceFormat"] == "mbd-markdown"
    assert data["metadata"]["irRole"] == "internal snapshot"
    assert data["component"]["name"] == "ToyPowerMonitorIC"
