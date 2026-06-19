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
from veph.markup_parser import MarkupParseError, parse_markup_file
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
from veph.scenario_runner import ScenarioError, run_scenario_file


Exporter = Callable[[object], str]


@dataclass(frozen=True)
class ExportCommand:
    exporter: Callable
    help: str
    source_required: bool = True
    out_required: bool = True


EXPORT_COMMANDS = {
    "export-docs": ExportCommand(export_markdown, "export Markdown documentation"),
    "export-demo": ExportCommand(export_demo_html, "export static HTML MBD visualization demo"),
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
        ScenarioError,
        PreviewScenarioError,
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


def _load_authoring_source(source: str):
    path = Path(source)
    if path.suffix == ".md" or path.name.endswith(".mbd.md"):
        return parse_markup_file(path)
    return load_model(path)
