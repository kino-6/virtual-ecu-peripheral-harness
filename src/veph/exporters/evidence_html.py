from __future__ import annotations

import re
from html import escape
from pathlib import Path

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
                "        <h3>Harness検証結果</h3>",
                "        <p>検証シナリオは未定義です。</p>",
                "      </section>",
            ]
        )
    body = "\n".join(_spec_verification_row(row) for row in rows)
    return "\n".join(
        [
            '      <section class="verification-summary">',
            "        <h3>Harness検証結果</h3>",
            "        <table class=\"review-table compact\">",
            "          <thead><tr><th>シナリオ</th><th>結果</th><th>最終状態</th><th>ステップ</th><th>主な確認</th><th>レポート</th></tr></thead>",
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
    return {
        "status": status,
        "final_state": final_state,
        "checks": checks,
        "steps": str(steps) if steps else "",
    }


def _regex_group(pattern: str, text: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1) if match else ""


def _report_section(text: str, start_heading: str, end_heading: str) -> str:
    pattern = rf"## {re.escape(start_heading)}\n(?P<body>.*?)\n## {re.escape(end_heading)}"
    match = re.search(pattern, text, re.DOTALL)
    return match.group("body") if match else ""


def _spec_verification_row(row: dict[str, object]) -> str:
    checks = row.get("checks", [])
    check_text = _ja_check_summary(checks) if isinstance(checks, list) else ""
    status = str(row.get("status", "未確認"))
    status_label = "PASS" if status == "PASS" else ("FAIL" if status == "FAIL" else "未確認")
    return (
        "          <tr>"
        f"<td>{escape(str(row.get('scenario', '')))}</td>"
        f"<td><strong>{escape(status_label)}</strong></td>"
        f"<td>{escape(str(row.get('final_state', '')))}</td>"
        f"<td>{escape(str(row.get('steps', '')))}</td>"
        f"<td>{escape(check_text or '確認項目なし')}</td>"
        f"<td><code>{escape(str(row.get('report', '')))}</code></td>"
        "</tr>"
    )


def _ja_check_summary(checks: list[object]) -> str:
    summaries: list[str] = []
    for check in checks[:3]:
        text = str(check)
        match = re.match(r"PASS finalState: actual ([^,]+), expected \1", text)
        if match:
            summaries.append(f"最終状態={match.group(1)}")
            continue
        match = re.match(r"PASS outputs\.([^:]+): actual ([^,]+), expected \2", text)
        if match:
            summaries.append(f"{match.group(1)}={match.group(2)}")
            continue
        summaries.append(text)
    return ", ".join(summaries)
