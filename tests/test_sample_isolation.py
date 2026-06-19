from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_common_layers_do_not_hardcode_thermal_sample_identifiers():
    common_files = [
        ROOT / "src" / "veph" / "cli.py",
        ROOT / "src" / "veph" / "exporters" / "code_preview.py",
        ROOT / "src" / "veph" / "exporters" / "demo_html.py",
        ROOT / "src" / "veph" / "preview_runtime" / "generic.py",
        ROOT / "src" / "veph" / "requirements_support.py",
    ]
    sample_identifiers = [
        "ToyThermalFanController",
        "ToyThermalProtectionController",
        "ToyTempSensorIC",
        "ToyFanDriverIC",
        "thermal_protection_",
        "thermal_fan_",
        "generated/protection",
        "generated/ecu_preview",
        "reports/thermal",
    ]

    for path in common_files:
        text = path.read_text(encoding="utf-8")
        for identifier in sample_identifiers:
            assert identifier not in text, f"{identifier!r} leaked into common layer {path}"
