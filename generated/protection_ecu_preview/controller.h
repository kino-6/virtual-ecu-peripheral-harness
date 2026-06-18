/* Generated preview-only controller scaffold.
 * Synthetic example; not production-derived and not certified.
 */
#ifndef TOYTHERMALPROTECTIONCONTROLLER_CONTROLLER_H
#define TOYTHERMALPROTECTIONCONTROLLER_CONTROLLER_H

#include <stdbool.h>

typedef enum {
    TOY_PROTECTION_STATE_RESET = 0,
    TOY_PROTECTION_STATE_IDLE = 1,
    TOY_PROTECTION_STATE_COOLING = 2,
    TOY_PROTECTION_STATE_DERATING = 3,
    TOY_PROTECTION_STATE_SENSOR_FAULT = 4,
    TOY_PROTECTION_STATE_FAULT_LATCHED = 5
} ToyProtectionState;

typedef struct {
    ToyProtectionState state;
    float coolingOnThreshold;
    float coolingOffThreshold;
    float deratingEntryThreshold;
    float coolingDuty;
    float deratingFanDuty;
    float deratingLimit;
    float safeDuty;
    float fanDuty;
    float deratingCommand;
    bool diagnosticFault;
    bool safeCommandActive;
} ToyThermalProtectionController;

void toy_thermal_protection_controller_init(ToyThermalProtectionController *controller);
void toy_thermal_protection_controller_step(ToyThermalProtectionController *controller);

#endif /* TOYTHERMALPROTECTIONCONTROLLER_CONTROLLER_H */
