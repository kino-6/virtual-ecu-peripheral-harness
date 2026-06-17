from pathlib import Path

from veph.model_loader import load_model
from veph.peripheral_runtime import PeripheralRuntime


ROOT = Path(__file__).resolve().parents[1]


def test_registers_initialize_from_field_resets():
    runtime = PeripheralRuntime(load_model(ROOT / "specs" / "toy_power_monitor.tmbd.yml"))

    assert runtime.state == "RESET"
    assert runtime.read_register("STATUS") == 0x00
    assert runtime.read_field("RESET_CAUSE", "powerOnReset") == 1
    assert runtime.signals["voltage"] == 12.0


def test_normal_startup_reaches_normal_and_sets_ready():
    runtime = PeripheralRuntime(load_model(ROOT / "specs" / "toy_power_monitor.tmbd.yml"))

    runtime.apply_event("powerOn")
    runtime.write_register("CONTROL", 0x01)

    assert runtime.state == "NORMAL"
    assert runtime.read_field("STATUS", "ready") == 1


def test_undervoltage_latches_fault_and_status_bit():
    runtime = PeripheralRuntime(load_model(ROOT / "specs" / "toy_power_monitor.tmbd.yml"))
    runtime.apply_event("powerOn")
    runtime.write_register("CONTROL", 0x01)

    runtime.set_signal("voltage", 6.5)

    assert runtime.state == "FAULT_LATCHED"
    assert runtime.read_field("STATUS", "undervoltageFault") == 1
    assert runtime.read_field("FAULT", "undervoltage") == 1


def test_spi_timeout_returns_no_response_for_spi_reads():
    runtime = PeripheralRuntime(load_model(ROOT / "specs" / "toy_power_monitor.tmbd.yml"))

    runtime.inject_fault("spiTimeout")

    assert runtime.read_register("STATUS") is None
