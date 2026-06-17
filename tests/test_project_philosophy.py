from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_states_source_of_truth_and_no_commercial_dependency():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "Textual MBD as the source of truth" in readme
    assert "not a Simulink replacement" in readme
    assert "Commercial MBD tools are optional export targets, not runtime dependencies" in readme
    assert "Product-like ECU code stays unchanged" in readme


def test_design_principles_document_covers_project_boundaries():
    principles = (ROOT / "docs" / "design_principles.md").read_text(encoding="utf-8")

    expected_sections = [
        "## Textual MBD",
        "## Source-Of-Truth Policy",
        "## Generated Artifact Policy",
        "## Virtual Peripheral Boundary",
        "## Product-Like ECU Code Boundary",
        "## Commercial-Tool-Free MVP Policy",
        "## Future Export Direction",
    ]

    for section in expected_sections:
        assert section in principles

    assert "fictional components" in principles
    assert "must not become canonical source" in principles
