from __future__ import annotations


def generate_thermal_protection_mbd_scaffold(extracted) -> str:
    system_refs = _ids_for_sections(extracted, {"System Requirements"})
    harness_refs = _ids_for_sections(extracted, {"Harness Requirements"})
    high_class_refs = [
        req.id for req in extracted.requirements if req.classification in {"DSC-B", "DSC-C"}
    ]
    return generate_thermal_mbd_scaffold(
        coverage_intent=_coverage_intent_lines(extracted),
        system_refs=system_refs,
        harness_refs=harness_refs,
        high_class_refs=high_class_refs,
    )


def generate_thermal_mbd_scaffold(
    coverage_intent: list[str],
    system_refs: list[str],
    harness_refs: list[str],
    high_class_refs: list[str],
) -> str:
    lines = [
        "# MBD Scaffold",
        "",
        "> Generated scaffold from requirements. Do not treat this scaffold as approved behavior",
        "> until open questions are reviewed.",
        "",
        "## Review Status",
        "",
        "- Behavior approval: **PENDING**",
        "- Coverage meaning: traces identify intended coverage, not accepted model semantics.",
        "- TODO values are explicit placeholders, not accepted demo answers.",
        "- External MBD/product-test infrastructure is still required for production-grade verification.",
        "",
        "## Requirement Coverage Intent",
        "",
        *coverage_intent,
        "",
        "```mbd-component",
        "component ToyThermalProtectionController",
        f"trace {' '.join(system_refs[:8])}".rstrip(),
        "bus virtual mode=preview wordBits=16",
        "parameter TODO_highThreshold: degC = 0",
        "parameter TODO_lowThreshold: degC = 0",
        "parameter TODO_deratingLimit: percent = 0",
        "parameter TODO_safeCommand: percent = 0",
        "",
        "port in temperatureC: degC = 0",
        "port in temperatureValid: bool = true",
        "port out coolingCommand: percent = 0",
        "port out deratingCommand: percent = 0",
        "port out diagnosticFault: bool = false",
        "```",
        "",
        "```mbd-state",
        "RESET --> NOMINAL: open-question SYS-008 trace SYS-008",
        "NOMINAL --> COOLING: open-question threshold-high trace SYS-003",
        "COOLING --> DERATING: open-question derating-entry trace SYS-005",
        "DERATING --> FAULT_LATCHED: open-question persistent-invalid-sensor trace SYS-007",
        "FAULT_LATCHED --> NOMINAL: open-question recovery-conditions trace SYS-008",
        "```",
        "",
        "```mbd-flow",
        "ToyTempSensorIC.temperatureC -> HAL_SPI.read_temperature: virtual sensor sample trace SYS-001 HAR-001",
        "HAL_SPI.read_temperature -> ToyThermalProtectionController.temperatureC: HAL input trace SWE-004 HAR-002",
        "ToyThermalProtectionController.coolingCommand -> HAL_PWM.set_cooling: virtual actuator command trace SYS-002 HAR-001",
        "ToyThermalProtectionController.deratingCommand -> ToyLoadLimiterIC.limit: virtual load limiter command trace SYS-005 HAR-006",
        "```",
        "",
        "```mbd-control",
        "rule TODO_sensorFault: when temperatureValid == false then diagnosticFault=true trace SYS-006 SYS-007",
        "rule TODO_highTemperature: when temperatureC >= TODO_highThreshold then coolingCommand=TODO trace SYS-003",
        "rule TODO_derating: when temperatureC >= TODO_deratingEntry then deratingCommand=TODO trace SYS-005",
        "```",
        "",
        "```mbd-harness",
        f"device ToyTempSensorIC role=sensor boundary=virtual_ic trace {' '.join(_matching_refs(harness_refs, ['HAR-001', 'HAR-006']))}",
        "device ToyFanDriverIC role=actuator boundary=virtual_ic trace HAR-001",
        "device ToyLoadLimiterIC role=actuator boundary=virtual_ic trace HAR-006",
        "ecu ToyThermalProtectionController role=controller boundary=hal trace HAR-002 SWE-004",
        "```",
        "",
        "## Open Questions",
        "",
        "Do not invent missing thresholds, timings, recovery rules, or fault semantics.",
        "",
    ]
    for req_id in high_class_refs:
        lines.append(f"- open-question {req_id}: define explicit state/control/harness/scenario/expected behavior coverage.")
    lines.append("")
    return "\n".join(lines)


def _matching_refs(refs: list[str], preferred: list[str]) -> list[str]:
    matches = [ref for ref in preferred if ref in refs]
    return matches or refs[:2]


def _ids_for_sections(extracted, sections: set[str]) -> list[str]:
    return [req.id for req in extracted.requirements if req.section in sections]


def _coverage_intent_lines(extracted) -> list[str]:
    lines = []
    for req in extracted.requirements:
        if _requires_mbd_coverage(req):
            lines.append(f"- `{req.id}`: scaffold coverage required; refine into concrete model element before approval.")
    return lines or ["- No MBD coverage requirements extracted."]


def _requires_mbd_coverage(req) -> bool:
    return req.section in {
        "System Requirements",
        "Software Requirements",
        "Harness Requirements",
        "Preview Engine Requirements",
        "MBD-To-C Process Requirements",
    } or req.classification in {"DSC-B", "DSC-C"}
