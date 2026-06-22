from pathlib import Path
from shutil import copytree

from veph.cli import main
from veph.sample_validation import validate_sample


ROOT = Path(__file__).resolve().parents[1]


def test_validate_sample_passes_for_toy_energy_buffer_mode(tmp_path):
    report = validate_sample("toy_energy_buffer_mode", ROOT)
    out = tmp_path / "sample_validation.md"

    assert report.passed
    assert "generated artifact demo deterministic" in report.checks
    assert "sequence expectations source_loss_recovery PASS" in report.checks
    assert main(["validate-sample", "toy_energy_buffer_mode", "--out", str(out)]) == 0
    assert "Result: **PASS**" in out.read_text(encoding="utf-8")


def test_validate_sample_reports_stale_review_html(tmp_path):
    sample_root = tmp_path / "samples" / "toy_energy_buffer_mode"
    copytree(ROOT / "samples" / "toy_energy_buffer_mode", sample_root)
    review = sample_root / "generated" / "from_spec_review.html"
    review.write_text(review.read_text(encoding="utf-8").replace("1分レビュー", "Review dump"), encoding="utf-8")

    report = validate_sample("toy_energy_buffer_mode", tmp_path)

    assert not report.passed
    assert any("review HTML quality convertedReviewHtml" in issue for issue in report.issues)
