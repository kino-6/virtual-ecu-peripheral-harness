#ifndef ECU_APP_HAL_SPI_H
#define ECU_APP_HAL_SPI_H

#include <stdint.h>

typedef enum {
    HAL_SPI_OK = 0,
    HAL_SPI_TIMEOUT = 1,
    HAL_SPI_ERROR = 2
} HalSpiStatus;

HalSpiStatus HalSpi_ReadRegister(uint8_t register_address, uint8_t *value);
HalSpiStatus HalSpi_WriteRegister(uint8_t register_address, uint8_t value);

#endif
