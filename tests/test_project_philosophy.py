from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_states_source_of_truth_and_no_commercial_dependency():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Author in text. Verify in MBD tools." in readme
    assert "Mermaid-like Markup for virtual ECU and peripheral model authoring" in readme
    assert "Python preview is only a preview/smoke-test helper" in readme
    assert "not a Simulink replacement" in readme
    assert "does not claim certification" in readme


def test_design_principles_document_covers_project_boundaries():
    principles = (ROOT / "docs" / "design_principles.md").read_text(encoding="utf-8")

    expected_sections = [
        "## Mermaid-Like Markup",
        "## Authoring Source Policy",
        "## Existing MBD Tools As Verification Backends",
        "## Generated Artifact Policy",
        "## Python Preview Boundary",
        "## YAML And IR Policy",
        "## Certification Boundary",
    ]

    for section in expected_sections:
        assert section in principles

    assert "fictional components" in principles
    assert "YAML is not the public source of truth" in principles
    assert "Author in text. Verify in MBD tools." in principles
