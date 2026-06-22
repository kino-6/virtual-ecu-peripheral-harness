from __future__ import annotations

from pathlib import Path

from veph.spec_dataflow import arithmetic_specs
from veph.spec_dataflow_mbd_generation import generate_arithmetic_dataflow_mbd_from_spec
from veph.spec_decision_mbd_generation import (
    decision_specs,
    generate_decision_mbd_from_spec,
)
from veph.spec_mbd_text import (
    display_path as _display_path,
    requirement_ids as _requirement_ids,
    title as _title,
)
from veph.spec_state_mbd_generation import generate_state_machine_mbd_from_spec
from veph.spec_state_model import parse_spec_state_diagram
from veph.spec_mbd_alignment import (
    SpecMbdAlignmentError,
    parse_spec_design_overview_flowchart,
    spec_uses_layered_design_views,
)


def generate_mbd_from_spec(
    spec_path: str | Path,
    *,
    component_name: str,
    parameter_defaults: dict[str, str] | None = None,
    input_defaults: dict[str, str] | None = None,
    output_defaults: dict[str, str] | None = None,
    scenario: str = "",
) -> str:
    spec = Path(spec_path)
    flowchart = parse_spec_design_overview_flowchart(spec)
    transitions = parse_spec_state_diagram(spec)
    requirements = _requirement_ids(spec)
    flow_source = _flow_source_description(spec)
    state_source = _state_source_description(spec)
    decisions = decision_specs(flowchart)
    if not decisions:
        arithmetic_blocks = arithmetic_specs(flowchart)
        if arithmetic_blocks:
            return generate_arithmetic_dataflow_mbd_from_spec(
                spec,
                flowchart=flowchart,
                blocks=arithmetic_blocks,
                requirements=requirements,
                component_name=component_name,
                parameter_defaults=parameter_defaults or {},
                input_defaults=input_defaults or {},
                output_defaults=output_defaults or {},
                scenario=scenario,
                generated_header=_generated_header(spec, flow_source),
                component_header=_component_header(component_name, " ".join(requirements)),
            )
        if transitions:
            return generate_state_machine_mbd_from_spec(
                spec,
                flowchart=flowchart,
                transitions=transitions,
                requirements=requirements,
                component_name=component_name,
                parameter_defaults=parameter_defaults or {},
                input_defaults=input_defaults or {},
                output_defaults=output_defaults or {},
                scenario=scenario,
                generated_header=_generated_header(spec, f"{flow_source} and {state_source}"),
                component_header=_component_header(component_name, " ".join(requirements)),
            )
        raise SpecMbdAlignmentError(f"no supported decision or state-machine node found in {spec}")

    return generate_decision_mbd_from_spec(
        flowchart=flowchart,
        transitions=transitions,
        requirements=requirements,
        decisions=decisions,
        component_name=component_name,
        parameter_defaults=parameter_defaults or {},
        input_defaults=input_defaults or {},
        output_defaults=output_defaults or {},
        scenario=scenario,
        generated_header=_generated_header(spec, flow_source),
        component_header=_component_header(component_name, " ".join(requirements)),
    )


def _generated_header(spec: Path, source_description: str) -> list[str]:
    return [
        f"# {_title(spec)}",
        "",
        f"Generated from {source_description} in `{_display_path(spec)}`.",
        "This file is deterministic authoring source for generated MBD review artifacts.",
        "",
    ]

def _component_header(component_name: str, trace_all: str) -> list[str]:
    return [
        "```mbd-component",
        f"component {component_name}",
        f"trace {trace_all}".rstrip(),
        "bus virtual mode=preview wordBits=8",
    ]


def _flow_source_description(spec: Path) -> str:
    if spec_uses_layered_design_views(spec):
        return "Spec Data Flow View"
    return "Spec Mermaid Design Overview"


def _state_source_description(spec: Path) -> str:
    if spec_uses_layered_design_views(spec):
        return "Control Semantics View"
    return "stateDiagram-v2"
