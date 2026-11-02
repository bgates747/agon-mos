/* Host test of the real application loop with mocked MOS I/O, not a CPU model.
   Checks user-owned boundaries, no periodic disk I/O, callback-before-return,
   source handling, scene preservation and bounded raw retention. */
#define _GNU_SOURCE
#define BALLS_PLATFORM_H
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
typedef uintptr_t uint24_t;
#define BD_TICK_HZ 1152000UL
#define BD_WALL_HZ 72000UL
#define FA_READ 1
#define FA_WRITE 2
#define FA_CREATE_NEW 4
#define FA_OPEN_APPEND 8
#define FA_CREATE_ALWAYS 16
#define sysvar_gp 0
uint24_t bd_result_hl;
volatile uint24_t bd_notify_id,bd_notify_context;
volatile uint8_t bd_notify_status,key_overruns;
static uint8_t vdp_vars[32];
static FILE *files[16];
static uint32_t clock_ticks,next_id;
static unsigned active_mode,key_case=999;
static uint24_t completion;
uint8_t mos_fopen(const char *,unsigned);
unsigned mos_fwrite(uint8_t,char *,unsigned),mos_fread(uint8_t,char *,unsigned);
void mos_fclose(uint8_t),mos_puts(const char *,unsigned,unsigned);
uint8_t *mos_sysvars(void);
int putch(int),clocks_start(void),transport_supported(void),transport_open(unsigned),transport_close(void),key_pop(void);
void clocks_stop(void),bd_notify(void);
uint32_t ticks(void),wall_ticks(void),notification_ticks(void);
uint8_t api_call(unsigned,uint24_t,uint24_t,uint24_t);
#define main demo_main
#include "../src/main.c"
#undef main
uint8_t mos_fopen(const char *name,unsigned flags){
 /* Saving during steady play would reproduce the reported defect. */
 assert(!scenario_frames||requested||stopped||failures);
 if((flags&FA_CREATE_NEW)&&access(name,F_OK)==0)return 0;
 const char *mode=flags&FA_READ?"rb":flags&FA_OPEN_APPEND?"ab":"wb";
 for(unsigned i=1;i<16;i++)if(!files[i]){files[i]=fopen(name,mode);return files[i]?(uint8_t)i:0;}
 return 0;
}
unsigned mos_fwrite(uint8_t f,char *p,unsigned n){return (unsigned)fwrite(p,1,n,files[f]);}
unsigned mos_fread(uint8_t f,char *p,unsigned n){return (unsigned)fread(p,1,n,files[f]);}
void mos_fclose(uint8_t f){fclose(files[f]);files[f]=0;}
void mos_puts(const char *p,unsigned n,unsigned ignored){
 (void)ignored;
 if(n>=7&&!memcmp(p+n-7,(uint8_t[]){23,0,195,23,0,128},6))vdp_vars[sysvar_gp]=(uint8_t)p[n-1];
}
uint8_t *mos_sysvars(void){return vdp_vars;}
int putch(int c){return c;}
int clocks_start(void){return 1;}
void clocks_stop(void){}
int transport_supported(void){return 1;}
uint32_t ticks(void){clock_ticks+=16;return clock_ticks;}
uint32_t wall_ticks(void){clock_ticks+=2304;return clock_ticks/16;}
uint32_t notification_ticks(void){return clock_ticks;}
void bd_notify(void){}
int transport_open(unsigned mode){active_mode=mode;return 1;}
int transport_close(void){assert(!completion);active_mode=0;return 1;}
uint8_t api_call(unsigned offset,uint24_t src,uint24_t count,uint24_t context){
 (void)context;
 if(offset==66){
  assert(!completion);uint24_t id=++next_id;
  mos_puts((const char *)src,(unsigned)count,0);
  if(active_mode==2){bd_notify_id=id;bd_notify_context=0x42444d;bd_notify_status=4;bd_note_completion();}
  else completion=id;
  bd_result_hl=id;return 0;
 }
 if(offset==63){if(!completion)return 1;bd_result_hl=completion;completion=0;return 0;}
 assert(offset==13||offset==31);return 0;
}
int key_pop(void){
 static const char changes[]="23bc=-r1q";
 if(case_id>=sizeof(changes)-1||key_case==case_id)return 0;
 uint32_t after=case_id==0?26:case_id==4?140:3;
 if(phase_frame<after||scenario_frames<after)return 0;
 key_case=case_id;return changes[case_id];
}
int main(void){
 char path[]="/tmp/balls-live-XXXXXX";assert(mkdtemp(path));assert(chdir(path)==0);
 char *args[]={"test.bin",0};assert(demo_main(1,args)==0);
 assert(case_id==9&&!failures&&scenario_live);
 printf("LIVE CONTROL PASS: report=%s/R0001.log; no periodic disk writes, user-only boundaries\n",path);
 return 0;
}
