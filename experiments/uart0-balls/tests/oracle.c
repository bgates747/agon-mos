#include "../src/core.h"
#include <stdio.h>
static World world;
static uint8_t pixels[BD_PIXELS];
int main(int argc,char **argv){
 for(unsigned balls=16;balls<=64;balls*=4)for(unsigned collide=0;collide<2;collide++){
  world_init(&world,balls,0x42414c4cUL);
  for(unsigned frame=0;frame<8;frame++){
   world_integrate(&world);world_collide(&world,(int)collide);world_draw(&world,pixels);
   if(argc>1){
    char path[512];uint8_t commands[BD_PACKET_CAP];
    snprintf(path,sizeof(path),"%s/B%uC%uF%u.bin",argv[1],balls,collide,frame);
    FILE *out=fopen(path,"wb");if(!out)return 1;fwrite(pixels,1,BD_PIXELS,out);fclose(out);
    unsigned n=frame_commands(commands,&world,1,frame&1,1);
    snprintf(path,sizeof(path),"%s/B%uC%uF%u.vdu",argv[1],balls,collide,frame);
    out=fopen(path,"wb");if(!out)return 1;fwrite(commands,1,n-7,out);fclose(out);
   }
   printf("%u %u %u %08lX %08lX\n",balls,collide,frame,(unsigned long)world_hash(&world),(unsigned long)pixels_hash(pixels));
  }
 }
 return 0;
}
