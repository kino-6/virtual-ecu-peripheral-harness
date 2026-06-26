from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from veph.exporters.demo_html import export_demo_html
from veph.exporters.fmi_metadata import export_fmi_metadata
from veph.exporters.markdown import export_markdown
from veph.exporters.mermaid import export_mermaid
from veph.exporters.modelica import export_modelica
from veph.exporters.plantuml import export_plantuml
from veph.exporters.scxml import export_scxml
from veph.exporters.simulink_m import export_simulink_m
from veph.markup_parser import parse_markup, parse_markup_file
from veph.preview_runtime import run_preview_file
from veph.report import render_report
from veph.review_quality import evaluate_review_html
from veph.sample_catalog import Sample, load_sample
from veph.sequence_expectations import compare_sequence_expectations, sequence_expectations_from_spec
from veph.spec_mbd_alignment import compare_spec_to_mbd_model
from veph.spec_mbd_conversion import generate_mbd_from_spec
from veph.spec_mbd_viewer import export_spec_mbd_viewer


@dataclass(frozen=True)
class SampleValidationReport:
    sample_id: str
    passed: bool
    checks: tuple[str, ...] = field(default_factory=tuple)
    issues: tuple[str, ...] = field(default_factory=tuple)

    def to_markdown(self) -> str:
        return "\n".join(
            [
                f"# Sample Validation: {self.sample_id}",
                "",
                f"Result: **{'PASS' if self.passed else 'FAIL'}**",
                "",
                "## Checks",
                *[f"- {check}" for check in self.checks],
                "",
                "## Issues",
                *([f"- {issue}" for issue in self.issues] or ["- None"]),
                "",
            ]
        )


def validate_sample(sample_id: str, repo_root: str | Path | None = None) -> SampleValidationReport:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    sample = load_sample(sample_id, root)
    checks: list[str] = []
    issues: list[str] = []
    model = parse_markup_file(sample.paths.model)
    _check_generated_artifacts(sample, model, checks, issues)
    converted_model = _check_spec_conversion(sample, checks, issues)
    _check_preview_reports(root, sample, checks, issues)
    _check_review_html(sample, converted_model, checks, issues)
    return SampleValidationReport(sample.id, not issues, tuple(checks), tuple(issues))


def _check_generated_artifacts(sample: Sample, model, checks: list[str], issues: list[str]) -> None:
    expected = {
        "ir": json.dumps(model.to_dict(), indent=2, sort_keys=True, default=str) + "\n",
        "docs": export_markdown(model),
        "demo": export_demo_html(model, spec_path=sample.paths.spec),
        "mermaid": export_mermaid(model),
        "plantuml": export_plantuml(model),
        "scxml": export_scxml(model),
        "modelica": export_modelica(model),
        "simulink": export_simulink_m(model),
        "fmi": export_fmi_metadata(model),
    }
    for name, content in expected.items():
        path = sample.paths.generated.get(name)
        if path is not None:
            _compare_text(path, content, f"generated artifact {name}", checks, issues)


def _check_spec_conversion(sample: Sample, checks: list[str], issues: list[str]):
    if sample.paths.spec is None or "convertedMbd" not in sample.paths.generated:
        return None
    config = sample.spec_mbd
    converted_mbd = generate_mbd_from_spec(
        sample.paths.spec,
        component_name=str(config["component"]),
        parameter_defaults={str(k): str(v) for k, v in dict(config.get("parameterDefaults") or {}).items()},
        input_defaults={str(k): str(v) for k, v in dict(config.get("inputDefaults") or {}).items()},
        output_defaults={str(k): str(v) for k, v in dict(config.get("outputDefaults") or {}).items()},
        scenario=str(config.get("scenario") or ""),
    )
    converted_path = sample.paths.generated["convertedMbd"]
    _compare_text(converted_path, converted_mbd, "converted MBD from spec", checks, issues)
    converted_model = parse_markup(converted_mbd, converted_path)
    alignment = compare_spec_to_mbd_model(sample.paths.spec, converted_model, converted_path)
    if alignment.passed:
        checks.append("spec-to-MBD semantic alignment PASS")
    else:
        issues.append("spec-to-MBD semantic alignment FAIL")
    return converted_model


def _check_preview_reports(root: Path, sample: Sample, checks: list[str], issues: list[str]) -> None:
    relative_model = _preview_path(root, sample.paths.model)
    for name, scenario_path in sample.paths.scenarios.items():
        result = run_preview_file(relative_model, _preview_path(root, scenario_path))
        report_path = sample.paths.reports.get(name)
        if report_path is not None:
            _compare_text(report_path, render_report(result), f"preview report {name}", checks, issues)
        if sample.paths.spec is not None and sequence_expectations_from_spec(sample.paths.spec):
            sequence_report = compare_sequence_expectations(sample.paths.spec, result)
            if sequence_report.passed:
                checks.append(f"sequence expectations {name} PASS")
            else:
                issues.extend(f"sequence expectation missing in {name}: {item}" for item in sequence_report.missing)


def _check_review_html(sample: Sample, converted_model, checks: list[str], issues: list[str]) -> None:
    for name in ("convertedReviewHtml", "specMbdViewer"):
        path = sample.paths.generated.get(name)
        if path is None:
            continue
        quality = evaluate_review_html(path.read_text(encoding="utf-8"), require_harness=name != "specMbdViewer")
        if quality.passed:
            checks.append(f"review HTML quality {name} PASS")
        else:
            issues.extend(f"review HTML quality {name}: {issue}" for issue in quality.issues)
    if converted_model is not None and sample.paths.spec is not None and "convertedReviewHtml" in sample.paths.generated:
        _compare_text(
            sample.paths.generated["convertedReviewHtml"],
            export_demo_html(converted_model, spec_path=sample.paths.spec),
            "converted review HTML",
            checks,
            issues,
        )
    if converted_model is not None and sample.paths.spec is not None and "specMbdViewer" in sample.paths.generated:
        alignment = compare_spec_to_mbd_model(
            sample.paths.spec,
            converted_model,
            sample.paths.generated.get("convertedMbd", sample.paths.generated_dir / "from_spec.model.mbd.md"),
        )
        _compare_text(
            sample.paths.generated["specMbdViewer"],
            export_spec_mbd_viewer(sample.paths.spec, converted_model, alignment),
            "spec MBD viewer",
            checks,
            issues,
        )


def _compare_text(path: Path, expected: str, label: str, checks: list[str], issues: list[str]) -> None:
    if not path.exists():
        issues.append(f"{label} missing: {path}")
        return
    if path.read_text(encoding="utf-8") == expected:
        checks.append(f"{label} deterministic")
    else:
        issues.append(f"{label} is stale: {path}")


def _relative_to_root(root: Path, path: Path) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return path


def _preview_path(root: Path, path: Path) -> Path:
    if root.resolve() == Path.cwd().resolve():
        return _relative_to_root(root, path)
    return path
