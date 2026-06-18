/* Preview-only HAL boundary for a fictional virtual temperature IC. */
#ifndef TOY_HAL_SPI_H
#define TOY_HAL_SPI_H

#include <stdbool.h>

float hal_spi_read_temperature_c(bool *valid);
bool hal_spi_read_invalid_debounced(void);
bool hal_spi_read_recovery_request(void);

#endif /* TOY_HAL_SPI_H */
