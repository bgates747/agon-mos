/* Bouncing-balls UART demo. Original C/AgonDev application; MIT. */
#include "core.h"
#include "platform.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "identity.h"
typedef struct {
 uint32_t physics,collision,draw,checksum,build,submit,release,confirm,drain;
 uint32_t first,submitted,wall_submitted,presented,world,pixels,pairs,contacts,frame,step;
 uint16_t number,balls,bytes,hud_bytes;uint8_t mode,output,collide,flags,token;
} Record;
typedef struct {uint8_t bytes[BD_PACKET_CAP];uint24_t id;Record *r;uint8_t released,token;} Slot;
typedef struct {uint24_t id;uint32_t stamp;} Notification;
typedef struct {unsigned mode,output,collide,balls;uint32_t seed;} Config;
static Slot slots[2];
static World world;
static Record records[128];
static unsigned record_count,record_write,case_id;
static uint32_t record_overwritten,scenario_frames,scenario_measured,scenario_first,scenario_last;
static unsigned scenario_live;
#define RATE_WINDOW 8
static Record rate_samples[RATE_WINDOW];
static unsigned rate_write;
static volatile Notification notifications[8];
static volatile uint8_t note_head,note_tail,note_bad;
static volatile uint8_t *sysvars;
static unsigned api_available,async_open,token_counter;
static unsigned run_id;
static char report_name[16];
static uint32_t overhead,wire_probe,last_fps,last_physics,last_collision,last_draw,last_checksum,last_submit,last_release;
static uint32_t last_pairs,last_contacts,last_bytes;
static unsigned failures,phase_total,phase_frames;
static uint32_t phase_frame;
static uint32_t sum_build,sum_confirm,last_build,last_confirm;
static uint32_t fps_window_start;
static uint32_t sum_physics,sum_collision,sum_draw,sum_checksum,sum_submit,sum_release;
static unsigned fps_window_frames;
static char failure_reason[100];
static Config config={0,0,0,24,0x42414c4cUL};
static int stopped,requested,reset_scene;
static int exists(const char *p){uint8_t f=mos_fopen(p,FA_READ);if(f)mos_fclose(f);return f!=0;}
#include "run_counter.inc"
static int reserve_report(void){
 unsigned n=first_report();if(!n)return 0;
 for(run_id=n;run_id<10000;run_id++){snprintf(report_name,sizeof(report_name),"R%04u.log",run_id);if(!exists(report_name))break;}
 if(run_id==10000)return 0;
 uint8_t f=mos_fopen(report_name,FA_WRITE|FA_CREATE_NEW);if(!f)return 0;
 char s[160];int len=snprintf(s,sizeof(s),"BALLS report_version=2 build=%s run=%04u tick_hz=%lu wall_hz=%lu\r\n",BD_BUILD,run_id,(unsigned long)BD_TICK_HZ,(unsigned long)BD_WALL_HZ);
 int ok=mos_fwrite(f,s,(unsigned)len)==(unsigned)len;mos_fclose(f);
 return ok&&save_next_report(run_id+1);
}
static int append_text(const char *name,const char *s){
 uint8_t f=mos_fopen(name,FA_WRITE|FA_OPEN_APPEND);if(!f)return 0;
 unsigned n=strlen(s);int ok=mos_fwrite(f,(char *)s,n)==n;mos_fclose(f);return ok;
}
static int report_text(const char *s){return append_text(report_name,s);}
static void fail(const char *s){if(!failures)snprintf(failure_reason,sizeof(failure_reason),"%s",s);failures++;}
void bd_note_completion(void){
 uint8_t next=(uint8_t)((note_head+1)&7);
 if(bd_notify_status!=4||bd_notify_context!=0x42444d||next==note_tail){note_bad=1;return;}
 notifications[note_head].id=bd_notify_id;
 notifications[note_head].stamp=notification_ticks();note_head=next;
}
static int release_events(Slot *s){
 if(s->r->mode==1){
  uint8_t status=api_call(63,0,0,0);
  if(!status){
   if(bd_result_hl!=s->id||s->released){fail("Unexpected foreground completion ID/count");return 0;}
   s->released=1;s->r->release=ticks()-s->r->submitted;
  }else if(status!=1){fail("Foreground completion API error");return 0;}
 }else if(s->r->mode==2){
  while(note_tail!=note_head){
   uint24_t id=notifications[note_tail].id;uint32_t stamp=notifications[note_tail].stamp;
   note_tail=(uint8_t)((note_tail+1)&7);
   if(id!=s->id||s->released){fail("Unexpected direct completion ID/count");return 0;}
   s->released=1;s->r->release=stamp-s->r->submitted;
  }
 }
 if(note_bad){fail("Callback context/status/queue error");return 0;}return 1;
}
static void read_keys(void){
 int c;while((c=key_pop())){
  if(c=='q'){stopped=1;requested=1;}
  else if(c>='1'&&c<='3'){
   unsigned mode=(unsigned)(c-'1');if(mode&&!api_available)continue;
   if(mode!=config.mode){config.mode=mode;requested=1;}
  }else if(c=='b'){config.output^=1;requested=1;}
  else if(c=='c'){config.collide^=1;requested=1;}
  else if(c=='r'){requested=reset_scene=1;}
  else if(c=='='&&config.balls<BD_MAX_BALLS){config.balls+=4;if(config.balls>BD_MAX_BALLS)config.balls=BD_MAX_BALLS;requested=1;}
  else if(c=='-'&&config.balls>4){config.balls-=4;requested=1;}
 }
}
static int wait_frame(Slot *s,int drain_probe){
 uint32_t began=ticks();uint8_t token=s->token;
 unsigned probe_opened=0;
 while(!s->released||sysvars[sysvar_gp]!=token||(drain_probe&&!s->r->drain)){
  if(s->r->mode&&!release_events(s))return 0;
  if(drain_probe&&!s->r->drain){
   uint8_t status;
   if(s->r->mode)status=api_call(31,0,0,0);
   else {status=api_call(13,0,0,0);if(!status)probe_opened=1;}
   if(!status)s->r->drain=ticks()-s->r->submitted;
   else if(status!=1){fail("Dedicated drain probe API error");return 0;}
  }
  read_keys();
  if((uint32_t)(ticks()-began)>BD_TICK_HZ*10){fail("Frame completion/presentation timed out");return 0;}
 }
 s->r->presented=wall_ticks();s->r->confirm=ticks()-s->r->submitted;last_release=s->r->release;
 if(!(s->r->flags&1)){
  if(!scenario_measured)scenario_first=s->r->presented;
  scenario_last=s->r->presented;scenario_measured++;
  Record *old=&rate_samples[rate_write];
  if(fps_window_frames==RATE_WINDOW){
   sum_physics-=old->physics;sum_collision-=old->collision;sum_draw-=old->draw;
   sum_checksum-=old->checksum;sum_build-=old->build;sum_submit-=old->submit;
   sum_release-=old->release;sum_confirm-=old->confirm;
  }else fps_window_frames++;
  *old=*s->r;rate_write=(rate_write+1)%RATE_WINDOW;
  sum_physics+=old->physics;sum_collision+=old->collision;sum_draw+=old->draw;
  sum_checksum+=old->checksum;sum_build+=old->build;sum_submit+=old->submit;
  sum_release+=old->release;sum_confirm+=old->confirm;
  last_build=sum_build/fps_window_frames;last_confirm=sum_confirm/fps_window_frames;
  last_physics=sum_physics/fps_window_frames;last_collision=sum_collision/fps_window_frames;
  last_draw=sum_draw/fps_window_frames;last_checksum=sum_checksum/fps_window_frames;
  last_submit=sum_submit/fps_window_frames;last_release=sum_release/fps_window_frames;
  unsigned oldest=(rate_write+RATE_WINDOW-fps_window_frames)%RATE_WINDOW;
  fps_window_start=rate_samples[oldest].presented;
  uint32_t elapsed=s->r->presented-fps_window_start;
  if(fps_window_frames>1&&elapsed)last_fps=(fps_window_frames-1)*BD_WALL_HZ*100UL/elapsed;
 }
 if(probe_opened&&!transport_close()){fail("Standard drain probe close failed");return 0;}
 return 1;
}
static unsigned add_line(uint8_t *p,unsigned n,unsigned x,unsigned y,const char *s){
 p[n++]=31;p[n++]=(uint8_t)x;p[n++]=(uint8_t)y;
 unsigned width=x?19:38,len=strlen(s);for(unsigned i=0;i<width;i++)p[n++]=i<len?(uint8_t)s[i]:' ';
 return n;
}
static unsigned fps100(uint32_t duration){return duration?(unsigned)(BD_TICK_HZ*100UL/duration):0;}
static unsigned metric_line(uint8_t *p,unsigned n,unsigned row,const char *name,uint32_t duration){
 char text[48];unsigned f=fps100(duration);
 if(!duration){snprintf(text,sizeof(text),"%-11s not measured yet",name);return add_line(p,n,0,row,text);}
 snprintf(text,sizeof(text),"%-11s %6lu us %3u.%02u fps",name,(unsigned long)(duration*125UL/144UL),f/100,f%100);
 return add_line(p,n,0,row,text);
}
static unsigned hud(uint8_t *p,unsigned n,const Config *c){
 char line[48];
 const char *mode=c->mode==0?"1 STANDARD":c->mode==1?"2 ASYNC EVENTS":"3 ASYNC CALLBACK";
 n=add_line(p,n,20,0,"UART0 BALLS");
 if(phase_total)snprintf(line,sizeof(line),"Case %u/%u  %u/%u",case_id+1,phase_total,(unsigned)phase_frame,phase_frames);
 else snprintf(line,sizeof(line),"LIVE %lu Q quit",(unsigned long)phase_frame);
 n=add_line(p,n,20,1,line);n=add_line(p,n,20,2,mode);
 n=add_line(p,n,20,3,c->output?"VDP CIRCLES":"BITMAP UPLOAD");
 snprintf(line,sizeof(line),"Balls %u  - / =",c->balls);n=add_line(p,n,20,5,line);
 n=add_line(p,n,20,6,c->collide?"C: BALL COLLISIONS":"C: WALLS ONLY");
 n=add_line(p,n,20,8,"1/2/3 transport");n=add_line(p,n,20,9,"B output  R restart");n=add_line(p,n,20,10,"Q quit / save log");
 snprintf(line,sizeof(line),"Shown %u.%02u FPS",(unsigned)(last_fps/100),(unsigned)(last_fps%100));n=add_line(p,n,20,12,line);
 n=add_line(p,n,20,13,"Confirmed via reply");
 n=metric_line(p,n,16,"Physics",last_physics);n=metric_line(p,n,17,"Collisions",last_collision);
 n=metric_line(p,n,18,"Local draw",last_draw);n=metric_line(p,n,19,"Checksum",last_checksum);
 n=metric_line(p,n,20,"Submit",last_submit);n=metric_line(p,n,21,"Release obs",last_release);
 n=metric_line(p,n,22,"Drain probe",wire_probe);n=metric_line(p,n,23,"Confirm obs",last_confirm);n=metric_line(p,n,26,"Packet prep",last_build);
 snprintf(line,sizeof(line),"Pairs %lu contacts %lu",(unsigned long)last_pairs,(unsigned long)last_contacts);n=add_line(p,n,0,24,line);
 snprintf(line,sizeof(line),"%lu bytes/frame  %lu B/s",(unsigned long)last_bytes,(unsigned long)(last_fps*last_bytes/100UL));n=add_line(p,n,0,25,line);
 n=add_line(p,n,0,27,"Async render overlaps previous upload");
 n=add_line(p,n,0,28,"Rolling 8 frames; no automatic stop");return n;
}
static int submit(Slot *s,const Config *c){
 s->r->wall_submitted=wall_ticks();s->r->submitted=ticks();s->released=0;
 if(!c->mode){
  mos_puts((const char *)s->bytes,s->r->bytes,0);s->released=1;s->r->release=ticks()-s->r->submitted;
 }else{
  uint8_t status=api_call(66,(uint24_t)s->bytes,s->r->bytes,0);
  if(status){fail("Borrowed frame submission refused");return 0;}s->id=bd_result_hl;
 }
 s->r->submit=ticks()-s->r->submitted;return 1;
}
static void setup_video(void){
 const uint8_t setup[]={22,136,23,0,0xc0,0,23,1,0,17,63,17,128,12};
 mos_puts((const char *)setup,sizeof(setup),0);
 for(unsigned i=0;i<64;i++){
  uint8_t colour[]={19,(uint8_t)i,255,(uint8_t)((i&3)*85),(uint8_t)(((i>>2)&3)*85),(uint8_t)(((i>>4)&3)*85)};
  mos_puts((const char *)colour,sizeof(colour),0);
 }
}
static int timer_check(void){
 uint32_t a=ticks(),b=wall_ticks();unsigned spins=0;
 while((uint32_t)(wall_ticks()-b)<7200&&spins++<1000000UL){}
 uint32_t main=ticks()-a,wall=wall_ticks()-b;
 if(wall<7200||main<wall*15UL||main>wall*17UL){fail("PRT timebases do not advance at the expected16:1 ratio");return 0;}
 char line[120];snprintf(line,sizeof(line),"CLOCK precision_ticks=%lu wall_ticks=%lu expected_ratio=16\r\n",(unsigned long)main,(unsigned long)wall);
 if(!report_text(line)){fail("Cannot write clock check");return 0;}
 overhead=0xffffffffUL;
 for(unsigned i=0;i<16;i++){a=ticks();uint32_t cost=ticks()-a;if(cost<overhead)overhead=cost;}
 return 1;
}
static int run_case(const Config *c,unsigned frames,int fresh){
 if(frames&&record_count+frames>=128){fail("RAM report capacity reached");return 0;}
 note_head=note_tail=note_bad=0;
 if(fresh)world_init(&world,c->balls,c->seed);
 else if(c->balls!=world.count)world_resize(&world,c->balls,c->seed);
 record_write=record_count=0;record_overwritten=scenario_frames=scenario_measured=scenario_first=scenario_last=0;scenario_live=!frames;
 char scene[180];snprintf(scene,sizeof(scene),"SCENE case=%u mode=%u output=%u collide=%u balls=%u fresh=%u start_step=%lu\r\n",case_id,c->mode,c->output,c->collide,c->balls,fresh,(unsigned long)world.step);
 if(!report_text(scene)){fail("Cannot save scenario setup");return 0;}
 if(c->mode&&!transport_open(c->mode)){fail("Cannot open/configure async transport");return 0;}async_open=c->mode!=0;
 Slot *pending=0;fps_window_frames=rate_write=0;
 sum_physics=sum_collision=sum_draw=sum_checksum=sum_submit=sum_release=sum_build=sum_confirm=0;
 last_physics=last_collision=last_draw=last_checksum=last_submit=last_release=last_fps=last_build=last_confirm=0;
 phase_frames=frames;
 for(uint32_t frame=0;(!frames||frame<frames)&&!failures;frame++){
  read_keys();if(requested&&frame)break;
  unsigned index=record_write;
  record_write=(record_write+1)%128;
  if(record_count<128)record_count++;else record_overwritten++;
  phase_frame=frame+1;Slot *s=&slots[frame&1];Record *r=&records[index];memset(r,0,sizeof(*r));s->r=r;
  r->number=(uint16_t)case_id;r->balls=(uint16_t)c->balls;r->mode=(uint8_t)c->mode;r->output=(uint8_t)c->output;r->collide=(uint8_t)c->collide;
  r->first=ticks();uint32_t start=r->first;world_integrate(&world);
  uint32_t col=ticks();world_collide(&world,c->collide);r->collision=ticks()-col;r->physics=ticks()-start;
  start=ticks();world_draw(&world,s->bytes+BD_PIXEL_OFFSET);r->draw=ticks()-start;
  start=ticks();r->pixels=pixels_hash(s->bytes+BD_PIXEL_OFFSET);r->checksum=ticks()-start;
  r->frame=frame+1;r->step=world.step;r->world=world_hash(&world);r->pairs=world.pairs;r->contacts=world.contacts;
  start=ticks();s->token=(uint8_t)(1+(token_counter++%250));r->token=s->token;
  unsigned n=frame_commands(s->bytes,&world,c->output,frame&1,s->token);
  n-=7; /* Insert identical HUD policy before flip and its confirmation. */
  unsigned before_hud=n;n=hud(s->bytes,n,c);r->hud_bytes=(uint16_t)(n-before_hud);
  const uint8_t end[]={23,0,0xc3,23,0,0x80,s->token};memcpy(s->bytes+n,end,sizeof(end));n+=sizeof(end);
  if(n>BD_PACKET_CAP){fail("Frame packet capacity exceeded");break;}r->bytes=(uint16_t)n;r->build=ticks()-start;
  if(pending&&!wait_frame(pending,0))break;
  read_keys();if(frames&&requested&&frame){record_count--;break;}
  if(!submit(s,c))break;scenario_frames++;pending=s;
  if(frame==0&&api_available){
   /* Dedicated tight drain observation; excluded from the pipelined FPS window. */
   r->flags|=1;if(!wait_frame(s,1))break;wire_probe=r->drain;pending=0;
  }
  last_pairs=r->pairs;last_contacts=r->contacts;last_bytes=r->bytes;
 }
 if(pending&&!wait_frame(pending,0))return 0;
 if(async_open){if(!transport_close()){fail("Async drain/close failed");return 0;}async_open=0;}
 case_id++;return !failures;
}
static int write_line(uint8_t file,char *text){unsigned n=strlen(text);return mos_fwrite(file,text,n)==n;}
static int save_records(void){
 uint8_t file=mos_fopen(report_name,FA_WRITE|FA_OPEN_APPEND);if(!file)return 0;
 char line[640];
 snprintf(line,sizeof(line),"SCENARIO case=%u interactive=%u frames=%lu retained=%u overwritten=%lu measured=%lu first_presented=%lu last_presented=%lu rate_window=8\r\n",case_id?case_id-1:0,scenario_live,(unsigned long)scenario_frames,record_count,(unsigned long)record_overwritten,(unsigned long)scenario_measured,(unsigned long)scenario_first,(unsigned long)scenario_last);
 if(!write_line(file,line)){mos_fclose(file);return 0;}
 snprintf(line,sizeof(line),"META timer_read_min_ticks=%lu key_scan_hz=100 key_overruns=%u release_mode1=foreground_observed drain=dedicated_observed\r\n",(unsigned long)overhead,key_overruns);
 if(!write_line(file,line)){mos_fclose(file);return 0;}
 for(unsigned i=0;i<record_count;i++){
  Record *r=&records[(record_write+128-record_count+i)%128];
  snprintf(line,sizeof(line),"FRAME case=%u mode=%u output=%u collide=%u balls=%u flags=%u token=%u frame=%lu step=%lu bytes=%u hud_bytes=%u physics=%lu collision=%lu draw=%lu checksum=%lu build=%lu submit=%lu release=%lu confirm=%lu drain=%lu first=%lu submitted=%lu wall_submitted=%lu presented=%lu world=%08lX pixels=%08lX pairs=%lu contacts=%lu\r\n",r->number,r->mode,r->output,r->collide,r->balls,r->flags,r->token,(unsigned long)r->frame,(unsigned long)r->step,r->bytes,r->hud_bytes,(unsigned long)r->physics,(unsigned long)r->collision,(unsigned long)r->draw,(unsigned long)r->checksum,(unsigned long)r->build,(unsigned long)r->submit,(unsigned long)r->release,(unsigned long)r->confirm,(unsigned long)r->drain,(unsigned long)r->first,(unsigned long)r->submitted,(unsigned long)r->wall_submitted,(unsigned long)r->presented,(unsigned long)r->world,(unsigned long)r->pixels,(unsigned long)r->pairs,(unsigned long)r->contacts);
  if(!write_line(file,line)){mos_fclose(file);return 0;}
 }
 mos_fclose(file);record_count=0;return 1;
}
int main(int argc,char **argv){
 putch(12);puts("UART0 BOUNCING BALLS - preparing timers and report...");
 if(!reserve_report()){puts("Cannot reserve sequential report; demo not started.");return 1;}
 char journal[120];snprintf(journal,sizeof(journal),"START run=%04u build=%s\r\n",run_id,BD_BUILD);
 if(!append_text("runs.log",journal)){puts("Cannot append running log; demo not started.");return 1;}
 sysvars=mos_sysvars();token_counter=sysvars[sysvar_gp];api_available=(unsigned)transport_supported();
 if(!clocks_start()){report_text("END FAIL timers already owned\r\n");puts("A required timer is running; left its owner intact.");return 1;}
 int automatic=argc>1;int quick=automatic&&!strcmp(argv[1],"quick");
 if(!timer_check())goto cleanup;
 setup_video();
 if(automatic){
  unsigned frames=quick?4:8;phase_total=quick?12:24;
  if(!api_available){fail("Automatic comparison requires experimental ABI1.3");goto cleanup;}
  for(unsigned balls=0;balls<(quick?1u:2u)&&!failures;balls++)for(unsigned collide=0;collide<2&&!failures;collide++)for(unsigned output=0;output<2&&!failures;output++)for(unsigned mode=0;mode<3&&!failures;mode++){
   Config c={mode,output,collide,balls?64u:16u,0x42414c4cUL};
   if(!run_case(&c,frames,1))goto cleanup;
   if(!save_records()){fail("Cannot write automatic report");goto cleanup;}
  }
 }else{
  int fresh=1;
  while(!stopped&&!failures){
   requested=reset_scene=0;Config c=config;
   if(!run_case(&c,0,fresh))break;
   if(!save_records()){fail("Cannot write interactive report");break;}
   fresh=reset_scene;
  }
 }
cleanup:
 if(async_open){transport_close();async_open=0;}
 const uint8_t restore[]={22,3,23,1,1};mos_puts((const char *)restore,sizeof(restore),0);
 clocks_stop();
 if(record_count&&!save_records())fail("Cannot write report");
 char line[180];snprintf(line,sizeof(line),"END %s frames_saved case_count=%u reason=%s\r\n",failures?"FAIL":"PASS",case_id,failures?failure_reason:"normal completion");
 if(!report_text(line))failures++;
 snprintf(journal,sizeof(journal),"END run=%04u %s cases=%u report=%s\r\n",run_id,failures?"FAIL":"PASS",case_id,report_name);
 if(!append_text("runs.log",journal))failures++;
 puts(failures?"BALLS DEMO FAIL - inspect the numbered report":"BALLS DEMO COMPLETE - numbered report saved");
 return failures?1:0;
}
