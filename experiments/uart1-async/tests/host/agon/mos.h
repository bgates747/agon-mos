/* SPDX-License-Identifier: MIT -- test declarations, no copied SDK code. */
#ifndef U1_TEST_MOS_H
#define U1_TEST_MOS_H
#include <stdint.h>
typedef struct {
    uint32_t baudRate;
    uint8_t dataBits,stopBits,parity,flowcontrol,eir;
} UART;
void *mos_setintvector(uint8_t,void(*)(void));
uint8_t mos_uopen(UART *);
void mos_uclose(void);
#endif
