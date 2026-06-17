#ifndef ECU_APP_HAL_GPIO_H
#define ECU_APP_HAL_GPIO_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    TOY_POWER_MONITOR_READY = 0
} HalGpioPin;

bool HalGpio_Read(HalGpioPin pin);
void HalGpio_Write(HalGpioPin pin, bool value);

#endif
