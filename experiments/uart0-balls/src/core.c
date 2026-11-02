/* Original deterministic demo physics/rasterization; MIT, 2026 bgates747. */
#include "core.h"
#include <string.h>
static uint32_t random32(uint32_t *s){*s=*s*1664525UL+1013904223UL;return *s;}
void world_init(World *w,unsigned count,uint32_t seed){
 memset(w,0,sizeof(*w));w->count=count>BD_MAX_BALLS?BD_MAX_BALLS:count;
 for(unsigned i=0;i<w->count;i++){
  Ball *b=&w->ball[i];b->radius=(uint8_t)(3+(random32(&seed)>>24)%4);
  b->x=(int16_t)((b->radius+1+(random32(&seed)>>16)%(BD_WIDTH-2*b->radius-2))*16);
  b->y=(int16_t)((b->radius+1+(random32(&seed)>>16)%(BD_HEIGHT-2*b->radius-2))*16);
  b->vx=(int16_t)(8+(random32(&seed)>>24)%25);if(i&1)b->vx=-b->vx;
  b->vy=(int16_t)(8+(random32(&seed)>>24)%25);if(i&2)b->vy=-b->vy;
  b->colour=(uint8_t)(0xc0|((i*23+11)%63+1));
 }
}
void world_resize(World *w,unsigned count,uint32_t seed){
 World added;world_init(&added,count,seed);
 for(unsigned i=w->count;i<added.count;i++)w->ball[i]=added.ball[i];
 w->count=added.count; /* Existing positions, velocities and scene step survive. */
}
static void wall(Ball *b){
 int16_t r=(int16_t)(b->radius*16),right=(int16_t)((BD_WIDTH-1)*16-r),bottom=(int16_t)((BD_HEIGHT-1)*16-r);
 if(b->x<r){b->x=r;if(b->vx<0)b->vx=-b->vx;}
 if(b->x>right){b->x=right;if(b->vx>0)b->vx=-b->vx;}
 if(b->y<r){b->y=r;if(b->vy<0)b->vy=-b->vy;}
 if(b->y>bottom){b->y=bottom;if(b->vy>0)b->vy=-b->vy;}
}
void world_integrate(World *w){for(unsigned i=0;i<w->count;i++){w->ball[i].x+=w->ball[i].vx;w->ball[i].y+=w->ball[i].vy;}w->step++;}
void world_collide(World *w,int pairs){
 w->pairs=w->contacts=0;
 for(unsigned i=0;i<w->count;i++)wall(&w->ball[i]);
 if(pairs)for(unsigned i=0;i<w->count;i++)for(unsigned j=i+1;j<w->count;j++){
  Ball *a=&w->ball[i],*b=&w->ball[j];
  int32_t dx=(int32_t)b->x-a->x,dy=(int32_t)b->y-a->y;
  int32_t radius=(int32_t)(a->radius+b->radius)*16;
  int32_t d2=dx*dx+dy*dy;w->pairs++;
  if(d2>radius*radius)continue;
  w->contacts++;
  if(!d2){dx=16;dy=0;d2=256;}
  int32_t dot=dx*((int32_t)b->vx-a->vx)+dy*((int32_t)b->vy-a->vy);
  if(dot<0){
   int32_t ix=dot*dx/d2,iy=dot*dy/d2;
   a->vx=(int16_t)(a->vx+ix);b->vx=(int16_t)(b->vx-ix);
   a->vy=(int16_t)(a->vy+iy);b->vy=(int16_t)(b->vy-iy);
  }
  /* Bounded dominant-axis separation; no square root or iterative solver. */
  if(dx*dx>=dy*dy){int16_t s=dx<0?-1:1;a->x-=s;b->x+=s;}
  else {int16_t s=dy<0?-1:1;a->y-=s;b->y+=s;}
 }
 for(unsigned i=0;i<w->count;i++){
  Ball *b=&w->ball[i];
  if(b->vx>64)b->vx=64;if(b->vx< -64)b->vx=-64;
  if(b->vy>64)b->vy=64;if(b->vy< -64)b->vy=-64;wall(b);
 }
}
void world_draw(const World *w,uint8_t *pixels){
 memset(pixels,0xc0,BD_PIXELS);
 for(unsigned i=0;i<w->count;i++){
  const Ball *b=&w->ball[i];int x=b->x/16,y=b->y/16,r=b->radius;
  for(int dy=-r;dy<=r;dy++){
   int yy=y+dy;if(yy<0||yy>=BD_HEIGHT)continue;
   int span=r;while(span*span+dy*dy>r*r)span--;
   int l=x-span,rr=x+span;if(l<0)l=0;if(rr>=BD_WIDTH)rr=BD_WIDTH-1;
   if(rr>=l)memset(pixels+(unsigned)yy*BD_WIDTH+(unsigned)l,b->colour,(unsigned)(rr-l+1));
  }
 }
}
uint32_t pixels_hash(const uint8_t *p){
 uint16_t a=0,b=0;for(unsigned i=0;i<BD_PIXELS;i++){a=(uint16_t)(a+p[i]);b=(uint16_t)(b+a);}return ((uint32_t)b<<16)|a;
}
uint32_t world_hash(const World *w){
 uint32_t h=2166136261UL;
 for(unsigned i=0;i<w->count;i++){
  const Ball *b=&w->ball[i];const int16_t values[]={b->x,b->y,b->vx,b->vy};
  for(unsigned k=0;k<4;k++){h^=(uint16_t)values[k];h*=16777619UL;}
  h^=b->colour;h*=16777619UL;
 }return h;
}
static void byte(uint8_t *p,unsigned *n,unsigned v){p[(*n)++]=(uint8_t)v;}
static void word(uint8_t *p,unsigned *n,unsigned v){byte(p,n,v);byte(p,n,v>>8);}
static void plot(uint8_t *p,unsigned *n,unsigned code,unsigned x,unsigned y){byte(p,n,25);byte(p,n,code);word(p,n,x);word(p,n,y);}
unsigned frame_commands(uint8_t *p,const World *w,unsigned circles,unsigned slot,uint8_t token){
 unsigned n=0,id=0x7000+slot;
 if(!circles){
  byte(p,&n,23);byte(p,&n,0);byte(p,&n,160);word(p,&n,id);byte(p,&n,2);
  byte(p,&n,23);byte(p,&n,0);byte(p,&n,160);word(p,&n,id);byte(p,&n,0);word(p,&n,BD_PIXELS);
  n+=BD_PIXELS; /* Pixel bytes are rendered in place; no extra frame copy. */
  byte(p,&n,23);byte(p,&n,27);byte(p,&n,32);word(p,&n,id);
  byte(p,&n,23);byte(p,&n,27);byte(p,&n,33);word(p,&n,BD_WIDTH);word(p,&n,BD_HEIGHT);byte(p,&n,1);
  byte(p,&n,23);byte(p,&n,27);byte(p,&n,3);word(p,&n,0);word(p,&n,0);
 }else{
  byte(p,&n,18);byte(p,&n,0);byte(p,&n,0);plot(p,&n,4,0,0);plot(p,&n,101,BD_WIDTH-1,BD_HEIGHT-1);
  for(unsigned i=0;i<w->count;i++){
   const Ball *b=&w->ball[i];unsigned x=(unsigned)(b->x/16),y=(unsigned)(b->y/16);
   byte(p,&n,18);byte(p,&n,0);byte(p,&n,b->colour&63);plot(p,&n,4,x,y);plot(p,&n,157,x+b->radius,y);
  }
 }
 byte(p,&n,23);byte(p,&n,0);byte(p,&n,0xc3);
 byte(p,&n,23);byte(p,&n,0);byte(p,&n,0x80);byte(p,&n,token);
 return n;
}
