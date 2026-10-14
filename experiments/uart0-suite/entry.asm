; Small MOS entry at the standard LOAD address; C menu lives outside flash buffers.
.assume adl=1
    DEFINE UART_ENTRY, SPACE=ROM
    SEGMENT UART_ENTRY
    XDEF app_entry
app_entry:
    jp start
    DS 60
    DB "MOS",0,1
start:
    push af
    push bc
    push de
    push ix
    push iy
    push hl
    ld hl,menu_image
    ld de,090000h
    ld bc,menu_end-menu_image
    ldir
    pop hl
    call 090000h
    pop iy
    pop ix
    pop de
    pop bc
    pop af
    ret
menu_image:
    INCLUDE "menu.inc"
menu_end:
    END
