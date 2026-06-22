from pathlib import Path

from veph.preview_runtime import run_preview_file
from veph.sequence_expectations import compare_sequence_expectations, sequence_expectations_from_spec


ROOT = Path(__file__).resolve().parents[1]


def test_simple_relay_sequence_view_matches_preview_scenario():
    spec = ROOT / "samples" / "simple_relay_hysteresis" / "spec.md"
    model = ROOT / "samples" / "simple_relay_hysteresis" / "model.mbd.md"
    scenario = ROOT / "samples" / "simple_relay_hysteresis" / "scenarios" / "hysteresis_cycle.yml"

    expectations = sequence_expectations_from_spec(spec)
    report = compare_sequence_expectations(spec, run_preview_file(model, scenario))

    assert [expectation.render() for expectation in expectations] == [
        "OFF -> ON, active=true",
        "ON -> OFF, active=false",
    ]
    assert report.passed
    assert report.missing == ()


def test_toy_energy_buffer_sequence_view_matches_preview_scenario():
    spec = ROOT / "samples" / "toy_energy_buffer_mode" / "spec.md"
    model = ROOT / "samples" / "toy_energy_buffer_mode" / "model.mbd.md"
    scenario = ROOT / "samples" / "toy_energy_buffer_mode" / "scenarios" / "source_loss_recovery.yml"

    report = compare_sequence_expectations(spec, run_preview_file(model, scenario))

    assert report.passed
    assert report.matched == (
        "CHARGE -> DISCHARGE, supplyEnabled=true",
        "DISCHARGE -> EMPTY, supplyEnabled=false",
        "EMPTY -> CHARGE, chargeIndicator=true",
    )


def test_sequence_view_expectation_drift_is_reported(tmp_path):
    source = ROOT / "samples" / "simple_relay_hysteresis" / "spec.md"
    spec = tmp_path / "spec.md"
    spec.write_text(source.read_text(encoding="utf-8").replace("OFF -> ON, active=true", "OFF -> ON, active=false"))
    model = ROOT / "samples" / "simple_relay_hysteresis" / "model.mbd.md"
    scenario = ROOT / "samples" / "simple_relay_hysteresis" / "scenarios" / "hysteresis_cycle.yml"

    report = compare_sequence_expectations(spec, run_preview_file(model, scenario))

    assert not report.passed
    assert report.missing == ("OFF -> ON, active=false",)
