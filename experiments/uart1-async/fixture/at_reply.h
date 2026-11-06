/* SPDX-License-Identifier: MIT -- bounded AT query reply, not a TCP parser. */
#ifndef U1_AT_REPLY_H
#define U1_AT_REPLY_H
#include <stdint.h>
enum { AT_WAIT, AT_OK, AT_FAIL };
typedef struct {
    char text[512],line[192];
    unsigned used,length;
    uint8_t result,at_version,sdk_version;
} at_reply;
void at_reply_init(at_reply *);
uint8_t at_reply_byte(at_reply *,uint8_t);
#endif
