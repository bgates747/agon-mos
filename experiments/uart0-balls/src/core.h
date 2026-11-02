#ifndef BALLS_CORE_H
#define BALLS_CORE_H
#include <stdint.h>
#define BD_WIDTH 160
#define BD_HEIGHT 120
#define BD_PIXELS (BD_WIDTH * BD_HEIGHT)
#define BD_MAX_BALLS 128
#define BD_PIXEL_OFFSET 14
#define BD_PACKET_CAP 24576
typedef struct { int16_t x,y,vx,vy; uint8_t radius,colour; } Ball;
typedef struct { Ball ball[BD_MAX_BALLS]; unsigned count; uint32_t step,pairs,contacts; } World;
void world_init(World *,unsigned,uint32_t);
void world_resize(World *,unsigned,uint32_t);
void world_integrate(World *);
void world_collide(World *,int);
void world_draw(const World *,uint8_t *);
uint32_t pixels_hash(const uint8_t *);
uint32_t world_hash(const World *);
unsigned frame_commands(uint8_t *,const World *,unsigned,unsigned,uint8_t);
#endif
