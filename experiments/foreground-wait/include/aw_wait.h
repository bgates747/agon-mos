/* SPDX-License-Identifier: MIT
 * Application-only AgonDev/eZ80 ADL1/MB0 foreground notification handoff.
 * No vector, MOS, UART or timer ownership. Source-only/native-build candidate.
 */
#ifndef AW_WAIT_H
#define AW_WAIT_H
#include <stdint.h>
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif

enum { AW_REFUSED=0, AW_PASS=1, AW_WORK=2, AW_HALTED=3 };
typedef struct __attribute__((packed)) {
    volatile uint8_t pending; /* producers only STORE 1; begin alone clears */
    uint8_t pass_valid;
    uint8_t pass_clock[4];
    const volatile uint8_t *clock; /* stable public MOS clock32, not private RAM */
} aw_state;
#define AW_INITIALIZER {0,0,{0,0,0,0},0}

/* Initialize once before attaching producers, then bind clock from public
 * mos_sysvars()+sysvar_time outside DI. Valid distinct nonwrapping RAM spans:
 * state9 bytes, clock4 bytes; clock remains stable for the whole association.
 * Do not reinitialize/free/rebind while any callback can access this object.
 * One foreground caller, no recursive begin/wait; ISR code only notifies.
 */
uint8_t aw_begin(aw_state *); /* AW_PASS or AW_REFUSED; before ALL service */
uint8_t aw_wait(aw_state *);  /* consumes pass: WORK, HALTED or REFUSED */
/* Call AFTER payload/ready/phase publication, with actual callback ABI saves.
 * Caller supplies a valid live object. This is a coalesced hint, not completion.
 * The caller must supply any compiler barrier needed around nonvolatile state.
 */
static inline void aw_notify(aw_state *s) { s->pending=1; }

/* Both leaves require actual ADL1 and enabled entry IFF, and refuse observed
 * MB!=0, IFF0, NULL state/clock. Refusal never EI/HALT. aw_wait also refuses
 * a missing begin token. Enabled entry is restored on ordinary return.
 * Result BYTE is A; flags unspecified. BC/DE/HL/IX/IY/shadows/SP/MB preserved.
 * HALTED means HALT executed, not a measured sleep duration. Recheck real state.
 */
#if defined(__ez80__)
typedef char aw_pending_offset[(offsetof(aw_state,pending)==0)?1:-1];
typedef char aw_valid_offset[(offsetof(aw_state,pass_valid)==1)?1:-1];
typedef char aw_token_offset[(offsetof(aw_state,pass_clock)==2)?1:-1];
typedef char aw_clock_offset[(offsetof(aw_state,clock)==6)?1:-1];
typedef char aw_state_extent[(sizeof(aw_state)==9)?1:-1];
#endif
#ifdef __cplusplus
}
#endif
#endif
