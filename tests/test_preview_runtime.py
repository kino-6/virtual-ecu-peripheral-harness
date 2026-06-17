from pathlib import Path

from veph.preview_runtime import run_preview_file


ROOT = Path(__file__).resolve().parents[1]


def test_thermal_fan_normal_preview_scenario_passes(tmp_path):
    report_path = tmp_path / "thermal_fan_normal.md"
    result = run_preview_file(
        ROOT / "examples" / "toy_thermal_fan_control.mbd.md",
        ROOT / "scenarios" / "thermal_fan_normal.yml",
        report_path=report_path,
    )

    assert result.passed is True
    assert result.final_state == "COOLING"
    assert result.generated_ecu_command_outputs == {
        "fanDuty": 80,
        "fault": False,
        "halCalls": ["hal_spi_read_temperature_c", "hal_pwm_set_fan_duty"],
    }
    report = report_path.read_text(encoding="utf-8")
    assert "preview-only; not a certified code generation or verification backend" in report
    assert "## Model Inputs" in report
    assert "## Scenario Steps" in report
    assert "## Observed Behavior" in report
    assert "## Generated ECU Command Outputs" in report
    assert "## Expected Behavior" in report
    assert "## Pass/Fail Result" in report


def test_thermal_fan_fault_preview_scenario_passes(tmp_path):
    result = run_preview_file(
        ROOT / "examples" / "toy_thermal_fan_control.mbd.md",
        ROOT / "scenarios" / "thermal_fan_fault.yml",
        report_path=tmp_path / "thermal_fan_fault.md",
    )

    assert result.passed is True
    assert result.final_state == "FAULT"
    assert result.generated_ecu_command_outputs["fanDuty"] == 35
    assert result.generated_ecu_command_outputs["fault"] is True
