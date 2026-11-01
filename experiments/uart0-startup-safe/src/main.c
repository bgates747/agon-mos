/* Original qualification application; AgonDev. MOS firmware remains ZDS II. */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "identity.h"
extern const uint8_t *uart_discover(void);
extern uint8_t rom_byte0(void),safe_call(void);
extern void menu_key_callback(void);
void *safe_function,*diag_function;
uint8_t diag_status;
volatile uint8_t menu_key_head,menu_key_tail,menu_key_data[16],menu_key_held[32];
static const uint8_t *api;
static unsigned run_id;
static uint8_t log_file,index_file;
static int logs_ok;
static uint24_t u24(const volatile uint8_t *p){return p[0]+((uint24_t)p[1]<<8)+((uint24_t)p[2]<<16);}
static uint24_t at(uint24_t p){return u24((const volatile uint8_t *)p);}
static uint8_t byte(uint24_t p){return *(const volatile uint8_t *)p;}
static uint32_t rom_crc(void){
 uint32_t c=0xffffffffUL;
 for(uint24_t i=0;i<0x20000;i++){
  uint8_t v=i?*(const volatile uint8_t *)i:rom_byte0();c^=v;
  for(unsigned n=0;n<8;n++)c=(c>>1)^((c&1)?0xedb88320UL:0);
 }
 return c^0xffffffffUL;
}
static int exists(const char *p){uint8_t f=mos_fopen(p,FA_READ);if(f)mos_fclose(f);return f!=0;}
static void record(const char *s){
 puts(s);if(!logs_ok)return;
 unsigned n=strlen(s);
 if(mos_fwrite(log_file,(char *)s,n)!=n || mos_fwrite(log_file,"\r\n",2)!=2 ||
    mos_fwrite(index_file,(char *)s,n)!=n || mos_fwrite(index_file,"\r\n",2)!=2)logs_ok=0;
}
static int begin(void){
 char p[24];
 for(run_id=1;run_id<10000;run_id++){
  snprintf(p,sizeof(p),"R%04u.log",run_id);if(exists(p))continue;
  const char *prefix="SPGIKJ";int used=0;
  for(;*prefix;prefix++){snprintf(p,sizeof(p),"%c%04u.dat",*prefix,run_id);if(exists(p))used=1;}
  if(used)continue;snprintf(p,sizeof(p),"R%04u.log",run_id);break;
 }
 if(run_id==10000)return 0;
 log_file=mos_fopen(p,FA_WRITE|FA_CREATE_NEW);if(!log_file)return 0;
 index_file=mos_fopen("runs.log",FA_WRITE|(exists("runs.log")?FA_OPEN_APPEND:FA_CREATE_NEW));
 if(!index_file){mos_fclose(log_file);return 0;}logs_ok=1;
 char text[160];snprintf(text,sizeof(text),"UARTSAFE report_version=1 build=%s run=%04u",SAFE_BUILD,run_id);record(text);
 return 1;
}
static int stock(void){return !byte(SAFE_OPENED) && at(SAFE_VECTOR)==SAFE_STOCK_ISR;}
static uint8_t call(unsigned offset){safe_function=(void *)u24(api+offset);return safe_call();}
static int retry(unsigned offset){uint32_t start=getsysvar_time();uint8_t s;
 do{s=call(offset);if(s!=1)return s==0;}while((uint32_t)(getsysvar_time()-start)<1200);
 record("FAIL: transport did not become ready within ten seconds.");return 0;
}
static int discovery_test(void){
 record("1/4: stock transport and non-activating API discovery...");
 if(!stock())return 0;uint8_t init=byte(SAFE_INITIALIZED);
 const uint8_t *found=uart_discover();
 if(found!=api || !stock() || byte(SAFE_INITIALIZED)!=init)return 0;
 printf("Stock handler retained; experimental initializer state=%u.\n",init);
 record("STOCK DISCOVERY PASS");return 1;
}
static int activation_test(void){
 record("2/4: explicit activation, ordinary output, close and reopen...");
 for(unsigned n=0;n<2;n++){
  if(!retry(13) || !byte(SAFE_OPENED) || at(SAFE_VECTOR)!=SAFE_ASYNC_ISR)return 0;
  /* Exercise synchronous compatibility while experimental transport owns UART. */
  puts("Explicitly enabled session: ordinary output still works.");
  if(!retry(34) || !stock())return 0;
 }
 record("ACTIVATION CLOSE PASS");return 1;
}
static int child(const char *file,const char *header,char report_prefix,unsigned size){
 char command[]="RUN &80000",name[24];uint8_t data[160];
 if(!stock() || mos_load(file,(char *)0x80000,0x10000) || memcmp((void *)0x80040,header,9))return 0;
 const char prefixes[]={report_prefix,report_prefix=='S'?'P':'K',report_prefix=='S'?'G':'J'};
 for(unsigned n=0;n<3;n++)snprintf((char *)(0x80049+n*16),16,"%c%04u.dat",prefixes[n],run_id);
 if(mos_oscli(command,NULL,0) || !stock())return 0;
 snprintf(name,sizeof(name),"%c%04u.dat",report_prefix,run_id);
 uint8_t f=mos_fopen(name,FA_READ);if(!f)return 0;
 unsigned got=mos_fread(f,(char *)data,size+1);mos_fclose(f);if(got!=size)return 0;
 if(report_prefix=='S'){
  if(memcmp(data,"UART0ST1\x01\x00\x04\x00",12))return 0;
  const uint8_t pauses[]={0,1,4,8};
  for(unsigned n=0;n<4;n++){const uint8_t *r=data+12+n*16;
   if(r[0]!=pauses[n] || r[1]!=32 || r[2]!=32 || !r[3] || u24(r+4)!=SAFE_STRESS_BYTES[n] || r[10] || r[12] || r[13]!=47 || r[14] || r[15])return 0;
  }
 }else if(memcmp(data,"UART0MOS\x00",9) || u24(data+9)!=128 || u24(data+12)!=4110 || u24(data+15)!=128 || data[18] || data[20]!=63)return 0;
 return 1;
}
static int stress_test(void){
 record("3/4: batch16 OTIRX, four pauses, ordered replies and 32768 compared receiver bytes...");
 if(!child("stress.bin","MOS\x00\x01UBD1",'S',76))return 0;
 record("STRESS AND STOCK RETURN PASS");return 1;
}
static int integration_test(void){
 record("4/4: masked-IFF output and application exit with a queued source...");
 if(!child("app.bin","MOS\x00\x01UTC1",'I',21))return 0;
 record("APPLICATION EXIT STOCK RESTORE PASS");return 1;
}
static int selection(char choice){
 if(!begin()){puts("Cannot reserve numbered reports; no test started.");return 1;}
 int ok=1;int (*tests[])(void)={discovery_test,activation_test,stress_test,integration_test};
 for(unsigned n=0;n<4;n++)if(choice=='0'||choice==(char)('1'+n)){if(!tests[n]()){ok=0;break;}}
 char end[64];snprintf(end,sizeof(end),"END run=%04u %s",run_id,ok?"PASS":"FAIL");record(end);
 mos_fclose(log_file);mos_fclose(index_file);
 if(!logs_ok)ok=0;
 puts(ok?"UART0 STARTUP-SAFE SUITE PASS":"UART0 STARTUP-SAFE SUITE FAIL: report the last progress line.");return !ok;
}
static void input_begin(void){menu_key_head=menu_key_tail=0;memset((void *)menu_key_held,0,sizeof(menu_key_held));mos_setkbvector(menu_key_callback,0);}
static char key(void){while(menu_key_head==menu_key_tail){}char c=menu_key_data[menu_key_tail];menu_key_tail=(menu_key_tail+1)&15;return c;}
int main(int argc,char **argv){
 putch(12);puts("UART0 STARTUP-SAFE QUALIFICATION v1");
 puts("Allow up to two minutes for Run all. A stall is FAIL; report the last progress line.");
 uint32_t crc=rom_crc();printf("Installed MOS CRC32 %08lX; expected %08lX (physical) or %08lX (emulator).\n",(unsigned long)crc,(unsigned long)SAFE_ROM_CRC,(unsigned long)SAFE_FLEXE_CRC);
 if(crc!=SAFE_ROM_CRC && crc!=SAFE_FLEXE_CRC){puts("FAIL: wrong MOS image; no experimental transport activated.");return 1;}
 api=uart_discover();if(!api || memcmp(api,"UTX1",4) || api[4]!=1 || api[5]<2 || api[6]<54){puts("FAIL: required API is missing.");return 1;}
 if(argc>1 && argv[1][0]>='0'&&argv[1][0]<='4')return selection(argv[1][0]);
 for(;;){
  puts("\n1 Stock transport and discovery\n2 Explicit activation and close/reopen\n3 OTIRX pause/full-duplex integrity\n4 Masked-IFF and application-exit cleanup\n0 Run all\nQ Return to MOS\nChoose:");
  input_begin();char c;do{c=key();}while(!strchr("01234qQ",c));mos_setkbvector(NULL,0);
  if(c=='q'||c=='Q')break;printf("Selected %c\n",c);selection(c);
 }
 puts("UART0 STARTUP-SAFE MENU RETURN");return 0;
}
