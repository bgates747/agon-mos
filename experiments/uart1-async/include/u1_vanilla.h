/* SPDX-License-Identifier: MIT */
#ifndef U1_VANILLA_H
#define U1_VANILLA_H
#include "u1_tx.h"

/* Single application, vanilla MOS 1.03+ UART1/vector APIs, ADL1/MB0.
 * UART1 MUST be otherwise unused. Not for EMOS or another resident owner.
 * No flow control: connected peer must supply application-level pacing.
 * RX storage remains resident through positive close. Capacity power of two,
 * 2..4096; usable bytes capacity-1. Baud 300..1152000, MOS divisor semantics.
 */
uint8_t u1_vanilla_open(u1_count baud, uint8_t *rx, uint16_t capacity);
/* C entry. Prearm callback flags. Full positive count, immutable source until
 * callback. EI/MB0 must remain true while installed. No MOS UART1 writes during
 * an outstanding transfer; ordinary UART0 remains independent.
 */
uint8_t u1_vanilla_submit(const uint8_t *, u1_count, u1_callback);
/* Nonblocking: OK only after actual UART TEMT; BUSY otherwise. No TX polling.
 * Source release alone is not wire-empty or module/remote acceptance.
 */
uint8_t u1_vanilla_finish(void);
int u1_vanilla_read(void); /* -1 empty/closed; otherwise 0..255. */
void u1_vanilla_stop(void); /* Drain existing transfer, refuse another. */
uint8_t u1_vanilla_close(void); /* Refuses live source/wire/foreign vector. */
typedef struct {
    u1_count received, overflows;
    uint16_t buffered;
    uint8_t phase, fault, first_error, line_errors;
} u1_vanilla_info;
void u1_vanilla_snapshot(u1_vanilla_info *);

/* Assembly CALL u1_vanilla_submit_regs: HL=source BC=count DE=callback, A=result.
 * Preserves BC/DE/HL/IX/IY/shadows/MB; flags unspecified. Not a MOS syscall.
 * C callers use u1_vanilla_submit above, not this register entry.
 */
#endif
