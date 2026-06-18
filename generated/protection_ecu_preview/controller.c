/* Generated from examples/toy_thermal_protection_controller.mbd.md.
 * Preview-only synthetic ECU scaffold; not certified code generation.
 * Requirement traces are preserved in the source MBD markup and reports.
 */
#include "controller.h"
#include "hal_load_limiter.h"
#include "hal_pwm.h"
#include "hal_spi.h"

void toy_thermal_protection_controller_init(ToyThermalProtectionController *controller)
{
    controller->state = TOY_PROTECTION_STATE_IDLE;
    controller->coolingOnThreshold = 78.0f;
    controller->coolingOffThreshold = 68.0f;
    controller->deratingEntryThreshold = 94.0f;
    controller->coolingDuty = 70.0f;
    controller->deratingFanDuty = 95.0f;
    controller->deratingLimit = 45.0f;
    controller->safeDuty = 30.0f;
    controller->fanDuty = 0.0f;
    controller->deratingCommand = 0.0f;
    controller->diagnosticFault = false;
    controller->safeCommandActive = false;
}

void toy_thermal_protection_controller_step(ToyThermalProtectionController *controller)
{
    bool temperatureValid = false;
    bool invalidDebounced = false;
    bool recoveryRequest = false;
    float temperatureC = hal_spi_read_temperature_c(&temperatureValid);
    invalidDebounced = hal_spi_read_invalid_debounced();
    recoveryRequest = hal_spi_read_recovery_request();

    /* priority 10 recoverFromLatch: owner FaultLatchRecoveryManager from FAULT_LATCHED */
    if (controller->state == TOY_PROTECTION_STATE_FAULT_LATCHED &&
        temperatureValid && !invalidDebounced && recoveryRequest) {
        controller->state = TOY_PROTECTION_STATE_IDLE;
        controller->fanDuty = 0.0f;
        controller->deratingCommand = 0.0f;
        controller->diagnosticFault = false;
        controller->safeCommandActive = false;
    /* priority 20 faultLatch: owner FaultLatchRecoveryManager from * */
    } else if (invalidDebounced) {
        controller->state = TOY_PROTECTION_STATE_FAULT_LATCHED;
        controller->fanDuty = controller->safeDuty;
        controller->deratingCommand = 0.0f;
        controller->diagnosticFault = true;
        controller->safeCommandActive = true;
    /* priority 30 holdLatchedFault: owner FaultLatchRecoveryManager from FAULT_LATCHED */
    } else if (controller->state == TOY_PROTECTION_STATE_FAULT_LATCHED) {
        controller->fanDuty = controller->safeDuty;
        controller->deratingCommand = 0.0f;
        controller->diagnosticFault = true;
        controller->safeCommandActive = true;
    /* priority 40 sensorInvalid: owner FaultLatchRecoveryManager from * */
    } else if (!temperatureValid) {
        controller->state = TOY_PROTECTION_STATE_SENSOR_FAULT;
        controller->fanDuty = controller->safeDuty;
        controller->deratingCommand = 0.0f;
        controller->diagnosticFault = true;
        controller->safeCommandActive = true;
    /* priority 50 derating: owner DeratingCommandManager from * */
    } else if (temperatureC >= controller->deratingEntryThreshold) {
        controller->state = TOY_PROTECTION_STATE_DERATING;
        controller->fanDuty = controller->deratingFanDuty;
        controller->deratingCommand = controller->deratingLimit;
        controller->diagnosticFault = false;
        controller->safeCommandActive = false;
    /* priority 60 highCooling: owner CoolingCommandManager from * */
    } else if (temperatureC >= controller->coolingOnThreshold) {
        controller->state = TOY_PROTECTION_STATE_COOLING;
        controller->fanDuty = controller->coolingDuty;
        controller->deratingCommand = 0.0f;
        controller->diagnosticFault = false;
        controller->safeCommandActive = false;
    /* priority 70 lowCooling: owner CoolingCommandManager from * */
    } else if (temperatureC <= controller->coolingOffThreshold) {
        controller->state = TOY_PROTECTION_STATE_IDLE;
        controller->fanDuty = 0.0f;
        controller->deratingCommand = 0.0f;
        controller->diagnosticFault = false;
        controller->safeCommandActive = false;
    }

    hal_pwm_set_fan_duty(controller->fanDuty);
    hal_load_limiter_set_derating(controller->deratingCommand);
}
