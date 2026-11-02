#include "../src/keys.h"
#include <assert.h>
#include <stdio.h>
int main(void){
 assert(key_edges(2,0,1,'2',1)==2); /* ordinary make */
 assert(key_edges(2,2,1,'2',1)==0); /* repeat/hold */
 assert(key_edges(0,2,1,'2',0)==0); /* ordinary release */
 assert(key_edges(0,0,2,'3',0)==4); /* queued make+break */
 assert(key_edges(0,0,2,'B',0)==8); /* uppercase ASCII */
 assert(key_edges(0,0,0,'3',0)==0); /* unchanged packet */
 assert(key_edges(0,0,1,'3',0)==0); /* no invented tap on release */
 assert(key_edges(0,0,2,'x',0)==0); /* unrelated key */
 assert(key_edges(0,0,(uint8_t)(1-255),'3',0)==4); /* counter wrap */
 puts("KEY EDGES PASS: press, hold, release, delayed tap, unrelated input, counter wrap");
}
