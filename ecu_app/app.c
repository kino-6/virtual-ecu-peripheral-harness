#include "hal_gpio.h"
#include "hal_spi.h"

#define TOY_CONTROL_REGISTER 0x02u
#define TOY_CONTROL_ENABLE_MONITORING 0x01u

void Diagnostics_PollPowerMonitor(void);
bool Diagnostics_IsPowerMonitorReady(void);
bool Diagnostics_HasUndervoltageFault(void);
bool Diagnostics_HasSpiTimeout(void);

typedef enum {
    APP_STARTING = 0,
    APP_MONITORING = 1,
    APP_FAULT = 2
} AppState;

static AppState g_app_state = APP_STARTING;

void App_Init(void)
{
    if (HalSpi_WriteRegister(TOY_CONTROL_REGISTER, TOY_CONTROL_ENABLE_MONITORING) != HAL_SPI_OK) {
        g_app_state = APP_FAULT;
        return;
    }

    g_app_state = APP_STARTING;
}

void App_Tick(void)
{
    Diagnostics_PollPowerMonitor();

    if (Diagnostics_HasSpiTimeout() || Diagnostics_HasUndervoltageFault()) {
        g_app_state = APP_FAULT;
        return;
    }

    if (Diagnostics_IsPowerMonitorReady() && HalGpio_Read(TOY_POWER_MONITOR_READY)) {
        g_app_state = APP_MONITORING;
    }
}

AppState App_GetState(void)
{
    return g_app_state;
}
