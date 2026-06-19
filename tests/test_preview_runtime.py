from pathlib import Path

from veph.preview_runtime import run_preview_file
from veph.sample_catalog import load_sample


ROOT = Path(__file__).resolve().parents[1]


def _sample(sample_id: str):
    return load_sample(sample_id, ROOT)


def test_thermal_fan_normal_preview_scenario_passes(tmp_path):
    report_path = tmp_path / "thermal_fan_normal.md"
    sample = _sample("thermal_fan_control")
    result = run_preview_file(
        sample.paths.model,
        sample.paths.scenarios["normal"],
        report_path=report_path,
    )

    assert result.passed is True
    assert result.final_state == "COOLING"
    assert result.generated_ecu_command_outputs["fanDuty"] == 80
    assert result.generated_ecu_command_outputs["fault"] is False
    assert result.generated_ecu_command_outputs["previewCodeSource"] == "sample-specific preview C export, if available"
    assert result.generated_ecu_command_outputs["commandFlows"][0]["target"] == "HAL_PWM.set_fan_duty"
    assert result.observed_behavior["stepEvidence"][-1]["appliedRule"] == "highTemperature"
    assert result.observed_behavior["stepEvidence"][-1]["requirementRefs"] == [
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
    assert "previewCodeSource" in report


def test_thermal_fan_fault_preview_scenario_passes(tmp_path):
    sample = _sample("thermal_fan_control")
    result = run_preview_file(
        sample.paths.model,
        sample.paths.scenarios["fault"],
        report_path=tmp_path / "thermal_fan_fault.md",
    )

    assert result.passed is True
    assert result.final_state == "FAULT"
    assert result.generated_ecu_command_outputs["fanDuty"] == 35
    assert result.generated_ecu_command_outputs["fault"] is True
    assert result.observed_behavior["stepEvidence"][-1]["appliedRule"] == "sensorFault"


def test_thermal_protection_derating_scenario_passes_with_report_sections(tmp_path):
    report_path = tmp_path / "thermal_protection_derating.md"
    sample = _sample("thermal_protection_controller")
    result = run_preview_file(
        sample.paths.model,
        sample.paths.scenarios["derating"],
        report_path=report_path,
    )

    assert result.passed is True
    assert result.final_state == "DERATING"
    assert result.generated_ecu_command_outputs["fanDuty"] == 95
    assert result.generated_ecu_command_outputs["deratingCommand"] == 45
    assert result.generated_ecu_command_outputs["diagnosticFault"] is False
    assert {flow["target"] for flow in result.generated_ecu_command_outputs["commandFlows"]} >= {
        "HAL_PWM.set_fan_duty",
        "HAL_LIMITER.set_derating",
    }

    report = report_path.read_text(encoding="utf-8")
    assert "## Model Inputs" in report
    assert "## Functional Decomposition Evidence" in report
    assert "## Scenario Steps" in report
    assert "## Observed Behavior" in report
    assert "## Expected Behavior" in report
    assert "## Pass/Fail Result" in report
    assert "Preview subset assumption" in report
    assert "samples/thermal_protection_controller/model.mbd.md" in report
    assert "previewCodeSource" in report
    assert "DeratingCommandManager" in report


def test_thermal_protection_boundary_scenario_proves_low_threshold_return(tmp_path):
    sample = _sample("thermal_protection_controller")
    result = run_preview_file(
        sample.paths.model,
        sample.paths.scenarios["boundary"],
        report_path=tmp_path / "thermal_protection_boundary.md",
    )

    assert result.passed is True
    assert result.final_state == "IDLE"
    assert result.generated_ecu_command_outputs["fanDuty"] == 0
    assert result.observed_behavior["stepEvidence"][-1]["appliedRule"] == "lowCooling"
    assert "SYS-004" in result.observed_behavior["stepEvidence"][-1]["requirementRefs"]


def test_thermal_protection_fault_latch_and_recovery_scenarios_pass(tmp_path):
    sample = _sample("thermal_protection_controller")
    fault = run_preview_file(
        sample.paths.model,
        sample.paths.scenarios["fault_latch"],
        report_path=tmp_path / "thermal_protection_fault_latch.md",
    )
    recovery = run_preview_file(
        sample.paths.model,
        sample.paths.scenarios["recovery"],
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
    final_step = recovery.observed_behavior["stepEvidence"][-1]
    assert final_step["appliedRule"] == "recoverFromLatch"
    assert final_step["appliedOwner"] == "FaultLatchRecoveryManager"
    assert final_step["selectionPolicy"] == "lowest numeric priority wins after state scope and guard match"
    assert final_step["controlRuleEvaluations"][0]["priority"] == 10
    assert final_step["controlRuleEvaluations"][0]["owner"] == "FaultLatchRecoveryManager"
    assert final_step["controlRuleEvaluations"][0]["stateScope"] == "FAULT_LATCHED"
    assert final_step["controlRuleEvaluations"][0]["scenarios"] == ["thermal_protection_recovery"]
