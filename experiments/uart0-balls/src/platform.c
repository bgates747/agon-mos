/* Original application adapters, not new MOS/VDP code. */
#include "platform.h"
#include <ez80f92.h>
#include <string.h>
#include "keys.h"
void *bd_api_function;
const uint8_t *bd_api;
uint24_t bd_hl,bd_de,bd_bc,bd_result_hl;
volatile uint24_t bd_timer1_wraps,bd_timer2_wraps;
volatile uint24_t bd_clock_wrap,bd_clock_count,bd_wall_wrap,bd_wall_count;
volatile uint24_t bd_notify_wrap,bd_notify_count,bd_notify_id,bd_notify_context;
volatile uint8_t bd_notify_status;
static void *old_timer1,*old_timer2;
static uint8_t old_ctl1,old_ctl2,old_iss,clock_running;
static volatile uint8_t *keymap,*keyvars;
static uint8_t key_counter;
static volatile uint8_t key_head,key_tail,key_queue[16];
volatile uint8_t key_overruns;
static uint16_t held;
static const uint8_t key_numbers[]={49,50,18,101,83,52,17,94,24};
void bd_keys_tick(void){
 if(!keymap)return;
 uint16_t now=0;
 for(unsigned i=0;i<sizeof(key_numbers);i++){
  unsigned k=key_numbers[i]-1;
  if(keymap[k/8]&(1u<<(k&7)))now|=(uint16_t)(1u<<i);
 }
 uint8_t counter=keyvars[sysvar_vkeycount];
 uint16_t edges=key_edges(now,held,(uint8_t)(counter-key_counter),keyvars[sysvar_keyascii],keyvars[sysvar_vkeydown]);
 key_counter=counter;held=now;
 for(unsigned i=0;i<sizeof(key_numbers);i++)if(edges&(1u<<i)){
  uint8_t next=(uint8_t)((key_head+1)&15);
  if(next==key_tail){key_overruns++;continue;}
  key_queue[key_head]=(uint8_t)key_chars[i];key_head=next;
 }
}
int key_pop(void){
 if(key_tail==key_head)return 0;
 unsigned c=key_queue[key_tail];key_tail=(uint8_t)((key_tail+1)&15);return (int)c;
}
int clocks_start(void){
 old_ctl1=IO(TMR1_CTL);old_ctl2=IO(TMR2_CTL);
 if((old_ctl1|old_ctl2)&1)return 0; /* Never replace a running PRT owner. */
 keymap=mos_getkbmap();keyvars=mos_sysvars();key_counter=keyvars[sysvar_vkeycount];held=0;key_head=key_tail=key_overruns=0;
 old_iss=IO(TMR_ISS);bd_timer1_wraps=bd_timer2_wraps=0;
 old_timer1=mos_setintvector(0x0c,bd_timer1_isr);
 old_timer2=mos_setintvector(0x0e,bd_timer2_isr);
 IO(TMR1_CTL)=0;IO(TMR2_CTL)=0;IO(TMR_ISS)=old_iss&0xc3;
 /* Reload zero selects65536 ticks. PRT1 precision:18.432MHz/16. */
 IO(TMR1_RR_L)=0;IO(TMR1_RR_H)=0;
 /* PRT2 wall time:18.432MHz/256;720ticks per10ms key scan. */
 IO(TMR2_RR_L)=(uint8_t)720;IO(TMR2_RR_H)=(uint8_t)(720>>8);
 IO(TMR1_CTL)=0x57;IO(TMR2_CTL)=0x5f;clock_running=1;return 1;
}
void clocks_stop(void){
 if(!clock_running)return;
 IO(TMR1_CTL)=0;IO(TMR2_CTL)=0;
 mos_setintvector(0x0c,old_timer1);mos_setintvector(0x0e,old_timer2);
 IO(TMR_ISS)=old_iss;IO(TMR1_CTL)=old_ctl1&0x7e;IO(TMR2_CTL)=old_ctl2&0x7e;
 clock_running=0;keymap=0;
 /* Reload registers are write-only; only initially disabled timers are claimed.
    Later owners must configure their own reload values, as normal. */
}
uint32_t ticks(void){bd_capture_clock();return ((uint32_t)bd_clock_wrap<<16)+(uint16_t)(0-(uint16_t)bd_clock_count);}
uint32_t wall_ticks(void){bd_capture_wall();return (uint32_t)bd_wall_wrap*720UL+(uint16_t)(720-(uint16_t)bd_wall_count);}
uint32_t notification_ticks(void){return ((uint32_t)bd_notify_wrap<<16)+(uint16_t)(0-(uint16_t)bd_notify_count);}
static uint24_t pointer_at(const uint8_t *p){return p[0]+((uint24_t)p[1]<<8)+((uint24_t)p[2]<<16);}
uint8_t api_call(unsigned offset,uint24_t hl,uint24_t bc,uint24_t de){
 bd_api_function=(void *)pointer_at(bd_api+offset);bd_hl=hl;bd_bc=bc;bd_de=de;return bd_api_call();
}
int transport_supported(void){
 bd_api=bd_discover();return bd_api&&!memcmp(bd_api,"UTX1",4)&&bd_api[4]==1&&bd_api[5]>=3&&bd_api[6]>=69&&(bd_api[7]&16)&&(bd_api[53]&128);
}
static int retry(unsigned offset){
 uint32_t start=ticks();uint8_t status;
 do{status=api_call(offset,0,0,0);if(status!=1)return status==0;}while((uint32_t)(ticks()-start)<BD_TICK_HZ*10);
 return 0;
}
int transport_open(unsigned mode){
 if(!mode)return 1;
 if(!retry(13))return 0;
 uint32_t start=ticks();
 uint8_t status;
 do{status=api_call(46,0,16u<<8,0);if((uint32_t)(ticks()-start)>BD_TICK_HZ*10)return 0;}while(status==1);
 if(status)return 0;
 /* Mode1 takes foreground events; mode2 posts direct notifications. */
 return api_call(54,mode==2?(uint24_t)bd_notify:0,mode==2?1:0,0x42444d)==0;
}
int transport_close(void){return retry(31)&&retry(34);}
