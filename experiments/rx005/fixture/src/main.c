/* RX-005: original finite synthetic app; no application/game integration. */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "identity.h"
#include "rom_crc.h"
extern void rx_arm(void),rx_invalid_di(void),rx_callback(void),rx_keyboard(void);
extern void rx_uart_snapshot(void);
extern uint8_t rx_context(void);
uint8_t *rx_destination;
uint24_t rx_capacity,rx_expected_callback;
uint8_t rx_use_callback;
volatile uint8_t *rx_result;
volatile uint8_t rx_api_code,rx_callbacks,rx_cb_status,rx_register_fail,rx_iff_fail;
volatile uint24_t rx_cb_count;
volatile uint8_t rx_legacy[10],rx_legacy_ready,rx_key_down,rx_key_up;
volatile uint8_t rx_uart_lctl,rx_uart_ier,rx_uart_issued;
static uint8_t source[512],guarded[544],other[16];
static uint8_t file,installed;
static uint16_t token;
static uint32_t total_work;
static volatile uint8_t *sv;
static const uint16_t buffer=60000;
static uint8_t sample(unsigned i){return(uint8_t)(i*157u+7u);}
static uint16_t get16(const volatile uint8_t*p){return(uint16_t)p[0]|(uint16_t)p[1]<<8;}
static uint24_t get24(const volatile uint8_t*p){return(uint24_t)p[0]|(uint24_t)p[1]<<8|(uint24_t)p[2]<<16;}
static void put16(uint8_t*p,unsigned n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
static void send(const uint8_t*p,unsigned n){mos_puts((const char*)p,n,0);}
static int record(const char*s){puts(s);unsigned n=strlen(s);return !file||(mos_fwrite(file,(char*)s,n)==n&&mos_fwrite(file,"\r\n",2)==2);}
#include "run_counter.inc"
static int open_report(void){
 unsigned first=first_report();if(!first)return 0;
 for(unsigned i=first;i<10000;i++){
  char name[16];snprintf(name,sizeof name,"R%04u.log",i);
  uint8_t f=mos_fopen(name,FA_READ);if(f){mos_fclose(f);continue;}
  file=mos_fopen(name,FA_WRITE|FA_CREATE_NEW);
  if(!file||!save_next_report(i+1))return 0;
  return 1;
 }return 0;
}
static int timed_out(uint32_t start){return(uint32_t)(getsysvar_time()-start)>2400UL;}
static int poll(uint8_t value){
 const uint8_t q[]={23,0,128,value};uint32_t start=getsysvar_time();sv[sysvar_gp]=(uint8_t)~value;send(q,sizeof q);
 while(sv[sysvar_gp]!=value)if(timed_out(start))return 0;
 return 1;
}
static unsigned request(uint8_t op,unsigned id,unsigned offset,unsigned count){
 uint8_t q[19]={23,0,216,14,0,1,op,0,0,1,0};put16(q+7,++token);put16(q+11,id);put16(q+13,offset);put16(q+17,count);
 if(op==4){q[3]=8;put16(q+11,id);rx_legacy_ready=0;send(q,13);}
 else{rx_legacy_ready=0;send(q,sizeof q);}
 return token;
}
static int legacy(unsigned expected,uint8_t kind){
 uint32_t start=getsysvar_time();while(!rx_legacy_ready)if(timed_out(start))return 0;
 return rx_legacy[4]==1&&rx_legacy[5]==kind&&get16(rx_legacy+6)==expected;
}
static int guards(unsigned count){
 for(unsigned i=0;i<16;i++)if(guarded[i]!=0xa5||guarded[528+i]!=0xa5)return 0;
 for(unsigned i=count;i<512;i++)if(guarded[16+i]!=0xa5)return 0;
 return 1;
}
static int arm(unsigned capacity,int callback){
 memset(guarded,0xa5,sizeof guarded);rx_destination=guarded+16;rx_capacity=capacity;rx_use_callback=(uint8_t)callback;
 rx_cb_status=0xff;rx_cb_count=0xffffff;rx_arm();
 return rx_api_code==0&&!rx_register_fail&&rx_result&&rx_result[0]==1;
}
static int received(unsigned count,unsigned before,int callback,int overflow){
 uint32_t start=getsysvar_time(),work=0;
 while(rx_result[0]==1){++work;if(timed_out(start))return 0;}
 total_work+=work;
 if(rx_result[0]!=(overflow?3:2)||get24(rx_result+2)!=(overflow?0:count)||get24(rx_result+5)!=count)return 0;
 if(rx_callbacks!=(uint8_t)(before+(callback?1:0)))return 0;
 if(callback&&(rx_cb_status!=(overflow?3:0)||rx_cb_count!=(overflow?0:count)))return 0;
 if(!guards(overflow?0:count))return 0;
 if(!overflow)for(unsigned i=0;i<count;i++)if(guarded[16+i]!=sample(i))return 0;
 return !rx_register_fail&&!rx_iff_fail&&poll(0x31);
}
static int one(unsigned count,int callback){
 unsigned before=rx_callbacks;uint8_t keys=getsysvar_vkeycount();if(!arm(count,callback))return 0;
 request(8,buffer,0,count);return received(count,before,callback,0)&&getsysvar_vkeycount()==keys;
}
static void clear_source(void){uint8_t q[]={23,0,160,(uint8_t)buffer,(uint8_t)(buffer>>8),2};send(q,sizeof q);}
static void upload(void){
 clear_source();uint8_t q[]={23,0,160,(uint8_t)buffer,(uint8_t)(buffer>>8),0,0,2};send(q,sizeof q);
 for(unsigned i=0;i<sizeof source;i++)source[i]=sample(i);
 send(source,sizeof source);
}
static int cases(void){
 static const unsigned sizes[]={0,1,2,8,16,17,127,255,256,512};char line[96];
 for(unsigned i=0;i<sizeof sizes/sizeof sizes[0];i++){
  snprintf(line,sizeof line,"Case %u/10: counted %u bytes...",i+1,sizes[i]);if(!record(line))return 0;
  if(sizes[i]==127){rx_uart_snapshot();if(!rx_uart_issued)return 0;puts("RX005 UART BEFORE127 BASELINE");}
  if(!one(sizes[i],1))return 0;
 }
 unsigned before=rx_callbacks;
 if(!record("Case: intact unarmed frame discard..."))return 0;
 request(8,buffer,0,17);
 if(!poll(0x32)||rx_callbacks!=before||rx_result[0]!=2||get24(rx_result+2)!=512||!guards(512))return 0;
 if(!record("Case: NULL callback,16 bytes...")||!one(16,0))return 0;
 if(!record("Case: BUSY refusal preserves first arm...")||!arm(1,1))return 0;
 rx_destination=other;rx_capacity=sizeof other;rx_arm();
 if(rx_api_code!=1)return 0;
 request(8,buffer,0,1);if(!received(1,before,1,0))return 0;
 before=rx_callbacks;
 if(!record("Case: oversize512 into capacity511, discard...")||!arm(511,1))return 0;
 request(8,buffer,0,512);if(!received(512,before,1,1))return 0;
 if(!record("Case: invalid NULL/wrap/capacity and preserved DI..."))return 0;
 rx_destination=0;rx_capacity=1;rx_invalid_di();if(rx_api_code!=2||rx_iff_fail)return 0;
 rx_destination=(uint8_t*)0xfffff8;rx_capacity=16;rx_arm();if(rx_api_code!=2)return 0;
 rx_destination=guarded+16;rx_capacity=65536;rx_arm();if(rx_api_code!=2)return 0;
 before=rx_callbacks;
 if(!record("Case: source error keeps arm, later valid response retires it...")||!arm(1,1))return 0;
 unsigned t=request(8,buffer,513,1);
 if(!legacy(t,5)||rx_result[0]!=1||rx_callbacks!=before||!guards(0))return 0;
 request(8,buffer,0,1);if(!received(1,before,1,0))return 0;
 if(!record("Case:16 repeated positive rearms..."))return 0;
 for(unsigned i=0;i<16;i++)if(!one((i&1)?17:1,1))return 0;
 before=rx_callbacks;
 if(rx_key_down||rx_key_up||!arm(512,1))return 0;
 rx_key_down=rx_key_up=0;
 if(!record("RX005 KEY READY: press and release A once."))return 0;
 uint32_t start=getsysvar_time();while(!rx_key_down||!rx_key_up)if(timed_out(start))return 0;
 if(rx_key_down!=1||rx_key_up!=1||rx_result[0]!=1||rx_callbacks!=before||!guards(0))return 0;
 request(8,buffer,0,512);if(!received(512,before,1,0))return 0;
 return record("RX005 KEY PASS down=1 up=1 bulk=512");
}
int main(void){
 putch(12);puts("RX005 COUNTED RETURN TRIAL");
 puts("Allow less than two minutes. A stall is FAIL; report the last case.");
 if(rx_context()||installed_crc(RX_MOS_BYTES)!=RX_MOS_CRC){puts("RX005 REFUSED: wrong MOS/context");return 15;}
 if(*(volatile uint24_t*)RX_KBVECTOR){puts("RX005 REFUSED: keyboard callback already owned");return 15;}
 sv=(volatile uint8_t*)mos_sysvars();
 /* Counted return admits the normal VDP route, not serial-console mirroring.
    Select that existing stock mode explicitly; do not assume startup state. */
 const uint8_t normal[]={23,0,254,0};send(normal,sizeof normal);
 if(!poll(0x30)||!open_report())return 15;
 record("RX005 START build=" RX_BUILD);
 mos_setkbvector(rx_keyboard,0);installed=1;
 unsigned t=request(4,27,0,0);
 int ok=legacy(t,4)&&get16(rx_legacy+8)==512;
 if(ok){upload();ok=poll(0x33)&&cases();}
 if(ok){clear_source();ok=poll(0x34);}
 /* Read/write the same IER under saved IFF: no FIFO/LSR/RBR/policy change.
    The selected emulator flushes its lifetime counters on this existing write. */
 rx_uart_snapshot();
 char snapshot[90];snprintf(snapshot,sizeof snapshot,"RX005 UART SNAPSHOT lctl=%02X ier=%02X issued=%u",rx_uart_lctl,rx_uart_ier,rx_uart_issued);record(snapshot);
 char result[110];snprintf(result,sizeof result,"RX005 RESULT callbacks=%u work=%lu keys=%u/%u regfail=%u ifffail=%u",rx_callbacks,(unsigned long)total_work,rx_key_down,rx_key_up,rx_register_fail,rx_iff_fail);record(result);
 if(ok&&total_work){
  if(installed)mos_setkbvector(0,0);
  record("RX005 SUITE PASS");if(file)mos_fclose(file);puts("RX005 RETURN PASS");return 0;
 }
 record("RX005 SUITE FAIL - live storage retained; reset required.");if(file)mos_fclose(file);
 puts("RX005 FAILURE LOG CLOSED; storage remains live");
 for(;;)__asm__ volatile("halt":::"memory");
}
