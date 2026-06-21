from pathlib import Path

from veph.sample_catalog import list_samples, load_sample


ROOT = Path(__file__).resolve().parents[1]


def test_sample_catalog_discovers_sample_workspaces():
    samples = {sample.id: sample for sample in list_samples(ROOT)}

    assert set(samples) == {
        "simple_state_machine",
        "simple_threshold_indicator",
        "thermal_fan_control",
        "thermal_protection_controller",
        "toy_power_monitor",
    }
    assert samples["toy_power_monitor"].paths.model == ROOT / "samples" / "toy_power_monitor" / "model.mbd.md"
    assert samples["thermal_protection_controller"].paths.generated["demo"].name == "demo.html"
    assert samples["thermal_fan_control"].paths.preview_code_dir == ROOT / "samples" / "thermal_fan_control" / "preview_c"


def test_sample_manifest_paths_exist_for_declared_artifacts():
    for sample in list_samples(ROOT):
        assert sample.paths.model.exists()
        if sample.paths.spec is not None:
            assert sample.paths.spec.exists()
        for path in sample.paths.scenarios.values():
            assert path.exists()
        for path in sample.paths.generated.values():
            assert path.exists()
        for path in sample.paths.reports.values():
            assert path.exists()
        for path in sample.paths.preview_code.values():
            assert path.exists()
        for path in sample.paths.legacy.values():
            assert path.exists()


def test_root_level_sample_directories_are_not_canonical_inputs():
    assert not list((ROOT / "examples").glob("*.mbd.md"))
    assert not list((ROOT / "scenarios").glob("*.yml"))
    assert set(path.name for path in (ROOT / "generated").iterdir()) <= {".gitkeep"}
    assert set(path.name for path in (ROOT / "reports").iterdir()) <= {".gitkeep"}


def test_load_sample_rejects_unknown_sample():
    try:
        load_sample("missing_sample", ROOT)
    except ValueError as exc:
        assert "missing_sample" in str(exc)
    else:
        raise AssertionError("expected unknown sample to fail")
