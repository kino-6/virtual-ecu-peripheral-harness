from pathlib import Path

from veph.model_loader import load_model
from veph.sample_catalog import load_sample
from veph.scenario_runner import run_scenario_file


ROOT = Path(__file__).resolve().parents[1]


def _sample():
    return load_sample("toy_power_monitor", ROOT)


def test_normal_startup_scenario_passes(tmp_path):
    report_path = tmp_path / "normal_startup.md"
    sample = _sample()
    result = run_scenario_file(
        load_model(sample.paths.legacy["legacyModel"]),
        sample.paths.scenarios["normal_startup"],
        report_path=report_path,
    )

    assert result.passed is True
    assert result.final_state == "NORMAL"
    report = report_path.read_text(encoding="utf-8")
    assert report.startswith("# Scenario Report")
    assert "## Model Inputs" in report
    assert "## Scenario Steps" in report
    assert "## Observed Behavior" in report
    assert "## Expected Behavior" in report
    assert "## Pass/Fail Result" in report


def test_undervoltage_fault_scenario_passes(tmp_path):
    sample = _sample()
    result = run_scenario_file(
        load_model(sample.paths.legacy["legacyModel"]),
        sample.paths.scenarios["undervoltage_fault"],
        report_path=tmp_path / "undervoltage_fault.md",
    )

    assert result.passed is True
    assert result.final_state == "FAULT_LATCHED"


def test_spi_timeout_scenario_passes(tmp_path):
    sample = _sample()
    result = run_scenario_file(
        load_model(sample.paths.legacy["legacyModel"]),
        sample.paths.scenarios["spi_timeout"],
        report_path=tmp_path / "spi_timeout.md",
    )

    assert result.passed is True
    assert result.reads[-1]["response"] == "timeout"
