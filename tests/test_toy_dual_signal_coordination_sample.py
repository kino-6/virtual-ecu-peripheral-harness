from pathlib import Path

from veph.exporters.demo_html import export_demo_html
from veph.markup_parser import parse_markup_file
from veph.preview_runtime import run_preview_file
from veph.sample_catalog import load_sample


ROOT = Path(__file__).resolve().parents[1]


def test_toy_dual_signal_sample_models_component_state_machine_roles():
    sample = load_sample("toy_dual_signal_coordination", ROOT)
    model = parse_markup_file(sample.paths.model)

    assert model.component.name == "ToyDualSignalCoordinator"
    assert sample.paths.generated["demo"].name == "review.html"
    assert {function.name for function in model.functions} >= {
        "ToyCrossingCoordinator",
        "MainSignalStateMachine",
        "SideSignalStateMachine",
        "InterlockMonitor",
    }
    assert len(model.transitions) == 6
    assert "DSC-007" in model.requirement_refs()
    assert any(
        flow.source == "ToyCrossingCoordinator.state"
        and flow.target == "MainSignalStateMachine.state"
        for flow in model.flows
    )
    assert any(
        flow.source == "ToyCrossingCoordinator.state"
        and flow.target == "SideSignalStateMachine.state"
        for flow in model.flows
    )


def test_toy_dual_signal_preview_proves_path_and_no_both_green():
    sample = load_sample("toy_dual_signal_coordination", ROOT)
    result = run_preview_file(sample.paths.model, sample.paths.scenarios["side_request_cycle"])

    assert result.passed
    assert result.final_state == "MAIN_GO_SIDE_STOP"
    assert result.observed_behavior["outputs"]["mainGreen"] is True
    assert result.observed_behavior["outputs"]["sideGreen"] is False
    assert "PASS neverBothTrue.mainGreen.sideGreen: no preview step had both true" in result.checks
    for step in result.observed_behavior["stepEvidence"]:
        outputs = step["after"]["outputs"]
        assert not (outputs["mainGreen"] and outputs["sideGreen"]), step


def test_toy_dual_signal_review_leads_with_component_state_machine_summary():
    sample = load_sample("toy_dual_signal_coordination", ROOT)
    model = parse_markup_file(sample.paths.model)
    html = export_demo_html(model, spec_path=sample.paths.spec)

    assert '<html lang="ja">' in html
    assert '<main class="chapter-review">' in html
    assert "1章30秒から1分で確認" in html
    assert "側道要求による信号切替レビュー" in html
    assert "二系統信号の連携レビュー" not in html
    assert "制御全体での位置づけ" in html
    assert "この仕様書が扱うコンポーネント" in html
    assert "設計図" in html
    assert "実装図（MBD）" in html
    assert "検証結果" in html
    assert html.index("制御全体での位置づけ") < html.index("この仕様書が扱うコンポーネント")
    assert html.index("この仕様書が扱うコンポーネント") < html.index("設計図")
    assert html.index("設計図") < html.index("実装図（MBD）")
    assert html.index("実装図（MBD）") < html.index("検証結果")
    assert "プレビュー確認済み。外部MBDでは未確認。" in html
    assert "側道から通行要求が来たとき、主道路側から側道側へ通行権を渡し、側道の通行後に主道路側へ戻す架空の信号制御を扱う。" in html
    assert "架空の主道路/側道信号切替制御" in html
    assert "側道要求に応じて通行権を安全な順序で渡す" in html
    assert "両方向が同時に青にならないこと" in html
    assert '<svg class="review-diagram control-context"' in html
    assert 'aria-label="制御全体のコンポーネントとレビュー対象範囲"' in html
    assert '<svg class="review-diagram spec-scope"' in html
    assert 'aria-label="この仕様書が扱うコンポーネント図"' in html
    assert "仕様対象" in html
    assert "調停・信号写像・監視" in html
    assert "主道路信号" in html
    assert "側道信号" in html
    assert "Harnessプレビュー" in html
    assert "外部MBD確認" in html
    assert "仕様書の対象は、要求入力を受ける調停、主信号/側信号の出力写像、同時青の監視である。" in html
    assert "現実の信号灯や交通流は扱わない。" in html
    assert "Spec.md / Side Request Scenario State Path" in html
    assert "Spec.mdから抜粋した側道要求1サイクルの状態遷移図" in html
    assert "全状態空間ではない" in html
    assert 'aria-label="Spec.md Side Request Scenario State Path"' in html
    assert 'aria-label="生成MBD状態遷移図"' in html
    assert '<svg class="review-diagram spec-state"' in html
    assert '<svg class="review-diagram mbd-state"' in html
    assert html.index('class="review-diagram spec-state"') < html.index('class="review-diagram mbd-state"')
    assert html.count('viewBox="0 0 1048 190"') >= 2
    assert "Component Review View" not in html
    assert "Coordinated Mode Path" not in html
    assert '<svg class="review-diagram spec-design"' not in html
    assert "ToyCrossingCoordinator" in html
    assert "MainSignalStateMachine" in html
    assert "SideSignalStateMachine" in html
    assert "Scenario Report" in html
    assert "タイマ群" in html
    assert "sideRequest" in html
    assert "mainWarningExpired" in html
    assert "clearanceExpired" in html
    assert "sideServed" in html
    assert "sideWarningExpired" in html
    assert "通行権の順序と両信号赤区間を決める" in html
    assert "調停状態を主道路信号へ写像" in html
    assert "調停状態を側道信号へ写像" in html
    assert "同時青でないことを観測" in html
    assert '<div class="component-grid">' not in html
    assert 'aria-label="Spec.md Transition Trigger Coverage"' not in html
    assert '<table class="trigger-table"' not in html
    assert "入力トリガ" not in html
    assert "出力意図" not in html
    assert "MAIN_GO_SIDE_STOP → MAIN_WARN_SIDE_STOP" not in html
    assert "側要求入力後:" not in html
    assert "主信号: 青 → 黄 → 赤 → 青" in html
    assert "側信号: 赤 → 青 → 黄 → 赤" in html
    assert "同時青なし: PASS" in html
    assert "外部MBD確認: メッセージ連携、並列状態、時間制約、実行順序" in html
    assert "設計上の流れは、側要求を調停で受け" not in html
    assert '<div class="diagram-line"' not in html
    assert '<div class="state-strip"' not in html
    assert "A4 1枚" not in html
    assert "a4-review-sheet" not in html
    assert "Human Review Question" not in html
    assert "State Machine Transition Review" not in html
    assert "Review Evidence Map" not in html
    for english in ["Preview PASS", "A4 review sheet", "Main signal", "Side signal", "OPEN", "timing", "side_request"]:
        assert english not in html
    for unclear_short_label in ["主黄", "側青", "側黄", "主青", "全赤"]:
        assert unclear_short_label not in html


def test_toy_dual_signal_design_chapter_reads_spec_state_diagram(tmp_path):
    sample = load_sample("toy_dual_signal_coordination", ROOT)
    model = parse_markup_file(sample.paths.model)
    spec = tmp_path / "spec.md"
    spec.write_text(
        sample.paths.spec.read_text(encoding="utf-8").replace("sideServed", "sideDone"),
        encoding="utf-8",
    )

    html = export_demo_html(model, spec_path=spec)

    design_section = html[html.index("Spec.md / Side Request Scenario State Path") : html.index("実装図（MBD）")]
    assert "sideDone" in design_section
    assert "sideServed" not in design_section


def test_toy_dual_signal_spec_names_topic_scope_and_state_path():
    sample = load_sample("toy_dual_signal_coordination", ROOT)
    spec = sample.paths.spec.read_text(encoding="utf-8")

    assert "# Side Request Signal Handoff Specification" in spec
    assert "## Control Context" in spec
    assert "## Specification Component Scope" in spec
    assert "## Side Request Scenario State Path" in spec
    assert "This path is the required scenario path for one side-road request cycle." in spec
    assert "not the complete state space" in spec
    assert "## Transition Trigger Coverage" not in spec
    assert "## Signal Handoff State Path" not in spec
    assert "Coordinated Mode Path" not in spec
    assert "Component Review View" not in spec
    assert "main-road / side-road signal" in spec
    assert "Physical signal lamps, traffic flow, real timing" in spec
