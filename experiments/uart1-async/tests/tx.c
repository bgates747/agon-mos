/* SPDX-License-Identifier: MIT
 * Runs the real portable core against a finite byte/event oracle. No UART.
 */
#include "u1_tx.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

static uint8_t input[65536],wire[65536];
static unsigned used,calls,callbacks,early,returned,checks;
static u1_tx tx;
static u1_sample ready={1,1,1,1,0};
#define CHECK(x) do { assert(x); ++checks; } while(0)

static void callback(void) {
    CHECK(tx.phase==U1_TAIL && tx.source==0 && tx.remaining==0);
    ++callbacks; if(!returned)++early;
}
static uint8_t emit(const uint8_t *p,uint8_t n) {
    CHECK(n>0 && n<=tx.burst && n<=16);
    CHECK(used+n<=sizeof(wire));
    memcpy(wire+used,p,n);used+=n;++calls;
    return 1;
}
static uint8_t partial(const uint8_t *p,uint8_t n) {
    CHECK(n==16);memcpy(wire,p,7);used=7;++calls;return 0;
}
static void fresh(unsigned burst) {
    CHECK(u1_init(&tx,(uint8_t)burst,(uint8_t)burst)==U1_OK);
    used=calls=callbacks=early=returned=0;
    memset(wire,0,sizeof(wire));
}
static void transfer(unsigned n,unsigned burst) {
    unsigned iterations=0;
    fresh(burst);
    CHECK(u1_start(&tx,input,n,callback)==U1_OK);
    while(tx.phase==U1_SOURCE) {
        unsigned before=used;uint8_t effects=u1_step(&tx,ready,emit);
        CHECK(used-before<=burst && used-before>0);
        if(tx.phase==U1_SOURCE) CHECK(effects==U1_TX && !callbacks);
        else CHECK(effects==(U1_RELEASED|U1_RETRY) && callbacks==1);
        CHECK(++iterations<=n);
    }
    CHECK(calls==(n+burst-1)/burst && used==n && !memcmp(wire,input,n));
    CHECK(callbacks==1 && early==1);returned=1;
    CHECK(u1_start(&tx,input,1,callback)==U1_BUSY);
    CHECK(u1_detach(&tx)==U1_BUSY); /* Pre-write TEMT never retires new bytes. */
    u1_sample tail=ready;tail.temt=0;
    CHECK(u1_step(&tx,tail,emit)==U1_RETRY && tx.phase==U1_TAIL);
    CHECK(u1_step(&tx,ready,emit)==U1_DRAINED && tx.phase==U1_IDLE);
    CHECK(u1_step(&tx,ready,emit)==0 && callbacks==1);
    CHECK(u1_detach(&tx)==U1_OK && tx.phase==U1_DETACHED);
}
static void refusals(void) {
    u1_tx prior;
    fresh(16);prior=tx;
    CHECK(u1_init(&tx,0,16)==U1_INVALID && !memcmp(&tx,&prior,sizeof(tx)));
    CHECK(u1_init(&tx,16,15)==U1_INVALID && !memcmp(&tx,&prior,sizeof(tx)));
    CHECK(u1_init(&tx,17,17)==U1_INVALID && !memcmp(&tx,&prior,sizeof(tx)));
    CHECK(u1_start(&tx,0,1,callback)==U1_INVALID);
    CHECK(u1_start(&tx,input,0,callback)==U1_INVALID);
    CHECK(u1_start(&tx,input,1,0)==U1_INVALID);
    CHECK(u1_start(&tx,input,0x1000000UL,callback)==U1_INVALID);
    CHECK(u1_start(&tx,(const uint8_t*)UINTPTR_MAX,2,callback)==U1_INVALID);
    CHECK(!memcmp(&tx,&prior,sizeof(tx)) && !callbacks && !used);
    CHECK(u1_start(&tx,input,17,callback)==U1_OK);prior=tx;
    CHECK(u1_start(&tx,input+20,1,callback)==U1_BUSY);
    CHECK(!memcmp(&tx,&prior,sizeof(tx)) && !callbacks && !used);
}
static void waits_and_stop(void) {
    u1_sample s=ready;
    fresh(16);CHECK(u1_start(&tx,input,17,callback)==U1_OK);
    s.cts=0;
    for(unsigned i=0;i<100;++i)CHECK(u1_step(&tx,s,emit)==U1_RETRY);
    CHECK(!used && !callbacks && tx.remaining==17);
    s.cts=1;s.thre=0;CHECK(u1_step(&tx,s,emit)==U1_TX && !used);
    /* Owner retry resamples after GPIO CTS changes; one burst per invocation. */
    s.thre=1;CHECK(u1_step(&tx,s,emit)==U1_TX && used==16);
    u1_stop(&tx);CHECK(u1_start(&tx,input,1,callback)==U1_BUSY);
    s.cts=0;CHECK(u1_step(&tx,s,emit)==U1_RETRY && used==16);
    s.cts=1;CHECK(u1_step(&tx,s,emit)==(U1_RELEASED|U1_RETRY));
    CHECK(used==17 && !memcmp(input,wire,17) && callbacks==1);
    CHECK(u1_step(&tx,s,emit)==U1_DRAINED);
    CHECK(u1_start(&tx,input,1,callback)==U1_UNAVAILABLE);
    CHECK(u1_detach(&tx)==U1_OK);
}
static void faults(void) {
    u1_sample s=ready;
    fresh(16);CHECK(u1_start(&tx,input,146,callback)==U1_OK);
    s.error=2;CHECK(!u1_step(&tx,s,emit));
    CHECK(tx.phase==U1_FAULT && tx.fault==U1_LINE_ERROR && tx.fault_error==2);
    CHECK(tx.source==input && tx.remaining==146 && !used && !callbacks);
    s.owner=0;s.error=8;CHECK(!u1_step(&tx,s,emit));
    CHECK(tx.fault==U1_LINE_ERROR && tx.fault_error==2);
    u1_stop(&tx);CHECK(u1_detach(&tx)==U1_BUSY);
    CHECK(u1_start(&tx,input,1,callback)==U1_UNAVAILABLE);

    fresh(16);CHECK(u1_start(&tx,input,146,callback)==U1_OK);
    s=ready;s.owner=0;CHECK(!u1_step(&tx,s,emit));
    CHECK(tx.fault==U1_OWNER_LOST && tx.remaining==146 && !used);

    fresh(16);CHECK(u1_start(&tx,input,146,callback)==U1_OK);
    CHECK(!u1_step(&tx,ready,partial));
    CHECK(tx.phase==U1_FAULT && tx.fault==U1_WRITE_UNCERTAIN);
    CHECK(tx.source==input && tx.remaining==146 && used==7 && callbacks==0);
    CHECK(!u1_step(&tx,ready,emit) && used==7); /* Never repeat a partial write. */
    CHECK(u1_detach(&tx)==U1_BUSY);
}
static void interrupted_transfers(void) {
    uint32_t random=0x12345678u;
    for(unsigned trial=0;trial<256;++trial) {
        unsigned n=1+(trial*271u)%1024,budget=0;
        fresh(1+trial%16);CHECK(u1_start(&tx,input,n,callback)==U1_OK);
        while(tx.phase==U1_SOURCE) {
            u1_sample s=ready;unsigned before=used;
            random^=random<<13;random^=random>>17;random^=random<<5;
            s.cts=(random&3)!=0;s.thre=(random&12)!=0;
            (void)u1_step(&tx,s,emit);
            if(!s.cts || !s.thre)CHECK(used==before);
            CHECK(++budget<20000);
        }
        CHECK(used==n && callbacks==1 && !memcmp(input,wire,n));
        CHECK(u1_step(&tx,ready,emit)==U1_DRAINED);
    }
}
int main(void) {
    const unsigned lengths[]={1,15,16,17,146,65535,65536};
    for(unsigned i=0;i<sizeof(input);++i)input[i]=(uint8_t)(i*157u+7u);
    refusals();waits_and_stop();faults();
    for(unsigned i=0;i<sizeof(lengths)/sizeof(lengths[0]);++i)transfer(lengths[i],16);
    transfer(146,1);interrupted_transfers();
    printf("U1 core PASS: %u assertions; exact bytes/callback/lifetime/fault controls; no target\n",checks);
    return 0;
}
