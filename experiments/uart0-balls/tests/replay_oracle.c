/* Host-only deterministic replay of version2 interactive scenario logs. */
#include "../src/core.h"
#include <stdio.h>
static World world;
static uint8_t pixels[BD_PIXELS];
int main(void){
 unsigned number,balls,collide,fresh;unsigned long frames;
 while(scanf("%u %u %u %u %lu",&number,&balls,&collide,&fresh,&frames)==5){
  if(!balls||balls>BD_MAX_BALLS||collide>1||frames>1000000)return 1;
  if(fresh||!world.count)world_init(&world,balls,0x42414c4cUL);
  else if(world.count!=balls)world_resize(&world,balls,0x42414c4cUL);
  for(unsigned long i=1;i<=frames;i++){
   world_integrate(&world);world_collide(&world,(int)collide);world_draw(&world,pixels);
   printf("%u %lu %lu %08lX %08lX %lu %lu\n",number,i,(unsigned long)world.step,(unsigned long)world_hash(&world),(unsigned long)pixels_hash(pixels),(unsigned long)world.pairs,(unsigned long)world.contacts);
  }
 }
 return 0;
}
