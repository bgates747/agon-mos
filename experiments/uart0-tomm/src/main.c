/* Controlled original benchmark. Firmware remains the existing ZDS II image. */
#include "platform.h"
#include "identity.h"
#include "packets.h"
#include <ez80f92.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
extern void tm_init(void),tm_exit(void),tm_send(void),tm_callback(void);
const uint8_t *tm_source;
uint24_t tm_length;
volatile uint8_t tm_done;
void bd_note_completion(void){} /* unused balls callback entry in timer bridge */
static uint8_t packet[8448],check_data[3840];
static volatile uint8_t *sv;
static uint8_t logfile;
static const char *names[]={"standard","MOS-OTIRX16","Tom-scalar16"};
static int line(const char *s){puts(s);return mos_fwrite(logfile,(char *)s,strlen(s))==strlen(s)&&mos_fwrite(logfile,"\r\n",2)==2;}
static void send(const uint8_t *p,unsigned n){mos_puts((const char *)p,n,0);}
static int gp(const uint8_t *p,unsigned n,uint8_t value){
 sv[sysvar_gp]=0xfe;send(p,n);uint32_t start=ticks();
 while(sv[sysvar_gp]!=value)if((uint32_t)(ticks()-start)>BD_TICK_HZ*10)return 0;
 return 1;
}
static int verify(void){
 send(v_reset_flag,sizeof v_reset_flag);
 uint8_t f=mos_fopen("checks.bin",FA_READ);if(!f)return 0;
 for(unsigned b=0;b<32;b++){
  if(mos_fread(f,(char *)check_data,sizeof check_data)!=sizeof check_data){mos_fclose(f);return 0;}
  for(unsigned i=0;i<sizeof check_data;i+=60){
   send(check_data+i,60);if(!gp(v_reply,sizeof v_reply,0)){mos_fclose(f);return 0;}
  }
 }
 mos_fclose(f);return 1;
}
static int open_mode(unsigned mode){
 if(mode==2){tm_init();return 1;}
 if(mode==1)return !api_call(13,0,0,0)&&!api_call(46,0,16u<<8,0)&&
  !api_call(54,(uint24_t)tm_callback,1,0x544d);
 return 1;
}
static int submit(unsigned mode,const uint8_t *src,unsigned n){
 /* Arm BEFORE send: original example wait_done clears AFTER send and can lose
    an early completion. No change to Tom's sender/ISR is hidden here. */
 tm_done=0;
 if(mode==0){send(src,n);tm_done=1;return 1;}
 if(mode==1)return !api_call(66,(uint24_t)src,n,0);
 tm_source=src;tm_length=n;tm_send();return 1;
}
static int wire_idle(void){
 uint32_t start=ticks();
 while(!(IO(UART0_LSR)&0x40))if((uint32_t)(ticks()-start)>BD_TICK_HZ*10)return 0;
 return 1;
}
static int close_mode(unsigned mode){
 if(!wire_idle())return 0;
 if(mode==2){tm_exit();return 1;}
 if(mode==1)return !api_call(31,0,0,0)&&!api_call(34,0,0,0);
 return 1;
}
static volatile uint32_t work_state;
static void work(void){for(unsigned j=0;j<16;j++)work_state=work_state*1664525UL+1013904223UL;}
static int trial(unsigned mode,unsigned paced,unsigned repeat){
 char text[200];
 snprintf(text,sizeof text,"BEGIN repeat=%u mode=%s paced=%u",repeat,names[mode],paced);if(!line(text))return 0;
 const uint8_t clear[]={23,0,160,240,106,2};send(clear,sizeof clear);
 if(!wire_idle()||!open_mode(mode))return 0;
 uint32_t work_count=0,submit_ticks=0,start=ticks(),deadline=start,released=0;
 unsigned missed=0;
 for(unsigned chunk=0;chunk<(paced?32u:1u);chunk++){
  unsigned n=paced?264u:sizeof packet;uint32_t before=ticks();
  if(!submit(mode,packet+(paced?chunk*264u:0),n))return 0;
  submit_ticks+=ticks()-before;
  if(paced)deadline+=6896; /* 264 bytes / 44100 payload bytes/s, rounded. */
  while(!tm_done){
   work();work_count++;
   if((uint32_t)(ticks()-before)>BD_TICK_HZ*10)return 0;
  }
  released=ticks()-start;
  if(paced){
   if((int32_t)(ticks()-deadline)>0)missed++;
   while((int32_t)(ticks()-deadline)<0){work();work_count++;}
  }
 }
 if(!close_mode(mode))return 0;
 uint32_t elapsed=ticks()-start;
 snprintf(text,sizeof text,"RESULT repeat=%u mode=%s paced=%u bytes=8448 payload=8192 ticks=%lu submit_ticks=%lu released_ticks=%lu work=%lu missed=%u state=%lu",
  repeat,names[mode],paced,(unsigned long)elapsed,(unsigned long)submit_ticks,(unsigned long)released,(unsigned long)work_count,missed,(unsigned long)work_state);
 if(!line(text))return 0;
 if(!verify())return 0;
 return line("VERIFY8192 PASS");
}
int main(int argc,char **argv){
 unsigned selected=argc>1?(unsigned)atoi(argv[1]):3;
 if(selected>3)return 1;
 putch(12);puts("TOM / MOS UART COMPARISON - finite benchmark\nAllow two minutes per selected sender; a stall is FAIL, reset required.\nTom ISR spins with interrupts disabled if CTS blocks.\n");
 sv=mos_sysvars();if(!transport_supported()||!clocks_start())return 1;
 /* One private profile/card per invocation; physical operator preserves logs. */
 char name[16];snprintf(name,sizeof name,"mode%u.log",selected);
 logfile=mos_fopen(name,FA_WRITE|FA_CREATE_NEW);if(!logfile){clocks_stop();return 1;}
 int ok=line("TM001 build=" TM_BUILD);
 for(unsigned i=0;i<32;i++){
  uint8_t *p=packet+i*264u;const uint8_t header[]={23,0,160,240,106,0,0,1};
  memcpy(p,header,8);for(unsigned j=0;j<256;j++)p[8+j]=(uint8_t)((i*256+j)*157+7);
 }
 send(v_setup,sizeof v_setup);
 if(!gp(v_mismatch_probe,sizeof v_mismatch_probe,1)||!gp(v_match_probe,sizeof v_match_probe,0))ok=0;
 if(ok)ok=line("COMPARATOR negative/positive PASS");
 for(unsigned repeat=0;repeat<3&&ok;repeat++)for(unsigned p=0;p<2&&ok;p++)
  for(unsigned m=0;m<3&&ok;m++)if(selected==3||selected==m)ok=trial(m,p,repeat);
 /* A failed Tom transfer can leave its vector live: do not return and free
    code/storage. Timeout loops here keep it resident; host runner stops it. */
 if(!ok){line("TM001 FAIL - reset required; retaining application memory");for(;;){}}
 send(v_cleanup,sizeof v_cleanup);ok=line("TM001 PASS");
 mos_fclose(logfile);clocks_stop();return ok?0:1;
}
