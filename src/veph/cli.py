from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from veph.exporters.markdown import export_markdown
from veph.exporters.demo_html import export_demo_html
from veph.exporters.modelica import export_modelica
from veph.exporters.plantuml import export_plantuml
from veph.exporters.scxml import export_scxml
from veph.exporters.simulink_m import export_simulink_m
from veph.model_loader import ModelValidationError, load_model
from veph.scenario_runner import ScenarioError, run_scenario_file


Exporter = Callable[[object], str]


@dataclass(frozen=True)
class ExportCommand:
    exporter: Callable
    help: str
    model_required: bool = True
    out_required: bool = True


EXPORT_COMMANDS = {
    "export-docs": ExportCommand(export_markdown, "export Markdown documentation"),
    "export-demo": ExportCommand(export_demo_html, "export static HTML MBD visualization demo"),
    "export-plantuml": ExportCommand(export_plantuml, "export PlantUML state diagram"),
    "export-scxml": ExportCommand(export_scxml, "export SCXML state machine"),
    "export-modelica": ExportCommand(export_modelica, "export Modelica text model"),
    "export-simulink-m": ExportCommand(export_simulink_m, "export MATLAB/Simulink .m script"),
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except (ModelValidationError, ScenarioError, OSError) as exc:
        parser.exit(1, f"error: {exc}\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m veph", description="Textual MBD virtual ECU harness")
    subparsers = parser.add_subparsers(required=True)

    validate = subparsers.add_parser("validate", help="validate a Textual MBD model")
    validate.add_argument("model")
    validate.set_defaults(func=_validate)

    run = subparsers.add_parser("run", help="run a scenario against a model")
    run.add_argument("--model", required=True)
    run.add_argument("--scenario", required=True)
    run.add_argument("--report", required=True)
    run.set_defaults(func=_run)

    for name, command in EXPORT_COMMANDS.items():
        _add_export(subparsers, name, command)
    return parser


def _add_export(
    subparsers: argparse._SubParsersAction,
    name: str,
    command: ExportCommand,
) -> None:
    subcommand = subparsers.add_parser(name, help=command.help)
    subcommand.add_argument("--model", required=command.model_required)
    subcommand.add_argument("--out", required=command.out_required)
    subcommand.set_defaults(func=lambda args, exporter=command.exporter: _export(args, exporter))


def _validate(args: argparse.Namespace) -> None:
    model = load_model(args.model)
    print(f"valid: {model.name}")


def _run(args: argparse.Namespace) -> None:
    model = load_model(args.model)
    result = run_scenario_file(model, args.scenario, args.report)
    print(f"{result.name}: {'PASS' if result.passed else 'FAIL'}")


def _export(args: argparse.Namespace, exporter: Callable) -> None:
    model = load_model(args.model)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(exporter(model), encoding="utf-8")
    print(f"wrote {output}")
