/* SPDX-License-Identifier: MIT
 * Executes actual adapter/core against a status-acknowledging fake port/MOS.
 */
#include "u1_vanilla.h"
#include <agon/mos.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
extern void u1_vanilla_service(void);
static uint8_t iff=1,mb,ier,thre=1,temt=1,errors,opened,deliver_on_unlock;
static uint8_t rx[1024],wire[65536],storage[512],source[65536];
static unsigned rh,rt,used,callbacks,checks,vecchanges,moscloses;
static void old_irq(void) {}
static void foreign_irq(void) {}
static void (*vector)(void)=old_irq;
#define CHECK(x) do { assert(x);++checks; } while(0)
uint8_t u1_context(void) { return (uint8_t)(mb || !iff); }
uint8_t u1_lock(void) { uint8_t prior=iff;iff=0;return prior; }
void u1_vanilla_irq(void) {
    CHECK(iff && vector==u1_vanilla_irq);iff=0;u1_vanilla_service();iff=1;
}
void u1_unlock(uint8_t x) {
    iff=x;
    if(deliver_on_unlock && iff && (ier&2) && thre) {
        deliver_on_unlock=0;u1_vanilla_irq();
    }
}
uint8_t u1_ier(void) { CHECK(!iff);return ier; }
void u1_set_ier(uint8_t x) { CHECK(!iff);ier=x; }
uint8_t u1_lsr(void) {
    uint8_t value=(uint8_t)((rh!=rt)|((thre!=0)<<5)|((temt!=0)<<6)|errors);
    CHECK(!iff);errors=0;return value;
}
uint8_t u1_rbr(void) { CHECK(!iff && rt<rh);return rx[rt++]; }
uint8_t u1_emit_uart1(const uint8_t *p,uint8_t n) {
    CHECK(!iff && thre && n>0 && n<=16 && used+n<=sizeof(wire));
    memcpy(wire+used,p,n);used+=n;thre=temt=0;return 1;
}
void *mos_setintvector(uint8_t number,void(*handler)(void)) {
    void (*prior)(void)=vector;CHECK(!iff && number==0x1a);
    vector=handler;++vecchanges;return (void*)prior;
}
uint8_t mos_uopen(UART *c) {
    CHECK(!iff && vector==u1_vanilla_irq && c->baudRate==115200);
    CHECK(c->dataBits==8 && c->stopBits==1 && !c->parity && !c->flowcontrol && c->eir==5);
    opened=1;ier=c->eir;thre=temt=1;return 0;
}
void mos_uclose(void) { CHECK(!iff);opened=0;ier=0;++moscloses; }
static void released(void) { CHECK(!iff);++callbacks; }
static void advance(void) {
    thre=temt=1;
    if((ier&2) || ((ier&5) && (rh!=rt || errors)))u1_vanilla_irq();
}
static void begin(unsigned capacity) {
    CHECK(!opened && !ier && vector==old_irq && iff);
    rh=rt=used=callbacks=0;
    CHECK(u1_vanilla_open(115200,storage,(uint16_t)capacity)==U1_OK);
    CHECK(iff && opened && ier==5);
}
static void finish(void) {
    advance();CHECK(u1_vanilla_finish()==U1_OK);
    CHECK(u1_vanilla_close()==U1_OK && !opened && !ier && vector==old_irq && iff);
}
static void transfer(unsigned length) {
    unsigned budget=0;
    begin(sizeof(storage));
    CHECK(u1_vanilla_submit(source,length,released)==U1_OK);
    CHECK(used==0 && (ier&2)); /* No foreground FIFO fill. */
    CHECK(u1_vanilla_submit(source,1,released)==U1_BUSY);
    CHECK(u1_vanilla_close()==U1_BUSY);
    while(!callbacks) { advance();CHECK(++budget<=length); }
    CHECK(used==length && callbacks==1 && !memcmp(wire,source,length));
    CHECK(!(ier&2) && (ier&5)==5 && u1_vanilla_finish()==U1_BUSY);
    CHECK(u1_vanilla_close()==U1_BUSY);finish();
}
int main(void) {
    const unsigned lengths[]={1,15,16,17,146,65535,65536};
    for(unsigned i=0;i<sizeof(source);++i)source[i]=(uint8_t)(i*157u+7u);
    CHECK(u1_vanilla_open(0,storage,8)==U1_INVALID);
    CHECK(u1_vanilla_open(115200,storage,3)==U1_INVALID && !vecchanges);
    iff=0;CHECK(u1_vanilla_open(115200,storage,8)==U1_UNSAFE && !iff);iff=1;
    ier=1;CHECK(u1_vanilla_open(115200,storage,8)==U1_BUSY && !vecchanges);ier=0;
    for(unsigned i=0;i<sizeof(lengths)/sizeof(lengths[0]);++i)transfer(lengths[i]);

    begin(8);rx[rh++]=0;rx[rh++]=255;rx[rh++]=42;
    CHECK(u1_vanilla_submit(source,1,released)==U1_OK);
    deliver_on_unlock=1;CHECK(u1_vanilla_read()==-1); /* IRQ arrives before return. */
    CHECK(callbacks==1 && rt==rh && used==1);
    CHECK(u1_vanilla_read()==0 && u1_vanilla_read()==255 && u1_vanilla_read()==42);
    CHECK(u1_vanilla_read()==-1);finish();

    begin(8);deliver_on_unlock=1;
    CHECK(u1_vanilla_submit(source,1,released)==U1_OK && callbacks==1);
    CHECK(u1_vanilla_finish()==U1_BUSY);advance();CHECK(u1_vanilla_finish()==U1_OK);
    unsigned closed=moscloses;vector=foreign_irq;errors=2;
    CHECK(u1_vanilla_close()==U1_BUSY && vector==foreign_irq && moscloses==closed);
    CHECK(errors==2); /* Foreign owner's acknowledging status must not be read. */
    errors=0;
    vector=u1_vanilla_irq;CHECK(u1_vanilla_close()==U1_OK && vector==old_irq);

    begin(8);CHECK(u1_vanilla_submit(source,17,released)==U1_OK);
    u1_vanilla_stop();while(!callbacks)advance();advance();
    CHECK(u1_vanilla_finish()==U1_OK && used==17);
    CHECK(u1_vanilla_submit(source,1,released)==U1_UNAVAILABLE);finish();

    begin(4);for(unsigned i=0;i<7;++i)rx[rh++]=(uint8_t)i;advance();
    u1_vanilla_info info;u1_vanilla_snapshot(&info);
    CHECK(info.received==7 && info.overflows==4 && info.buffered==3 && info.fault==U1_RX_OVERFLOW);
    CHECK(u1_vanilla_finish()==U1_UNAVAILABLE);
    CHECK(u1_vanilla_close()==U1_OK); /* No borrowed TX, wire empty, positive unhook. */

    begin(8);iff=0;
    CHECK(u1_vanilla_submit(source,1,released)==U1_UNSAFE && !iff && used==0);iff=1;
    mb=1;CHECK(u1_vanilla_submit(source,1,released)==U1_UNSAFE && iff);mb=0;finish();
    begin(8);iff=0;CHECK(u1_vanilla_close()==U1_OK && !iff);iff=1;

    /* Last case retains a genuinely borrowed faulted source; no fake cancel. */
    begin(8);CHECK(u1_vanilla_submit(source,146,released)==U1_OK);
    errors=2;rx[rh++]=17;advance();u1_vanilla_snapshot(&info);
    CHECK(info.fault==U1_LINE_ERROR && info.first_error==2 && info.received==1);
    CHECK(!used && !callbacks && !(ier&2) && (ier&5)==5);
    errors=4;advance();u1_vanilla_snapshot(&info);
    CHECK(info.first_error==2 && info.line_errors==6);
    CHECK(u1_vanilla_close()==U1_BUSY && opened && vector==u1_vanilla_irq);
    printf("U1 vanilla adapter PASS: %u assertions; actual C adapter, fake MOS/UART only\n",checks);
    return 0;
}
