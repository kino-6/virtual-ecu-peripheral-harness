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


def test_thermal_protection_derating_scenario_passes_with_report_sections(tmp_path):
    report_path = tmp_path / "thermal_protection_derating.md"
    result = run_preview_file(
        ROOT / "examples" / "toy_thermal_protection_controller.mbd.md",
        ROOT / "scenarios" / "thermal_protection_derating.yml",
        report_path=report_path,
    )

    assert result.passed is True
    assert result.final_state == "DERATING"
    assert result.generated_ecu_command_outputs["fanDuty"] == 95
    assert result.generated_ecu_command_outputs["deratingCommand"] == 45
    assert result.generated_ecu_command_outputs["diagnosticFault"] is False
    assert result.generated_ecu_command_outputs["halCalls"][1]["target"] == "ToyFanDriverIC"
    assert result.generated_ecu_command_outputs["halCalls"][2]["target"] == "ToyLoadLimiterIC"

    report = report_path.read_text(encoding="utf-8")
    assert "## Model Inputs" in report
    assert "## Scenario Steps" in report
    assert "## Observed Behavior" in report
    assert "## Expected Behavior" in report
    assert "## Pass/Fail Result" in report
    assert "Preview subset assumption" in report
    assert "examples/toy_thermal_protection_controller.mbd.md" in report
    assert "generated/protection_ecu_preview/controller.c" in report


def test_thermal_protection_boundary_scenario_proves_low_threshold_return(tmp_path):
    result = run_preview_file(
        ROOT / "examples" / "toy_thermal_protection_controller.mbd.md",
        ROOT / "scenarios" / "thermal_protection_boundary.yml",
        report_path=tmp_path / "thermal_protection_boundary.md",
    )

    assert result.passed is True
    assert result.final_state == "IDLE"
    assert result.generated_ecu_command_outputs["fanDuty"] == 0
    assert result.observed_behavior["stepEvidence"][-1]["appliedRule"] == "lowCooling"
    assert result.observed_behavior["stepEvidence"][-1]["requirementRefs"] == [
        "HAR-001",
        "HAR-002",
        "HAR-004",
        "SYS-004",
    ]


def test_thermal_protection_fault_latch_and_recovery_scenarios_pass(tmp_path):
    fault = run_preview_file(
        ROOT / "examples" / "toy_thermal_protection_controller.mbd.md",
        ROOT / "scenarios" / "thermal_protection_fault_latch.yml",
        report_path=tmp_path / "thermal_protection_fault_latch.md",
    )
    recovery = run_preview_file(
        ROOT / "examples" / "toy_thermal_protection_controller.mbd.md",
        ROOT / "scenarios" / "thermal_protection_recovery.yml",
        report_path=tmp_path / "thermal_protection_recovery.md",
    )

    assert fault.passed is True
    assert fault.final_state == "FAULT_LATCHED"
    assert fault.generated_ecu_command_outputs["diagnosticFault"] is True
    assert fault.generated_ecu_command_outputs["safeCommandActive"] is True
    assert fault.observed_behavior["stepEvidence"][-1]["appliedRule"] == "faultLatch"

    assert recovery.passed is True
    assert recovery.final_state == "IDLE"
    assert recovery.generated_ecu_command_outputs["diagnosticFault"] is False
    assert recovery.generated_ecu_command_outputs["safeCommandActive"] is False
