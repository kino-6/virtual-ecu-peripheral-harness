import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "mermaid_to_mbd_supported_items.md"


def _coverage_rows() -> list[dict[str, str]]:
    text = DOC.read_text(encoding="utf-8")
    match = re.search(
        r"## Coverage Matrix\n\n(?P<table>\| ID \| Area \| Item \| Status \| Evidence \|\n"
        r"\| --- \| --- \| --- \| --- \| --- \|\n(?:\| .+\n)+)",
        text,
    )
    assert match is not None, "missing Coverage Matrix table with ID/Area/Item/Status/Evidence columns"
    rows: list[dict[str, str]] = []
    for line in match.group("table").splitlines()[2:]:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        assert len(cells) == 5
        rows.append(
            {
                "id": cells[0],
                "area": cells[1],
                "item": cells[2],
                "status": cells[3],
                "evidence": cells[4],
            }
        )
    return rows


def test_mermaid_to_mbd_mvp_catalog_has_stable_34_item_matrix():
    rows = _coverage_rows()
    ids = [row["id"] for row in rows]

    assert len(rows) == 34
    assert len(set(ids)) == 34
    assert ids == sorted(ids)
    assert all(re.fullmatch(r"MBD-[A-Z]+-\d{2}", item_id) for item_id in ids)


def test_mermaid_to_mbd_coverage_summary_matches_matrix():
    rows = _coverage_rows()
    supported = [row for row in rows if row["status"] == "supported"]
    unsupported = [row for row in rows if row["status"] == "unsupported"]
    partial = [row for row in rows if row["status"] == "partial"]
    text = DOC.read_text(encoding="utf-8")
    summary = re.search(
        r"Overall for this deliberately small MVP catalog: \*\*(?P<supported>\d+) / (?P<total>\d+) items\*\*",
        text,
    )

    assert summary is not None
    assert int(summary.group("supported")) == len(supported)
    assert int(summary.group("total")) == len(rows)
    assert len(supported) + len(unsupported) + len(partial) == len(rows)
    assert len(partial) == 0


def test_mermaid_to_mbd_coverage_evidence_is_actionable():
    for row in _coverage_rows():
        assert row["evidence"]
        if row["status"] == "supported":
            assert "test" in row["evidence"] or "sample" in row["evidence"]
        if row["status"] == "unsupported":
            assert "planned" in row["evidence"] or "explicit" in row["evidence"]
