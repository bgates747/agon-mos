/* Original AgonDev application; the tested ZDS II MOS is unchanged. */
#define main startup_safe_baseline_main
#include "baseline.inc"
#undef main

extern uint8_t reset_call(void);
extern void reset_stop(void);
uint24_t reset_arg_hl,reset_arg_de,reset_arg_bc,reset_result_hl,reset_result_bc;
static uint8_t stream[16384],arm[64];
static unsigned stream_length,partial_after;
static uint32_t installed_crc;
enum { ARMED=1, EXPIRED=2, VERIFIED=3 };

static uint8_t operation(unsigned offset,uint24_t de,uint24_t hl,uint24_t bc){
 safe_function=(void *)u24(api+offset);reset_arg_de=de;reset_arg_hl=hl;reset_arg_bc=bc;
 return reset_call();
}
static void set24(uint8_t *p,uint24_t n){p[0]=n;p[1]=n>>8;p[2]=n>>16;}
static uint32_t checksum(const uint8_t *p,unsigned size){
 uint32_t c=0xffffffffUL;
 while(size--){c^=*p++;for(unsigned n=0;n<8;n++)c=(c>>1)^((c&1)?0xedb88320UL:0);}
 return c^0xffffffffUL;
}
static uint32_t get32(const uint8_t *p){return (uint32_t)u24(p)|((uint32_t)p[3]<<24);}
static void set32(uint8_t *p,uint32_t n){set24(p,n);p[3]=n>>24;}
static int save_file(const char *name,const uint8_t *p,unsigned count){
 uint8_t f=mos_fopen(name,FA_WRITE|FA_CREATE_ALWAYS);if(!f)return 0;
 unsigned written=mos_fwrite(f,(char *)p,count);mos_fclose(f);return written==count;
}
/* -1 corrupt, 0 absent, 1 structurally valid. No activation or mutation. */
static int load_arm(void){
 uint8_t f=mos_fopen("reset.arm",FA_READ);if(!f)return 0;
 uint8_t extra;unsigned got=mos_fread(f,(char *)arm,sizeof(arm));
 unsigned more=mos_fread(f,(char *)&extra,1);mos_fclose(f);
 if(got!=sizeof(arm)||more||memcmp(arm,"URST0001",8)||
    checksum(arm,60)!=get32(arm+60)||memcmp(arm+12,SAFE_BUILD,16)||
    (arm[8]!=5&&arm[8]!=6)||arm[9]<ARMED||arm[9]>VERIFIED||
    !((unsigned)arm[10]+((unsigned)arm[11]<<8))||
    ((unsigned)arm[10]+((unsigned)arm[11]<<8))>=10000||
    !u24(arm+32)||u24(arm+32)>=u24(arm+41)||arm[35]!=3||
    arm[36]!=1||arm[37]!=1||u24(arm+38)!=SAFE_ASYNC_ISR)return -1;
 return 1;
}
static int store_arm(void){
 char name[16];snprintf(name,sizeof(name),"X%04u.dat",run_id);
 set32(arm+60,checksum(arm,60));
 return save_file(name,arm,sizeof(arm))&&save_file("reset.arm",arm,sizeof(arm));
}
static void close_logs(void){
 if(log_file)mos_fclose(log_file);if(index_file)mos_fclose(index_file);
 log_file=index_file=0;logs_ok=0;
}
static int resume_logs(void){
 char name[16];snprintf(name,sizeof(name),"R%04u.log",run_id);
 log_file=mos_fopen(name,FA_WRITE|FA_OPEN_APPEND);if(!log_file)return 0;
 index_file=mos_fopen("runs.log",FA_WRITE|FA_OPEN_APPEND);
 if(!index_file){close_logs();return 0;}logs_ok=1;return 1;
}
static int within(uint32_t started,uint32_t limit){return (uint32_t)(getsysvar_time()-started)<limit;}
static int drain(void){
 uint32_t start=getsysvar_time();
 do{uint8_t s=call(31);if(s!=1)return s==0;}while(within(start,1200));return 0;
}
static int reap(uint24_t ticket){return operation(28,ticket,0,0)==0;}
static int publish(uint24_t *ticket){
 if(operation(16,0,0,0))return 0;*ticket=reset_result_hl;
 return operation(19,*ticket,(uint24_t)stream,stream_length)==0;
}
static void packet(int ready,int mode){
 unsigned n=0;stream[n++]=12;
 const char *label=ready?(mode==5?
  "RESET NOW - SENDING CONTINUOUSLY\r\nPower OFF/ON within 60 seconds.\r\nAfter reboot: reopen test.bin, choose 7, then Y.\r\nAll SD files are CLOSED. No keypress is needed now.\r\n":
  "RESET NOW - CONTROLLED MID-PACKET STOP\r\nThe CPU stops; part of a VDP packet remains queued.\r\nPower OFF/ON, reopen test.bin, choose 7, then Y.\r\nAll SD files are CLOSED. A stopped screen is EXPECTED.\r\n"):
  "PREPARING RESET TEST - DO NOT RESET YET\r\nChecking active sending and saving the run record...\r\n";
 unsigned len=strlen(label);memcpy(stream+n,label,len);n+=len;
 /* Stock VDP commands: private buffer6AF2 clear, then32 complete256-byte writes. */
 const uint8_t clear[]={23,0,0xa0,0xf2,0x6a,2};memcpy(stream+n,clear,sizeof(clear));n+=sizeof(clear);
 partial_after=n+8+48;
 for(unsigned chunk=0;chunk<32;chunk++){
  const uint8_t header[]={23,0,0xa0,0xf2,0x6a,0,0,1};
  memcpy(stream+n,header,sizeof(header));n+=sizeof(header);
  for(unsigned i=0;i<256;i++)stream[n++]=(uint8_t)(i*157+7);
 }
 stream_length=n;
}
static void preparation_failed(const char *why){
 /* No RESET NOW marker has been published here. Preserve borrowed memory. */
 if(!stock()){
  while(call(31)==1){} /* A permanent stall retains source storage until reset. */
  uint8_t s=call(34);(void)s;
 }
 if(logs_ok){record(why);record("END RESET PREPARATION FAIL");}
 close_logs();puts("Reset preparation failed; no reset test is counted PASS.");
}
static int start_reset(int mode){
 int old=load_arm();if(old<0){puts("RESET ARM CORRUPT: preserve card for inspection.");return 1;}
 if(old&&arm[9]==ARMED){puts("A reset run is pending. Choose 7 before starting another.");return 1;}
 if(!stock()||!begin())return 1;
 record("RESET PREPARING: do not reset until RESET NOW appears; all files will be closed.");
 if(!retry(13)||operation(46,0,0,16u<<8)){preparation_failed("FAIL: cannot activate batch16.");return 1;}
 packet(0,mode);uint24_t probe;
 if(!publish(&probe)){preparation_failed("FAIL: cannot publish preparation packet.");return 1;}
 uint32_t started=getsysvar_time();uint24_t accepted=0;uint8_t state=0;
 do{
  if(operation(22,probe,0,0)){preparation_failed("FAIL: probe status.");return 1;}
  accepted=reset_result_hl;state=(uint8_t)(reset_result_bc>>8);
  if(accepted&&accepted<stream_length&&state==3)break;
  call(37);
 }while(within(started,1200));
 if(!accepted||accepted>=stream_length||state!=3){preparation_failed("FAIL: active partial probe not observed.");return 1;}
 memset(arm,0,sizeof(arm));memcpy(arm,"URST0001",8);arm[8]=mode;arm[9]=ARMED;
 arm[10]=run_id;arm[11]=run_id>>8;memcpy(arm+12,SAFE_BUILD,16);
 set32(arm+28,installed_crc);set24(arm+32,accepted);arm[35]=state;
 arm[36]=byte(SAFE_OPENED);arm[37]=byte(SAFE_INITIALIZED);
 set24(arm+38,at(SAFE_VECTOR));set24(arm+41,stream_length);set24(arm+44,probe);
 if(!arm[36]||!arm[37]||at(SAFE_VECTOR)!=SAFE_ASYNC_ISR||!store_arm()){
  preparation_failed("FAIL: cannot persist active-run record.");return 1;
 }
 char line[160];snprintf(line,sizeof(line),"RESET PENDING mode=%d accepted_probe=%lu source_bytes=%u state=%u; await RESET NOW",mode,(unsigned long)accepted,stream_length,state);
 record(line);int saved=logs_ok;close_logs();
 if(!saved||!drain()||!reap(probe)){preparation_failed("FAIL: preparation cleanup.");return 1;}
 /* From here until drain/close after expiry: no filesystem calls at all. */
 packet(1,mode);uint24_t tickets[3]={0,0,0};
 if(!publish(&tickets[0])){preparation_failed("FAIL: ready packet publication.");return 1;}
 if(mode==6){
  for(;;){
   if(operation(22,tickets[0],0,0))reset_stop();
   if(reset_result_hl>=partial_after){
    /* Stop refills permanently with an intentionally unfinished borrowed span. */
    __asm__("di");
    reset_stop();
   }
  }
 }
 if(!publish(&tickets[1])||!publish(&tickets[2]))reset_stop();
 started=getsysvar_time();
 while(within(started,7200)){
  for(unsigned i=0;i<3;i++){
   if(operation(22,tickets[i],0,0))reset_stop();
   if((reset_result_bc>>8)==4){if(!reap(tickets[i])||!publish(&tickets[i]))reset_stop();}
  }
 }
 /* Window expired without reset: restore stock before opening any SD file. */
 if(!drain())reset_stop();
 for(unsigned i=0;i<3;i++)if(!reap(tickets[i]))reset_stop();
 if(!retry(34)||!stock())reset_stop();
 /* Keep disk I/O disabled until the operator acknowledges that READY ended. */
 puts("RESET WINDOW EXPIRED - DO NOT RESET. Press E to save EXPIRED (NOT PASS).");
 input_begin();char c;do{c=key();}while(c!='e'&&c!='E');mos_setkbvector(NULL,0);
 arm[9]=EXPIRED;if(!store_arm())return 1;
 if(resume_logs()){record("END RESET EXPIRED - no reset performed, NOT PASS");close_logs();}
 puts("RESET EXPIRY SAVED - NOT PASS.");
 return 1;
}
static int verify_reset(int simulated_confirmation){
 int found=load_arm();if(found!=1){puts(found?"RESET VERIFY REFUSED: corrupt arm record.":"RESET VERIFY REFUSED: no armed test.");return 1;}
 if(arm[9]!=ARMED){puts("RESET VERIFY REFUSED: run expired or already verified.");return 1;}
 if(get32(arm+28)!=installed_crc||!stock()||byte(SAFE_INITIALIZED)||
    byte(SAFE_BATCH)||byte(SAFE_SYNC_DEPTH)||at(SAFE_NEXT_TICKET)){
  puts("RESET VERIFY REFUSED: fresh disabled reset state is missing. Do not count PASS.");return 1;
 }
 if(!simulated_confirmation){
  puts("Did you see RESET NOW, then power OFF/ON, and come straight here? Y/N");
  input_begin();char c;do{c=key();}while(c!='y'&&c!='Y'&&c!='n'&&c!='N');mos_setkbvector(NULL,0);
  if(c=='n'||c=='N'){puts("Not confirmed; armed report preserved, no PASS.");return 1;}
 }
 /* Prove the preserved stock output/receive parser can still complete a query. */
 *(volatile uint8_t *)SAFE_GP=0;putch(23);putch(0);putch(0x80);putch(0x5a);
 uint32_t started=getsysvar_time();while(byte(SAFE_GP)!=0x5a&&within(started,1200)){}
 if(byte(SAFE_GP)!=0x5a||!stock()||byte(SAFE_INITIALIZED)){
  puts("RESET VERIFY FAIL: stock VDP query/reply did not recover.");return 1;
 }
 run_id=arm[10]+((unsigned)arm[11]<<8);
 if(!resume_logs()){puts("RESET VERIFY FAIL: cannot reopen run log.");return 1;}
 record(simulated_confirmation?"RESET CONFIRMATION source=automated-command-line":"RESET CONFIRMATION source=operator-Y");
 record("RESET RECOVERY PASS: fresh disabled state, original handler, stock VDP query/reply.");
 char line[64];snprintf(line,sizeof(line),"END run=%04u RESET PASS mode=%u",run_id,arm[8]);record(line);
 int ok=logs_ok;close_logs();if(!ok)return 1;
 arm[9]=VERIFIED;if(!store_arm()){puts("RESET VERIFY FAIL: final record write.");return 1;}
 puts("UART0 RESET RECOVERY PASS - return to MOS and check DIR.");return 0;
}
int main(int argc,char **argv){
 putch(12);puts("UART0 QUALIFICATION v2 - RESET FIXTURE");
 installed_crc=rom_crc();printf("Installed MOS CRC32 %08lX; required %08lX physical / %08lX emulator.\n",(unsigned long)installed_crc,(unsigned long)SAFE_ROM_CRC,(unsigned long)SAFE_FLEXE_CRC);
 if(installed_crc!=SAFE_ROM_CRC&&installed_crc!=SAFE_FLEXE_CRC){puts("FAIL: wrong MOS image; no activation.");return 1;}
 api=uart_discover();if(!api||memcmp(api,"UTX1",4)||api[4]!=1||api[5]<2||api[6]<54){puts("FAIL: missing API.");return 1;}
 if(argc>1){
  char c=argv[1][0];if(c=='7')return verify_reset(argv[1][1]=='y');
  if(c=='5'||c=='6')return start_reset(c-'0');
  if(c>='0'&&c<='4')return selection(c);
 }
 for(;;){
  int pending=load_arm();if(pending==1&&arm[9]==ARMED)puts("RESET RUN PENDING: choose 7 before any activation test.");
  puts("\n1 Stock/discovery   2 Activation/close\n3 OTIRX integrity   4 Masked-IFF/app exit\n0 Run all ordinary tests (no reset tests)\n5 Continuous sending: deliberate power-cycle\n6 Mid-packet CPU stop: deliberate power-cycle\n7 Verify pending reset after reboot\nQ Return to MOS\nChoose:");
  input_begin();char c;do{c=key();}while(!strchr("01234567qQ",c));mos_setkbvector(NULL,0);
  if(c=='q'||c=='Q')break;
  if(c=='7'){verify_reset(0);continue;}
  if(c=='5'||c=='6'){start_reset(c-'0');continue;}
  if(pending<0||(pending==1&&arm[9]==ARMED)){puts("Preserve the pending test: verify with 7 first.");continue;}
  selection(c);
 }
 puts("UART0 RESET FIXTURE MENU RETURN");return 0;
}
