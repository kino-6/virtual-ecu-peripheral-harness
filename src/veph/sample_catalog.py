from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class SampleCatalogError(ValueError):
    """Raised when a sample manifest is missing or malformed."""


@dataclass(frozen=True)
class SamplePaths:
    root: Path
    model: Path
    spec: Path | None
    generated_dir: Path
    reports_dir: Path
    preview_code_dir: Path | None
    scenarios: dict[str, Path]
    generated: dict[str, Path]
    reports: dict[str, Path]
    preview_code: dict[str, Path]
    legacy: dict[str, Path]


@dataclass(frozen=True)
class Sample:
    id: str
    title: str
    kind: str
    manifest_path: Path
    paths: SamplePaths
    spec_mbd: dict[str, Any] = field(default_factory=dict)


def samples_root(repo_root: str | Path | None = None) -> Path:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    return root / "samples"


def list_samples(repo_root: str | Path | None = None) -> list[Sample]:
    root = samples_root(repo_root)
    if not root.exists():
        return []
    return [
        load_sample(path.parent.name, repo_root=Path(repo_root) if repo_root is not None else Path.cwd())
        for path in sorted(root.glob("*/sample.yml"))
    ]


def load_sample(sample_id: str, repo_root: str | Path | None = None) -> Sample:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    sample_root = root / "samples" / sample_id
    manifest_path = sample_root / "sample.yml"
    if not manifest_path.exists():
        raise SampleCatalogError(f"sample {sample_id!r} does not have a manifest at {manifest_path}")
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SampleCatalogError(f"sample manifest must be a YAML mapping: {manifest_path}")
    declared_id = _required_str(data, "id", manifest_path)
    if declared_id != sample_id:
        raise SampleCatalogError(
            f"sample manifest id {declared_id!r} does not match directory name {sample_id!r}"
        )
    generated_dir = _resolve(sample_root, _optional_str(data, "generatedDir") or "generated")
    reports_dir = _resolve(sample_root, _optional_str(data, "reportsDir") or "reports")
    preview_code_dir = (
        _resolve(sample_root, preview_dir)
        if (preview_dir := _optional_str(data, "previewCodeDir")) is not None
        else None
    )
    spec = _optional_str(data, "spec")
    paths = SamplePaths(
        root=sample_root,
        model=_resolve(sample_root, _required_str(data, "model", manifest_path)),
        spec=_resolve(sample_root, spec) if spec is not None else None,
        generated_dir=generated_dir,
        reports_dir=reports_dir,
        preview_code_dir=preview_code_dir,
        scenarios=_resolve_mapping(sample_root, data.get("scenarios"), "scenarios", manifest_path),
        generated=_resolve_mapping(sample_root, data.get("generated"), "generated", manifest_path),
        reports=_resolve_mapping(sample_root, data.get("reports"), "reports", manifest_path),
        preview_code=_resolve_mapping(sample_root, data.get("previewCode"), "previewCode", manifest_path),
        legacy=_legacy_paths(sample_root, data),
    )
    return Sample(
        id=sample_id,
        title=_optional_str(data, "title") or sample_id,
        kind=_optional_str(data, "kind") or "sample",
        manifest_path=manifest_path,
        paths=paths,
        spec_mbd=data.get("specMbd") if isinstance(data.get("specMbd"), dict) else {},
    )


def _legacy_paths(sample_root: Path, data: dict[str, Any]) -> dict[str, Path]:
    legacy: dict[str, Path] = {}
    for key in ("legacyModel", "legacyEcuInterface"):
        value = _optional_str(data, key)
        if value is not None:
            legacy[key] = _resolve(sample_root, value)
    return legacy


def _resolve_mapping(
    sample_root: Path,
    value: object,
    key: str,
    manifest_path: Path,
) -> dict[str, Path]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise SampleCatalogError(f"{key} must be a mapping in {manifest_path}")
    resolved: dict[str, Path] = {}
    for name, relative in value.items():
        if not isinstance(name, str) or not isinstance(relative, str):
            raise SampleCatalogError(f"{key} entries must map strings to paths in {manifest_path}")
        resolved[name] = _resolve(sample_root, relative)
    return resolved


def _resolve(sample_root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute():
        raise SampleCatalogError(f"sample paths must be relative to sample root: {relative}")
    return sample_root / path


def _required_str(data: dict[str, Any], key: str, manifest_path: Path) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise SampleCatalogError(f"{key} must be a non-empty string in {manifest_path}")
    return value


def _optional_str(data: dict[str, Any], key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise SampleCatalogError(f"{key} must be a non-empty string when present")
    return value
