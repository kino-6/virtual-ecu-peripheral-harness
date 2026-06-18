from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


REQ_RE = re.compile(r"^- `(?P<id>[A-Z0-9]+-\d+)`(?: \(`(?P<class>DSC-[A-Z]+)`\))?: (?P<text>.*)$")
TRACE_ROW_RE = re.compile(r"^\| `(?P<start>[A-Z0-9]+-\d+)` - `(?P<end>[A-Z0-9]+-\d+)` \| (?P<evidence>.*?) \|$")


@dataclass(frozen=True)
class RequirementRecord:
    id: str
    statement: str
    section: str
    classification: str | None = None
    planned_evidence: str = ""


@dataclass(frozen=True)
class ExtractedRequirements:
    source_path: Path
    requirements: list[RequirementRecord]

    def by_id(self) -> dict[str, RequirementRecord]:
        return {item.id: item for item in self.requirements}


@dataclass(frozen=True)
class TraceabilityReport:
    passed: bool
    missing_spec_coverage: list[str]
    missing_mbd_coverage: list[str]
    untraced_mbd_behavior: list[str]
    findings: list[str]

    def to_markdown(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [
            "# Requirements Traceability Report",
            "",
            f"- Result: **{status}**",
            "",
            "## Findings",
            "",
        ]
        lines.extend(f"- {finding}" for finding in self.findings)
        lines.extend(["", "## Missing Spec Coverage", ""])
        lines.extend(_list_or_none(self.missing_spec_coverage))
        lines.extend(["", "## Missing MBD Coverage", ""])
        lines.extend(_list_or_none(self.missing_mbd_coverage))
        lines.extend(["", "## Untraced MBD Behavior", ""])
        lines.extend(_list_or_none(self.untraced_mbd_behavior))
        lines.append("")
        return "\n".join(lines)


def extract_requirements(path: str | Path) -> ExtractedRequirements:
    source_path = Path(path)
    lines = source_path.read_text(encoding="utf-8").splitlines()
    evidence_by_id = _parse_traceability_seed(lines)
    requirements: list[RequirementRecord] = []
    section = ""
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("## "):
            section = line.removeprefix("## ").strip()
            index += 1
            continue
        match = REQ_RE.match(line)
        if match is None:
            index += 1
            continue
        req_id = match.group("id")
        statement_lines = [match.group("text").strip()]
        index += 1
        while index < len(lines) and _is_continuation(lines[index]):
            statement_lines.append(lines[index].strip())
            index += 1
        requirements.append(
            RequirementRecord(
                id=req_id,
                classification=match.group("class"),
                statement=" ".join(statement_lines),
                section=section,
                planned_evidence=evidence_by_id.get(req_id, ""),
            )
        )
    return ExtractedRequirements(source_path=source_path, requirements=requirements)


def render_requirements_json(extracted: ExtractedRequirements) -> str:
    data = {
        "source": str(extracted.source_path),
        "requirements": [asdict(item) for item in extracted.requirements],
    }
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def generate_spec_scaffold(extracted: ExtractedRequirements) -> str:
    rows = [
        "| Requirement | Class | Source section | Statement | Planned evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for req in extracted.requirements:
        rows.append(
            f"| `{req.id}` | `{req.classification or ''}` | {req.section} | "
            f"{req.statement} | {req.planned_evidence or 'TBD'} |"
        )

    lines = [
        "# Specification Scaffold",
        "",
        f"Source requirements: `{_source_name(extracted.source_path)}`",
        "",
        "> Generated scaffold. Review and resolve open questions before using it",
        "> as approved MBD input.",
        "",
        "## Requirement Summary",
        "",
        *rows,
        "",
        "## Item Behavior",
        "",
        *_bullets_for_sections(extracted, {"System Requirements", "Stakeholder Needs"}),
        "",
        "## Software And Control Behavior",
        "",
        *_bullets_for_sections(extracted, {"Software Requirements", "Preview Engine Requirements"}),
        "",
        "## Harness And Test Behavior",
        "",
        *_bullets_for_sections(extracted, {"Harness Requirements", "MBD-To-C Process Requirements"}),
        "",
        "## MBD And Toolchain Behavior",
        "",
        *_bullets_for_sections(
            extracted,
            {
                "Mermaid-To-MBD Engine Requirements",
                "Requirements-To-Spec Support Requirements",
                "Requirements-To-MBD Support Requirements",
                "MBD IR Requirements",
                "MBD Handoff Requirements",
            },
        ),
        "",
        "## AI And RAG Behavior",
        "",
        *_bullets_for_sections(extracted, {"AI Development Efficiency Requirements", "RAG And Context Requirements"}),
        "",
        "## Open Questions",
        "",
        "Do not invent missing thresholds, timings, recovery rules, or fault semantics.",
        "",
        *_open_questions(extracted),
        "",
    ]
    return "\n".join(lines)


def generate_mbd_scaffold(extracted: ExtractedRequirements) -> str:
    system_refs = _ids_for_sections(extracted, {"System Requirements"})
    harness_refs = _ids_for_sections(extracted, {"Harness Requirements"})
    high_class_refs = [req.id for req in extracted.requirements if req.classification in {"DSC-B", "DSC-C"}]
    lines = [
        "# MBD Scaffold",
        "",
        "> Generated scaffold from requirements. Do not treat this scaffold as approved behavior",
        "> until open questions are reviewed.",
        "",
        "## Requirement Coverage Intent",
        "",
        *_coverage_intent_lines(extracted),
        "",
        "```mbd-component",
        "component ToyThermalProtectionController",
        f"trace {' '.join(system_refs[:8])}".rstrip(),
        "bus virtual mode=preview wordBits=16",
        "parameter TODO_highThreshold: degC = 0",
        "parameter TODO_lowThreshold: degC = 0",
        "parameter TODO_deratingLimit: percent = 0",
        "parameter TODO_safeCommand: percent = 0",
        "",
        "port in temperatureC: degC = 0",
        "port in temperatureValid: bool = true",
        "port out coolingCommand: percent = 0",
        "port out deratingCommand: percent = 0",
        "port out diagnosticFault: bool = false",
        "```",
        "",
        "```mbd-state",
        "RESET --> NOMINAL: open-question SYS-008 trace SYS-008",
        "NOMINAL --> COOLING: open-question threshold-high trace SYS-003",
        "COOLING --> DERATING: open-question derating-entry trace SYS-005",
        "DERATING --> FAULT_LATCHED: open-question persistent-invalid-sensor trace SYS-007",
        "FAULT_LATCHED --> NOMINAL: open-question recovery-conditions trace SYS-008",
        "```",
        "",
        "```mbd-flow",
        "ToyTempSensorIC.temperatureC -> HAL_SPI.read_temperature: virtual sensor sample trace SYS-001 HAR-001",
        "HAL_SPI.read_temperature -> ToyThermalProtectionController.temperatureC: HAL input trace SWE-004 HAR-002",
        "ToyThermalProtectionController.coolingCommand -> HAL_PWM.set_cooling: virtual actuator command trace SYS-002 HAR-001",
        "ToyThermalProtectionController.deratingCommand -> ToyLoadLimiterIC.limit: virtual load limiter command trace SYS-005 HAR-006",
        "```",
        "",
        "```mbd-control",
        "rule TODO_sensorFault: when temperatureValid == false then diagnosticFault=true trace SYS-006 SYS-007",
        "rule TODO_highTemperature: when temperatureC >= TODO_highThreshold then coolingCommand=TODO trace SYS-003",
        "rule TODO_derating: when temperatureC >= TODO_deratingEntry then deratingCommand=TODO trace SYS-005",
        "```",
        "",
        "```mbd-harness",
        f"device ToyTempSensorIC role=sensor boundary=virtual_ic trace {' '.join(_matching_refs(harness_refs, ['HAR-001', 'HAR-006']))}",
        "device ToyFanDriverIC role=actuator boundary=virtual_ic trace HAR-001",
        "device ToyLoadLimiterIC role=actuator boundary=virtual_ic trace HAR-006",
        "ecu ToyThermalProtectionController role=controller boundary=hal trace HAR-002 SWE-004",
        "```",
        "",
        "## Open Questions",
        "",
        "Do not invent missing thresholds, timings, recovery rules, or fault semantics.",
        "",
    ]
    for req_id in high_class_refs:
        lines.append(f"- open-question {req_id}: define explicit state/control/harness/scenario/expected behavior coverage.")
    lines.append("")
    return "\n".join(lines)


def validate_traceability(
    extracted: ExtractedRequirements,
    spec_text: str,
    mbd_text: str,
) -> TraceabilityReport:
    missing_spec = [req.id for req in extracted.requirements if f"`{req.id}`" not in spec_text and req.id not in spec_text]
    missing_mbd = [req.id for req in extracted.requirements if _requires_mbd_coverage(req) and req.id not in mbd_text]
    untraced = _find_untraced_mbd_behavior(mbd_text)
    findings: list[str] = []
    if missing_spec:
        findings.append(f"FAIL missing spec coverage for {len(missing_spec)} requirement(s)")
    if missing_mbd:
        findings.append(f"FAIL missing MBD coverage for {len(missing_mbd)} requirement(s)")
    if untraced:
        findings.append(f"FAIL untraced MBD behavior found: {len(untraced)} line(s)")
    if not findings:
        findings.append("PASS all extracted requirements have required scaffold coverage")
    return TraceabilityReport(
        passed=not missing_spec and not missing_mbd and not untraced,
        missing_spec_coverage=missing_spec,
        missing_mbd_coverage=missing_mbd,
        untraced_mbd_behavior=untraced,
        findings=findings,
    )


def _parse_traceability_seed(lines: list[str]) -> dict[str, str]:
    evidence: dict[str, str] = {}
    for line in lines:
        match = TRACE_ROW_RE.match(line.strip())
        if match is None:
            continue
        for req_id in _expand_range(match.group("start"), match.group("end")):
            evidence[req_id] = match.group("evidence").strip()
    return evidence


def _expand_range(start: str, end: str) -> list[str]:
    start_prefix, start_number = start.rsplit("-", 1)
    end_prefix, end_number = end.rsplit("-", 1)
    if start_prefix != end_prefix:
        return [start, end]
    width = max(len(start_number), len(end_number))
    return [f"{start_prefix}-{number:0{width}d}" for number in range(int(start_number), int(end_number) + 1)]


def _is_continuation(line: str) -> bool:
    return bool(line.startswith("  ") and line.strip() and not line.lstrip().startswith("- `"))


def _source_name(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def _bullets_for_sections(extracted: ExtractedRequirements, sections: set[str]) -> list[str]:
    items = [
        f"- `{req.id}`{f' (`{req.classification}`)' if req.classification else ''}: {req.statement}"
        for req in extracted.requirements
        if req.section in sections
    ]
    return items or ["- No requirements extracted for this section."]


def _open_questions(extracted: ExtractedRequirements) -> list[str]:
    questions: list[str] = []
    for req in extracted.requirements:
        if req.classification in {"DSC-B", "DSC-C"}:
            questions.append(
                f"- `{req.id}`: confirm threshold/timing/recovery/fault semantics and required scenario evidence."
            )
    return questions or ["- No high-class open questions generated."]


def _ids_for_sections(extracted: ExtractedRequirements, sections: set[str]) -> list[str]:
    return [req.id for req in extracted.requirements if req.section in sections]


def _coverage_intent_lines(extracted: ExtractedRequirements) -> list[str]:
    lines = []
    for req in extracted.requirements:
        if _requires_mbd_coverage(req):
            lines.append(f"- `{req.id}`: scaffold coverage required; refine into concrete model element before approval.")
    return lines or ["- No MBD coverage requirements extracted."]


def _matching_refs(refs: Iterable[str], wanted: list[str]) -> list[str]:
    ref_set = set(refs)
    return [ref for ref in wanted if ref in ref_set]


def _requires_mbd_coverage(req: RequirementRecord) -> bool:
    return req.section in {
        "System Requirements",
        "Software Requirements",
        "Harness Requirements",
        "Preview Engine Requirements",
        "MBD-To-C Process Requirements",
    } or req.classification in {"DSC-B", "DSC-C"}


def _find_untraced_mbd_behavior(mbd_text: str) -> list[str]:
    untraced: list[str] = []
    for raw_line in mbd_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith(">") or line.startswith("```"):
            continue
        behavior_like = line.startswith("rule ") or "-->" in line or " -> " in line
        if behavior_like and "trace " not in line:
            untraced.append(line)
    return untraced


def _list_or_none(items: list[str]) -> list[str]:
    return [f"- `{item}`" for item in items] if items else ["- None"]
