/* UART0 qualification suite. C menu: AgonDev; native children: ZDS II.
 * Reports use sequence numbers, never the unreliable RTC. No private UART owner.
 */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "identity.h"

#define PASS 0
#define FAIL 1
#define SKIP 2
#define PENDING 3
#define CHILD ((char *)0x80000)
extern const uint8_t *uart_discover(void);
extern uint24_t diag_take(void);
extern uint8_t rom_byte0(void);
void *diag_function;
uint8_t diag_status;
static const uint8_t *api;
static uint24_t entry_flags;
static volatile uint8_t *sv;
static uint32_t crc_table[256],rom_crc;
static unsigned run_id;
static uint8_t detail,index_log;
static int log_ok;
static char line[256],name[32];
static char board[64]="unspecified hardware";
static char vdp_label[64]="not recorded";
static char mos_image[64]="mos-candidate.bin",vdp_image[64]="vdp-2.16.0.bin";
static int vdp_flash=1;
static int physical_receiver=0;
static char vdp_restore[64]="vdp-2.16.0.bin";
static const char *status_name[]={"PASS","FAIL","SKIP","PENDING"};
static uint24_t u24(const uint8_t *p) {return p[0]+((uint24_t)p[1]<<8)+((uint24_t)p[2]<<16);}
static void crc_init(void) {
    for(unsigned n=0;n<256;n++) {uint32_t c=n;for(unsigned j=0;j<8;j++)c=(c>>1)^((c&1)?0xedb88320UL:0);crc_table[n]=c;}
}
static uint32_t crc_byte(uint32_t c,uint8_t b) {return crc_table[(c^b)&255]^(c>>8);}
static uint32_t installed_crc(void) {
    uint32_t c=crc_byte(0xffffffffUL,rom_byte0());
    const volatile uint8_t *p=(const volatile uint8_t *)1;
    for(uint24_t n=1;n<0x20000;n++) c=crc_byte(c,*p++);
    return c^0xffffffffUL;
}
static int exists(const char *path) {uint8_t f=mos_fopen(path,FA_READ);if(f)mos_fclose(f);return f!=0;}
static int journal(const char *s) {
    unsigned n=strlen(s);
    if(!log_ok)return 0;
    if(mos_fwrite(detail,(char *)s,n)!=n || mos_fwrite(index_log,(char *)s,n)!=n)log_ok=0;
    return log_ok;
}
static void record_status(unsigned test,int status) {
    snprintf(line,sizeof(line),"TEST %u %s\r\n",test,status_name[status]);puts(line);journal(line);
}
static void filename(char *out,char prefix,const char *ext) {snprintf(out,32,"%c%04u.%s",prefix,run_id,ext);}
static void checkpoint(void) {
    /* FAT directory lengths/data are committed after every completed stage. */
    if(detail)mos_fclose(detail);
    if(index_log)mos_fclose(index_log);
    filename(name,'R',"log");
    detail=mos_fopen(name,FA_WRITE|FA_OPEN_APPEND);
    index_log=mos_fopen("runs.log",FA_WRITE|FA_OPEN_APPEND);
    if(!detail || !index_log)log_ok=0;
}
static unsigned last_run(void) {
    uint8_t f=mos_fopen("runs.log",FA_READ);
    if(!f)return 0;
    char buf[512];unsigned got,state=0,value=0,last=0;
    do {
        got=mos_fread(f,buf,sizeof(buf));
        for(unsigned n=0;n<got;n++) {
            char c=buf[n];
            if(state<4) {
                state=c=="run="[state]?state+1:(c=='r'?1:0);
                if(state==4)value=0;
            } else if(c>='0'&&c<='9') {
                value=value*10+c-'0';
                if(++state==8){if(value>last)last=value;state=0;}
            } else state=0;
        }
    } while(got==sizeof(buf));
    mos_fclose(f);return last;
}
static int begin_run(const char *action) {
    /* Reserve the run log first; an interrupted run's number cannot be reused. */
    const char *prefixes="BNFSPGDIKJHLE";
    for(run_id=last_run()+1;run_id<10000;run_id++) {
        filename(name,'R',"log");if(exists(name))continue;
        int used=0;
        for(const char *p=prefixes;*p;p++){filename(name,*p,"dat");if(exists(name))used=1;}
        filename(name,'C',"txt");if(exists(name))used=1;
        filename(name,'M',"bin");if(exists(name))used=1;
        if(!used)break;
    }
    if(run_id==10000){puts("Run numbers exhausted; preserve results in workspace first.");return 0;}
    filename(name,'R',"log");detail=mos_fopen(name,FA_WRITE|FA_CREATE_NEW);
    if(!detail){puts("Cannot reserve a result log; no test started.");return 0;}
    index_log=mos_fopen("runs.log",FA_WRITE|(exists("runs.log")?FA_OPEN_APPEND:FA_CREATE_NEW));
    if(!index_log){mos_fclose(detail);puts("Cannot open runs.log; no test started.");return 0;}
    log_ok=1;
    snprintf(line,sizeof(line),"UARTSUITE report_version=1 build=%s run=%04u action=%s\r\n",SUITE_BUILD_ID,run_id,action);journal(line);
    snprintf(line,sizeof(line),"board=%s MOS_ROM128K_CRC32=%08lX API=%u.%u entry_RX=%02X entry_modem=%02X\r\n",
        board,(unsigned long)rom_crc,api?api[4]:0,api?api[5]:0,(unsigned)(entry_flags&255),(unsigned)((entry_flags>>8)&255));journal(line);
    snprintf(line,sizeof(line),"VDP_operator_label=%s (not autodetected)\r\n",vdp_label);journal(line);
    puts("Results use sequential run numbers; the RTC is not used.");
    snprintf(line,sizeof(line),"Run %04u; log R%04u.log and running index runs.log",run_id,run_id);puts(line);
    checkpoint();
    return log_ok;
}
static void close_logs(void) {
    if(detail)mos_fclose(detail);
    if(index_log)mos_fclose(index_log);
    detail=index_log=0;
}
static int finish_run(int status) {
    snprintf(line,sizeof(line),"END run=%04u %s\r\n",run_id,status_name[status]);journal(line);
    close_logs();
    if(!log_ok){puts("Result log write failed; preserve card for inspection.");return FAIL;}
    printf("Run %04u: %s\n",run_id,status_name[status]);return status;
}
static int valid_basename(const char *s) {
    if(!*s || strlen(s)>=64 || strstr(s,".."))return 0;
    for(;*s;s++)if(!((*s>='a'&&*s<='z')||(*s>='A'&&*s<='Z')||(*s>='0'&&*s<='9')||*s=='.'||*s=='-'||*s=='_'))return 0;
    return 1;
}
static void config(void) {
    char cfg[512];uint8_t f=mos_fopen("suite.cfg",FA_READ);if(!f)return;
    unsigned n=mos_fread(f,cfg,sizeof(cfg)-1);mos_fclose(f);cfg[n]=0;
    for(char *p=strtok(cfg,"\r\n");p;p=strtok(NULL,"\r\n")) {
        if(!strncmp(p,"board=",6)){strncpy(board,p+6,sizeof(board)-1);board[sizeof(board)-1]=0;}
        else if(!strncmp(p,"vdp_label=",10)){strncpy(vdp_label,p+10,sizeof(vdp_label)-1);vdp_label[sizeof(vdp_label)-1]=0;}
        else if(!strncmp(p,"mos=",4)&&valid_basename(p+4))strcpy(mos_image,p+4);
        else if(!strncmp(p,"vdp=",4)&&valid_basename(p+4))strcpy(vdp_image,p+4);
        else if(!strcmp(p,"vdp_flash=0"))vdp_flash=0;
        else if(!strcmp(p,"vdp_flash=1"))vdp_flash=1;
        else if(!strncmp(p,"vdp_restore=",12)&&valid_basename(p+12))strcpy(vdp_restore,p+12);
        else if(!strcmp(p,"physical_receiver=1"))physical_receiver=1;
        else if(!strcmp(p,"physical_receiver=0"))physical_receiver=0;
    }
}
static int available(void) {return api && api[4]==1 && api[5]>=1 && api[6]>=46 && (api[7]&4);}
static uint24_t snapshot(const char *phase) {
    uint24_t flags=diag_take();
    snprintf(line,sizeof(line),"RX phase=%s status=%u flags=%02X modem=%02X\r\n",phase,diag_status,(unsigned)(flags&255),(unsigned)((flags>>8)&255));
    puts(line);journal(line);return flags;
}
static int gp_fence(uint8_t token,int vsync) {
    uint8_t bytes[]={23,0,0xc3,23,0,0x80,token};
    sv[sysvar_gp]=0xfe;
    mos_puts((const char *)(bytes+(vsync?0:3)),vsync?7:4,0);
    uint32_t at=getsysvar_time();
    while(sv[sysvar_gp]!=token)if((uint32_t)(getsysvar_time()-at)>2400)return 0;
    return 1;
}
static int diagnostics(void) {
    puts("T1: phased RX diagnostics. Entry flags are recorded separately.");
    if(!available()){puts("SKIP: this MOS has no UART0 diagnostic API 1.1.");return SKIP;}
    uint8_t data[12];memset(data,0,sizeof(data));
    data[0]=entry_flags&255;data[1]=(entry_flags>>8)&255;
    uint24_t flags=snapshot("before-mode");data[3]=flags&255;data[4]=(flags>>8)&255;
    if(diag_status)return FAIL;
    const uint8_t mode[]={22,0,12};mos_puts((const char *)mode,sizeof(mode),0);
    puts("T1: mode 0 and receiver barrier...");
    if(!gp_fence(0x61,0))return FAIL;
    flags=snapshot("after-mode-and-GP");data[6]=flags&255;data[7]=(flags>>8)&255;
    int ok=!diag_status && !(flags&255);
    puts("T1: sixteen VSYNC/GP barriers...");
    for(unsigned n=0;n<16;n++)if(!gp_fence(0x62,1))ok=0;
    flags=snapshot("after-VSYNC-and-GP");data[9]=flags&255;data[10]=(flags>>8)&255;
    ok=ok && !diag_status && !(flags&255);
    filename(name,'D',"dat");uint8_t f=mos_fopen(name,FA_WRITE|FA_CREATE_NEW);
    if(!f)return FAIL;ok=mos_fwrite(f,(char *)data,sizeof(data))==sizeof(data) && ok;mos_fclose(f);
    return ok?PASS:FAIL;
}
static int read_report(const char *path,uint8_t *data,unsigned size) {
    uint8_t f=mos_fopen(path,FA_READ);if(!f)return 0;
    unsigned n=mos_fread(f,(char *)data,size+1);mos_fclose(f);return n==size;
}
static int integration(void) {
    puts("T6: API ordering, masked-IFF output, callbacks, exit fence and ADL=0.");
    if(!available()){puts("SKIP: UART0 API 1.1 is required.");return SKIP;}
    snapshot("before-integration");if(diag_status)return FAIL;
    if(mos_load("app.bin",CHILD,0x10000) || memcmp(CHILD+64,"MOS\x00\x01UTC1",9))return FAIL;
    filename(CHILD+73,'I',"dat");filename(CHILD+89,'K',"dat");filename(CHILD+105,'J',"dat");
    char command[]="RUN &80000";
    uint8_t error=mos_oscli(command,NULL,0),report[23];
    filename(name,'I',"dat");
    if(error || !read_report(name,report,21) || memcmp(report,"UART0MOS\x00",9) || u24(report+9)!=128 || u24(report+12)!=4110 || u24(report+15)!=128 || report[18] || report[20]!=63)return FAIL;
    uint24_t flags=snapshot("after-return-fence");
    if(diag_status || (flags&255))return FAIL;
    if(mos_load("short.bin",CHILD,0x10000) || memcmp(CHILD+64,"MOS\x00\x00",5))return FAIL;
    char short_command[]="RUN &80000";
    if(mos_oscli(short_command,NULL,0))return FAIL;
    flags=snapshot("after-ADL0");if(diag_status || (flags&255))return FAIL;
    journal("INTEGRATION accepted=128/4110/128 GP=63 exit_session_closed=1 ADL0_return=1\r\n");
    return PASS;
}
static int validate_child(unsigned test,const uint8_t *b,unsigned size) {
    if(test==2) {
        if(size!=148 || memcmp(b,"UART0BN1\x01\x00\x08\x00",12))return 0;
        for(unsigned n=0;n<8;n++) {
            const uint8_t *r=b+12+n*17;
            if(r[0]!=((n/2)^(n%2))%2 || r[1]!=n/2 || u24(r+5)!=1202774 || u24(r+11)!=8210 || r[14] || r[16])return 0;
            if((!r[0] && u24(r+8)) || (r[0] && (!u24(r+8)||u24(r+8)>131072)))return 0;
        }
    } else {
        const uint8_t pause[]={0,1,4,8};const unsigned bytes[]=SUITE_STRESS_BYTES;
        if(size!=76 || memcmp(b,"UART0ST1\x01\x00\x04\x00",12))return 0;
        for(unsigned n=0;n<4;n++) {
            const uint8_t *r=b+12+n*16;
            if(r[0]!=pause[n] || r[1]!=32 || r[2]!=32 || !r[3] || r[3]>32 || u24(r+4)!=bytes[n] || r[10] || r[12] || r[13]!=47 || r[14] || r[15])return 0;
        }
    }
    return 1;
}
static int child_test(unsigned test) {
    puts(test==2?"T2: legacy/async benchmark; normally under two minutes.":"T3: pause/full-duplex; normally under two minutes.");
    if(!available()){puts("SKIP: UART0 API 1.1 is required.");return SKIP;}
    const char *bin=test==2?"bench.bin":"stress.bin";
    uint8_t error=mos_load(bin,CHILD,0x10000);
    if(error){printf("Cannot load %s; MOS error %u\n",bin,error);return FAIL;}
    if(memcmp(CHILD+64,"MOS\x00\x01UTC1",9)){puts("Child fixture header mismatch.");return FAIL;}
    filename(CHILD+73,test==2?'B':'S',"dat");
    filename(CHILD+89,test==2?'N':'P',"dat");
    filename(CHILD+105,test==2?'F':'G',"dat");
    char command[]="RUN &80000";
    error=mos_oscli(command,NULL,0);
    uint8_t b[150];unsigned size=test==2?148:76;
    filename(name,test==2?'B':'S',"dat");
    int ok=!error && read_report(name,b,size) && validate_child(test,b,size);
    if(ok) {
        char hx[3];snprintf(line,sizeof(line),"REPORT %s hex=",name);journal(line);
        for(unsigned n=0;n<size;n++){snprintf(hx,sizeof(hx),"%02X",b[n]);journal(hx);}journal("\r\n");
        unsigned count=test==2?8:4,step=test==2?17:16;
        for(unsigned n=0;n<count;n++) {
            uint8_t *r=b+12+n*step;
            snprintf(line,sizeof(line),"CASE test=%u n=%u ticks=%lu rx=%02X modem=%02X\r\n",test,n+1,(unsigned long)u24(r+(test==2?2:7)),r[test==2?14:10],r[test==2?15:11]);journal(line);
        }
    }
    filename(name,test==2?'N':'P',"dat");
    uint8_t baseline[4];
    if(!read_report(name,baseline,3))ok=0;
    else {snprintf(line,sizeof(line),"BASELINE %s RX=%02X modem=%02X\r\n",name,baseline[0],baseline[1]);journal(line);}
    return ok?PASS:FAIL;
}
static uint32_t parse_ms(const char *s) {
    uint32_t v=0;unsigned digits=0;int dot=0;
    if(!*s)return 0;
    for(;*s;s++) {
        if(*s=='.'&&!dot){dot=1;continue;}
        if(*s<'0'||*s>'9'||(dot&&digits==3))return 0;
        v=v*10+*s-'0';if(v>600000)return 0;if(dot)digits++;
    }
    if(!dot)digits=0;
    while(digits++<3)v*=10;
    return v;
}
static int calibration(int automated) {
    puts("T4: MOS ticks against an independent stopwatch.");
    if(automated){journal("CALIBRATION NOT_MEASURED automated run has no independent reference\r\n");return PENDING;}
    puts("Start stopwatch with ENTER. Stop both with ENTER after 10-600 seconds.");
    puts("Press ESC to skip. This measures manual key timing, not precision timing.");
    char key;do{key=getch();}while(key!=13 && key!=27);
    if(key==27){return SKIP;}
    uint32_t at=getsysvar_time();puts("Timing active; press ENTER when stopping the stopwatch.");
    do{key=getch();}while(key!=13 && key!=27);
    uint32_t delta=getsysvar_time()-at;
    if(key==27){return SKIP;}
    char seconds[32]={0};puts("Enter stopwatch seconds (e.g. 30.125), then ENTER:");mos_editline(seconds,sizeof(seconds),1);
    uint32_t ms=parse_ms(seconds);
    if(ms<10000 || ms>600000 || !delta || delta>100000){puts("Invalid measurement; select T4 again to retry.");return FAIL;}
    uint32_t whole=delta*1000UL/ms,fraction=(delta*1000UL%ms)*1000UL/ms;
    snprintf(line,sizeof(line),"CALIBRATION raw_ticks=%lu external_ms=%lu ticks_per_second=%lu.%03lu video_mode=%u method=manual_keys\r\n",(unsigned long)delta,(unsigned long)ms,(unsigned long)whole,(unsigned long)fraction,sv[sysvar_scrMode]);puts(line);journal(line);
    filename(name,'C',"txt");uint8_t f=mos_fopen(name,FA_WRITE|FA_CREATE_NEW);
    if(!f)return FAIL;unsigned len=strlen(line);int ok=mos_fwrite(f,line,len)==len;mos_fclose(f);
    return ok?PASS:FAIL;
}
static uint32_t u32(const uint8_t *p) {return (uint32_t)p[0]+((uint32_t)p[1]<<8)+((uint32_t)p[2]<<16)+((uint32_t)p[3]<<24);}
static int receiver_margin(void) {
    puts("T7: diagnostic VDP receiver-margin experiment; 42 trials, under two minutes.");
    if(!available())return SKIP;
    if(mos_load("margin.bin",CHILD,0x10000) || memcmp(CHILD+64,"MOS\x00\x01UTC1",9))return FAIL;
    filename(CHILD+73,'H',"dat");filename(CHILD+89,'L',"dat");filename(CHILD+105,'E',"dat");
    char command[]="RUN &80000";uint8_t error=mos_oscli(command,NULL,0);
    uint8_t b[2030];filename(name,'H',"dat");
    if(error || !read_report(name,b,2028) || memcmp(b,"URMHOST1\x01",9))return FAIL;
    if(b[9]==3){journal("MARGIN SKIP diagnostic_VDP_required\r\n");return SKIP;}
    if(b[9] || b[10]!=42 || b[11])return FAIL;
    const uint8_t thresholds[]={64,96,112,120,124,126,127};
    unsigned invalid=0,boundary=0,reserve=128;
    for(unsigned n=0;n<42;n++) {
        uint8_t *p=b+12+n*48;unsigned threshold=thresholds[(n%21)/3],hold=n<21?5:20;
        if(memcmp(p,"URM1\x01",5)||p[5]!=threshold||p[6]!=hold||p[44]||!p[45]||p[47])return FAIL;
        int crc_ok=u32(p+36)==4096 && u32(p+40)==0x87897582UL;
        uint32_t errors=u32(p+24);
        if((errors&~16UL) || (!crc_ok && !(errors&16)))return FAIL;
        if(threshold==64 && (!crc_ok || errors))return FAIL;
        int valid=p[46] && !p[7] && !u32(p+8) && !u32(p+12) && p[16]==threshold && p[17]==1 && !u32(p+18) && p[22]>threshold && p[22]<=128 && p[23]==p[22] && u32(p+32)>=200 && u32(p+28)>=hold*1000;
        if(!valid)invalid++;
        if(valid && (errors&16))boundary++;
        if(valid && threshold==64 && 128-p[23]<reserve)reserve=128-p[23];
        snprintf(line,sizeof(line),"MARGIN case=%u threshold=%u hold_ms=%u fifo=%u crc_ok=%u errors=%lu valid=%u\r\n",n+1,threshold,hold,p[23],crc_ok,(unsigned long)errors,valid);journal(line);
    }
    snprintf(line,sizeof(line),"MARGIN physical_target=%u invalid=%u overflow_cases=%u stock_min_space=%u electrical_edge_timing=NOT_MEASURED\r\n",physical_receiver,invalid,boundary,reserve);puts(line);journal(line);
    if(!physical_receiver){puts("Emulator protocol only; physical margin remains unqualified.");return PENDING;}
    if(invalid || !reserve || reserve==128){puts("Receiver evidence is inconclusive; preserve reports for inspection.");return PENDING;}
    puts("Empirical receiver experiment complete; inspect the saved threshold boundary.");
    return PASS;
}
static int capture_guide(void) {
    puts("T5: physical CTS margin needs a passive TX/RX/CTS capture.");
    puts("Console8 expansion header does not expose these signals.");
    puts("Probe access and receiver reserve must be established first.");
    puts("T7 provides a separate diagnostic-firmware receiver experiment.");
    puts("See capture.txt for passive capture format and limits.");
    puts("No software PASS is claimed for electrical CTS margin.");
    journal("CTS_MARGIN NOT_MEASURED passive capture and receiver reserve required\r\n");return PENDING;
}
static int file_crc(const char *path,uint32_t *crc,uint32_t *size) {
    uint8_t f=mos_fopen(path,FA_READ);if(!f)return 0;
    char buf[512];uint32_t c=0xffffffffUL,n=0;unsigned got;
    do{got=mos_fread(f,buf,sizeof(buf));for(unsigned i=0;i<got;i++)c=crc_byte(c,(uint8_t)buf[i]);n+=got;if(got && !(n%65536UL))putch('.');}while(got==sizeof(buf));
    mos_fclose(f);*crc=c^0xffffffffUL;*size=n;return n!=0;
}
static int backup_mos(void) {
    filename(name,'M',"bin");uint8_t err=mos_save(name,(char *)0,0x20000);
    uint32_t crc,size;
    if(err || !file_crc(name,&crc,&size) || size!=0x20000 || crc!=rom_crc){puts("MOS backup verification FAIL");return FAIL;}
    snprintf(line,sizeof(line),"BACKUP %s bytes=%lu CRC32=%08lX\r\n",name,(unsigned long)size,(unsigned long)crc);puts(line);journal(line);return PASS;
}
static void firmware_menu(void) {
    puts("STAGED FIRMWARE: 1 MOS; 2 VDP; 3 MOS backup; 4 restore stock VDP; 0 back");
    puts("Read firmware.txt for backup/recovery and VDP update restrictions.");
    if(!vdp_flash)puts("VDP flashing is unavailable in this emulator profile.");
    char choice=getch();if(choice<'1'||choice>'4')return;
    if(!begin_run("firmware"))return;
    if(choice=='3'){finish_run(backup_mos());return;}
    if((choice=='2'||choice=='4') && !vdp_flash) {
        puts("VDP flashing unavailable in this emulator profile; updater not launched.");
        journal("FLASH_SKIP target=VDP reason=emulator_OTA_not_qualified\r\n");
        finish_run(SKIP);return;
    }
    const char *image=choice=='1'?mos_image:choice=='4'?vdp_restore:vdp_image;
    uint32_t crc,size;
    printf("Checking staged %s...\n",image);
    if(!file_crc(image,&crc,&size) || (choice=='1'&&size>0x20000)){puts("Firmware file missing/invalid size.");finish_run(FAIL);return;}
    snprintf(line,sizeof(line),"FLASH_REQUEST target=%s file=%s bytes=%lu CRC32=%08lX\r\n",choice=='1'?"MOS":"VDP",image,(unsigned long)size,(unsigned long)crc);puts(line);journal(line);
    puts("The flash utility will show the target/CRC and ask Y/N. Choose N to cancel.");
    /* A reset can prevent return. Leave an explicit pending handoff, not PASS. */
    journal("FLASH_HANDOFF verification=PENDING\r\n");
    close_logs();
    if(!log_ok){puts("Cannot record firmware request; utility not launched.");return;}
    if(mos_load("flash.bin",(char *)0xb0000,0x10000)){
        puts("Cannot load staged flash.bin.");checkpoint();
        journal("FLASH_RETURN result=FAIL reason=utility_load_failed\r\n");
        finish_run(FAIL);return;
    }
    char command[128];snprintf(command,sizeof(command),"RUN &B0000 %s %s",choice=='1'?"mos":"vdp",image);
    uint8_t error=mos_oscli(command,NULL,0);
    checkpoint();
    snprintf(line,sizeof(line),"FLASH_RETURN code=%u result=%s\r\n",error,error?"FAIL":"UNVERIFIED");journal(line);
    finish_run(error?FAIL:PENDING);
    if(error)printf("FLASH RESULT FAIL: utility return code %u.\n",error);
    else {
        puts("FLASH RESULT UNVERIFIED: utility return code 0 does not prove success.");
        puts("Any updater error means FAIL. A completed update needs readback verification.");
    }
}
static int execute(unsigned test,int automated) {
    if(test==7)return receiver_margin();
    if(test==6)return integration();
    if(test==1)return diagnostics();if(test==2||test==3)return child_test(test);
    if(test==4)return calibration(automated);return capture_guide();
}
static int selection(unsigned test,int automated) {
    if(!begin_run(test?"individual":"all"))return FAIL;
    int overall=PASS;
    const unsigned order[]={1,6,2,3,4,5};
    for(unsigned i=0;i<(test?1:6);i++) {
        unsigned n=test?test:order[i];
        int status=execute(n,automated);
        record_status(n,status);
        checkpoint();
        if(status==FAIL || !log_ok){overall=FAIL;puts("Suite stopped; earlier results are preserved.");break;}
        if(status!=PASS)overall=PENDING;
    }
    return finish_run(overall);
}
int main(int argc,char **argv) {
    sv=mos_sysvars();api=uart_discover();
    if(api && (memcmp(api,"UTX1",4)||api[4]!=1))api=NULL;
    if(available()){diag_function=(void *)u24(api+43);entry_flags=diag_take();}
    crc_init();putch(12);puts("UART0 QUALIFICATION SUITE v1");
    puts("Reading installed MOS fingerprint...");rom_crc=installed_crc();config();
    if(argc>1) {
        if(!strcmp(argv[1],"auto")){int r=selection(0,1);puts(r==FAIL?"UART0 SUITE AUTO FAIL":"UART0 SUITE AUTO COMPLETE; manual measurements pending");return r==FAIL;}
        if(argv[1][0]>='1'&&argv[1][0]<='7'&&!argv[1][1])return selection(argv[1][0]-'0',0)==FAIL;
    }
    for(;;) {
        puts("\nUART0 QUALIFICATION SUITE v1");
        printf("Hardware label: %s; installed MOS CRC32 %08lX\n",board,(unsigned long)rom_crc);
        printf("VDP label: %s (operator supplied)\n",vdp_label);
        puts("1 Firmware/API and phased RX diagnostics\n2 Legacy/async benchmark\n3 Pause / full-duplex stress\n4 Independent stopwatch calibration\n5 CTS capture preparation\n6 API / masked-IFF / exit / ADL=0 smoke tests\n7 Diagnostic VDP receiver-margin experiment (separate)\n0 Run all baseline tests (manual timing can be skipped)\n9 Staged firmware / MOS backup\nQ Return to MOS\nPress a choice key:");
        char c=getch();if(c=='q'||c=='Q')break;
        if(c=='9'){firmware_menu();continue;}
        if(c>='0'&&c<='7'){selection(c-'0',0);puts("Press any key for menu.");getch();}
        else puts("Choose 0-7, 9 or Q.");
    }
    puts("UART0 SUITE RETURN PASS");return 0;
}
