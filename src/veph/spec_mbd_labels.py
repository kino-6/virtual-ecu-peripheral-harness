from __future__ import annotations

import re

from veph.spec_mbd_alignment import MermaidNode, SpecMbdAlignmentError


OUTPUT_RE = re.compile(r"^Output\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.+)$")
OUTPUT_PORT_RE = re.compile(r"^Output\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)(?P<vector>\[\d+\])?$")
INPUT_RE = re.compile(r"^Input Port:\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)(?P<vector>\[\d+\])?$")
PARAMETER_RE = re.compile(r"^Parameter:\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)$")
CONSTANT_RE = re.compile(r"^Constant:\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.+)$")
ARITHMETIC_OPERATORS = {"Gain", "Sum", "Product", "Saturation", "Lookup1D"}


def is_input(node: MermaidNode) -> bool:
    return INPUT_RE.match(node.label) is not None


def is_parameter(node: MermaidNode) -> bool:
    return PARAMETER_RE.match(node.label) is not None


def is_constant(node: MermaidNode) -> bool:
    return CONSTANT_RE.match(node.label) is not None


def is_arithmetic(node: MermaidNode) -> bool:
    return operator_label(node) in ARITHMETIC_OPERATORS


def is_output(node: MermaidNode) -> bool:
    return OUTPUT_RE.match(node.label) is not None


def is_output_port(node: MermaidNode) -> bool:
    return OUTPUT_PORT_RE.match(node.label) is not None


def is_report(node: MermaidNode) -> bool:
    return node.label.startswith("ScenarioReport.")


def input_name(node: MermaidNode) -> str:
    match = INPUT_RE.match(node.label)
    if match is None:
        raise SpecMbdAlignmentError(f"not an input port node: {node.label}")
    return match.group("name")


def output_port_name(node: MermaidNode) -> str:
    match = OUTPUT_PORT_RE.match(node.label)
    if match is None:
        raise SpecMbdAlignmentError(f"not an output port node: {node.label}")
    return match.group("name")


def parameter_name(node: MermaidNode) -> str:
    match = PARAMETER_RE.match(node.label)
    if match is None:
        raise SpecMbdAlignmentError(f"not a parameter node: {node.label}")
    return match.group("name")


def constant_name(node: MermaidNode) -> str:
    match = CONSTANT_RE.match(node.label)
    if match is None:
        raise SpecMbdAlignmentError(f"not a constant node: {node.label}")
    return match.group("name")


def constant_value(node: MermaidNode) -> str:
    match = CONSTANT_RE.match(node.label)
    if match is None:
        raise SpecMbdAlignmentError(f"not a constant node: {node.label}")
    return match.group("value").strip()


def output_action(node: MermaidNode) -> tuple[str, str]:
    match = OUTPUT_RE.match(node.label)
    if match is None:
        raise SpecMbdAlignmentError(f"not an output action node: {node.label}")
    return match.group("name"), match.group("value").strip()


def operator_label(node: MermaidNode) -> str:
    return node.label.rsplit("/", 1)[-1]


def node_port_type(node: MermaidNode, default: str) -> str:
    vector = vector_suffix(node)
    return f"{port_type(default)}{vector}"


def port_type(default: str) -> str:
    return "bool" if default in {"true", "false"} else "count"


def vector_suffix(node: MermaidNode) -> str:
    for pattern in (INPUT_RE, OUTPUT_PORT_RE):
        match = pattern.match(node.label)
        if match is not None:
            return match.group("vector") or ""
    return ""
