from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape


@dataclass(frozen=True)
class ReviewQualityReport:
    passed: bool
    issues: tuple[str, ...]


ONE_MINUTE_MARKERS = ("1分レビュー", "One-Minute Review")
HARNESS_MARKERS = ("Harnessテスト要約", "Harness検証結果", "Harness Evidence", "Harness Boundary Evidence")
PASS_MARKERS = ("<strong>PASS</strong>", "Alignment: PASS", "Result: **PASS**")
DENSE_FIRST_READ_MARKERS = ("機能:", "信号線:", "Harness:", "Matched edges")


def evaluate_review_html(
    html: str,
    *,
    require_harness: bool = False,
    max_one_minute_text_chars: int = 900,
) -> ReviewQualityReport:
    issues: list[str] = []
    marker_position = _first_position(html, ONE_MINUTE_MARKERS)
    if marker_position < 0:
        issues.append("missing one-minute review marker")
    elif marker_position > 12000:
        issues.append("one-minute review appears too late in the HTML")

    if _first_position(html, PASS_MARKERS) < 0:
        issues.append("missing early PASS/alignment marker")

    if require_harness:
        harness_position = _first_position(html, HARNESS_MARKERS)
        if harness_position < 0:
            issues.append("missing Harness evidence marker")
        elif marker_position >= 0 and harness_position < marker_position:
            issues.append("Harness evidence appears before the one-minute review")

    one_minute_block = _section_after_marker(html, ONE_MINUTE_MARKERS)
    if one_minute_block:
        text = _plain_text(one_minute_block)
        if len(text) > max_one_minute_text_chars:
            issues.append(
                f"one-minute review text is too long: {len(text)} chars > {max_one_minute_text_chars}"
            )
        dense_markers = [marker for marker in DENSE_FIRST_READ_MARKERS if marker in one_minute_block]
        if dense_markers:
            issues.append("dense generated evidence appears in first review path: " + ", ".join(dense_markers))
    elif marker_position >= 0:
        issues.append("could not isolate one-minute review block")

    return ReviewQualityReport(passed=not issues, issues=tuple(issues))


def assert_review_html_quality(
    html: str,
    *,
    require_harness: bool = False,
    max_one_minute_text_chars: int = 900,
) -> None:
    report = evaluate_review_html(
        html,
        require_harness=require_harness,
        max_one_minute_text_chars=max_one_minute_text_chars,
    )
    if not report.passed:
        raise AssertionError("; ".join(report.issues))


def _first_position(text: str, markers: tuple[str, ...]) -> int:
    positions = [text.find(marker) for marker in markers if marker in text]
    return min(positions) if positions else -1


def _section_after_marker(html: str, markers: tuple[str, ...]) -> str:
    start = _first_position(html, markers)
    if start < 0:
        return ""
    next_heading = re.search(r"<h[23][^>]*>", html[start + 1 :])
    if next_heading is None:
        return html[start:]
    end = start + 1 + next_heading.start()
    return html[start:end]


def _plain_text(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()
