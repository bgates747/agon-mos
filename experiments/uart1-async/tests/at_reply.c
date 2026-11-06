/* SPDX-License-Identifier: MIT */
#include "../fixture/at_reply.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t feed(at_reply *p,const char *s) {
    while(*s && !p->result)at_reply_byte(p,(uint8_t)*s++);
    return p->result;
}
int main(void) {
    at_reply p;
    at_reply_init(&p);assert(feed(&p,"AT\r\n\r\nOK\r\n")==AT_OK);
    at_reply_init(&p);assert(feed(&p,"SEND OK\r\n")==AT_WAIT);
    assert(feed(&p,"AT version:1.3.0.0\r\nSDK version:2.0.0\r\nOK\r\n")==AT_OK);
    assert(p.at_version && p.sdk_version);
    const char *bad[]={"ERROR\r\n","FAIL\r\n","busy p...\r\n","CLOSED\r\n","+IPD,6:\r\nOK\r\n"};
    for(unsigned i=0;i<sizeof(bad)/sizeof(bad[0]);++i) {
        at_reply_init(&p);assert(feed(&p,bad[i])==AT_FAIL);
    }
    at_reply_init(&p);assert(at_reply_byte(&p,0)==AT_FAIL);
    at_reply_init(&p);for(unsigned i=0;i<192;++i)at_reply_byte(&p,'A');assert(p.result==AT_FAIL);
    at_reply_init(&p);for(unsigned i=0;i<200;++i)feed(&p,"X\r\n");assert(p.result==AT_FAIL);
    puts("U1 AT query parser PASS: echo/version/terminal/overflow/IPD-negative cases; no peer");
    return 0;
}
