from pathlib import Path

from veph.review_quality import assert_review_html_quality, evaluate_review_html


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_spec_first_review_html_stays_one_minute_readable():
    for relative in [
        "samples/simple_relay_hysteresis/generated/from_spec_review.html",
        "samples/simple_state_machine/generated/from_spec_review.html",
        "samples/toy_energy_buffer_mode/generated/from_spec_review.html",
    ]:
        html = _read(relative)
        assert_review_html_quality(html, require_harness=True)
        assert html.index("状態図レビュー") < html.index("Harness検証結果")
        assert html.index("状態図レビュー") < html.index("要求ごとの確認")


def test_spec_mbd_viewer_html_omits_dense_matched_edge_dump():
    for relative in [
        "samples/simple_threshold_indicator/generated/spec_mbd_viewer.html",
        "samples/simple_switch_selector/generated/spec_mbd_viewer.html",
    ]:
        assert_review_html_quality(_read(relative))
        assert "Matched edge details are omitted from this compact HTML view." in _read(relative)


def test_review_quality_reports_actionable_issues():
    report = evaluate_review_html(
        """
        <html><body>
          <h3>1分レビュー</h3>
          <table><tr><td>機能: too much generated detail</td></tr></table>
        </body></html>
        """,
        require_harness=True,
    )

    assert not report.passed
    assert any("missing Harness" in issue for issue in report.issues)
    assert any("dense generated evidence" in issue for issue in report.issues)
