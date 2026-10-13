; Legacy ADL=0 application. Link at zero, load at 040000h; MBASE supplies bank.
.assume adl=0
    DEFINE SHORT_APP, SPACE=ROM
    SEGMENT SHORT_APP
    jp start
    DS 61
    DB "MOS",0,0
start:
    ld (saved_sps),sp
    ld sp,0ff00h
    ld hl,message
    ld bc,0
    xor a,a
    rst.lil 18h
    ld a,'!'
    rst.lil 10h
    ; The new discovery retains MOS's ADL-only rejection for short callers.
    ld bc,01300h
    ld a,050h
    rst.lil 08h
    cp a,20
    jr nz,failed
    ld a,mb
    cp a,4
    jr nz,failed
    ld hl,passed
    ld bc,0
    xor a,a
    rst.lil 18h
    ld hl,0
    ld sp,(saved_sps)
    ret.lis
failed:
    ld hl,failure
    ld bc,0
    xor a,a
    rst.lil 18h
    halt
    jr failed
saved_sps: DW 0
message: DB "UART0 SHORT LEGACY",13,10,0
passed: DB "UART0 SHORT PASS",13,10,0
failure: DB "UART0 SHORT FAIL",13,10,0
    END
