from __future__ import annotations

from pathlib import Path

from veph.ir import MbdModelIR
from veph.samples.code_preview import PREVIEW_CODE_GENERATORS


class CodePreviewExportError(ValueError):
    """Raised when a component has no preview C generator."""


def export_code_preview(model: MbdModelIR, out_dir: str | Path) -> list[Path]:
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    generator = PREVIEW_CODE_GENERATORS.get(model.component.name)
    if generator is None:
        supported = ", ".join(sorted(PREVIEW_CODE_GENERATORS))
        raise CodePreviewExportError(
            f"no preview C generator registered for {model.component.name!r}; supported components: {supported}"
        )
    files = generator(model)
    written: list[Path] = []
    for name, content in files.items():
        path = output / name
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written
