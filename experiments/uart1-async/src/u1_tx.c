/* SPDX-License-Identifier: MIT */
#include "u1_tx.h"

uint8_t u1_init(u1_tx *t, uint8_t burst, uint8_t reserve) {
    if (!t || !burst || burst>reserve || reserve>16) return U1_INVALID;
    t->source=0; t->remaining=0; t->callback=0;
    t->phase=U1_IDLE; t->burst=burst; t->stopping=0;
    t->fault=U1_NO_FAULT; t->fault_error=0;
    return U1_OK;
}

uint8_t u1_start(u1_tx *t, const uint8_t *source, u1_count n, u1_callback callback) {
    if (!t || !source || !callback || !n || n>0xffffffUL ||
        (uintptr_t)source>UINTPTR_MAX-(n-1)) return U1_INVALID;
    if (t->phase==U1_SOURCE || t->phase==U1_TAIL) return U1_BUSY;
    if (t->phase!=U1_IDLE || t->stopping) return U1_UNAVAILABLE;
    t->source=source; t->remaining=n; t->callback=callback;
    t->phase=U1_SOURCE;
    return U1_OK;
}

static void fail(u1_tx *t, uint8_t reason, uint8_t error) {
    if (!t->fault) { t->fault=reason; t->fault_error=error; }
    t->phase=U1_FAULT;
}

uint8_t u1_step(u1_tx *t, u1_sample s, u1_emit emit) {
    uint8_t n;
    u1_callback callback;
    if (t->phase==U1_IDLE || t->phase==U1_DETACHED || t->phase==U1_FAULT) return 0;
    if (!s.owner) { fail(t,U1_OWNER_LOST,s.error); return 0; }
    if (s.error) { fail(t,U1_LINE_ERROR,s.error); return 0; }
    if (t->phase==U1_TAIL) {
        if (!s.temt) return U1_RETRY;
        t->phase=U1_IDLE;
        return U1_DRAINED;
    }
    if (!s.cts) return U1_RETRY;
    if (!s.thre) return U1_TX;
    n=t->remaining<t->burst ? (uint8_t)t->remaining : t->burst;
    /* A partial/unknown write cannot release the source or be retried. */
    if (!emit || !emit(t->source,n)) { fail(t,U1_WRITE_UNCERTAIN,s.error); return 0; }
    t->remaining-=n;
    if (t->remaining) { t->source+=n; return U1_TX; }
    /* Pre-write TEMT is stale after this write. Require a LATER sample. */
    callback=t->callback; t->callback=0; t->source=0; t->phase=U1_TAIL;
    callback();
    return U1_RELEASED|U1_RETRY;
}

void u1_stop(u1_tx *t) { t->stopping=1; }

uint8_t u1_detach(u1_tx *t) {
    if (t->phase!=U1_IDLE) return U1_BUSY;
    t->phase=U1_DETACHED;
    return U1_OK;
}
