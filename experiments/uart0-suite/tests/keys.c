#define _GNU_SOURCE
#include <SDL3/SDL.h>
#include <dlfcn.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
/* Input-only automation for one disposable headless process, not a VDP patch. */
bool SDL_PollEvent(SDL_Event *event) {
    static bool (*poll_event)(SDL_Event *);
    static int fd=-1;
    static SDL_Scancode held;
    static SDL_Keycode held_code;
    static Uint64 hold_ms=100;
    static Uint64 release_at;
    if(!poll_event)poll_event=dlsym(RTLD_NEXT,"SDL_PollEvent");
    const char *path=getenv("UART_SUITE_KEYS");
    if(fd<0 && path)fd=open(path,O_RDONLY|O_NONBLOCK);
    if(event && held && SDL_GetTicks()>=release_at) {
        memset(event,0,sizeof(*event));event->type=SDL_EVENT_KEY_UP;
        event->key.scancode=held;event->key.key=held_code;held=0;return true;
    }
    char c;
    while(event && !held && fd>=0 && read(fd,&c,1)==1) {
        /* Harness controls: a quick tap, ordinary tap, or held key. */
        if(c=='~'){hold_ms=0;continue;}
        if(c=='#'){hold_ms=20;continue;}
        if(c=='%'){hold_ms=100;continue;}
        if(c=='^'){hold_ms=500;continue;}
        SDL_Scancode scan=SDL_SCANCODE_SPACE;SDL_Keycode code=SDLK_SPACE;
        if(c>='1'&&c<='9'){scan=SDL_SCANCODE_1+c-'1';code=c;}
        else if(c=='0'){scan=SDL_SCANCODE_0;code=SDLK_0;}
        else if(c>='a'&&c<='z'){scan=SDL_SCANCODE_A+c-'a';code=c;}
        else if(c=='\n'){scan=SDL_SCANCODE_RETURN;code=SDLK_RETURN;}
        else if(c==27){scan=SDL_SCANCODE_ESCAPE;code=SDLK_ESCAPE;}
        else if(c=='.'){scan=SDL_SCANCODE_PERIOD;code=SDLK_PERIOD;}
        memset(event,0,sizeof(*event));event->type=SDL_EVENT_KEY_DOWN;
        event->key.scancode=held=scan;event->key.key=held_code=code;event->key.down=true;
        release_at=SDL_GetTicks()+hold_ms;return true;
    }
    return poll_event(event);
}
