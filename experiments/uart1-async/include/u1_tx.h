/* SPDX-License-Identifier: MIT
 * Application RAM only. The port owner supplies admission and atomic service.
 * This core neither installs a vector nor reads/writes UART registers.
 */
#ifndef U1_TX_H
#define U1_TX_H
#include <stdint.h>

#ifdef AGONDEV
typedef uint24_t u1_count;
#else
typedef uint32_t u1_count;
#endif
typedef void (*u1_callback)(void);
/* Called once per service, with 1..burst bytes. False means uncertain writes. */
typedef uint8_t (*u1_emit)(const uint8_t *, uint8_t);

enum { U1_OK=0, U1_INVALID=19, U1_BUSY=31, U1_UNSAFE=32, U1_UNAVAILABLE=35 };
enum { U1_IDLE, U1_SOURCE, U1_TAIL, U1_FAULT, U1_DETACHED };
enum { U1_NO_FAULT, U1_OWNER_LOST, U1_LINE_ERROR, U1_WRITE_UNCERTAIN };
/* These are APPLICATION effects, not IER bit values or a numeric MOS ABI.
 * TX: owner enables TX-empty. RETRY: TX-empty off; owner retry source required.
 * Neither: owner disables this TX demand, retaining RX and other enables.
 */
enum { U1_TX=1, U1_RETRY=2, U1_RELEASED=4, U1_DRAINED=8 };
typedef struct {
    uint8_t owner, thre, cts, temt, error;
} u1_sample;
typedef struct {
    const uint8_t *source;
    u1_count remaining;
    u1_callback callback;
    uint8_t phase, burst, stopping, fault, fault_error;
} u1_tx;

/* New storage only, before installing an adapter. reserve is an explicit peer
 * headroom CONTRACT, not measured FIFO space. 1<=burst<=reserve<=16 required.
 * No-flow-control adapters must also provide an actual receiver contract.
 */
uint8_t u1_init(u1_tx *, uint8_t burst, uint8_t reserve);
/* Owner serializes every call against IRQ/tick service. Prearm caller flags
 * before start. After OK apply TX demand atomically before restoring entry IFF.
 * Assembly adapter will use HL=source/BC=full count/DE=callback; no RST assigned.
 */
uint8_t u1_start(u1_tx *, const uint8_t *, u1_count, u1_callback);
/* Owner saves interrupted regs, services RX/errors first, and supplies one
 * consistent admitted sample. Interrupts are excluded during this bounded step.
 * Callback runs here, after source retirement; it may precede submit return.
 * Target callback: flag-only assembly RET, no MOS/output/EI/reentrancy.
 */
uint8_t u1_step(u1_tx *, u1_sample, u1_emit);
/* Stop refuses new sources; it continues the existing source, not cancellation. */
void u1_stop(u1_tx *);
/* Logical detach only. Actual hook/vector retirement is the owner's operation,
 * after idle and positive removal. This NEVER clears live or faulted storage.
 */
uint8_t u1_detach(u1_tx *);
#endif
