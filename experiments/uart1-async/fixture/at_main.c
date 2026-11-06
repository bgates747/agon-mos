/* SPDX-License-Identifier: MIT
 * Console8 functional AT query fixture. No network or ESP config/flash writes.
 * This is NOT a continuous-throughput or CPU-capacity benchmark.
 */
#include <agon/mos.h>
#include <stdio.h>
#include <string.h>
#include "u1_vanilla.h"
#include "at_reply.h"
#include "run_counter.inc"
#include "u1_build_id.h"
extern uint8_t u1_lock(void);
extern void u1_unlock(uint8_t);
extern void u1_at_callback(void);
volatile uint8_t u1_at_done;
static uint8_t rx[512];
static struct {
    at_reply reply;
    uint32_t total,call;
    u1_count work;
    uint8_t mode,pass;
} cases[4];
static uint32_t now(void) {
    uint8_t irq=u1_lock();uint32_t stamp=sys_vars->time;u1_unlock(irq);return stamp;
}
static int query(unsigned cell,const char *command,uint8_t async) {
    uint32_t start=now();unsigned fuse=0;int c;
    cases[cell].mode=async;at_reply_init(&cases[cell].reply);u1_at_done=0;
    if(u1_vanilla_read()!=-1)return 0; /* No outstanding prior reply accepted. */
    if(async) {
        if(u1_vanilla_submit((const uint8_t*)command,(u1_count)strlen(command),u1_at_callback))return 0;
    } else {
        for(unsigned i=0;command[i];++i)if(!mos_uputc(command[i]))return 0;
        u1_at_done=1;
    }
    cases[cell].call=now()-start;
    for(;;) {
        while((c=u1_vanilla_read())>=0) {
            if(cases[cell].reply.result) {
                if(c!='\r' && c!='\n')return 0;
            } else if(at_reply_byte(&cases[cell].reply,(uint8_t)c)==AT_FAIL)return 0;
        }
        uint8_t drain=u1_vanilla_finish();
        if(drain!=U1_OK && drain!=U1_BUSY)return 0;
        if(u1_at_done && drain==U1_OK && cases[cell].reply.result==AT_OK)break;
        if(now()-start>480UL || ++fuse>1000000u)return 0;
        if(cases[cell].work<0xffffffUL)++cases[cell].work;
    }
    cases[cell].total=now()-start;cases[cell].pass=1;
    return 1;
}
int main(void) {
    const char *commands[]={"AT\r\n","AT+GMR\r\n","AT+GMR\r\n","AT\r\n"};
    const uint8_t modes[]={0,1,0,1};
    char name[16];unsigned run=first_report();uint8_t log,opened=0,result=1;
    putchar(12);
    puts("UART1 ESP8266 FUNCTIONAL CHECK - vanilla MOS, 115200 8N1, no CTS/RTS");
    puts("Build " U1_BUILD_ID);
    puts("Allow one minute. Longer than two minutes is wrong; report the last case.");
    puts("Requires idle AT command mode and unused UART1; no EMOS/resident UART owner.");
    puts("AT and AT+GMR only. No WiFi/network/flash configuration changes.");
    if(!run || run>9999) { puts("Invalid/exhausted next.txt; UART untouched.");return 1; }
    snprintf(name,sizeof(name),"R%04u.log",run);
    log=mos_fopen(name,FA_WRITE|FA_CREATE_NEW);
    if(!log) { puts("Cannot create the next report without overwriting; UART untouched.");return 1; }
    if(!save_next_report(run+1))goto report;
    if(u1_vanilla_open(115200,rx,sizeof(rx)))goto report;
    opened=1;
    for(unsigned i=0;i<4;++i) {
        /* Screen output before submit; no display or SD writes during reply. */
        printf("Case %u/4: %s %s\n",i+1,modes[i]?"async":"ordinary",i==0||i==3?"AT":"AT+GMR");
        if(!query(i,commands[i],modes[i]))goto report;
    }
    if(!cases[1].reply.at_version || !cases[1].reply.sdk_version ||
       !cases[2].reply.at_version || !cases[2].reply.sdk_version ||
       strcmp(cases[0].reply.text,cases[3].reply.text) ||
       strcmp(cases[1].reply.text,cases[2].reply.text))goto report;
    result=0;
report:;
    u1_vanilla_info info={0};u1_vanilla_snapshot(&info);
    if(info.fault || info.line_errors || info.overflows)result=1;
    uint8_t closed=opened?u1_vanilla_close():U1_OK;
    if(closed)result=1;
    /* All reply collection has ended. Retain first failure/partial transcript. */
    char row[170];int n=snprintf(row,sizeof(row),"U1AT schema=1 build=" U1_BUILD_ID " result=%u close=%u rx=%lu overflows=%lu fault=%u errors=%u\r\n",
        result,closed,(unsigned long)info.received,(unsigned long)info.overflows,info.fault,info.line_errors);
    if(mos_fwrite(log,row,(unsigned)n)!=(unsigned)n)result=1;
    for(unsigned i=0;i<4;++i) {
        n=snprintf(row,sizeof(row),"case=%u mode=%u pass=%u call_mos_counts=%lu total_mos_counts=%lu work=%lu reply_bytes=%u\r\n",
            i+1,cases[i].mode,cases[i].pass,(unsigned long)cases[i].call,
            (unsigned long)cases[i].total,(unsigned long)cases[i].work,cases[i].reply.used);
        if(mos_fwrite(log,row,(unsigned)n)!=(unsigned)n)result=1;
        if(cases[i].reply.used && mos_fwrite(log,cases[i].reply.text,cases[i].reply.used)!=cases[i].reply.used)result=1;
    }
    n=snprintf(row,sizeof(row),"\r\nU1AT END result=%u\r\n",result);
    if(mos_fwrite(log,row,(unsigned)n)!=(unsigned)n)result=1;
    mos_fclose(log);
    printf("%s; report %s. Functional query evidence only, no bulk performance claim.\n",result?"U1AT FAIL":"U1AT PASS",name);
    if(closed) {
        puts("Live/uncertain source or vector remains: RESET REQUIRED; retaining app RAM.");
        for(;;)__asm__ volatile("halt":::"memory");
    }
    return result;
}
