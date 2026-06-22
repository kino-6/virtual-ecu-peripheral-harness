from __future__ import annotations

import re
from html import escape
from pathlib import Path

import yaml

from veph.control_semantics import find_threshold_pair
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
            row["test_type"] = _test_type(model)
            row["stimulus"] = _stimulus_summary(row)
            row["expected"] = _expected_summary(model, row)
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
    body = "\n".join(_spec_verification_row(row) for row in rows)
    return "\n".join(
        [
            '      <section class="verification-summary">',
            "        <h3>Harnessテスト要約</h3>",
            "        <p>Harnessはpreview証跡です。制御判断はMBD source側の責務です。</p>",
            "        <table class=\"review-table compact\">",
            "          <thead><tr><th>テスト</th><th>型</th><th>刺激</th><th>期待</th><th>判定</th><th>証跡</th></tr></thead>",
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
    return {
        "status": status,
        "final_state": final_state,
        "checks": checks,
        "observed": observed,
        "expected_behavior": expected,
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


def _spec_verification_row(row: dict[str, object]) -> str:
    status = str(row.get("status", "未確認"))
    status_label = "PASS" if status == "PASS" else ("FAIL" if status == "FAIL" else "未確認")
    return (
        "          <tr>"
        f"<td>{escape(str(row.get('scenario', '')))}</td>"
        f"<td>{escape(str(row.get('test_type', 'シナリオ')))}</td>"
        f"<td>{escape(str(row.get('stimulus', '')))}</td>"
        f"<td>{escape(str(row.get('expected', '')))}</td>"
        f"<td><strong>{escape(status_label)}</strong></td>"
        f"<td><code>{escape(str(row.get('report', '')))}</code></td>"
        "</tr>"
    )


def _test_type(model: MbdModelIR) -> str:
    if find_threshold_pair(model.controls) is not None or any(
        "threshold" in name.lower() for name in model.component.parameters
    ):
        return "閾値/ヒステリシス"
    if model.transitions:
        return "状態遷移"
    return "信号判定"


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


def _expected_summary(model: MbdModelIR, row: dict[str, object]) -> str:
    parts: list[str] = []
    path = _transition_path(model, row)
    if path:
        parts.append(path)
    if _test_type(model) == "閾値/ヒステリシス":
        thresholds = _threshold_summary(model)
        if thresholds:
            parts.append(thresholds)
        if _step_count(row) > _applied_rule_count(row):
            parts.append("中間保持含む")
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


def _transition_path(model: MbdModelIR, row: dict[str, object]) -> str:
    observed = row.get("observed")
    if not isinstance(observed, dict):
        return _transition_path_from_model(model, _step_count(row))
    applied_rules = observed.get("appliedRules")
    if not isinstance(applied_rules, list):
        return _transition_path_from_model(model, _step_count(row))
    controls = {control.name: control for control in model.controls}
    states: list[str] = []
    for name in applied_rules:
        control = controls.get(str(name))
        if control is None:
            continue
        target = control.actions.get("state", "")
        if not target:
            continue
        if not states:
            states.append(control.state_scope)
        states.append(target)
    return "->".join(states) if states else _transition_path_from_model(model, len(applied_rules))


def _transition_path_from_model(model: MbdModelIR, limit: int) -> str:
    transitions = model.transitions[:limit] if limit > 0 else model.transitions
    states: list[str] = []
    for transition in transitions:
        if transition.source == "[*]":
            continue
        if not states:
            states.append(transition.source)
        states.append(transition.target)
    return "->".join(states)


def _threshold_summary(model: MbdModelIR) -> str:
    threshold_names = [name for name in model.component.parameters if "threshold" in name.lower()]
    if threshold_names:
        return ", ".join(
            f"{name}={model.component.parameters[name].default}" for name in threshold_names
        )
    pair = find_threshold_pair(model.controls)
    if pair is None:
        return ""
    names = [
        name
        for name in model.component.parameters
        if any(name in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", control.condition) for control in pair)
    ]
    if not names:
        return ""
    return ", ".join(f"{name}={model.component.parameters[name].default}" for name in names)


def _step_count(row: dict[str, object]) -> int:
    steps = row.get("scenario_steps")
    return len(steps) if isinstance(steps, list) else 0


def _applied_rule_count(row: dict[str, object]) -> int:
    observed = row.get("observed")
    applied = observed.get("appliedRules") if isinstance(observed, dict) else []
    return len(applied) if isinstance(applied, list) else 0


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
