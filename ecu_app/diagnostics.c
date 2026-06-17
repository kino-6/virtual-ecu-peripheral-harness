#include "hal_gpio.h"
#include "hal_spi.h"

#define TOY_STATUS_REGISTER 0x01u
#define TOY_STATUS_READY_MASK 0x80u
#define TOY_STATUS_UNDERVOLTAGE_MASK 0x01u

static uint8_t g_last_status;
static bool g_spi_timeout_seen;

void Diagnostics_PollPowerMonitor(void)
{
    uint8_t status = 0u;
    HalSpiStatus spi_status = HalSpi_ReadRegister(TOY_STATUS_REGISTER, &status);

    if (spi_status == HAL_SPI_TIMEOUT) {
        g_spi_timeout_seen = true;
        HalGpio_Write(TOY_POWER_MONITOR_READY, false);
        return;
    }

    if (spi_status != HAL_SPI_OK) {
        HalGpio_Write(TOY_POWER_MONITOR_READY, false);
        return;
    }

    g_last_status = status;
    HalGpio_Write(TOY_POWER_MONITOR_READY, (status & TOY_STATUS_READY_MASK) != 0u);
}

bool Diagnostics_IsPowerMonitorReady(void)
{
    return (g_last_status & TOY_STATUS_READY_MASK) != 0u;
}

bool Diagnostics_HasUndervoltageFault(void)
{
    return (g_last_status & TOY_STATUS_UNDERVOLTAGE_MASK) != 0u;
}

bool Diagnostics_HasSpiTimeout(void)
{
    return g_spi_timeout_seen;
}
