from __future__ import annotations

from pathlib import Path

from veph.ir import MbdModelIR


def export_code_preview(model: MbdModelIR, out_dir: str | Path) -> list[Path]:
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    files = {
        "controller.h": _controller_h(model),
        "controller.c": _controller_c(model),
        "hal_spi.h": _hal_spi_h(),
        "hal_pwm.h": _hal_pwm_h(),
        "README.md": _readme(model),
    }
    written: list[Path] = []
    for name, content in files.items():
        path = output / name
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


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


def _readme(model: MbdModelIR) -> str:
    refs = ", ".join(sorted(model.requirement_refs()))
    return "\n".join(
        [
            "# Preview ECU Scaffold",
            "",
            "Generated from Mermaid-like MBD markup.",
            "",
            "- Status: preview-only; not certified code generation.",
            "- Source: `examples/toy_thermal_fan_control.mbd.md`.",
            "- Boundary: product-like controller logic uses HAL-style headers.",
            "- Fictional-only: no real IC, real register map, or production ECU code.",
            f"- Requirement refs: {refs}",
            "",
        ]
    )
