from __future__ import annotations

from collections.abc import Callable

from veph.requirements_support import ExtractedRequirements
from veph.samples.thermal_requirements import generate_thermal_protection_mbd_scaffold


class SampleScaffoldError(ValueError):
    """Raised when a requested sample scaffold is not registered."""


MBD_SCAFFOLD_GENERATORS: dict[str, Callable[[ExtractedRequirements], str]] = {
    "thermal-protection": generate_thermal_protection_mbd_scaffold,
}


def generate_sample_mbd_scaffold(sample: str, extracted: ExtractedRequirements) -> str:
    generator = MBD_SCAFFOLD_GENERATORS.get(sample)
    if generator is None:
        supported = ", ".join(sorted(MBD_SCAFFOLD_GENERATORS))
        raise SampleScaffoldError(
            f"no MBD scaffold generator registered for sample {sample!r}; supported samples: {supported}"
        )
    return generator(extracted)
