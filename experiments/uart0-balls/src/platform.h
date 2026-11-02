#ifndef BALLS_PLATFORM_H
#define BALLS_PLATFORM_H
#include <agon/mos.h>
#include <stdint.h>
#define BD_TICK_HZ 1152000UL
#define BD_WALL_HZ 72000UL
extern uint24_t bd_hl,bd_de,bd_bc,bd_result_hl;
extern volatile uint24_t bd_timer1_wraps,bd_timer2_wraps;
extern volatile uint24_t bd_clock_wrap,bd_clock_count,bd_wall_wrap,bd_wall_count;
extern volatile uint24_t bd_notify_wrap,bd_notify_count,bd_notify_id,bd_notify_context;
extern volatile uint8_t bd_notify_status;
extern const uint8_t *bd_discover(void);
extern void bd_notify(void),bd_timer1_isr(void),bd_timer2_isr(void);
extern void bd_capture_clock(void),bd_capture_wall(void),bd_capture_notification(void);
extern uint8_t bd_api_call(void);
extern void *bd_api_function;
int clocks_start(void);
void clocks_stop(void);
uint32_t ticks(void),wall_ticks(void),notification_ticks(void);
void bd_keys_tick(void);
int key_pop(void);
extern volatile uint8_t key_overruns;
uint8_t api_call(unsigned,uint24_t,uint24_t,uint24_t);
int transport_open(unsigned),transport_close(void);
int transport_supported(void);
extern const uint8_t *bd_api;
#endif
