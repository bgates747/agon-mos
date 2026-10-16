/* Compile in a disposable directory with the actual menu and callback.
 * Flexe's ASCII keyboard source omits virtual-key codes and release packets;
 * exercise those physical packet paths directly, on the emulated eZ80.
 */
#define main suite_main
#include "../src/main.c"
#undef main

uint8_t menu_test_packet[4];
extern void menu_test_event(void);

static void event(uint8_t ascii,uint8_t code,uint8_t down) {
    menu_test_packet[0]=ascii;menu_test_packet[1]=0;
    menu_test_packet[2]=code;menu_test_packet[3]=down;
    menu_test_event();
}
static int take(char expected) {
    return menu_key_head!=menu_key_tail && menu_key()==expected;
}
int main(void) {
    menu_key_head=menu_key_tail=0;
    memset((void *)menu_key_held,0,sizeof(menu_key_held));
    /* A complete tap arrives before the foreground consumes anything. */
    event('2',130,1);event('2',130,0);
    if(!take('2') || menu_key_head!=menu_key_tail)return 1;
    /* One held key produces one selection, despite repeat events. */
    for(unsigned i=0;i<8;i++)event('9',159,1);
    event('9',159,0);
    if(!take('9') || menu_key_head!=menu_key_tail)return 2;
    /* Release allows the same key to be tapped again. */
    event('9',159,1);event('9',159,0);
    if(!take('9'))return 3;
    /* Exercise every held-key byte and mask; FIFO wraps repeatedly. */
    for(unsigned code=1;code<256;code++) {
        event('q',code,1);event('q',code,1);event('q',code,0);
        if(!take('q') || menu_key_head!=menu_key_tail)return 4;
    }
    /* Bounded overflow preserves the first 15 events in order. */
    for(unsigned i=0;i<32;i++){event('a'+i%26,130,1);event(0,130,0);}
    for(unsigned i=0;i<15;i++)if(!take('a'+i%26))return 5;
    if(menu_key_head!=menu_key_tail)return 6;
    /* ASCII-only sources are distinct keys, even without release events. */
    event('9',0,1);event('0',0,1);
    if(!take('9') || !take('0'))return 7;
    event(0,130,1);event(0,130,0);
    if(menu_key_head!=menu_key_tail)return 8;
    puts("MENU PACKET QUEUE PASS: taps, releases, repeats, all VK bits, wrap, overflow, ASCII-only");
    return 0;
}
