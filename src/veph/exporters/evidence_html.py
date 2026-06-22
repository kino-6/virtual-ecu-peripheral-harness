from __future__ import annotations

import re
from html import escape
from pathlib import Path

import yaml

from veph.ir import MbdModelIR


def spec_verification_data(model: MbdModelIR, spec: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for scenario, report in spec.get("scenarios", []):
        report_path = _resolve_report_path(model, str(report))
        row: dict[str, object] = {
            "scenario": str(scenario),
            "report": str(report),
            "status": "未確認",
            "final_state": "",
            "checks": [],
            "steps": "",
        }
        if report_path is not None and report_path.exists():
            text = report_path.read_text(encoding="utf-8")
            row.update(_parse_preview_report_summary(text))
        rows.append(row)
    return rows


def spec_verification_summary_html(rows: list[dict[str, object]]) -> str:
    if not rows:
        return "\n".join(
            [
                '      <section class="verification-summary">',
                "        <h3>Harnessテスト要約</h3>",
                "        <p>Harnessはpreview証跡です。正式検証は外部MBD環境で行います。</p>",
                "        <p>検証シナリオは未定義です。</p>",
                "      </section>",
            ]
        )
    body = "\n".join(_spec_verification_rows(row) for row in rows)
    return "\n".join(
        [
            '      <section class="verification-summary">',
            "        <h3>Harnessテスト要約</h3>",
            "        <p>preview証跡。制御判断はMBD source側。</p>",
            "        <table class=\"review-table compact\">",
            "          <thead><tr><th>テスト</th><th>刺激</th><th>期待</th><th>判定</th></tr></thead>",
            "          <tbody>",
            body,
            "          </tbody>",
            "        </table>",
            "      </section>",
        ]
    )


def _resolve_report_path(model: MbdModelIR, report: str) -> Path | None:
    report_path = Path(report)
    if report_path.is_absolute():
        return report_path
    source_dir = model.source_path.parent
    candidates = [
        source_dir / report_path,
        source_dir.parent / report_path,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[-1] if candidates else None


def _parse_preview_report_summary(text: str) -> dict[str, object]:
    status = _regex_group(r"- Result: \*\*(PASS|FAIL)\*\*", text) or "未確認"
    final_state = _regex_group(r"- Final state: `([^`]+)`", text) or ""
    checks = re.findall(r"^- ((?:PASS|FAIL) [^\n]+)$", text, re.MULTILINE)
    scenario_steps = _report_section(text, "Scenario Steps", "Harness Boundary Evidence")
    steps = len(re.findall(r"^\s*-\s*atMs:", scenario_steps, re.MULTILINE))
    observed = _yaml_section(text, "Observed Behavior")
    expected = _yaml_section(text, "Expected Behavior")
    preview_steps = _yaml_section(text, "Per-Step Preview Execution")
    return {
        "status": status,
        "final_state": final_state,
        "checks": checks,
        "observed": observed,
        "expected_behavior": expected,
        "preview_steps": preview_steps,
        "scenario_steps": _safe_yaml_load(scenario_steps, []),
        "steps": str(steps) if steps else "",
    }


def _regex_group(pattern: str, text: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1) if match else ""


def _report_section(text: str, start_heading: str, end_heading: str) -> str:
    pattern = rf"## {re.escape(start_heading)}\n(?P<body>.*?)\n## {re.escape(end_heading)}"
    match = re.search(pattern, text, re.DOTALL)
    return match.group("body") if match else ""


def _yaml_section(text: str, heading: str) -> object:
    pattern = rf"## {re.escape(heading)}\n\n```yaml\n(?P<body>.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    return _safe_yaml_load(match.group("body"), {}) if match else {}


def _safe_yaml_load(text: str, fallback: object) -> object:
    cleaned = text.strip()
    if cleaned.startswith("```yaml"):
        cleaned = cleaned.removeprefix("```yaml").strip()
    if cleaned.endswith("```"):
        cleaned = cleaned.removesuffix("```").strip()
    if not cleaned:
        return fallback
    try:
        loaded = yaml.safe_load(cleaned)
    except yaml.YAMLError:
        return fallback
    return fallback if loaded is None else loaded


def _spec_verification_rows(row: dict[str, object]) -> str:
    preview_steps = row.get("preview_steps")
    if isinstance(preview_steps, list) and preview_steps:
        return "\n".join(
            _spec_verification_step_row(row, step, index)
            for index, step in enumerate(preview_steps)
        )
    return _spec_verification_summary_row(row)


def _spec_verification_summary_row(row: dict[str, object]) -> str:
    status = str(row.get("status", "未確認"))
    status_label = "PASS" if status == "PASS" else ("FAIL" if status == "FAIL" else "未確認")
    return (
        "          <tr>"
        f"<td>{escape(str(row.get('scenario', '')))}</td>"
        f"<td>{escape(_stimulus_summary(row))}</td>"
        f"<td>{escape(_expected_summary(row))}</td>"
        f"<td><strong>{escape(status_label)}</strong></td>"
        "</tr>"
    )


def _spec_verification_step_row(row: dict[str, object], step: object, index: int) -> str:
    status = str(row.get("status", "未確認"))
    status_label = "PASS" if status == "PASS" else ("FAIL" if status == "FAIL" else "未確認")
    scenario = str(row.get("scenario", "")) if index == 0 else ""
    return (
        "          <tr>"
        f"<td>{escape(scenario)}</td>"
        f"<td>{escape(_step_stimulus(step))}</td>"
        f"<td>{escape(_step_expected(step))}</td>"
        f"<td><strong>{escape(status_label)}</strong></td>"
        "</tr>"
    )


def _stimulus_summary(row: dict[str, object]) -> str:
    steps = row.get("scenario_steps")
    if not isinstance(steps, list):
        return ""
    values: list[str] = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        set_input = step.get("setInput")
        if not isinstance(set_input, dict):
            continue
        name = str(set_input.get("name", ""))
        value = _format_value(set_input.get("value"))
        values.append(f"{name}={value}" if name else value)
    return " -> ".join(values)


def _expected_summary(row: dict[str, object]) -> str:
    parts: list[str] = []
    expected = row.get("expected_behavior")
    if isinstance(expected, dict):
        final_state = expected.get("finalState") or row.get("final_state")
        if final_state:
            parts.append(f"final={_format_value(final_state)}")
        outputs = expected.get("outputs")
        if isinstance(outputs, dict):
            parts.append(", ".join(f"{name}={_format_value(value)}" for name, value in outputs.items()))
    if not parts:
        checks = row.get("checks", [])
        if isinstance(checks, list):
            parts.append(_check_summary(checks))
    return "; ".join(part for part in parts if part)


def _step_stimulus(step: object) -> str:
    if not isinstance(step, dict):
        return ""
    scenario_input = step.get("scenarioInput")
    if not isinstance(scenario_input, dict):
        return ""
    name = str(scenario_input.get("name", ""))
    value = _format_value(scenario_input.get("value"))
    return f"{name}={value}" if name else value


def _step_expected(step: object) -> str:
    if not isinstance(step, dict):
        return ""
    before = step.get("before")
    after = step.get("after")
    before_state = before.get("state") if isinstance(before, dict) else ""
    after_state = after.get("state") if isinstance(after, dict) else ""
    transition = (
        f"{_format_value(before_state)}保持"
        if before_state == after_state
        else f"{_format_value(before_state)}->{_format_value(after_state)}"
    )
    outputs = after.get("outputs") if isinstance(after, dict) else {}
    output_text = _mapping_summary(outputs) if isinstance(outputs, dict) else ""
    return f"{transition}; {output_text}" if output_text else transition


def _mapping_summary(values: dict[object, object]) -> str:
    return ", ".join(f"{name}={_format_value(value)}" for name, value in values.items())


def _check_summary(checks: list[object]) -> str:
    summaries: list[str] = []
    for check in checks[:3]:
        text = str(check)
        match = re.match(r"PASS finalState: actual ([^,]+), expected \1", text)
        if match:
            summaries.append(f"final={match.group(1)}")
            continue
        match = re.match(r"PASS outputs\.([^:]+): actual ([^,]+), expected \2", text)
        if match:
            summaries.append(f"{match.group(1)}={match.group(2)}")
            continue
        summaries.append(text)
    return ", ".join(summaries)


def _format_value(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)
