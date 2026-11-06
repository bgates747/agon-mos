/* SPDX-License-Identifier: MIT
 * Standalone port adapter. Not an EMOS hook or resident firmware engine.
 */
#include <agon/mos.h>
#include "u1_vanilla.h"
#ifdef AGONDEV
_Static_assert(sizeof(UART)==8,"MOS UART config must use three-byte baud");
#endif
extern uint8_t u1_context(void),u1_lock(void);
extern void u1_unlock(uint8_t);
extern uint8_t u1_lsr(void),u1_rbr(void),u1_ier(void);
extern void u1_set_ier(uint8_t);
extern uint8_t u1_emit_uart1(const uint8_t *,uint8_t);
extern void u1_vanilla_irq(void);
static u1_tx tx;
static uint8_t attached,*ring,line_errors;
static uint16_t head,tail,mask;
static u1_count received,overflows;
static void (*previous)(void);
#define BARRIER() __asm__ volatile("":::"memory")
static uint8_t lock(void) { BARRIER();uint8_t x=u1_lock();BARRIER();return x; }
static void unlock(uint8_t x) { BARRIER();u1_unlock(x);BARRIER(); }
static uint8_t observe(void) {
    uint8_t status=u1_lsr(),errors=status&0x9e;
    if(errors) {
        line_errors|=errors;
        u1_report_fault(&tx,U1_LINE_ERROR,errors);
    }
    return status;
}
static void demand(uint8_t effect) {
    uint8_t ier=u1_ier()&0xfd; /* Preserve RX/line/other enables. */
    if(effect&U1_TX)ier|=2;
    u1_set_ier(ier);
}

uint8_t u1_vanilla_open(u1_count baud,uint8_t *rx,uint16_t capacity) {
    uint8_t irq,result;
    UART cfg;
    if(!rx || capacity<2 || capacity>4096 || (capacity&(capacity-1)) ||
       (uintptr_t)rx>UINTPTR_MAX-(capacity-1) || baud<300 || baud>1152000UL)
        return U1_INVALID;
    if(u1_context())return U1_UNSAFE;
    irq=lock();
    if(attached || u1_ier()) { unlock(irq);return U1_BUSY; }
    (void)u1_init(&tx,16,16); /* Local FIFO batching; peer pacing is external. */
    ring=rx;mask=capacity-1;head=tail=0;received=overflows=0;line_errors=0;
    previous=(void(*)(void))mos_setintvector(0x1a,u1_vanilla_irq);
    cfg.baudRate=baud;cfg.dataBits=8;cfg.stopBits=1;cfg.parity=0;
    cfg.flowcontrol=0;cfg.eir=5; /* RX and line errors, no modem or TX yet. */
    result=mos_uopen(&cfg);
    if(result) {
        mos_uclose();(void)mos_setintvector(0x1a,previous);ring=0;
        unlock(irq);return U1_UNAVAILABLE;
    }
    attached=1;unlock(irq);return U1_OK;
}

uint8_t u1_vanilla_submit(const uint8_t *source,u1_count n,u1_callback cb) {
    uint8_t irq,result;
    if(u1_context())return U1_UNSAFE;
    irq=lock();
    if(!attached)result=U1_UNAVAILABLE;
    else {
        /* Tail can be retired before another submit, without a finish syscall. */
        uint8_t status=observe();
        if(tx.phase==U1_TAIL) {
            u1_sample s={1,0,1,(uint8_t)((status&0x40)!=0),0};
            (void)u1_step(&tx,s,0);
        }
        if(tx.phase==U1_FAULT)demand(0);
        result=u1_start(&tx,source,n,cb);
        if(result==U1_OK)demand(U1_TX);
    }
    unlock(irq);return result;
}

/* Full interrupt wrapper in u1_vanilla_io.src saves primary, index and shadow
 * registers. One bounded RX drain first, then at most one TX FIFO refill.
 * The same code is compiled against fake I/O for host byte/event checks.
 */
void u1_vanilla_service(void) {
    uint8_t status=0;
    if(!attached)return;
    for(unsigned count=0;count<16;++count) {
        status=observe();
        if(!(status&1))break;
        uint8_t value=u1_rbr();uint16_t next=(head+1)&mask;
        if(received<0xffffffUL)++received;
        if(next==tail) {
            if(overflows<0xffffffUL)++overflows;
            u1_report_fault(&tx,U1_RX_OVERFLOW,0);
        } else { ring[head]=value;head=next; }
    }
    /* Use the last acknowledging LSR sample; never hide an RX error by reread. */
    u1_sample s={1,(uint8_t)((status&0x20)!=0),1,
                   (uint8_t)((status&0x40)!=0),0};
    demand(u1_step(&tx,s,u1_emit_uart1));
}

uint8_t u1_vanilla_finish(void) {
    uint8_t irq=lock(),result=U1_UNAVAILABLE;
    if(attached) {
        uint8_t status=observe();
        if(tx.phase==U1_TAIL) {
            u1_sample s={1,0,1,(uint8_t)((status&0x40)!=0),0};
            (void)u1_step(&tx,s,0);
        }
        if(tx.phase!=U1_FAULT)result=(tx.phase==U1_IDLE && (status&0x40))?U1_OK:U1_BUSY;
        if(tx.phase==U1_FAULT)demand(0);
    }
    unlock(irq);return result;
}
int u1_vanilla_read(void) {
    uint8_t irq=lock();int result=-1;
    if(attached && tail!=head) { result=ring[tail];tail=(tail+1)&mask; }
    unlock(irq);return result;
}
void u1_vanilla_stop(void) {
    uint8_t irq=lock();if(attached)u1_stop(&tx);unlock(irq);
}
void u1_vanilla_snapshot(u1_vanilla_info *s) {
    uint8_t irq=lock();
    s->phase=tx.phase;s->fault=tx.fault;s->first_error=tx.fault_error;
    s->line_errors=line_errors;s->received=received;s->overflows=overflows;
    s->buffered=(head-tail)&mask;unlock(irq);
}
uint8_t u1_vanilla_close(void) {
    uint8_t irq=lock();void (*current)(void);
    if(!attached) { unlock(irq);return U1_OK; }
    if(tx.source || tx.callback) { unlock(irq);return U1_BUSY; }
    /* Atomic public-API exchange/check; restore a later owner's vector if it
     * replaced ours. Do not close its UART or clobber its enable bits. */
    current=(void(*)(void))mos_setintvector(0x1a,u1_vanilla_irq);
    if(current!=u1_vanilla_irq) {
        (void)mos_setintvector(0x1a,current);unlock(irq);return U1_BUSY;
    }
    uint8_t status=observe();
    if(!(status&0x40)) { unlock(irq);return U1_BUSY; }
    mos_uclose();(void)mos_setintvector(0x1a,previous);
    attached=0;tx.phase=U1_DETACHED;ring=0;
    unlock(irq);return U1_OK;
}
