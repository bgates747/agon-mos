/* Host-only reference output for an interactive hardware report. */
#include "../src/core.h"
#include <stdio.h>
#include <stdlib.h>
static World world;
static uint8_t pixels[BD_PIXELS];
int main(int argc,char **argv){
 if(argc!=4)return 1;
 unsigned balls=(unsigned)atoi(argv[1]),collide=(unsigned)atoi(argv[2]),frames=(unsigned)atoi(argv[3]);
 if(!balls||balls>BD_MAX_BALLS||collide>1||frames>100000)return 1;
 world_init(&world,balls,0x42414c4cUL);
 for(unsigned i=1;i<=frames;i++){
  world_integrate(&world);world_collide(&world,(int)collide);world_draw(&world,pixels);
  printf("%u %08lX %08lX %lu %lu\n",i,(unsigned long)world_hash(&world),(unsigned long)pixels_hash(pixels),(unsigned long)world.pairs,(unsigned long)world.contacts);
 }
 return 0;
}
