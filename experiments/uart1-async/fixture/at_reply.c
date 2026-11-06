/* SPDX-License-Identifier: MIT */
#include "at_reply.h"
#include <string.h>
void at_reply_init(at_reply *p) { memset(p,0,sizeof(*p)); }
uint8_t at_reply_byte(at_reply *p,uint8_t c) {
    if(p->result)return p->result;
    if((c<32 && c!='\r' && c!='\n') || c>126 ||
       p->used+1>=sizeof(p->text) || p->length+1>=sizeof(p->line))
        return p->result=AT_FAIL;
    p->text[p->used++]=(char)c;p->text[p->used]=0;
    if(c=='\n') {
        if(p->length && p->line[p->length-1]=='\r')--p->length;
        p->line[p->length]=0;
        if(!strcmp(p->line,"OK"))p->result=AT_OK;
        else if(!strcmp(p->line,"ERROR") || !strcmp(p->line,"FAIL") ||
                !strcmp(p->line,"CLOSED") || !strncmp(p->line,"busy",4))p->result=AT_FAIL;
        if(!strncmp(p->line,"AT version:",11))p->at_version=1;
        if(!strncmp(p->line,"SDK version:",12))p->sdk_version=1;
        p->length=0;
    } else {
        p->line[p->length++]=(char)c;p->line[p->length]=0;
        /* Never mistake a TCP payload's embedded OK line for a query reply. */
        if(strstr(p->line,"+IPD,"))p->result=AT_FAIL;
    }
    return p->result;
}
