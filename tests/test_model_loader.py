from pathlib import Path

import pytest

from veph.model_loader import ModelValidationError, load_model


ROOT = Path(__file__).resolve().parents[1]


def test_loads_toy_power_monitor_model():
    model = load_model(ROOT / "specs" / "toy_power_monitor.tmbd.yml")

    assert model.name == "ToyPowerMonitorIC"
    assert model.bus.type == "spi"
    assert model.registers["STATUS"].address == 0x01
    assert model.registers["STATUS"].fields["ready"].bits == [7]
    assert model.states.initial == "RESET"
    assert model.blocks["UndervoltageComparator"].kind == "comparator"
    assert model.blocks["RegisterMap"].inputs["ready"].signal == "ready"
    assert model.connections[0].source == "VoltageInput.voltage"
    assert model.connections[0].target == "UndervoltageComparator.voltage"


def test_schema_validation_rejects_missing_required_sections(tmp_path):
    invalid = tmp_path / "invalid.yml"
    invalid.write_text(
        """
schemaVersion: 0.1
kind: PeripheralModel
name: BrokenIC
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ModelValidationError, match="missing required section"):
        load_model(invalid)


def test_schema_validation_rejects_unknown_block_connection_endpoint(tmp_path):
    invalid = tmp_path / "invalid_connection.yml"
    invalid.write_text(
        """
schemaVersion: 0.1
kind: PeripheralModel
name: BrokenIC
bus:
  type: spi
  mode: 0
  wordBits: 8
registers:
  STATUS:
    address: 0x01
    width: 8
    access: ro
    fields:
      ready:
        bits: [0]
        reset: 0
states:
  initial: RESET
  nodes: [RESET]
  transitions: []
signals:
  inputs: []
  outputs: []
faults: []
timing:
  tickMs: 1
blocks:
  - name: A
    kind: source
    outputs:
      - name: out
        signal: out
connections:
  - from: A.out
    to: Missing.in
    signal: out
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ModelValidationError, match="unknown connection endpoint"):
        load_model(invalid)
