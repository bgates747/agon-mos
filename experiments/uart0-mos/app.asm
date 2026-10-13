; Production MOS qualification. Discover the installed API; no private driver,
; parser replacement, UART register writes or interrupt-vector takeover.
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
    push hl
    push ix
    push iy
    ld (saved_sp),sp
    ld a,8
    rst.lil 08h
    ld (sysvars),ix
    ld bc,01300h
    ld a,050h
    rst.lil 08h
    or a,a
    jp nz,failed
    ld (discovery+1),hl
    call discovery
    ld de,api_magic
    ld b,4
check_magic:
    ld a,(de)
    cp a,(hl)
    jp nz,failed
    inc hl
    inc de
    djnz check_magic
    ld a,(hl)
    cp a,1
    jp nz,failed
    ld de,9
    add hl,de
    ld de,tx_open+1
    ld b,9
install_calls:
    push bc
    ld bc,3
    ldir
    inc de                  ; Skip next JP opcode.
    pop bc
    djnz install_calls
    ld hl,(hl)              ; diagnostic snapshot address
    ld (diagnostics),hl
    ld hl,legacy
    ld bc,legacy_end-legacy
    rst.lil 18h
    ld a,'!'
    rst.lil 10h
    call tx_open
    or a,a
    jp nz,failed
    ld a,1
    ld (stage),a
    call tx_reserve
    or a,a
    jp nz,failed
    ld (ticket1),hl
    ex de,hl
    ld hl,packet1
    ld bc,packet1_end-packet1
    call tx_publish
    or a,a
    jp nz,failed
    call tx_reserve
    or a,a
    jp nz,failed
    ld (ticket2),hl
    ex de,hl
    ld hl,packet2
    ld bc,packet2_end-packet2
    call tx_publish
    or a,a
    jp nz,failed
    call tx_reserve
    or a,a
    jp nz,failed
    ld (ticket3),hl
    ex de,hl
    ld hl,packet3
    ld bc,packet3_end-packet3
    call tx_publish
    or a,a
    jp nz,failed
    ; Ordinary block must wait for the complete ordered command batch.
    ld hl,ordered
    ld bc,ordered_end-ordered
    rst.lil 18h
wait_wire:
    call tx_poll_drain
    cp a,1
    jr z,wait_wire
    or a,a
    jp nz,failed
    ld de,(ticket1)
    call tx_status
    or a,a
    jp nz,failed
    ld a,b
    cp a,4
    jp nz,failed
    ld (accepted1),hl
    ld de,(ticket1)
    call tx_reap
    or a,a
    jp nz,failed
    ld de,(ticket2)
    call tx_status
    or a,a
    jp nz,failed
    ld (accepted2),hl
    ld de,(ticket2)
    call tx_reap
    or a,a
    jp nz,failed
    ld de,(ticket3)
    call tx_status
    or a,a
    jp nz,failed
    ld (accepted3),hl
    ld de,(ticket3)
    call tx_reap
    or a,a
    jp nz,failed
    ; Wait for receiver execution separately from transport drain, through
    ; the real MOS GP parser (last reply value is 63).
    ld ix,(sysvars)
    ld bc,1000000
wait_reply:
    ld a,(ix+037h)
    cp a,63
    jr z,reply_done
    dec bc
    ld a,b
    or a,c
    jr nz,wait_reply
    jp failed
reply_done:
    ld (last_gp),a
    ; Masked foreground RST18 must pump pending TX and RX without IRQ help.
    di
    call tx_reserve
    or a,a
    jp nz,failed
    ld (ticket4),hl
    ex de,hl
    ld hl,masked_packet
    ld bc,masked_packet_end-masked_packet
    call tx_publish
    or a,a
    jp nz,failed
    ld hl,masked
    ld bc,0
    xor a,a
    rst.lil 18h
    ld a,i
    jp pe,failed            ; RST18 must leave DI intact.
    ei
    ld de,(ticket4)
    call tx_status
    or a,a
    jp nz,failed
    ld a,b
    cp a,4
    jp nz,failed
    ld de,(ticket4)
    call tx_reap
    or a,a
    jp nz,failed
wait_close:
    call tx_close
    cp a,1
    jr z,wait_close
    or a,a
    jp nz,failed
    ; Callback registration must close an open session. No actual callback
    ; output is manufactured here; native-ROM scenarios test ISR callbacks.
    call tx_open
    or a,a
    jp nz,failed
    ld hl,empty_callback
    ld bc,0
    ld a,01dh
    rst.lil 08h
    call tx_open
    cp a,1
    jp nz,failed
    ld hl,0
    ld bc,0
    ld a,01dh
    rst.lil 08h
    call tx_open
    or a,a
    jp nz,failed
    ; Snapshot before the deliberate outstanding transaction at normal exit.
    ld hl,(diagnostics)
    ld a,(hl)
    ld (rx_errors),a
    inc hl
    ld a,(hl)
    ld (modem_deltas),a
    xor a,a
    ld (stage),a
    ld hl,result_name
    ld de,report
    ld bc,report_end-report
    ld a,2
    rst.lil 08h
    or a,a
    jp nz,failed
    call tx_reserve
    or a,a
    jp nz,failed
    ex de,hl
    ld hl,exit_packet
    ld bc,exit_packet_end-exit_packet
    call tx_publish
    or a,a
    jp nz,failed
    ; Leave both the ticket and its buffer outstanding: MOS must fence exit.
    ld sp,(saved_sp)
    pop iy
    pop ix
    pop hl
    pop de
    pop bc
    pop af
    ld hl,0
    ret
failed:
    ei
    ld hl,failure_name
    ld de,report
    ld bc,report_end-report
    ld a,2
    rst.lil 08h
failed_hold:
    halt
    jr failed_hold
empty_callback:
    ret
discovery: jp 0
tx_open: jp 0
tx_reserve: jp 0
tx_publish: jp 0
tx_status: jp 0
tx_cancel: jp 0
tx_reap: jp 0
tx_poll_drain: jp 0
tx_close: jp 0
tx_kick: jp 0
saved_sp: DB 0,0,0
sysvars: DB 0,0,0
diagnostics: DB 0,0,0
ticket1: DB 0,0,0
ticket2: DB 0,0,0
ticket3: DB 0,0,0
ticket4: DB 0,0,0
report: DB "UART0MOS"
stage: DB 0
accepted1: DB 0,0,0
accepted2: DB 0,0,0
accepted3: DB 0,0,0
rx_errors: DB 0
modem_deltas: DB 0
last_gp: DB 0
report_end:
api_magic: DB "UTX1"
result_name: DB "integrated.dat",0
failure_name: DB "failure.dat",0
legacy: DB "UART0 LEGACY PASS",13,10
legacy_end:
ordered: DB "UART0 ORDERED PASS",13,10
ordered_end:
masked: DB "UART0 MASKED PASS",13,10,0
masked_packet: DB "UART0 MASKED QUEUE",13,10
masked_packet_end:
exit_packet:
    DB 32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32
    DB 32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32
    DB 32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32
    DB 32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32
    DB 32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32
    DB 32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32
    DB 32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32
    DB 32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32
    DB 32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32
    DB 32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32
    DB 32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32
    DB 32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32
    DB 32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32
    DB 32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32
    DB 32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32
    DB 32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32,32
    DB "UART0 EXIT QUEUE PASS",13,10
exit_packet_end:
    INCLUDE "packets.inc"
    END
