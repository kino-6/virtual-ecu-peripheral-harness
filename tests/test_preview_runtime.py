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
    assert result.generated_ecu_command_outputs["fanDuty"] == 80
    assert result.generated_ecu_command_outputs["fault"] is False
    assert result.generated_ecu_command_outputs["controllerSource"] == "generated/ecu_preview/controller.c"
    assert result.generated_ecu_command_outputs["halCalls"][0]["api"] == "hal_spi_read_temperature_c"
    assert result.observed_behavior["stepEvidence"][-1]["appliedRule"] == "highTemperature"
    assert result.observed_behavior["stepEvidence"][-1]["requirementRefs"] == [
        "HAR-001",
        "HAR-002",
        "HAR-004",
        "SYS-003",
        "SYS-006",
    ]
    report = report_path.read_text(encoding="utf-8")
    assert "preview-only; not a certified code generation or verification backend" in report
    assert "## Model Inputs" in report
    assert "## Traceability Matrix" in report
    assert "## Scenario Steps" in report
    assert "## Harness Boundary Evidence" in report
    assert "## Per-Step Preview Execution" in report
    assert "## Observed Behavior" in report
    assert "## Generated ECU Command Outputs" in report
    assert "## Expected Behavior" in report
    assert "## Pass/Fail Result" in report
    assert "controlRuleEvaluations" in report
    assert "generated/ecu_preview/controller.c" in report


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
    assert result.observed_behavior["stepEvidence"][-1]["appliedRule"] == "sensorFault"
