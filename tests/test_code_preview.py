from pathlib import Path
import shutil
import subprocess

import pytest

from veph.exporters.code_preview import CodePreviewExportError, export_code_preview
from veph.markup_parser import parse_markup_file
from veph.sample_catalog import load_sample


ROOT = Path(__file__).resolve().parents[1]


def test_export_code_preview_writes_hal_style_c_scaffold(tmp_path):
    model = parse_markup_file(load_sample("thermal_fan_control", ROOT).paths.model)
    written = export_code_preview(model, tmp_path)

    assert {path.name for path in written} == {
        "README.md",
        "controller.c",
        "controller.h",
        "hal_pwm.h",
        "hal_spi.h",
    }
    controller = (tmp_path / "controller.c").read_text(encoding="utf-8")
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")

    assert '#include "hal_spi.h"' in controller
    assert '#include "hal_pwm.h"' in controller
    assert "hal_spi_read_temperature_c" in controller
    assert "hal_pwm_set_fan_duty" in controller
    assert "TOY_THERMAL_STATE_FAULT" in controller
    assert "not certified code generation" in controller
    assert "preview-only" in readme
    assert "SYS-005" in readme


def test_generated_preview_c_is_syntax_checkable_when_cc_exists(tmp_path):
    if shutil.which("cc") is None:
        return
    model = parse_markup_file(load_sample("thermal_fan_control", ROOT).paths.model)
    export_code_preview(model, tmp_path)

    subprocess.run(
        ["cc", "-fsyntax-only", "controller.c"],
        cwd=tmp_path,
        check=True,
    )


def test_export_code_preview_supports_thermal_protection_controller(tmp_path):
    model = parse_markup_file(load_sample("thermal_protection_controller", ROOT).paths.model)
    export_code_preview(model, tmp_path)

    controller = (tmp_path / "controller.c").read_text(encoding="utf-8")
    header = (tmp_path / "controller.h").read_text(encoding="utf-8")
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")

    assert "ToyThermalProtectionController" in header
    assert "TOY_PROTECTION_STATE_FAULT_LATCHED" in header
    assert "hal_spi_read_temperature_c" in controller
    assert "hal_pwm_set_fan_duty" in controller
    assert "hal_load_limiter_set_derating" in controller
    assert "invalidDebounced" in controller
    assert "priority 10 recoverFromLatch" in controller
    assert "owner FaultLatchRecoveryManager" in controller
    assert "temperatureValid && !invalidDebounced && recoveryRequest" in controller
    assert "priority 20 faultLatch" in controller
    assert "preview-only" in readme
    assert "SYS-008" in readme


def test_generated_thermal_protection_preview_c_is_syntax_checkable_when_cc_exists(tmp_path):
    if shutil.which("cc") is None:
        return
    model = parse_markup_file(load_sample("thermal_protection_controller", ROOT).paths.model)
    export_code_preview(model, tmp_path)

    subprocess.run(
        ["cc", "-fsyntax-only", "controller.c"],
        cwd=tmp_path,
        check=True,
    )


def test_export_code_preview_rejects_unregistered_sample_without_thermal_fallback(tmp_path):
    model = parse_markup_file(load_sample("toy_power_monitor", ROOT).paths.model)

    with pytest.raises(CodePreviewExportError, match="ToyPowerMonitorIC.*supported components"):
        export_code_preview(model, tmp_path)
