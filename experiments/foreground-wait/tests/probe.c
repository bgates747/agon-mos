#include "aw_wait.h"
static volatile uint8_t clock_bytes[4];
aw_state probe_state=AW_INITIALIZER;
uint8_t probe(aw_state *s) {
    uint8_t r=aw_begin(s);
    if(r!=AW_PASS)return r;
    return aw_wait(s);
}
uint8_t bind_probe(void) {
    probe_state.clock=clock_bytes;
    aw_notify(&probe_state);
    return probe(&probe_state);
}
