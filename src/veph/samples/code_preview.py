from __future__ import annotations

from collections.abc import Callable

from veph.ir import MbdModelIR
from veph.samples.thermal_code_preview import PREVIEW_CODE_GENERATORS as THERMAL_PREVIEW_CODE_GENERATORS


PREVIEW_CODE_GENERATORS: dict[str, Callable[[MbdModelIR], dict[str, str]]] = {
    **THERMAL_PREVIEW_CODE_GENERATORS,
}
