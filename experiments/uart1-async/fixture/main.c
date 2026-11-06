/* SPDX-License-Identifier: MIT
 * Device-free worked core example. It never calls the UART1 OTIRX leaf.
 */
#include <stdio.h>
#include <string.h>
#include "u1_tx.h"
static u1_tx tx;
static uint8_t source[17],copy[17],used,done;
static void released(void) { done=1; }
static uint8_t emit(const uint8_t *p,uint8_t n) {
    memcpy(copy+used,p,n);used+=n;return 1;
}
int main(void) {
    u1_sample s={1,1,1,0,0};unsigned steps=0;
    for(unsigned i=0;i<sizeof(source);++i)source[i]=(uint8_t)(i+1);
    if(u1_init(&tx,16,16) || u1_start(&tx,source,sizeof(source),released))return 1;
    while(tx.phase==U1_SOURCE && steps++<3)(void)u1_step(&tx,s,emit);
    if(!done || used!=17 || memcmp(source,copy,17) || tx.phase!=U1_TAIL)return 2;
    s.temt=1;
    if(u1_step(&tx,s,emit)!=U1_DRAINED || u1_detach(&tx))return 3;
    puts("U1 core example PASS; simulated port only, no UART1/vector change");
    return 0;
}
