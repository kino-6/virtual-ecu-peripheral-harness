from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from veph.exporters.code_preview import CodePreviewExportError, export_code_preview
from veph.exporters.fmi_metadata import export_fmi_metadata
from veph.exporters.markdown import export_markdown
from veph.exporters.demo_html import export_demo_html
from veph.exporters.mermaid import export_mermaid
from veph.exporters.modelica import export_modelica
from veph.exporters.plantuml import export_plantuml
from veph.exporters.scxml import export_scxml
from veph.exporters.simulink_m import export_simulink_m
from veph.markup_parser import MarkupParseError, parse_markup, parse_markup_file
from veph.model_loader import ModelValidationError, load_model
from veph.preview_runtime import PreviewScenarioError, run_preview_file
from veph.requirements_support import (
    extract_requirements,
    generate_mbd_scaffold,
    generate_spec_scaffold,
    render_requirements_json,
    validate_traceability,
)
from veph.samples.requirements_scaffolds import SampleScaffoldError, generate_sample_mbd_scaffold
from veph.sample_catalog import SampleCatalogError, find_sample_by_spec, list_samples, load_sample
from veph.scenario_runner import ScenarioError, run_scenario_file
from veph.spec_mbd_alignment import SpecMbdAlignmentError, compare_spec_to_mbd, compare_spec_to_mbd_model
from veph.spec_mbd_conversion import generate_mbd_from_spec
from veph.spec_mbd_viewer import export_spec_mbd_viewer


Exporter = Callable[[object], str]


@dataclass(frozen=True)
class ExportCommand:
    exporter: Callable
    help: str
    source_required: bool = True
    out_required: bool = True


EXPORT_COMMANDS = {
    "export-docs": ExportCommand(export_markdown, "export Markdown documentation"),
    "export-demo": ExportCommand(export_demo_html, "export HTML MBD review artifact"),
    "export-review-html": ExportCommand(export_demo_html, "export HTML MBD review artifact"),
    "export-mermaid": ExportCommand(export_mermaid, "export Mermaid preview diagram"),
    "export-plantuml": ExportCommand(export_plantuml, "export PlantUML state diagram"),
    "export-scxml": ExportCommand(export_scxml, "export SCXML state machine"),
    "export-modelica": ExportCommand(export_modelica, "export Modelica text model"),
    "export-simulink-m": ExportCommand(export_simulink_m, "export MATLAB/Simulink .m script"),
    "export-fmi-metadata": ExportCommand(export_fmi_metadata, "export FMI-oriented metadata stub"),
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except (
        CodePreviewExportError,
        MarkupParseError,
        ModelValidationError,
        SampleScaffoldError,
        SampleCatalogError,
        ScenarioError,
        PreviewScenarioError,
        SpecMbdAlignmentError,
        OSError,
    ) as exc:
        parser.exit(1, f"error: {exc}\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m veph", description="Markup-to-MBD artifact bridge")
    subparsers = parser.add_subparsers(required=True)

    parse = subparsers.add_parser("parse", help="parse MBD markdown into an internal IR snapshot")
    parse.add_argument("source")
    parse.add_argument("--out", required=True)
    parse.set_defaults(func=_parse)

    validate = subparsers.add_parser("validate", help="validate a Textual MBD model")
    validate.add_argument("model")
    validate.set_defaults(func=_validate)

    run = subparsers.add_parser("run", help="run a scenario against a model")
    run.add_argument("--model", required=True)
    run.add_argument("--scenario", required=True)
    run.add_argument("--report", required=True)
    run.set_defaults(func=_run)

    run_preview = subparsers.add_parser("run-preview", help="run a preview-only scenario from MBD markdown")
    run_preview.add_argument("--model", required=True)
    run_preview.add_argument("--scenario", required=True)
    run_preview.add_argument("--report", required=True)
    run_preview.set_defaults(func=_run_preview)

    export_code = subparsers.add_parser("export-code-preview", help="export preview-only ECU C scaffold")
    export_code.add_argument("source")
    export_code.add_argument("--out", required=True)
    export_code.set_defaults(func=_export_code_preview)

    list_samples_cmd = subparsers.add_parser("list-samples", help="list registered sample workspaces")
    list_samples_cmd.set_defaults(func=_list_samples)

    export_sample = subparsers.add_parser("export-sample", help="regenerate sample-local handoff artifacts")
    export_sample.add_argument("sample")
    export_sample.set_defaults(func=_export_sample)

    extract_requirements_cmd = subparsers.add_parser(
        "extract-requirements",
        help="extract requirement records from Requirements.md",
    )
    extract_requirements_cmd.add_argument("source")
    extract_requirements_cmd.add_argument("--out", required=True)
    extract_requirements_cmd.set_defaults(func=_extract_requirements)

    scaffold_spec = subparsers.add_parser(
        "scaffold-spec",
        help="generate a human-readable specification scaffold from requirements",
    )
    scaffold_spec.add_argument("source")
    scaffold_spec.add_argument("--out", required=True)
    scaffold_spec.set_defaults(func=_scaffold_spec)

    scaffold_mbd = subparsers.add_parser(
        "scaffold-mbd",
        help="generate a Mermaid-like MBD scaffold from requirements",
    )
    scaffold_mbd.add_argument("source")
    scaffold_mbd.add_argument("--out", required=True)
    scaffold_mbd.add_argument(
        "--sample",
        help="optional explicit sample scaffold; omitted means sample-neutral",
    )
    scaffold_mbd.set_defaults(func=_scaffold_mbd)

    validate_trace = subparsers.add_parser(
        "validate-trace",
        help="validate requirements coverage in generated spec and MBD scaffold",
    )
    validate_trace.add_argument("--requirements", required=True)
    validate_trace.add_argument("--spec", required=True)
    validate_trace.add_argument("--mbd", required=True)
    validate_trace.add_argument("--out", required=True)
    validate_trace.set_defaults(func=_validate_trace)

    validate_spec_mbd = subparsers.add_parser(
        "validate-spec-mbd",
        help="validate Spec.md Mermaid Design Overview against MBD source semantics",
    )
    validate_spec_mbd.add_argument("--spec", required=True)
    validate_spec_mbd.add_argument("--mbd", required=True)
    validate_spec_mbd.add_argument("--out", required=True)
    validate_spec_mbd.set_defaults(func=_validate_spec_mbd)

    generate_mbd_spec = subparsers.add_parser(
        "generate-mbd-from-spec",
        help="generate MBD authoring Markdown from supported Spec.md Mermaid",
    )
    generate_mbd_spec.add_argument("--spec", required=True)
    generate_mbd_spec.add_argument("--component", required=True)
    generate_mbd_spec.add_argument("--out", required=True)
    generate_mbd_spec.add_argument("--scenario", default="")
    generate_mbd_spec.add_argument(
        "--parameter-default",
        action="append",
        default=[],
        help="parameter default as name=value; repeatable",
    )
    generate_mbd_spec.add_argument(
        "--input-default",
        action="append",
        default=[],
        help="input default as name=value; repeatable",
    )
    generate_mbd_spec.add_argument(
        "--output-default",
        action="append",
        default=[],
        help="output default as name=value; repeatable",
    )
    generate_mbd_spec.set_defaults(func=_generate_mbd_from_spec)

    render_spec_mbd = subparsers.add_parser(
        "render-spec-mbd",
        help="render Spec.md Mermaid to MBD review viewer using sample metadata when available",
    )
    render_spec_mbd.add_argument("spec")
    render_spec_mbd.add_argument("--component", help="component name when spec is not in a sample manifest")
    render_spec_mbd.add_argument("--out", help="viewer output path; defaults to sample generated/spec_mbd_viewer.html")
    render_spec_mbd.add_argument("--mbd-out", help="converted MBD output path; defaults to sample generated/from_spec.model.mbd.md")
    render_spec_mbd.add_argument("--scenario", default="")
    render_spec_mbd.add_argument("--parameter-default", action="append", default=[])
    render_spec_mbd.add_argument("--input-default", action="append", default=[])
    render_spec_mbd.add_argument("--output-default", action="append", default=[])
    render_spec_mbd.set_defaults(func=_render_spec_mbd)

    for name, command in EXPORT_COMMANDS.items():
        _add_export(subparsers, name, command)
    return parser


def _add_export(
    subparsers: argparse._SubParsersAction,
    name: str,
    command: ExportCommand,
) -> None:
    subcommand = subparsers.add_parser(name, help=command.help)
    subcommand.add_argument("source", nargs="?" if not command.source_required else None)
    subcommand.add_argument("--model", required=False, help="legacy YAML model input")
    subcommand.add_argument("--out", required=command.out_required)
    subcommand.set_defaults(func=lambda args, exporter=command.exporter: _export(args, exporter))


def _parse(args: argparse.Namespace) -> None:
    model = parse_markup_file(args.source)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(model.to_dict(), indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(f"wrote {output}")


def _validate(args: argparse.Namespace) -> None:
    model = load_model(args.model)
    print(f"valid: {model.name}")


def _run(args: argparse.Namespace) -> None:
    model = load_model(args.model)
    result = run_scenario_file(model, args.scenario, args.report)
    print(f"{result.name}: {'PASS' if result.passed else 'FAIL'}")


def _run_preview(args: argparse.Namespace) -> None:
    result = run_preview_file(args.model, args.scenario, args.report)
    print(f"{result.name}: {'PASS' if result.passed else 'FAIL'}")


def _export_code_preview(args: argparse.Namespace) -> None:
    model = parse_markup_file(args.source)
    written = export_code_preview(model, args.out)
    print(f"wrote {len(written)} files to {Path(args.out)}")


def _list_samples(args: argparse.Namespace) -> None:
    for sample in list_samples():
        print(f"{sample.id}\t{sample.kind}\t{sample.title}\t{sample.paths.root}")


def _export_sample(args: argparse.Namespace) -> None:
    sample = load_sample(args.sample)
    model = parse_markup_file(sample.paths.model)
    converted_mbd = ""
    converted_model = None
    alignment_report = None
    if "convertedMbd" in sample.paths.generated or "specMbdViewer" in sample.paths.generated:
        if sample.paths.spec is None:
            raise OSError(f"sample {sample.id!r} requests spec MBD conversion but has no spec path")
        converted_mbd = _generate_sample_mbd_from_spec(sample)
        converted_path = sample.paths.generated.get("convertedMbd", sample.paths.generated_dir / "from_spec.model.mbd.md")
        converted_model = parse_markup(converted_mbd, converted_path)
        alignment_report = compare_spec_to_mbd_model(sample.paths.spec, converted_model, converted_path)
        if not alignment_report.passed:
            raise OSError(f"sample {sample.id!r} converted MBD does not match Spec Mermaid semantics")
    exported = {
        "ir": json.dumps(model.to_dict(), indent=2, sort_keys=True, default=str) + "\n",
        "docs": export_markdown(model),
        "demo": export_demo_html(model),
        "mermaid": export_mermaid(model),
        "plantuml": export_plantuml(model),
        "scxml": export_scxml(model),
        "modelica": export_modelica(model),
        "simulink": export_simulink_m(model),
        "fmi": export_fmi_metadata(model),
    }
    if converted_mbd:
        exported["convertedMbd"] = converted_mbd
    if converted_model is not None and alignment_report is not None:
        exported["specMbdViewer"] = export_spec_mbd_viewer(sample.paths.spec, converted_model, alignment_report)
        exported["convertedReviewHtml"] = export_demo_html(converted_model)
    if "specMbdAlignment" in sample.paths.generated:
        if sample.paths.spec is None:
            raise OSError(f"sample {sample.id!r} requests spec/MBD alignment but has no spec path")
        source_alignment_report = compare_spec_to_mbd(sample.paths.spec, sample.paths.model)
        exported["specMbdAlignment"] = source_alignment_report.to_markdown()
        if not source_alignment_report.passed:
            _write_text(sample.paths.generated["specMbdAlignment"], source_alignment_report.to_markdown())
            raise OSError(f"sample {sample.id!r} spec Mermaid does not match MBD source semantics")
    count = 0
    for artifact, content in exported.items():
        output = sample.paths.generated.get(artifact)
        if output is None:
            continue
        _write_text(output, content)
        count += 1
    if sample.paths.preview_code_dir is not None:
        written = export_code_preview(model, sample.paths.preview_code_dir)
        count += len(written)
    print(f"exported {count} sample artifact(s) for {sample.id}")


def _extract_requirements(args: argparse.Namespace) -> None:
    extracted = extract_requirements(args.source)
    _write_text(args.out, render_requirements_json(extracted))


def _scaffold_spec(args: argparse.Namespace) -> None:
    extracted = extract_requirements(args.source)
    _write_text(args.out, generate_spec_scaffold(extracted))


def _scaffold_mbd(args: argparse.Namespace) -> None:
    extracted = extract_requirements(args.source)
    if args.sample:
        _write_text(args.out, generate_sample_mbd_scaffold(args.sample, extracted))
        return
    _write_text(args.out, generate_mbd_scaffold(extracted))


def _validate_trace(args: argparse.Namespace) -> None:
    extracted = extract_requirements(args.requirements)
    spec_text = Path(args.spec).read_text(encoding="utf-8")
    mbd_text = Path(args.mbd).read_text(encoding="utf-8")
    report = validate_traceability(extracted, spec_text, mbd_text)
    _write_text(args.out, report.to_markdown())
    if not report.passed:
        raise OSError("requirements trace validation failed")


def _validate_spec_mbd(args: argparse.Namespace) -> None:
    report = compare_spec_to_mbd(args.spec, args.mbd)
    _write_text(args.out, report.to_markdown())
    if not report.passed:
        raise OSError("spec Mermaid does not match MBD source semantics")


def _generate_mbd_from_spec(args: argparse.Namespace) -> None:
    mbd_text = generate_mbd_from_spec(
        args.spec,
        component_name=args.component,
        parameter_defaults=_parse_default_args(args.parameter_default),
        input_defaults=_parse_default_args(args.input_default),
        output_defaults=_parse_default_args(args.output_default),
        scenario=args.scenario,
    )
    _write_text(args.out, mbd_text)


def _render_spec_mbd(args: argparse.Namespace) -> None:
    spec_path = Path(args.spec)
    sample = find_sample_by_spec(spec_path)
    config = sample.spec_mbd if sample is not None else {}
    component = args.component or config.get("component")
    if not isinstance(component, str) or not component:
        raise OSError("component is required; pass --component or use a spec listed in sample.yml specMbd")
    parameter_defaults = {
        **_string_mapping(config.get("parameterDefaults")),
        **_parse_default_args(args.parameter_default),
    }
    input_defaults = {
        **_string_mapping(config.get("inputDefaults")),
        **_parse_default_args(args.input_default),
    }
    output_defaults = {
        **_string_mapping(config.get("outputDefaults")),
        **_parse_default_args(args.output_default),
    }
    scenario = args.scenario or str(config.get("scenario") or "")
    mbd_text = generate_mbd_from_spec(
        spec_path,
        component_name=component,
        parameter_defaults=parameter_defaults,
        input_defaults=input_defaults,
        output_defaults=output_defaults,
        scenario=scenario,
    )
    mbd_out = Path(args.mbd_out) if args.mbd_out else _default_converted_mbd_path(sample, spec_path)
    model = parse_markup(mbd_text, mbd_out)
    report = compare_spec_to_mbd_model(spec_path, model, mbd_out)
    if not report.passed:
        raise OSError("converted MBD does not match Spec Mermaid semantics")
    viewer = export_spec_mbd_viewer(spec_path, model, report)
    viewer_out = Path(args.out) if args.out else _default_spec_mbd_viewer_path(sample, spec_path)
    _write_text(mbd_out, mbd_text)
    _write_text(viewer_out, viewer)


def _export(args: argparse.Namespace, exporter: Callable) -> None:
    source = args.source or args.model
    if not source:
        raise OSError("missing source markdown path or --model legacy YAML path")
    model = _load_authoring_source(source)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(exporter(model), encoding="utf-8")
    print(f"wrote {output}")


def _write_text(path: str | Path, content: str) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"wrote {output}")


def _generate_sample_mbd_from_spec(sample) -> str:
    config = sample.spec_mbd
    component = config.get("component")
    if not isinstance(component, str) or not component:
        raise OSError(f"sample {sample.id!r} specMbd.component must be set for conversion")
    return generate_mbd_from_spec(
        sample.paths.spec,
        component_name=component,
        parameter_defaults=_string_mapping(config.get("parameterDefaults")),
        input_defaults=_string_mapping(config.get("inputDefaults")),
        output_defaults=_string_mapping(config.get("outputDefaults")),
        scenario=str(config.get("scenario") or ""),
    )


def _parse_default_args(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in values:
        key, separator, value = item.partition("=")
        if separator != "=" or not key or not value:
            raise OSError(f"default value must use name=value form: {item}")
        parsed[key] = value
    return parsed


def _string_mapping(value: object) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise OSError("specMbd defaults must be mappings")
    return {str(key): str(item) for key, item in value.items()}


def _default_converted_mbd_path(sample, spec_path: Path) -> Path:
    if sample is not None:
        return sample.paths.generated.get("convertedMbd", sample.paths.generated_dir / "from_spec.model.mbd.md")
    return spec_path.with_name("from_spec.model.mbd.md")


def _default_spec_mbd_viewer_path(sample, spec_path: Path) -> Path:
    if sample is not None:
        return sample.paths.generated.get("specMbdViewer", sample.paths.generated_dir / "spec_mbd_viewer.html")
    return spec_path.with_name("spec_mbd_viewer.html")


def _load_authoring_source(source: str):
    path = Path(source)
    if path.suffix == ".md" or path.name.endswith(".mbd.md"):
        return parse_markup_file(path)
    return load_model(path)
