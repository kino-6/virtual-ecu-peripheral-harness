from __future__ import annotations

from pathlib import Path

from veph.ir import MbdModelIR


PREVIEW_CODE_GENERATORS = {
    "ToyThermalFanController": lambda model: _fan_files(model),
    "ToyThermalProtectionController": lambda model: _protection_files(model),
}


def _fan_files(model: MbdModelIR) -> dict[str, str]:
    return {
        "controller.h": _controller_h(model),
        "controller.c": _controller_c(model),
        "hal_spi.h": _hal_spi_h(),
        "hal_pwm.h": _hal_pwm_h(),
        "README.md": _readme(model),
    }


def _protection_files(model: MbdModelIR) -> dict[str, str]:
    return {
        "controller.h": _protection_controller_h(model),
        "controller.c": _protection_controller_c(model),
        "hal_spi.h": _protection_hal_spi_h(),
        "hal_pwm.h": _hal_pwm_h(),
        "hal_load_limiter.h": _hal_load_limiter_h(),
        "README.md": _readme(model),
    }


def _controller_h(model: MbdModelIR) -> str:
    guard = f"{model.component.name.upper()}_CONTROLLER_H"
    return "\n".join(
        [
            "/* Generated preview-only controller scaffold.",
            " * Synthetic example; not production-derived and not certified.",
            " */",
            f"#ifndef {guard}",
            f"#define {guard}",
            "",
            "#include <stdbool.h>",
            "",
            "typedef enum {",
            "    TOY_THERMAL_STATE_RESET = 0,",
            "    TOY_THERMAL_STATE_IDLE = 1,",
            "    TOY_THERMAL_STATE_COOLING = 2,",
            "    TOY_THERMAL_STATE_FAULT = 3",
            "} ToyThermalFanState;",
            "",
            "typedef struct {",
            "    ToyThermalFanState state;",
            "    float fanOnThreshold;",
            "    float fanOffThreshold;",
            "    float coolingDuty;",
            "    float safeDuty;",
            "    float fanDuty;",
            "    bool fault;",
            "} ToyThermalFanController;",
            "",
            "void toy_thermal_fan_controller_init(ToyThermalFanController *controller);",
            "void toy_thermal_fan_controller_step(ToyThermalFanController *controller);",
            "",
            f"#endif /* {guard} */",
            "",
        ]
    )


def _controller_c(model: MbdModelIR) -> str:
    params = {name: parameter.default for name, parameter in model.component.parameters.items()}
    return "\n".join(
        [
            "/* Generated from examples/toy_thermal_fan_control.mbd.md.",
            " * Preview-only synthetic ECU scaffold; not certified code generation.",
            " * Requirement traces are preserved in the source MBD markup and reports.",
            " */",
            "#include \"controller.h\"",
            "#include \"hal_pwm.h\"",
            "#include \"hal_spi.h\"",
            "",
            "void toy_thermal_fan_controller_init(ToyThermalFanController *controller)",
            "{",
            "    controller->state = TOY_THERMAL_STATE_IDLE;",
            f"    controller->fanOnThreshold = {params.get('fanOnThreshold', '75')}.0f;",
            f"    controller->fanOffThreshold = {params.get('fanOffThreshold', '65')}.0f;",
            f"    controller->coolingDuty = {params.get('coolingDuty', '80')}.0f;",
            f"    controller->safeDuty = {params.get('safeDuty', '35')}.0f;",
            "    controller->fanDuty = 0.0f;",
            "    controller->fault = false;",
            "}",
            "",
            "void toy_thermal_fan_controller_step(ToyThermalFanController *controller)",
            "{",
            "    bool temperatureValid = false;",
            "    float temperatureC = hal_spi_read_temperature_c(&temperatureValid);",
            "",
            "    if (!temperatureValid) {",
            "        controller->state = TOY_THERMAL_STATE_FAULT;",
            "        controller->fanDuty = controller->safeDuty;",
            "        controller->fault = true;",
            "    } else if (temperatureC >= controller->fanOnThreshold) {",
            "        controller->state = TOY_THERMAL_STATE_COOLING;",
            "        controller->fanDuty = controller->coolingDuty;",
            "        controller->fault = false;",
            "    } else if (temperatureC <= controller->fanOffThreshold) {",
            "        controller->state = TOY_THERMAL_STATE_IDLE;",
            "        controller->fanDuty = 0.0f;",
            "        controller->fault = false;",
            "    }",
            "",
            "    hal_pwm_set_fan_duty(controller->fanDuty);",
            "}",
            "",
        ]
    )


def _protection_controller_h(model: MbdModelIR) -> str:
    guard = f"{model.component.name.upper()}_CONTROLLER_H"
    return "\n".join(
        [
            "/* Generated preview-only controller scaffold.",
            " * Synthetic example; not production-derived and not certified.",
            " */",
            f"#ifndef {guard}",
            f"#define {guard}",
            "",
            "#include <stdbool.h>",
            "",
            "typedef enum {",
            "    TOY_PROTECTION_STATE_RESET = 0,",
            "    TOY_PROTECTION_STATE_IDLE = 1,",
            "    TOY_PROTECTION_STATE_COOLING = 2,",
            "    TOY_PROTECTION_STATE_DERATING = 3,",
            "    TOY_PROTECTION_STATE_SENSOR_FAULT = 4,",
            "    TOY_PROTECTION_STATE_FAULT_LATCHED = 5",
            "} ToyProtectionState;",
            "",
            "typedef struct {",
            "    ToyProtectionState state;",
            "    float coolingOnThreshold;",
            "    float coolingOffThreshold;",
            "    float deratingEntryThreshold;",
            "    float coolingDuty;",
            "    float deratingFanDuty;",
            "    float deratingLimit;",
            "    float safeDuty;",
            "    float fanDuty;",
            "    float deratingCommand;",
            "    bool diagnosticFault;",
            "    bool safeCommandActive;",
            "} ToyThermalProtectionController;",
            "",
            "void toy_thermal_protection_controller_init(ToyThermalProtectionController *controller);",
            "void toy_thermal_protection_controller_step(ToyThermalProtectionController *controller);",
            "",
            f"#endif /* {guard} */",
            "",
        ]
    )


def _protection_controller_c(model: MbdModelIR) -> str:
    params = {name: parameter.default for name, parameter in model.component.parameters.items()}
    return "\n".join(
        [
            f"/* Generated from {_source_display(model)}.",
            " * Preview-only synthetic ECU scaffold; not certified code generation.",
            " * Requirement traces are preserved in the source MBD markup and reports.",
            " */",
            "#include \"controller.h\"",
            "#include \"hal_load_limiter.h\"",
            "#include \"hal_pwm.h\"",
            "#include \"hal_spi.h\"",
            "",
            "void toy_thermal_protection_controller_init(ToyThermalProtectionController *controller)",
            "{",
            "    controller->state = TOY_PROTECTION_STATE_IDLE;",
            f"    controller->coolingOnThreshold = {params.get('coolingOnThreshold', '78')}.0f;",
            f"    controller->coolingOffThreshold = {params.get('coolingOffThreshold', '68')}.0f;",
            f"    controller->deratingEntryThreshold = {params.get('deratingEntryThreshold', '94')}.0f;",
            f"    controller->coolingDuty = {params.get('coolingDuty', '70')}.0f;",
            f"    controller->deratingFanDuty = {params.get('deratingFanDuty', '95')}.0f;",
            f"    controller->deratingLimit = {params.get('deratingLimit', '45')}.0f;",
            f"    controller->safeDuty = {params.get('safeDuty', '30')}.0f;",
            "    controller->fanDuty = 0.0f;",
            "    controller->deratingCommand = 0.0f;",
            "    controller->diagnosticFault = false;",
            "    controller->safeCommandActive = false;",
            "}",
            "",
            "void toy_thermal_protection_controller_step(ToyThermalProtectionController *controller)",
            "{",
            "    bool temperatureValid = false;",
            "    bool invalidDebounced = false;",
            "    bool recoveryRequest = false;",
            "    float temperatureC = hal_spi_read_temperature_c(&temperatureValid);",
            "    invalidDebounced = hal_spi_read_invalid_debounced();",
            "    recoveryRequest = hal_spi_read_recovery_request();",
            "",
            "    /* priority 10 recoverFromLatch: owner FaultLatchRecoveryManager from FAULT_LATCHED */",
            "    if (controller->state == TOY_PROTECTION_STATE_FAULT_LATCHED &&",
            "        temperatureValid && !invalidDebounced && recoveryRequest) {",
            "        controller->state = TOY_PROTECTION_STATE_IDLE;",
            "        controller->fanDuty = 0.0f;",
            "        controller->deratingCommand = 0.0f;",
            "        controller->diagnosticFault = false;",
            "        controller->safeCommandActive = false;",
            "    /* priority 20 faultLatch: owner FaultLatchRecoveryManager from * */",
            "    } else if (invalidDebounced) {",
            "        controller->state = TOY_PROTECTION_STATE_FAULT_LATCHED;",
            "        controller->fanDuty = controller->safeDuty;",
            "        controller->deratingCommand = 0.0f;",
            "        controller->diagnosticFault = true;",
            "        controller->safeCommandActive = true;",
            "    /* priority 30 holdLatchedFault: owner FaultLatchRecoveryManager from FAULT_LATCHED */",
            "    } else if (controller->state == TOY_PROTECTION_STATE_FAULT_LATCHED) {",
            "        controller->fanDuty = controller->safeDuty;",
            "        controller->deratingCommand = 0.0f;",
            "        controller->diagnosticFault = true;",
            "        controller->safeCommandActive = true;",
            "    /* priority 40 sensorInvalid: owner FaultLatchRecoveryManager from * */",
            "    } else if (!temperatureValid) {",
            "        controller->state = TOY_PROTECTION_STATE_SENSOR_FAULT;",
            "        controller->fanDuty = controller->safeDuty;",
            "        controller->deratingCommand = 0.0f;",
            "        controller->diagnosticFault = true;",
            "        controller->safeCommandActive = true;",
            "    /* priority 50 derating: owner DeratingCommandManager from * */",
            "    } else if (temperatureC >= controller->deratingEntryThreshold) {",
            "        controller->state = TOY_PROTECTION_STATE_DERATING;",
            "        controller->fanDuty = controller->deratingFanDuty;",
            "        controller->deratingCommand = controller->deratingLimit;",
            "        controller->diagnosticFault = false;",
            "        controller->safeCommandActive = false;",
            "    /* priority 60 highCooling: owner CoolingCommandManager from * */",
            "    } else if (temperatureC >= controller->coolingOnThreshold) {",
            "        controller->state = TOY_PROTECTION_STATE_COOLING;",
            "        controller->fanDuty = controller->coolingDuty;",
            "        controller->deratingCommand = 0.0f;",
            "        controller->diagnosticFault = false;",
            "        controller->safeCommandActive = false;",
            "    /* priority 70 lowCooling: owner CoolingCommandManager from * */",
            "    } else if (temperatureC <= controller->coolingOffThreshold) {",
            "        controller->state = TOY_PROTECTION_STATE_IDLE;",
            "        controller->fanDuty = 0.0f;",
            "        controller->deratingCommand = 0.0f;",
            "        controller->diagnosticFault = false;",
            "        controller->safeCommandActive = false;",
            "    }",
            "",
            "    hal_pwm_set_fan_duty(controller->fanDuty);",
            "    hal_load_limiter_set_derating(controller->deratingCommand);",
            "}",
            "",
        ]
    )


def _hal_spi_h() -> str:
    return "\n".join(
        [
            "/* Preview-only HAL boundary for a fictional virtual temperature IC. */",
            "#ifndef TOY_HAL_SPI_H",
            "#define TOY_HAL_SPI_H",
            "",
            "#include <stdbool.h>",
            "",
            "float hal_spi_read_temperature_c(bool *valid);",
            "",
            "#endif /* TOY_HAL_SPI_H */",
            "",
        ]
    )


def _protection_hal_spi_h() -> str:
    return "\n".join(
        [
            "/* Preview-only HAL boundary for a fictional virtual temperature IC. */",
            "#ifndef TOY_HAL_SPI_H",
            "#define TOY_HAL_SPI_H",
            "",
            "#include <stdbool.h>",
            "",
            "float hal_spi_read_temperature_c(bool *valid);",
            "bool hal_spi_read_invalid_debounced(void);",
            "bool hal_spi_read_recovery_request(void);",
            "",
            "#endif /* TOY_HAL_SPI_H */",
            "",
        ]
    )


def _hal_pwm_h() -> str:
    return "\n".join(
        [
            "/* Preview-only HAL boundary for a fictional virtual fan driver IC. */",
            "#ifndef TOY_HAL_PWM_H",
            "#define TOY_HAL_PWM_H",
            "",
            "void hal_pwm_set_fan_duty(float duty_percent);",
            "",
            "#endif /* TOY_HAL_PWM_H */",
            "",
        ]
    )


def _hal_load_limiter_h() -> str:
    return "\n".join(
        [
            "/* Preview-only HAL boundary for a fictional virtual load limiter IC. */",
            "#ifndef TOY_HAL_LOAD_LIMITER_H",
            "#define TOY_HAL_LOAD_LIMITER_H",
            "",
            "void hal_load_limiter_set_derating(float limit_percent);",
            "",
            "#endif /* TOY_HAL_LOAD_LIMITER_H */",
            "",
        ]
    )


def _readme(model: MbdModelIR) -> str:
    refs = ", ".join(sorted(model.requirement_refs()))
    return "\n".join(
        [
            "# Preview ECU Scaffold",
            "",
            "Generated from Mermaid-like MBD markup.",
            "",
            "- Status: preview-only; not certified code generation.",
            f"- Source: `{_source_display(model)}`.",
            "- Boundary: product-like controller logic uses HAL-style headers.",
            "- Fictional-only: no real IC, real register map, or production ECU code.",
            f"- Requirement refs: {refs}",
            "",
        ]
    )


def _source_display(model: MbdModelIR) -> str:
    try:
        return str(model.source_path.relative_to(Path.cwd()))
    except ValueError:
        return str(model.source_path)
