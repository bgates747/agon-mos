; UX-001 experiment: copied RST18 and optional bounded completion callbacks.
; Included only by the production adapter. Does not run on stock startup.
; All payload storage is fixed BSS; existing borrowed descriptors stay unchanged.
QSTRIDE EQU 8                 ; kind, pending, id24, descriptor-ticket24
QBYTES EQU 256
    SEGMENT .STARTUP
    XDEF tx_write_config,tx_write_query,tx_write_last,tx_completion_take
    XDEF tx_write_borrowed,uart0_queue_rst,uart0_write_reset
    XDEF uart0_write_release,tx_write_mode
QAPI MACRO entry,core
    XDEF entry
entry:
    ld a,mb
    or a,a
    jp nz,$$bad
    ld a,(tx_in_isr)
    or a,a
    jp z,$$go
$$bad:
    ld a,4
    ret
$$go:
    ld a,i
    push af
    di
    push ix
    push iy
    call core
    pop iy
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
    QAPI tx_write_config,write_config_core
    QAPI tx_write_query,write_query_core
    QAPI tx_write_last,write_last_core
    QAPI tx_completion_take,completion_take_core
    QAPI tx_write_borrowed,write_borrowed_core

; B=0 standard RST18 / 1 copied RST18; C=0 take events / 1 direct callback.
; HL=callback (zero allowed with C=0), DE=context. All three slots must be free.
write_config_core:
    call check_open
    jp z,closed
    ld a,b
    cp a,2
    jp nc,invalid
    ld a,c
    cp a,2
    jp nc,invalid
    ld a,b
    or a,a
    jp z,write_config_choice
    ld a,c
    or a,a
    jp z,invalid           ; Copied mode requires automatic retirement.
write_config_choice:
    push bc
    push de
    push hl
    ld a,c
    or a,a
    jp z,write_config_address_ok
    ; A null callback is allowed: auto-retirement without notification.
    call hl_zero
    jp z,write_config_address_ok
    ; Non-null callbacks must be application code in ordinary RAM.
    ld de,040000h
    or a,a
    sbc hl,de
    jp c,write_config_bad
    add hl,de
    ld de,0bc000h
    or a,a
    sbc hl,de
    jp nc,write_config_bad
write_config_address_ok:
    ld a,(uart0_sync_depth)
    or a,a
    jp nz,write_config_busy
    ld a,(tx_barrier)
    or a,a
    jp nz,write_config_busy
    ld a,(tx_write_active)
    or a,a
    jp nz,write_config_busy
    ld ix,tx_slots
    ld b,3
write_config_scan:
    ld a,(ix+0)
    or a,a
    jp nz,write_config_busy
    ld de,STRIDE
    add ix,de
    djnz write_config_scan
    call read_lsr
    bit 6,a
    jp z,write_config_busy
    pop hl
    pop de
    pop bc
    ld (tx_write_callback),hl
    ld (tx_write_context),de
    ld a,c
    ld (tx_write_delivery),a
    ld a,b
    ld (tx_write_mode),a
    jp ok
write_config_bad:
    pop hl
    pop de
    pop bc
    jp invalid
write_config_busy:
    pop hl
    pop de
    pop bc
    jp busy
write_query_core:
    call check_open
    jp z,closed
    ld hl,(tx_write_callback)
    ld de,(tx_write_context)
    ld a,(tx_write_delivery)
    rlca
    rlca
    rlca
    rlca
    ld b,a
    ld a,(tx_write_mode)
    or a,b
    ld b,a
    jp ok
write_last_core:
    call check_open
    jp z,closed
    ld hl,(tx_write_last_id)
    jp ok

; Private metadata for IX's descriptor. Preserve caller state and flags.
write_meta:
    push hl
    push de
    push bc
    push ix
    pop hl
    ld de,tx_slots
    or a,a
    sbc hl,de
    ld de,tx_write_meta
    call hl_zero
    jp z,write_meta_found
    ld bc,STRIDE
    or a,a
    sbc hl,bc
    ld de,tx_write_meta+QSTRIDE
    jp z,write_meta_found
    ld de,tx_write_meta+QSTRIDE*2
write_meta_found:
    push de
    pop iy
    pop bc
    pop de
    pop hl
    ret

; Hook after unlinking a RELEASED descriptor. No hook on legacy raw tickets.
; Mode1 callback can run here in UART ISR OR a masked foreground service call.
uart0_write_release:
    push af
    push bc
    push de
    push hl
    push ix
    push iy
    call write_meta
    ld a,(iy+0)
    or a,a
    jp z,write_release_done
    ld hl,(iy+2)
    call hl_zero
    jp z,write_release_silent
    ld a,(tx_write_delivery)
    or a,a
    jp z,write_release_pending
    ld (ix+0),FREE
    ld (iy+0),0
    ld de,(tx_write_context)
    call write_callback
    jp write_release_done
write_release_pending:
    ld (iy+1),1             ; Retain slot until event is taken; bounded storage.
    jp write_release_done
write_release_silent:
    ld (ix+0),FREE          ; Intermediate copied chunk; no logical completion.
    ld (iy+0),0
write_release_done:
    pop iy
    pop ix
    pop hl
    pop de
    pop bc
    pop af
    ret

; Callback A=4 SOURCE_CONSUMED, HL=logical write ID, DE=registered context.
; Preserve both register banks and indexes; callback must preserve ADL/MBASE,
; leave interrupts disabled, return normally, and only post bounded app work.
write_callback:
    push hl
    ld hl,(tx_write_callback)
    call hl_zero
    pop hl
    ret z
    push bc
    push ix
    push iy
    exx
    push bc
    push de
    push hl
    exx
    ex af,af'
    push af
    ex af,af'
    ld a,mb
    push af
    xor a,a
    ld mb,a
    ld a,(tx_in_isr)
    push af
    ld a,1
    ld (tx_in_isr),a
    ld a,RELEASED
    ld bc,write_callback_return
    push bc
    ld bc,(tx_write_callback)
    push bc
    ret
write_callback_return:
    pop af
    ld (tx_in_isr),a
    pop af
    ld mb,a
    ex af,af'
    pop af
    ex af,af'
    exx
    pop hl
    pop de
    pop bc
    exx
    pop iy
    pop ix
    pop bc
    ret

; Event taking is foreground-only; the application/library invokes its callback
; AFTER this returns, with its ordinary IFF. No foreground callback runs in MOS.
; A=OK, HL=id, DE=context, B=kind (1 borrowed,2 copied); BUSY if none.
completion_take_core:
    call check_open
    jp z,closed
    ld hl,0ffffffh
    ld (tx_write_event_id),hl
    ld hl,0
    ld (tx_write_event_meta),hl
    ld iy,tx_write_meta
    ld ix,tx_slots
    ld b,3
completion_scan:
    ld a,(iy+1)
    or a,a
    jp z,completion_next
    push bc
    ld hl,(iy+2)
    ld de,(tx_write_event_id)
    or a,a
    sbc hl,de
    jp z,completion_select
    jp nc,completion_skip
completion_select:
    ld hl,(iy+2)
    ld (tx_write_event_id),hl
    push iy
    pop hl
    ld (tx_write_event_meta),hl
    push ix
    pop hl
    ld (tx_write_event_slot),hl
completion_skip:
    pop bc
completion_next:
    ld de,QSTRIDE
    add iy,de
    ld de,STRIDE
    add ix,de
    djnz completion_scan
    ld hl,(tx_write_event_meta)
    call hl_zero
    jp z,busy
    push hl
    pop iy
    ld ix,(tx_write_event_slot)
completion_found:
    ld hl,(iy+2)
    ld a,(iy+0)
    ld b,a
    ld (iy+0),0
    ld (iy+1),0
    ld (ix+0),FREE
    ld de,(tx_write_context)
    jp ok

; New convenience borrowed write: HL=source BC=count, returns HL=opaque write ID.
; Configuration supplies callback/context. Automatically reaps on notification.
; Internal tickets are not public cancel/reap handles for this entry.
write_borrowed_core:
    ld a,(tx_write_mode)
    or a,a
    jp nz,busy             ; Do not mix convenience writes into copied mode.
    push hl
    push bc
    call reserve_core
    pop bc
    pop de                 ; DE=source; HL=ticket.
    or a,a
    ret nz
    push hl
    ld (tx_write_ticket),hl
    ex de,hl               ; HL=source DE=ticket
    call find
    call write_meta
    ld (iy+0),1
    ld (iy+1),0
    push hl
    ld hl,(tx_write_last_id)
    ld (tx_write_previous_id),hl
    call write_new_id
    ld (iy+2),hl
    ld hl,(tx_write_ticket)
    ld (iy+5),hl
    pop hl
    call publish_core
    or a,a
    jp z,write_borrowed_ok
    ld (iy+0),0
    ld (ix+0),FREE
    pop hl
    ld hl,(tx_write_previous_id)
    ld (tx_write_last_id),hl
    ret
write_borrowed_ok:
    pop hl
    ld hl,(tx_write_last_id)
    jp ok
write_new_id:
    ld hl,(tx_write_sequence)
    inc hl
    call hl_zero
    jp nz,write_id_ok
    inc hl
write_id_ok:
    ld (tx_write_sequence),hl
    ld (tx_write_last_id),hl
    ret

; Adapter called from RST18 only after explicit mode selection. ADL/MBASE0.
; Exact release fixed/delimited behavior is retained by falling back for short
; callers; IFF-masked long callers are serviced by the existing bounded pump.
; Payload chunks use private slots; no app source retained after return.
uart0_queue_rst:
    push ix
    push iy
    push de
    ld (tx_write_source),hl
    ld (tx_write_count),bc
    push af
    xor a,a
    ld (tx_write_count+2),a ; Release RST18 counts only BC low16 bits.
    pop af
    ld (tx_write_delimiter),a
    xor a,a
    ld (tx_write_delimited),a
    ld a,b
    or a,c
    jp nz,queue_fixed
    inc a
    ld (tx_write_delimited),a
queue_fixed:
    ld a,i
    push af
    di
    call write_new_id
    ld (tx_write_call_id),hl
    ld a,1
    ld (tx_write_active),a
    pop af
    jp po,queue_next
    ei
queue_next:
    ; Find a free descriptor. Existing raw reservations must not share this
    ; mode: config required all free; public reserve is refused in copied mode.
    call queue_reserve
    or a,a
    jp z,queue_reserved
    call uart0_pump
    ; Copied mode uses auto-retirement (delivery1, null callback allowed).
    ; Event-taking mode is rejected at configuration, avoiding a full-queue
    ; wait that could require this same foreground caller to consume events.
    jp queue_next
queue_reserved:
    ld (tx_write_ticket),hl
    ex de,hl
    call write_meta
    ; IY metadata pointer maps to one fixed256-byte buffer.
    push iy
    pop hl
    ld de,tx_write_meta
    or a,a
    sbc hl,de
    ld de,tx_write_buffers
    call hl_zero
    jp z,queue_buffer
    ld de,tx_write_buffers+QBYTES
    ld bc,QSTRIDE
    or a,a
    sbc hl,bc
    jp z,queue_buffer
    ld de,tx_write_buffers+QBYTES*2
queue_buffer:
    ld (tx_write_buffer),de
    ld hl,(tx_write_source)
    ld a,(tx_write_delimited)
    or a,a
    jp nz,queue_copy_delimiter
    ; Common binary write: copy a full contiguous chunk using LDIR.
    push hl
    ld hl,(tx_write_count)
    ld bc,QBYTES
    ld a,h
    or a,a
    jp nz,queue_fixed_count
    push hl
    pop bc
queue_fixed_count:
    or a,a
    sbc hl,bc
    ld (tx_write_count),hl
    pop hl
    push bc
    ldir
    pop bc
    jp queue_copy_end
queue_copy_delimiter:
    ld bc,0
queue_copy:
    ld a,(tx_write_delimited)
    or a,a
    jp z,queue_copy_fixed
    ld a,(tx_write_delimiter)
    cp a,(hl)
    jp z,queue_copy_end
    jp queue_copy_byte
queue_copy_fixed:
    push hl
    ld hl,(tx_write_count)
    ld a,h
    or a,l
    pop hl
    jp z,queue_copy_end
queue_copy_byte:
    ld a,(hl)
    ld (de),a
    inc hl
    inc de
    inc bc
    ld a,(tx_write_delimited)
    or a,a
    jp nz,queue_copy_counted
    push hl
    ld hl,(tx_write_count)
    dec hl
    ld (tx_write_count),hl
    pop hl
queue_copy_counted:
    ld a,b
    or a,a
    jp z,queue_copy
queue_copy_end:
    ld (tx_write_source),hl
    ld a,c
    or a,b
    jp nz,queue_publish
    ; Empty delimited call: preserve ordering with earlier writes.
    ld (ix+0),FREE
queue_empty_drain:
    call uart0_pump
    call uart0_drain_try
    or a,a
    jp nz,queue_empty_drain
    ld hl,(tx_write_call_id)
    ld de,(tx_write_context)
    ld a,i
    push af
    di
    call write_callback
    pop af
    jp po,queue_done
    ei
    jp queue_done
queue_publish:
    ld (iy+0),2
    ld (iy+1),0
    ld hl,0
    ld (iy+2),hl            ; Intermediate chunk does not notify.
    ld a,(tx_write_delimited)
    or a,a
    jp z,queue_last_fixed
    ld hl,(tx_write_source)
    ld a,(tx_write_delimiter)
    cp a,(hl)
    jp z,queue_last
    jp queue_not_last
queue_last_fixed:
    ld hl,(tx_write_count)
    ld a,h
    or a,l
    jp nz,queue_not_last
queue_last:
    ld hl,(tx_write_call_id)
    ld (iy+2),hl
queue_not_last:
    ld hl,(tx_write_buffer)
    call queue_publish_private
    ld a,(tx_write_delimited)
    or a,a
    jp z,queue_more_fixed
    ld hl,(tx_write_source)
    ld a,(tx_write_delimiter)
    cp a,(hl)
    jp nz,queue_next
    jp queue_done
queue_more_fixed:
    ld hl,(tx_write_count)
    ld a,h
    or a,l
    jp nz,queue_next
queue_done:
    xor a,a
    ld (tx_write_active),a
    ld hl,(tx_write_source)
    ld bc,0
    pop de
    pop iy
    pop ix
    ret
queue_reserve:
    ld a,i
    push af
    di
    call reserve_core
    ld (tx_write_result),a
    or a,a
    jp nz,queue_reserve_return
    push hl
    pop de
    call find
queue_reserve_return:
    pop af
    jp po,queue_reserve_masked
    ei
queue_reserve_masked:
    ld a,(tx_write_result)
    or a,a
    ret
    INTERNAL queue_publish_private,publish_ram_ok

uart0_write_reset:
    xor a,a
    ld (tx_write_mode),a
    ld (tx_write_delivery),a
    ld (tx_write_active),a
    ld hl,0
    ld (tx_write_callback),hl
    ld (tx_write_context),hl
    ld (tx_write_last_id),hl
    ld hl,tx_write_meta
    ld b,QSTRIDE*3
write_reset_loop:
    ld (hl),a
    inc hl
    djnz write_reset_loop
    ret

    SECTION BSS
 tx_write_mode: DS 1
 tx_write_delivery: DS 1
 tx_write_active: DS 1
 tx_write_callback: DS 3
 tx_write_context: DS 3
 tx_write_sequence: DS 3
 tx_write_last_id: DS 3
 tx_write_meta: DS QSTRIDE*3
 tx_write_buffers: DS QBYTES*3
 tx_write_source: DS 3
 tx_write_count: DS 3
 tx_write_buffer: DS 3
 tx_write_ticket: DS 3
 tx_write_call_id: DS 3
 tx_write_delimiter: DS 1
 tx_write_delimited: DS 1
 tx_write_previous_id: DS 3
 tx_write_result: DS 1
 tx_write_event_id: DS 3
 tx_write_event_meta: DS 3
 tx_write_event_slot: DS 3
