/* Generated from samples/thermal_fan_control/model.mbd.md.
 * Preview-only synthetic ECU scaffold; not certified code generation.
 * Requirement traces are preserved in the source MBD markup and reports.
 */
#include "controller.h"
#include "hal_pwm.h"
#include "hal_spi.h"

void toy_thermal_fan_controller_init(ToyThermalFanController *controller)
{
    controller->state = TOY_THERMAL_STATE_IDLE;
    controller->fanOnThreshold = 75.0f;
    controller->fanOffThreshold = 65.0f;
    controller->coolingDuty = 80.0f;
    controller->safeDuty = 35.0f;
    controller->fanDuty = 0.0f;
    controller->fault = false;
}

void toy_thermal_fan_controller_step(ToyThermalFanController *controller)
{
    bool temperatureValid = false;
    float temperatureC = hal_spi_read_temperature_c(&temperatureValid);

    if (!temperatureValid) {
        controller->state = TOY_THERMAL_STATE_FAULT;
        controller->fanDuty = controller->safeDuty;
        controller->fault = true;
    } else if (temperatureC >= controller->fanOnThreshold) {
        controller->state = TOY_THERMAL_STATE_COOLING;
        controller->fanDuty = controller->coolingDuty;
        controller->fault = false;
    } else if (temperatureC <= controller->fanOffThreshold) {
        controller->state = TOY_THERMAL_STATE_IDLE;
        controller->fanDuty = 0.0f;
        controller->fault = false;
    }

    hal_pwm_set_fan_duty(controller->fanDuty);
}
