/* Generated preview-only controller scaffold.
 * Synthetic example; not production-derived and not certified.
 */
#ifndef TOYTHERMALFANCONTROLLER_CONTROLLER_H
#define TOYTHERMALFANCONTROLLER_CONTROLLER_H

#include <stdbool.h>

typedef enum {
    TOY_THERMAL_STATE_RESET = 0,
    TOY_THERMAL_STATE_IDLE = 1,
    TOY_THERMAL_STATE_COOLING = 2,
    TOY_THERMAL_STATE_FAULT = 3
} ToyThermalFanState;

typedef struct {
    ToyThermalFanState state;
    float fanOnThreshold;
    float fanOffThreshold;
    float coolingDuty;
    float safeDuty;
    float fanDuty;
    bool fault;
} ToyThermalFanController;

void toy_thermal_fan_controller_init(ToyThermalFanController *controller);
void toy_thermal_fan_controller_step(ToyThermalFanController *controller);

#endif /* TOYTHERMALFANCONTROLLER_CONTROLLER_H */
