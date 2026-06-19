from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


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
    approval_pending: list[str]
    findings: list[str]

    def to_markdown(self) -> str:
        coverage_status = "PASS" if self.passed else "FAIL"
        approval_status = "PENDING" if self.approval_pending else "READY FOR REVIEW"
        lines = [
            "# Requirements Traceability Report",
            "",
            f"- Coverage result: **{coverage_status}**",
            f"- Behavior approval: **{approval_status}**",
            "- Scope: scaffold trace coverage only; not a safety case, tool qualification, or production approval.",
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
        lines.extend(["", "## Approval Pending Items", ""])
        lines.extend(_plain_list_or_none(self.approval_pending))
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
    lines = [
        "# Specification Scaffold",
        "",
        f"Source requirements: `{_source_name(extracted.source_path)}`",
        "",
        "> Generated scaffold. This scaffold is not an approved specification.",
        "> Resolve open questions before using it as approved MBD input.",
        "",
        "## Review Status",
        "",
        "- Behavior approval: **PENDING**",
        "- Coverage meaning: requirement IDs are preserved for review; behavior is not approved by trace presence alone.",
        "- Demo role: business-process demo for requirements, MBD handoff, harness preview, generated C preview, and reports.",
        "- Tool boundary: repo-local execution is preview-only; existing MBD/product-test infrastructure remains the verification backend.",
        "",
        "## Demo Assumption Policy",
        "",
        "- The demo may use fictional component names and fictional requirement classes already stated in `Requirements.md`.",
        "- The demo may generate scaffolds, TODO placeholders, trace tables, and review questions from the requirements.",
        "- The demo must not invent accepted threshold values, timings, recovery conditions, fault semantics, or pass criteria.",
        "- Missing behavior must remain visible as `TODO` or `open-question` until reviewed.",
        "",
        "## Review Path",
        "",
        "1. Review `Requirements.md` for stakeholder and system intent.",
        "2. Review this scaffold for grouped behavior and unresolved decisions.",
        "3. Approve or revise the missing behavior before accepting generated MBD source.",
        "4. Regenerate MBD IR, handoff artifacts, preview C, scenarios, and reports from the approved source.",
        "5. Use external MBD/product-test infrastructure for production-grade verification.",
        "",
        "## Open Questions",
        "",
        "Do not invent missing thresholds, timings, recovery rules, or fault semantics.",
        "",
        *_open_questions(extracted),
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
        "## Requirement Trace Appendix",
        "",
        *_requirement_table_rows(extracted),
        "",
    ]
    return "\n".join(lines)


def generate_mbd_scaffold(extracted: ExtractedRequirements) -> str:
    system_refs = _ids_for_sections(extracted, {"System Requirements"})
    high_class_refs = [req.id for req in extracted.requirements if req.classification in {"DSC-B", "DSC-C"}]
    lines = [
        "# MBD Scaffold",
        "",
        "> Generated sample-neutral scaffold from requirements. Do not treat this scaffold as approved behavior",
        "> until open questions are reviewed and sample-specific boundaries are selected.",
        "",
        "## Review Status",
        "",
        "- Behavior approval: **PENDING**",
        "- Coverage meaning: traces identify intended coverage, not accepted model semantics.",
        "- TODO values are explicit placeholders, not accepted demo answers.",
        "- Sample policy: this common scaffold does not choose a controller, IC, signal set, threshold, or scenario.",
        "- External MBD/product-test infrastructure is still required for production-grade verification.",
        "",
        "## Requirement Coverage Intent",
        "",
        *_coverage_intent_lines(extracted),
        "",
        "```mbd-component",
        "component TODO_ComponentName",
        f"trace {' '.join(system_refs[:8])}".rstrip(),
        "bus virtual mode=preview wordBits=TODO",
        "parameter TODO_parameterName: TODO_unit = TODO_value",
        "",
        "port in TODO_inputSignal: TODO_type = TODO_default",
        "port out TODO_outputSignal: TODO_type = TODO_default",
        "```",
        "",
        "```mbd-state",
        "# Add state transitions only after behavior is approved.",
        "# Example shape: TODO_Source --> TODO_Target: TODO_condition trace TODO_REQ",
        "```",
        "",
        "```mbd-flow",
        "# Add data flows after component and harness boundaries are approved.",
        "# Example shape: TODO_Source.signal -> TODO_Target.signal: TODO_purpose trace TODO_REQ",
        "```",
        "",
        "```mbd-control",
        "# Add priority-ordered control rules after behavior is approved.",
        "# Example shape: priority TODO rule TODO_name: owner TODO_Owner from * when TODO_condition then TODO_action=TODO_value trace TODO_REQ",
        "```",
        "",
        "```mbd-harness",
        "# Add virtual IC and ECU boundaries after the sample boundary is approved.",
        "# Example shape: device TODO_Device role=TODO_role boundary=virtual_ic trace TODO_REQ",
        "# Example shape: ecu TODO_Controller role=controller boundary=hal trace TODO_REQ",
        "```",
        "",
        "## Open Questions",
        "",
        "Do not invent missing thresholds, timings, recovery rules, component names, IC roles, or fault semantics.",
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
        findings.append("PASS scaffold trace coverage exists for extracted requirements")
    approval_pending = _find_approval_pending(spec_text, mbd_text)
    if approval_pending:
        findings.append(
            f"PENDING behavior approval: {len(approval_pending)} open question or TODO item(s) remain"
        )
    return TraceabilityReport(
        passed=not missing_spec and not missing_mbd and not untraced,
        missing_spec_coverage=missing_spec,
        missing_mbd_coverage=missing_mbd,
        untraced_mbd_behavior=untraced,
        approval_pending=approval_pending,
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


def _requirement_table_rows(extracted: ExtractedRequirements) -> list[str]:
    rows = [
        "| Requirement | Class | Source section | Statement | Planned evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for req in extracted.requirements:
        rows.append(
            f"| `{req.id}` | `{req.classification or ''}` | {req.section} | "
            f"{req.statement} | {req.planned_evidence or 'TBD'} |"
        )
    return rows


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


def _find_approval_pending(spec_text: str, mbd_text: str) -> list[str]:
    pending: list[str] = []
    for raw_line in (spec_text + "\n" + mbd_text).splitlines():
        line = raw_line.strip()
        if not line:
            continue
        is_spec_open_question = (
            line.startswith("- `SYS-")
            and "confirm threshold/timing/recovery/fault semantics" in line
        )
        is_mbd_open_question = line.startswith("- open-question") or (
            "--> " in line and "open-question" in line
        )
        is_mbd_todo = line.startswith("parameter TODO") or line.startswith("rule TODO")
        has_pending_marker = is_spec_open_question or is_mbd_open_question or is_mbd_todo
        display_line = line.removeprefix("- ").strip()
        if has_pending_marker and display_line not in pending:
            pending.append(display_line)
    return pending


def _list_or_none(items: list[str]) -> list[str]:
    return [f"- `{item}`" for item in items] if items else ["- None"]


def _plain_list_or_none(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items] if items else ["- None"]
