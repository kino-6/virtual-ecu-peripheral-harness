from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_states_source_of_truth_and_no_commercial_dependency():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Author in text. Verify in MBD tools." in readme
    assert "Mermaid-like Markup for virtual ECU and peripheral model authoring" in readme
    assert "Python preview is only a preview/smoke-test helper" in readme
    assert "not a Simulink replacement" in readme
    assert "does not claim certification" in readme
    assert "preview evidence layer" in readme
    assert "Harness does not own control decisions" in readme


def test_design_principles_document_covers_project_boundaries():
    principles = (ROOT / "docs" / "design_principles.md").read_text(encoding="utf-8")

    expected_sections = [
        "## Mermaid-Like Markup",
        "## Authoring Source Policy",
        "## Existing MBD Tools As Verification Backends",
        "## Generated Artifact Policy",
        "## Python Preview Boundary",
        "## Harness Evidence Boundary",
        "## YAML And IR Policy",
        "## Certification Boundary",
    ]

    for section in expected_sections:
        assert section in principles

    assert "fictional components" in principles
    assert "YAML is not the public source of truth" in principles
    assert "Author in text. Verify in MBD tools." in principles
    assert "Harness is a preview evidence layer" in principles
    assert "Control decisions, state transitions, and output decisions belong to MBD source" in principles


def test_agent_rules_and_review_principles_guard_demo_and_harness_boundaries():
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    principles = (ROOT / "docs" / "mbd_review_principles.md").read_text(encoding="utf-8")
    quality_gate_skill = (
        ROOT / ".agents" / "skills" / "quality-gate-expectation-control" / "SKILL.md"
    ).read_text(encoding="utf-8")
    mbd_review_skill = (
        ROOT / ".agents" / "skills" / "mbd-review-quality-gate" / "SKILL.md"
    ).read_text(encoding="utf-8")

    for text in [agents, principles, quality_gate_skill, mbd_review_skill]:
        assert "MBD review artifact" in text
        assert "preview evidence layer" in text
        assert "Harness" in text
        assert "scenario YAML" in text

    assert "review.html" in agents
    assert "not a casual-demo claim" in agents
    assert "review.html" in principles
    assert "review.html" in mbd_review_skill
    assert "Harness evidence lane" in principles
    assert "## Design Layer Separation" in principles
    assert "explicit Control Semantics View" in principles
    assert "behavior confirmation table" in mbd_review_skill
    assert "not an allocation" in mbd_review_skill
    assert "Role / Owns / Reads / Emits" in mbd_review_skill
    assert "30-second to 1-minute review path" in mbd_review_skill
    assert "chapter-level readability" in mbd_review_skill
    assert "overview, component split, design" in mbd_review_skill
    for phrase in ["`check`", "`stimulus / relation`", "`expected", "`verdict`"]:
        assert phrase in principles
    assert "chapter-level gate by default" in principles
    assert "Only when the user explicitly asks for A4-one-page readability" in principles
    assert "## Generated-Side Consistency Checks" in principles
    assert "Control decisions, state transitions, and output decisions" in quality_gate_skill
    assert "Reject harness shortcuts" in mbd_review_skill


def test_timeboxed_goal_policy_prevents_stopping_at_first_green_checkpoint():
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    skill = (ROOT / ".agents" / "skills" / "timeboxed-pdca-goal" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    skill_ui = (
        ROOT / ".agents" / "skills" / "timeboxed-pdca-goal" / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")

    for text in [agents, skill]:
        assert "Timeboxed" in text
        assert "2h Goal" in text
        assert "時間を余らせるな" in text
        assert "自律的にPlan" in text
        assert "PDCAで回す" in text
        assert "green checkpoint" in text
        assert "Remaining Budget Decision" in text
        assert "not the end of a timeboxed Goal" in text
        assert "Stop condition satisfied? yes/no" in text
        assert "Do not call `update_goal` with `complete`" in text

    assert "usable work budget, not merely a deadline" in agents
    assert "Do not stop" in skill
    assert "one vertical slice" in skill
    assert "If more than roughly 25%" in skill
    assert "Completion Hard Gate" in skill
    assert "final Remaining Budget Decision" in skill
    assert "Timeboxed PDCA Goal" in skill_ui
    assert "Remaining Budget Decision names a satisfied stop condition" in skill_ui
