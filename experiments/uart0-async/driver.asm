; MOS ASY-001 isolated ADL driver. NOT installed into MOS.
; Native ZDS II syntax; all multibyte storage below is explicitly THREE bytes.
; API: A=status (0 OK,1 BUSY,2 INVALID,3 CLOSED,4 CONTEXT).
; reserve returns HL=ticket; others consume DE=ticket; publish HL=source BC=len.
; status returns B=state, HL=accepted. Other primary registers scratch;
; IX/IY, shadow banks, MBASE, ADL and ordinary caller IFF are preserved.
; Only normal maskable foreground context (IFF1=IFF2); NMI is unsupported.
.assume adl=1
    DEFINE UART_DRIVER, SPACE=ROM
    SEGMENT UART_DRIVER
    XREF tx_rx_sink
    XDEF ok,busy,invalid,closed,check_open,hl_zero,open_core,reserve_core,reserve_scan,reserve_found,find,find_loop,find_next,find_yes,publish_core,publish_first,publish_kick,status_core,cancel_core,cancel_search,cancel_link,cancel_restore,cancel_head,cancel_mark,reap_core,reap_go,drain_core,close_core,close_scan,kick_core,barrier_core,unbarrier_core,sync_core,read_lsr,read_msr,service_next,service_more,service_running,service_blocked,service_idle,isr_dispatch,isr_line,isr_rx,isr_tx,isr_modem,isr_next,isr_done,tx_tmp,tx_saved_ier,tx_ier,tx_cause_budget,tx_rx_budget,tx_tx_serviced
FREE EQU 0
RESERVED EQU 1
QUEUED EQU 2
ACTIVE EQU 3
RELEASED EQU 4
CANCELLED EQU 5
STRIDE EQU 19
THR EQU 0c0h
IER EQU 0c1h
IIR EQU 0c2h
LSR EQU 0c5h
MSR EQU 0c6h

API MACRO entry,core
    XDEF entry
entry:
    ld a,(tx_in_isr)
    or a,a
    jr z,$$foreground
    ld a,4
    ret
$$foreground:
    ld a,i
    push af
    di
    push ix
    call core
    pop ix
    ld c,a
    pop af
    jp po,$$masked
    ld a,c
    ei
    ret
$$masked:
    ld a,c
    ret
ENDMACRO
    API tx_open,open_core
    API tx_reserve,reserve_core
    API tx_publish,publish_core
    API tx_status,status_core
    API tx_cancel,cancel_core
    API tx_reap,reap_core
    API tx_poll_drain,drain_core
    API tx_close,close_core
    API tx_kick,kick_core
    API tx_barrier_enter,barrier_core
    API tx_barrier_leave,unbarrier_core
    API tx_sync_byte,sync_core

ok:
    xor a,a
    ret
busy:
    ld a,1
    ret
invalid:
    ld a,2
    ret
closed:
    ld a,3
    ret
check_open:
    ld a,(tx_opened)
    or a,a
    ret
; Full 24-bit null test. Looking only at H/L would misclassify 010000h.
; Preserve HL and DE, return Z iff HL=0; BC is untouched.
hl_zero:
    push de
    ld de,0
    or a,a
    sbc hl,de
    pop de
    ret

open_core:
    call check_open
    jr nz,busy
    in0 a,(IER)
    ; Isolated contract accepts only normal receive/line-status baseline.
    and a,0fah
    jr nz,busy
    in0 a,(IER)
    ld (tx_saved_ier),a
    or a,5
    ld (tx_ier),a
    out0 (IER),a
    ld a,1
    ld (tx_opened),a
    jp ok

; All ticket values are monotonic across close/open. Zero is never issued.
; Exhaustion is sticky until the entire driver is reinitialized, avoiding ABA.
reserve_core:
    call check_open
    jp z,closed
    ld hl,(tx_next_ticket)
    ld a,h
    or a,l
    ld (tx_tmp),hl
    ld a,(tx_tmp+2)
    or a,h
    or a,l
    jp z,busy
    ld ix,tx_slots
    ld b,3
reserve_scan:
    ld a,(ix+0)
    or a,a
    jr z,reserve_found
    ld de,STRIDE
    add ix,de
    djnz reserve_scan
    jp busy
reserve_found:
    ld (ix+1),hl          ; ADL24 OK: ticket occupies offsets 1..3.
    inc hl
    ld (tx_next_ticket),hl
    ld hl,0
    ld (ix+4),hl
    ld (ix+7),hl
    ld (ix+10),hl
    ld (ix+13),hl
    ld (ix+16),hl
    ld hl,(ix+1)
    ld a,RESERVED
    ld (ix+0),a
    jp ok

; Preserve source/count/ticket while locating a descriptor. IX is scratch.
find:
    push hl
    push bc
    ld ix,tx_slots
    ld b,3
find_loop:
    ld a,(ix+0)
    or a,a
    jr z,find_next
    ld hl,(ix+1)
    or a,a
    sbc hl,de
    jr z,find_yes
find_next:
    push de
    ld de,STRIDE
    add ix,de
    pop de
    djnz find_loop
    pop bc
    pop hl
    ld a,2
    or a,a
    ret
find_yes:
    pop bc
    pop hl
    xor a,a
    ret

publish_core:
    call check_open
    jp z,closed
    ld a,(tx_barrier)
    or a,a
    jp nz,busy
    call find
    ret nz
    ld a,(ix+0)
    cp a,RESERVED
    jp nz,invalid
    ld (tx_tmp),bc
    ld a,(tx_tmp+2)
    or a,a
    jp nz,invalid
    ld a,b
    or a,c
    jp z,invalid
    push hl
    add hl,bc
    pop hl
    jp c,invalid
    ld (ix+4),hl          ; ADL24 OK: source pointer 4..6.
    ld (ix+7),bc          ; ADL24 OK: remaining 7..9.
    ld (ix+13),bc         ; ADL24 OK: original length 13..15.
    ld hl,0
    ld (ix+10),hl         ; ADL24 OK: accepted 10..12.
    ld (ix+16),hl         ; ADL24 OK: next link 16..18.
    ld a,QUEUED
    ld (ix+0),a
    ld hl,(tx_tail)
    ld a,h
    or a,l
    ld (tx_tmp),hl
    ld a,(tx_tmp+2)
    or a,h
    or a,l
    jr z,publish_first
    ; Link through the previous tail without clobbering the new descriptor.
    push ix
    push hl
    pop ix
    pop hl
    ld (ix+16),hl
    ld (tx_tail),hl
    jr publish_kick
publish_first:
    push ix
    pop hl
    ld (tx_head),hl
    ld (tx_tail),hl
publish_kick:
    call tx_service
    jp ok

status_core:
    call check_open
    jp z,closed
    call find
    ret nz
    ld b,(ix+0)
    ld hl,(ix+10)
    jp ok

cancel_core:
    call check_open
    jp z,closed
    call find
    ret nz
    ld a,(ix+0)
    cp a,RESERVED
    jr z,cancel_mark
    cp a,QUEUED
    jp nz,busy
    ; A queued descriptor has emitted no bytes. ACTIVE is never cancellable.
    push ix
    pop de
    ld hl,(tx_head)
    or a,a
    sbc hl,de
    jr z,cancel_head
    push ix
    ld ix,(tx_head)
    ld b,3
cancel_search:
    ld hl,(ix+16)
    or a,a
    sbc hl,de
    jr z,cancel_link
    ld ix,(ix+16)
    djnz cancel_search
    pop ix
    jp invalid
cancel_link:
    ; IX=predecessor; saved descriptor is recovered through HL.
    pop hl
    push ix
    push hl
    pop ix
    ld hl,(ix+16)
    pop ix
    ld (ix+16),hl
    ld hl,(tx_tail)
    or a,a
    sbc hl,de
    jr nz,cancel_restore
    push ix
    pop hl
    ld (tx_tail),hl
cancel_restore:
    push de
    pop ix
    jr cancel_mark
cancel_head:
    ld hl,(ix+16)
    ld (tx_head),hl
    call hl_zero
    jr nz,cancel_mark
    ld (tx_tail),hl
cancel_mark:
    ld a,CANCELLED
    ld (ix+0),a
    call tx_service
    jp ok

reap_core:
    call check_open
    jp z,closed
    call find
    ret nz
    ld a,(ix+0)
    cp a,RELEASED
    jr z,reap_go
    cp a,CANCELLED
    jp nz,busy
reap_go:
    ld (ix+0),FREE
    jp ok

drain_core:
    call check_open
    jp z,closed
    ld hl,(tx_head)
    call hl_zero
    jp nz,busy
    call read_lsr
    bit 6,a
    jp z,busy
    jp ok

close_core:
    call drain_core
    or a,a
    ret nz
    ld ix,tx_slots
    ld b,3
close_scan:
    ld a,(ix+0)
    or a,a
    jp nz,busy
    ld de,STRIDE
    add ix,de
    djnz close_scan
    ld a,(tx_saved_ier)
    out0 (IER),a
    ld (tx_ier),a
    xor a,a
    ld (tx_opened),a
    ld (tx_barrier),a
    ret
kick_core:
    call check_open
    jp z,closed
    call tx_service
    jp ok

; Isolated synchronous barrier: nonblocking try-enter, no new publication.
; Caller retries drain/kick and owns the barrier until explicit leave.
barrier_core:
    call check_open
    jp z,closed
    ld a,(tx_barrier)
    or a,a
    jp nz,busy
    ld a,1
    ld (tx_barrier),a
    jp ok
unbarrier_core:
    call check_open
    jp z,closed
    ld a,(tx_barrier)
    or a,a
    jp z,invalid
    xor a,a
    ld (tx_barrier),a
    ret
; E=ordinary byte, barrier required; returns BUSY until earlier work is drained.
sync_core:
    call check_open
    jp z,closed
    ld a,(tx_barrier)
    or a,a
    jp z,invalid
    push de
    call drain_core
    pop de
    or a,a
    ret nz
    call read_msr
    bit 4,a
    jp z,busy
    ld a,e
    out0 (THR),a
    jp ok

; Every LSR/MSR read acknowledges through a shared sticky latch.
read_lsr:
    in0 a,(LSR)
    push af
    and a,09eh
    ld c,a
    ld a,(tx_rx_errors)
    or a,c
    ld (tx_rx_errors),a
    pop af
    ret
read_msr:
    in0 a,(MSR)
    push af
    and a,00fh
    ld c,a
    ld a,(tx_modem_deltas)
    or a,c
    ld (tx_modem_deltas),a
    pop af
    ret

; Bounded single burst, at most 16 THR writes, no busy waits.
; Sole THR owner while async work is outstanding. Called with DI.
    XDEF tx_service
 tx_service:
    ld hl,(tx_head)
    call hl_zero
    jp z,service_idle
    ; Arm modem wakeups BEFORE sampling CTS; never depend solely on DCTS.
    ld a,(tx_ier)
    or a,8
    ld (tx_ier),a
    out0 (IER),a
    call read_lsr
    bit 5,a
    jr z,service_running
    ld b,16
service_next:
    call read_msr
    bit 4,a
    jr z,service_blocked
    ld ix,(tx_head)
    ld hl,(ix+4)
    ld a,(hl)
    XDEF tx_write
 tx_write:
    out0 (THR),a
    inc hl
    ld (ix+4),hl
    ld a,ACTIVE
    ld (ix+0),a
    ld hl,(ix+10)
    inc hl
    ld (ix+10),hl
    ld hl,(ix+7)
    dec hl
    ld (ix+7),hl
    ld a,h
    or a,l
    jr nz,service_more
    ld a,RELEASED
    ld (ix+0),a
    ld hl,(ix+16)
    ld (tx_head),hl
    call hl_zero
    jr nz,service_more
    ld (tx_tail),hl
    jr service_idle
service_more:
    djnz service_next
service_running:
    ld a,(tx_ier)
    or a,00ah
    ld (tx_ier),a
    out0 (IER),a
    ret
service_blocked:
    ; FIFO empty and CTS blocked: TIE must be off to avoid a level storm.
    ld a,(tx_ier)
    and a,0fdh
    ld (tx_ier),a
    out0 (IER),a
    call read_msr
    bit 4,a
    ret z
    ; CTS recovered while masking TIE. Re-arm, don't spin or exceed budget.
    jr service_running
service_idle:
    ld a,(tx_ier)
    and a,0f5h
    ld (tx_ier),a
    out0 (IER),a
    ret

; UART cause dispatcher. Hardware acknowledge/vector entry is harness-owned;
; actual DI, saves/restores, cause reads and EI/RETI.L execute on the CPU model.
; One entry: <=8 cause reads, <=16 RX bytes and <=one TX service burst.
    XDEF tx_isr
 tx_isr:
    di
    push af
    push bc
    push de
    push hl
    push ix
    ld a,1
    ld (tx_in_isr),a
    ld a,8
    ld (tx_cause_budget),a
    ld a,16
    ld (tx_rx_budget),a
    xor a,a
    ld (tx_tx_serviced),a
isr_dispatch:
    in0 a,(IIR)
    bit 0,a
    jr nz,isr_done
    and a,00eh
    cp a,6
    jr z,isr_line
    cp a,4
    jr z,isr_rx
    cp a,12
    jr z,isr_rx
    cp a,2
    jr z,isr_tx
    or a,a
    jr z,isr_modem
    ; TCIE is never enabled; unknown causes are a diagnostic, not RX data.
    ld (tx_unknown_cause),a
    jr isr_done
isr_line:
    call read_lsr
    jr isr_next
isr_rx:
    ld a,(tx_rx_budget)
    or a,a
    jr z,isr_done
    call read_lsr
    bit 0,a
    jr z,isr_next
    in0 a,(THR)
    call tx_rx_sink
    ld a,(tx_rx_budget)
    dec a
    ld (tx_rx_budget),a
    jr isr_rx
isr_tx:
    ld a,(tx_tx_serviced)
    or a,a
    jr nz,isr_done
    inc a
    ld (tx_tx_serviced),a
    call tx_service
    jr isr_next
isr_modem:
    ld a,(tx_tx_serviced)
    or a,a
    ; Do not acknowledge a new CTS edge after spending this entry's TX
    ; budget: it may be the only wakeup while TIE is off. Leave it pending
    ; for a fresh entry, which can reconcile the level and service once.
    jr nz,isr_done
    call read_msr
    ld a,1
    ld (tx_tx_serviced),a
    call tx_service
isr_next:
    ld a,(tx_cause_budget)
    dec a
    ld (tx_cause_budget),a
    jr nz,isr_dispatch
isr_done:
    xor a,a
    ld (tx_in_isr),a
    pop ix
    pop hl
    pop de
    pop bc
    pop af
    ei
    reti.l

; Immutable structure layout: state:u8,ticket:u24,ptr:u24,remaining:u24,
; accepted:u24,length:u24,next:u24. Every wide memory access has a 3-byte field.
    XDEF tx_slots,tx_head,tx_tail,tx_next_ticket,tx_rx_errors,tx_modem_deltas
    XDEF tx_opened,tx_barrier,tx_in_isr,tx_unknown_cause
 tx_slots: DS 3*STRIDE
 tx_head: DB 0,0,0
 tx_tail: DB 0,0,0
 tx_next_ticket: DB 1,0,0
 tx_tmp: DB 0,0,0
 tx_opened: DB 0
 tx_barrier: DB 0
 tx_in_isr: DB 0
 tx_saved_ier: DB 0
 tx_ier: DB 0
 tx_rx_errors: DB 0
 tx_modem_deltas: DB 0
 tx_cause_budget: DB 0
 tx_rx_budget: DB 0
 tx_tx_serviced: DB 0
 tx_unknown_cause: DB 0

    END
