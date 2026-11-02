/* Original application; no test hooks in the VDP or private MOS writes. */
#define main startup_safe_baseline_main
#include "baseline.inc"
#undef main
#include "packets.h"
extern uint8_t ux_call(void);
extern void ux_notify(void);
uint24_t ux_hl,ux_de,ux_bc,ux_result;
volatile uint24_t ux_count,ux_last,ux_bad,ux_context;
static uint8_t packet[8448],check_data[3840];
static volatile uint8_t *sv;
static uint8_t op(unsigned offset,uint24_t de,uint24_t hl,uint24_t bc){
 safe_function=(void *)u24(api+offset);ux_de=de;ux_hl=hl;ux_bc=bc;return ux_call();
}
static void send(const uint8_t *p,unsigned n){mos_puts((const char *)p,n,0);}
static int wait_gp(uint8_t expected){
 uint32_t start=getsysvar_time();
 while(sv[sysvar_gp]!=expected)if((uint32_t)(getsysvar_time()-start)>1200)return 0;
 return 1;
}
static int probe(const uint8_t *p,unsigned n,uint8_t expected){
 sv[sysvar_gp]=0xfe;send(p,n);return wait_gp(expected);
}
static int verify(void){
 send(v_reset_flag,sizeof(v_reset_flag));
 uint8_t f=mos_fopen("checks.bin",FA_READ);if(!f)return 0;
 for(unsigned block=0;block<32;block++){
  if(mos_fread(f,(char *)check_data,sizeof(check_data))!=sizeof(check_data)){mos_fclose(f);return 0;}
  for(unsigned k=0;k<3840;k+=60){
   send(check_data+k,60);
   if(!probe(v_reply,sizeof(v_reply),0)){mos_fclose(f);return 0;}
  }
  if((block&7)==7)printf("Receiver byte check %u/4 complete.\n",(block+1)/8);
 }
 mos_fclose(f);return 1;
}
static void fill(void){
 for(unsigned i=0;i<32;i++){
  uint8_t *p=packet+i*264;const uint8_t header[]={23,0,160,240,106,0,0,1};
  memcpy(p,header,8);for(unsigned j=0;j<256;j++)p[8+j]=(uint8_t)((i*256+j)*157+7);
 }
}
static int test(unsigned mode){
 char line[160];snprintf(line,sizeof(line),"Case %u/4: %s",mode+1,
 mode==0?"borrowed write / direct callback":mode==1?"borrowed write / foreground event":mode==2?"32 copied RST18 writes / callback":"one large copied RST18 / no callback");record(line);
 fill();const uint8_t clear[]={23,0,160,240,106,2};send(clear,sizeof(clear));
 ux_count=ux_last=ux_bad=ux_context=0;
 if(!retry(13)||op(46,0,0,16<<8))return 0;
 uint24_t cb=(mode==0||mode==2)?(uint24_t)ux_notify:0;
 uint24_t flags=mode<2?(mode==0?1:0):0x101;
 if(op(54,0x654321,cb,flags))return 0;
 uint32_t start=getsysvar_time();
 if(mode<2){if(op(66,0,(uint24_t)packet,sizeof(packet)))return 0;}
 else if(mode==2){for(unsigned n=0;n<32;n++){send(packet+n*264,264);memset(packet+n*264,0xee,264);}}
 else {send(packet,sizeof(packet));memset(packet,0xee,sizeof(packet));}
 if(!retry(31))return 0;
 unsigned ticks=(unsigned)(getsysvar_time()-start);
 if(mode==1){if(op(63,0,0,0)||!ux_result)return 0;ux_count=1;}
 if(ux_bad || ux_count!=(mode==2?32:mode==3?0:1))return 0;
 if((mode==0||mode==2)&&ux_context!=0x654321)return 0;
 if(!retry(34)||!stock())return 0;
 snprintf(line,sizeof(line),"Transfer PASS: elapsed=%u frame ticks; notifications=%u. Checking8192 receiver bytes...",ticks,(unsigned)ux_count);record(line);
 if(!verify())return 0;
 record("Case PASS: full receiver bytes and notification count.");return 1;
}
int main(void){
 putch(12);puts("UART0 WRITE-MODE / CALLBACK EXPERIMENT\nAllow two minutes. A stall is not PASS; report the last progress line.");
 api=uart_discover();sv=mos_sysvars();
 uint32_t crc=rom_crc();printf("MOS CRC32 %08lX; fixture build %s\n",(unsigned long)crc,SAFE_BUILD);
 if(!api||memcmp(api,"UTX1",4)||api[4]!=1||api[5]<3||api[6]<69||!(api[7]&16)||
    (crc!=SAFE_ROM_CRC&&crc!=SAFE_FLEXE_CRC)||!stock()){
  puts("Wrong MOS/API or active session: no tests started.");return 1;
 }
 if(!begin())return 1;
 int ok=1;send(v_setup,sizeof(v_setup));
 record("Setup: confirm receiver comparator detects a bad byte, then accepts a good byte.");
 if(!probe(v_mismatch_probe,sizeof(v_mismatch_probe),1)||!probe(v_match_probe,sizeof(v_match_probe),0))ok=0;
 if(ok)record("Comparator negative/positive controls PASS.");
 for(unsigned mode=0;mode<4&&ok;mode++)ok=test(mode);
 /* Never free a borrowed source on failure before the ordinary MOS fence. */
 if(byte(SAFE_OPENED)){puts("FAIL: retaining queued sources; return fence must drain before CLI.");}
 else send(v_cleanup,sizeof(v_cleanup));
 record(ok?"END CALLBACK SUITE PASS":"END CALLBACK SUITE FAIL - report last progress line");
 mos_fclose(log_file);mos_fclose(index_file);
 return ok&&logs_ok?0:1;
}
