#ifndef BALLS_KEYS_H
#define BALLS_KEYS_H
#include <stdint.h>
static const char key_chars[]="123bcrq=-";
/* The VDP can postpone keyboard reporting while receiving a bitmap, then send
   make+break together. Recover the last complete tap from the public MOS event
   counter/ASCII/state, without a keyboard callback or a second UART owner. */
static inline uint16_t key_edges(uint16_t now,uint16_t before,uint8_t events,uint8_t ascii,uint8_t down){
 uint16_t edges=now&~before;
 if(events>=2&&!down){
  if(ascii>='A'&&ascii<='Z')ascii=(uint8_t)(ascii+'a'-'A');
  for(unsigned i=0;i<sizeof(key_chars)-1;i++)if(ascii==(uint8_t)key_chars[i]){
   uint16_t bit=(uint16_t)(1u<<i);if(!((now|before)&bit))edges|=bit;
  }
 }
 return edges;
}
#endif
