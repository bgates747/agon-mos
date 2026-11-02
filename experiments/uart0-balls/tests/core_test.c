#include "../src/core.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static World w,a;
static uint8_t p[BD_PACKET_CAP+16],q[BD_PIXELS];
int main(void){
 for(unsigned count=4;count<=BD_MAX_BALLS;count*=2)for(unsigned pairs=0;pairs<2;pairs++){
  world_init(&w,count,0x42414c4cUL);world_init(&a,count,0x42414c4cUL);
  for(unsigned frame=0;frame<40;frame++){
   world_integrate(&w);world_collide(&w,(int)pairs);
   world_integrate(&a);world_collide(&a,(int)pairs);
   assert(world_hash(&w)==world_hash(&a));
   assert(w.pairs==(pairs?count*(count-1)/2:0));
   memset(p,0x5a,sizeof(p));world_draw(&w,p+BD_PIXEL_OFFSET);world_draw(&a,q);
   assert(!memcmp(p+BD_PIXEL_OFFSET,q,BD_PIXELS));
   for(unsigned i=0;i<BD_PIXELS;i++)assert((q[i]&0xc0)==0xc0);
   for(unsigned i=0;i<count;i++){
    Ball *b=&w.ball[i];assert(b->x>=b->radius*16&&b->x<=(BD_WIDTH-1-b->radius)*16);
    assert(b->y>=b->radius*16&&b->y<=(BD_HEIGHT-1-b->radius)*16);
   }
   uint32_t hash=pixels_hash(q);unsigned n=frame_commands(p,&w,0,0,41);
   assert(n==BD_PIXEL_OFFSET+BD_PIXELS+5+8+7+7);
   assert(p[0]==23&&p[5]==2&&p[11]==0&&p[12]==0&&p[13]==75);
   assert(pixels_hash(p+BD_PIXEL_OFFSET)==hash);
   assert(!memcmp(p+n-7,(uint8_t[]){23,0,0xc3,23,0,0x80,41},7));
   memset(p,0x5a,sizeof(p));n=frame_commands(p,&w,1,0,42);
   assert(n==15+count*15+7&&n<BD_PACKET_CAP);
   assert(p[15+3+6+1]==157);
   assert(!memcmp(p+n-7,(uint8_t[]){23,0,0xc3,23,0,0x80,42},7));
   for(unsigned i=BD_PACKET_CAP;i<sizeof(p);i++)assert(p[i]==0x5a);
  }
  printf("ORACLE balls=%u collide=%u world=%08lX pixels=%08lX\n",count,pairs,(unsigned long)world_hash(&w),(unsigned long)pixels_hash(q));
 }
 /* Exact overlap and a head-on approaching contact exercise the division guards. */
 world_init(&w,2,123);w.ball[0].x=w.ball[1].x=800;w.ball[0].y=w.ball[1].y=800;
 w.ball[0].vx=16;w.ball[1].vx=-16;world_collide(&w,1);assert(w.contacts==1);
 w.ball[0].x=700;w.ball[1].x=796;w.ball[0].radius=w.ball[1].radius=3;
 w.ball[0].vx=16;w.ball[1].vx=-16;w.ball[0].vy=w.ball[1].vy=0;
 world_collide(&w,1);assert(w.ball[0].vx==-16&&w.ball[1].vx==16);
 world_init(&w,8,123);world_integrate(&w);Ball first=w.ball[0];uint32_t step=w.step;
 world_resize(&w,12,123);assert(w.count==12&&w.step==step&&!memcmp(&w.ball[0],&first,sizeof(first)));
 world_resize(&w,4,123);assert(w.count==4&&w.step==step&&!memcmp(&w.ball[0],&first,sizeof(first)));
 puts("CORE PASS:480frames, deterministic physics, packet bounds and contact guards");
}
