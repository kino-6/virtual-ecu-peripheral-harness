from pathlib import Path

from veph.model_loader import load_model
from veph.scenario_runner import run_scenario_file


ROOT = Path(__file__).resolve().parents[1]


def test_normal_startup_scenario_passes(tmp_path):
    report_path = tmp_path / "normal_startup.md"
    result = run_scenario_file(
        load_model(ROOT / "specs" / "toy_power_monitor.tmbd.yml"),
        ROOT / "scenarios" / "normal_startup.yml",
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
    result = run_scenario_file(
        load_model(ROOT / "specs" / "toy_power_monitor.tmbd.yml"),
        ROOT / "scenarios" / "undervoltage_fault.yml",
        report_path=tmp_path / "undervoltage_fault.md",
    )

    assert result.passed is True
    assert result.final_state == "FAULT_LATCHED"


def test_spi_timeout_scenario_passes(tmp_path):
    result = run_scenario_file(
        load_model(ROOT / "specs" / "toy_power_monitor.tmbd.yml"),
        ROOT / "scenarios" / "spi_timeout.yml",
        report_path=tmp_path / "spi_timeout.md",
    )

    assert result.passed is True
    assert result.reads[-1]["response"] == "timeout"
