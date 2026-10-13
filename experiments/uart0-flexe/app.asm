; TX-007 isolated foreground test. Stock MOS loads this app, never a new ROM.
; Native ZDS II, ADL only. All wide-memory fields below are three bytes.
.assume adl=1
    DEFINE UART_ENTRY, SPACE=ROM
    SEGMENT UART_ENTRY
    XREF tx_open,tx_reserve,tx_publish,tx_status,tx_reap,tx_poll_drain,tx_close,tx_isr
    XREF rx_count,rx_bytes,rx_overflow,tx_rx_errors,tx_modem_deltas
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
    in0 a,(0c1h)
    ld (saved_ier),a
    di
    xor a,a
    out0 (0c1h),a
    ld hl,counted_isr
    ld e,018h
    ld a,014h
    rst.lil 08h
    ld (saved_vector),hl
    ld a,5
    out0 (0c1h),a
    ei
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
    ld a,2
    ld (stage),a
    ; Bounded foreground wait. RX and TX use real CPU interrupt delivery.
    ld ix,8000000
wait_drain:
    call tx_poll_drain
    or a,a
    jr z,wait_receive
    cp a,1
    jp nz,failed
    dec ix
    push ix
    pop hl
    ld de,0
    or a,a
    sbc hl,de
    jr nz,wait_drain
    jp failed
wait_receive:
    ld hl,(rx_count)
    ld de,192
    or a,a
    sbc hl,de
    jr z,check_tickets
    jp nc,failed
    dec ix
    push ix
    pop hl
    ld de,0
    or a,a
    sbc hl,de
    jr nz,wait_receive
    jp failed
check_tickets:
    ld a,3
    ld (stage),a
    ld de,(ticket1)
    call tx_status
    or a,a
    jp nz,failed
    ld (accepted1),hl
    ld a,b
    cp a,4
    jp nz,failed
    ld de,(ticket1)
    call tx_reap
    or a,a
    jp nz,failed
    ld de,(ticket2)
    call tx_status
    or a,a
    jp nz,failed
    ld (accepted2),hl
    ld a,b
    cp a,4
    jp nz,failed
    ld de,(ticket2)
    call tx_reap
    or a,a
    jp nz,failed
    ld de,(ticket3)
    call tx_status
    or a,a
    jp nz,failed
    ld (accepted3),hl
    ld a,b
    cp a,4
    jp nz,failed
    ld de,(ticket3)
    call tx_reap
    or a,a
    jp nz,failed
    call tx_close
    or a,a
    jp nz,failed
    ld hl,(rx_count)
    ld (report_rx),hl
    ld a,(rx_overflow)
    ld (report_overflow),a
    ld a,(tx_rx_errors)
    ld (report_errors),a
    ld a,(tx_modem_deltas)
    ld (report_deltas),a
    ; Remove the experimental owner before invoking any ordinary MOS output.
    di
    xor a,a
    out0 (0c1h),a
    ld hl,(saved_vector)
    ld e,018h
    ld a,014h
    rst.lil 08h
    ld a,(saved_ier)
    out0 (0c1h),a
    ei
    ld hl,rx_name
    ld de,rx_bytes
    ld bc,192
    ld a,2
    rst.lil 08h
    or a,a
    jp nz,failed
    xor a,a
    ld (stage),a
    ld hl,result_name
    ld de,report
    ld bc,report_end-report
    ld a,2
    rst.lil 08h
    or a,a
    jp nz,failed
    ld hl,success
    ld bc,success_end-success
    xor a,a
    rst.lil 18h
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
    ; Never return and reclaim a source after an unexpected transport failure.
    ; Save a diagnostic for the harness, then retain ownership until shutdown.
    ld hl,failure_name
    ld de,report
    ld bc,report_end-report
    ld a,2
    rst.lil 08h
failed_hold:
    halt
    jr failed_hold
counted_isr:
    push af
    push hl
    ld hl,(report_irqs)
    inc hl
    ld (report_irqs),hl
    pop hl
    pop af
    jp tx_isr
saved_sp: DB 0,0,0
saved_vector: DB 0,0,0
saved_ier: DB 0
ticket1: DB 0,0,0
ticket2: DB 0,0,0
ticket3: DB 0,0,0
report: DB "UART0TX1"
stage: DB 0
report_rx: DB 0,0,0
report_irqs: DB 0,0,0
report_overflow: DB 0
report_errors: DB 0
report_deltas: DB 0
accepted1: DB 0,0,0
accepted2: DB 0,0,0
accepted3: DB 0,0,0
report_end:
result_name: DB "result.dat",0
failure_name: DB "failure.dat",0
rx_name: DB "rx.dat",0
success: DB "UART0 ASYNC PASS",13,10
success_end:
    INCLUDE "packets.inc"
    END
