// MOS UART0 diagnostic additions. SPDX-License-Identifier: MIT
// Included in a private copy of ESP-IDF uart.c after its driver state definitions.
// Original driver operations remain in place. No hook is armed at boot.
#include <stdint.h>
static volatile uint32_t race_armed, race_trigger, race_published, race_recovered, race_masked, race_expired, race_errors;
static uint8_t race_events[4][24];
static uint32_t race_cycles(void) { uint32_t n; __asm__ volatile("rsr.ccount %0":"=a"(n)); return n; }
static void race_barrier(void) { __asm__ volatile("memw" ::: "memory"); }
static void race_put32(uint8_t *p, uint32_t n) { for (unsigned i=0;i<4;i++) p[i]=n>>(8*i); }
static void race_event(unsigned slot, unsigned type) {
    uart_obj_t *p=p_uart_obj[UART_NUM_2];
    uart_dev_t *hw=uart_context[UART_NUM_2].hal.dev;
    uint8_t *e=race_events[slot];
    e[0]=type;e[1]=xPortGetCoreID();e[2]=p->rx_buffer_full_flg;e[3]=uart_hal_get_rxfifo_len(&uart_context[UART_NUM_2].hal);
    race_put32(e+4,hw->int_ena.val);race_put32(e+8,hw->int_raw.val);
    race_put32(e+12,p->rx_buffered_len);race_put32(e+16,p->rx_stash_len);race_put32(e+20,race_cycles());
    race_barrier();
}
static void race_after_publish(uart_port_t uart_num) {
    if (uart_num!=UART_NUM_2 || !race_armed || race_published) return;
    race_event(0,1);race_published=1;race_barrier();
    if (race_trigger) {
        uint32_t start=race_cycles();
        // At 240 MHz, at most 10 ms. Never wait under the UART lock.
        while (!race_recovered && (uint32_t)(race_cycles()-start)<2400000U) race_barrier();
        if (!race_recovered) race_expired=1;
    }
}
static void race_after_recovery(uart_port_t uart_num) {
    if (uart_num!=UART_NUM_2 || !race_armed || !race_published || race_recovered) return;
    race_event(1,2);race_recovered=1;race_barrier();
}
static void race_after_mask(uart_port_t uart_num) {
    if (uart_num!=UART_NUM_2 || !race_armed || !race_published || race_masked) return;
    race_event(2,3);race_masked=1;race_barrier();
}
static void race_note_interrupt(uart_port_t uart_num,uint32_t status) {
    if(uart_num==UART_NUM_2 && race_armed) race_errors |= status & 0x9c;
}
void uart0_race_arm(unsigned trigger) {
    race_armed=0;race_barrier();
    memset(race_events,0,sizeof(race_events));
    race_trigger=trigger;race_published=race_recovered=race_masked=race_expired=race_errors=0;
    race_barrier();race_armed=1;
}
unsigned uart0_race_state(void) {
    race_barrier();return (race_published?1:0)|(race_recovered?2:0)|(race_masked?4:0)|(race_expired?8:0);
}
void uart0_race_snapshot(uint8_t *r) {
    uart_obj_t *p=p_uart_obj[UART_NUM_2];uart_dev_t *hw=uart_context[UART_NUM_2].hal.dev;
    // This is a stopped-progress observation, not an atomic driver snapshot.
    race_put32(r+24,uart_hal_get_rxfifo_len(&uart_context[UART_NUM_2].hal));
    race_put32(r+28,hw->int_ena.val);race_put32(r+32,hw->int_raw.val);
    race_put32(r+36,p->rx_buffer_full_flg);race_put32(r+40,p->rx_buffered_len);
    race_put32(r+44,p->rx_stash_len);race_put32(r+48,p->rx_cur_remain);
    r[52]=race_events[0][1];r[53]=xPortGetCoreID();r[54]=hw->conf1.rx_flow_en;r[55]=hw->conf1.rx_flow_thrhd;
}
void uart0_race_escape(void) {
    // Explicit diagnostic intervention only, after saved pre-intervention state.
    uart_enable_intr_mask(UART_NUM_2,UART_INTR_RXFIFO_TOUT|UART_INTR_RXFIFO_FULL);
    race_event(3,4);
}
void uart0_race_collect(uint8_t *r) {
    race_armed=0;race_barrier();
    memcpy(r+64,race_events,sizeof(race_events));
    race_put32(r+16,race_errors | (uart_context[UART_NUM_2].hal.dev->int_raw.val & 0x9c));
    r[6]=0;for(unsigned i=0;i<4;i++) if(race_events[i][0]) ++r[6];
    race_put32(r+20,uart0_race_state());race_put32(r+56,uart_context[UART_NUM_2].hal.dev->int_ena.val);
}
