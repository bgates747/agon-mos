; Test-only receive sink and useful-work loop. Never linked into MOS.
.assume adl=1
    DEFINE UART_FIXTURE, SPACE=ROM
    SEGMENT UART_FIXTURE
    XDEF blocking_wait,rx_full
    XDEF tx_rx_sink,rx_count,rx_bytes,rx_overflow,producer,producer_tick,producer_done
    XDEF rx_callback_test,rx_callback_status
    XREF tx_status
    XDEF blocking_send
blocking_send:
    in0 a,(0c6h)
    bit 4,a
    jr z,blocking_send
blocking_wait:
    in0 a,(0c5h)
    bit 5,a
    jr z,blocking_wait
    ld a,(hl)
    out0 (0c0h),a
    inc hl
    dec bc
    ld a,b
    or a,c
    jr nz,blocking_send
    ret
 tx_rx_sink:
    push af
    ld hl,(rx_count)
    ld de,256
    or a,a
    sbc hl,de
    jr nc,rx_full
    add hl,de
    ld de,rx_bytes
    add hl,de
    pop af
    ld (hl),a
    ld hl,(rx_count)
    inc hl
    ld (rx_count),hl
    ld a,(rx_callback_test)
    or a,a
    ret z
    call tx_status
    ld (rx_callback_status),a
    ret
rx_full:
    pop af
    ld a,1
    ld (rx_overflow),a
    ret
; Exactly BC iterations, each computes a deterministic accumulator in HL.
; Tick is an actual instruction boundary used to count useful work.
producer:
    ld hl,0
producer_tick:
    inc hl
    dec bc
    ld a,b
    or a,c
    jr nz,producer_tick
producer_done:
    halt
rx_count: DB 0,0,0
rx_overflow: DB 0
rx_callback_test: DB 0
rx_callback_status: DB 0
rx_bytes: DS 256

    END
