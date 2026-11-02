; Interrupt-based UART0 transmission. ADL assembly API; see docs/uart0-async.md.
UART0_PRODUCTION EQU 1
UART0_BATCH_SCALAR EQU 0
    INCLUDE "uart0_tx.inc"
    SEGMENT .STARTUP
    XREF vdp_protocol,_vdp_protocol_data
    XDEF _uart0_tx_init,uart0_sync_begin,uart0_sync_end,uart0_sync_put
    XDEF uart0_return_fence,_uart0_return_fence,uart0_read_lsr,uart0_read_msr
    XDEF uart0_async_getapi,tx_rx_sink
    XREF _set_vector,_uart0_handler
    XDEF uart0_activate,uart0_deactivate,uart0_install_vector
    XDEF uart0_initialized,uart0_saved_vector
    XDEF uart0_pump

; Lazy initialization, called only on the first explicit successful activation.
; Ordinary release BSS initialization leaves the driver disabled after reset.
_uart0_tx_init:
    ld a,(uart0_initialized)
    or a,a
    ret nz
    ld hl,1
    ld (tx_next_ticket),hl
    ld a,1
    ld (tx_cts_batch),a
    ld (uart0_initialized),a
    ret

; API holds DI. Do not activate over bytes still leaving the stock transport.
; set_vector is the release's existing C-ABI RAM-vector operation.
uart0_activate:
    call read_lsr            ; Explicit activation retains acknowledged errors.
    bit 6,a
    jp z,busy
    ld hl,tx_isr
    call uart0_install_vector
    ld (uart0_saved_vector),hl
    ld de,_uart0_handler
    or a,a
    sbc hl,de
    jr z,activate_owned
    ; A user replaced the stock UART handler: restore it, refuse ownership.
    ld hl,(uart0_saved_vector)
    call uart0_install_vector
    jp busy
activate_owned:
    call _uart0_tx_init
    jp ok

uart0_deactivate:
    ld hl,(uart0_saved_vector)
    jp uart0_install_vector

uart0_install_vector:
    push hl                  ; C argument 2: handler.
    ld hl,018h
    push hl                  ; C argument 1: UART0 vector.
    call _set_vector
    pop bc
    pop bc
    ret                      ; HL = previous handler.

; Existing MOS parser and keyboard state remain the receive owner.
tx_rx_sink:
    ld c,a
    ld hl,_vdp_protocol_data
    jp vdp_protocol

; Legacy serial leaves BC intact; every status read still latches diagnostics.
uart0_read_lsr:
    push bc
    ld a,i
    push af
    di
    call read_lsr
    jr read_status_return
uart0_read_msr:
    push bc
    ld a,i
    push af
    di
    call read_msr
read_status_return:
    ld b,a
    pop af
    jp po,read_status_masked
    ld a,b
    pop bc
    ei
    ret
read_status_masked:
    ld a,b
    pop bc
    ret

; Preserve every caller register/flag and IFF for compatibility entry points.
SAVE_ALL MACRO
    push af
    push bc
    push de
    push hl
    push ix
ENDMACRO
RESTORE_ALL MACRO
    pop ix
    pop hl
    pop de
    pop bc
    pop af
    ret
ENDMACRO

; A byte PUTCH nests inside a whole RST18 scope. No foreground producer can
; publish while the scope is held. Installed callbacks imply async is closed.
uart0_sync_begin:
    SAVE_ALL
    ld a,i
    push af
    di
    ld a,(uart0_sync_depth)
    inc a
    ld (uart0_sync_depth),a
    ld a,(tx_opened)
    or a,a
    jr z,sync_begin_restore
    ld a,1
    ld (tx_barrier),a
sync_begin_restore:
    pop af
    jp po,sync_begin_wait
    ei
sync_begin_wait:
    ld a,(tx_opened)
    or a,a
    jr z,sync_begin_done
sync_begin_drain:
    call uart0_pump
    call uart0_drain_try
    or a,a
    jr nz,sync_begin_drain
sync_begin_done:
    RESTORE_ALL

uart0_sync_end:
    SAVE_ALL
    ld a,i
    push af
    di
    ld a,(uart0_sync_depth)
    dec a
    ld (uart0_sync_depth),a
    jr nz,sync_end_restore
    xor a,a
    ld (tx_barrier),a
sync_end_restore:
    pop af
    jp po,sync_end_done
    ei
sync_end_done:
    RESTORE_ALL

; A=byte. The serial wrapper calls this only with an open async session.
; Polling pumps both directions so foreground DI cannot strand the queue.
uart0_sync_put:
    SAVE_ALL
    ld e,a
    call uart0_sync_begin
sync_put_wait:
    push de
    call uart0_pump
    pop de
    call uart0_sync_try
    or a,a
    jr nz,sync_put_wait
    call uart0_sync_end
    RESTORE_ALL

; Internal compatibility calls already execute in ADL and must work with a
; nonzero MBASE inherited from a short-mode caller. Public API guards do not
; apply to these MOS-owned operations.
INTERNAL MACRO entry,core
entry:
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
    INTERNAL uart0_drain_try,drain_core
    INTERNAL uart0_sync_try,sync_core

; Bounded polling service. No IIR reads: never acknowledge an unhandled TX
; cause. Parser re-entry uses the same guard as the actual receive ISR.
uart0_pump:
    ld a,i
    push af
    di
    push ix
    ld a,1
    ld (tx_in_isr),a
    ld b,16
pump_rx:
    push bc
    call read_lsr
    bit 0,a
    jr z,pump_no_rx
    in0 a,(THR)
    call tx_rx_sink
    pop bc
    djnz pump_rx
    jr pump_tx
pump_no_rx:
    pop bc
pump_tx:
    call tx_service
    xor a,a
    ld (tx_in_isr),a
    pop ix
    pop af
    jp po,pump_done
    ei
pump_done:
    ret

; C-002: retain every borrowed source and the application's stack until queue
; and wire drain. Then discard reservations/completions (no further reads),
; close, and preserve monotonic tickets. A permanent CTS stall waits forever.
; Also called before OSCLI/child loading and before installing a callback.
_uart0_return_fence:
uart0_return_fence:
    SAVE_ALL
    ld a,(tx_opened)
    or a,a
    jr z,return_done
    ld a,i
    push af
    di
    call uart0_write_reset  ; Suppress app callbacks before return/drain.
    pop af
    jp po,return_write_reset
    ei
return_write_reset:
    call uart0_sync_begin
    ld a,i
    push af
    di
    ld ix,tx_slots
    ld b,3
return_clear:
    ld (ix+0),FREE
    ld de,STRIDE
    add ix,de
    djnz return_clear
    call close_core
    pop af
    jp po,return_scope_end
    ei
return_scope_end:
    call uart0_sync_end
return_done:
    RESTORE_ALL

; Discover through MOS getfunction 13h. This returns a versioned ROM table,
; not writable driver state. All operation pointers use the register ABI.
uart0_async_getapi:
    ld hl,uart0_async_api
    xor a,a
    ret
uart0_async_api:
    DB "UTX1",1,3,uart0_async_api_end-uart0_async_api,31
    DB 3,16
    DB 255,255,0
    DW24 tx_open,tx_reserve,tx_publish,tx_status,tx_cancel,tx_reap
    DW24 tx_poll_drain,tx_close,tx_kick
    DW24 tx_rx_errors
    DW24 tx_diag_take
    DW24 tx_set_cts_batch,tx_get_cts_batch
    DW 0808bh
    DW24 tx_write_config,tx_write_query,tx_write_last,tx_completion_take
    DW24 tx_write_borrowed
uart0_async_api_end:
    SECTION BSS
    XDEF uart0_sync_depth
uart0_sync_depth: DS 1
uart0_initialized: DS 1
uart0_saved_vector: DS 3
    INCLUDE "uart0_completion.inc"
    END
