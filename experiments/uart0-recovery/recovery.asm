; HW-001. Unchanged-VDP traffic through installed MOS API1.1 only.
; No private UART owner, altered CTS threshold or receiver pause injection.
.assume adl=1
    DEFINE UART_ENTRY, SPACE=ROM
    SEGMENT UART_ENTRY
    XDEF app_entry
app_entry:
    jp start
    DS 60
    DB "MOS",0,1,"URH1"
result_name: DB "recovery.dat",0
    DS 3
progress_name: DB "progress.dat",0
    DS 3
failure_name: DB "rx-fail.dat",0
    DS 4
campaign_repeats: DB 1
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
    ld a,(campaign_repeats)
    cp a,1
    jr z,valid_repeats
    cp a,4
    jp nz,failed
valid_repeats:
    ld (report_repeats),a
    ld b,a
    add a,a
    add a,b
    add a,a
    ld (record_count),a
    ld hl,intro
    ld bc,intro_end-intro
    rst.lil 18h
    call checkpoint
    ld bc,01300h
    ld a,050h
    rst.lil 08h
    or a,a
    jp nz,failed
    ld (discovery+1),hl
    call discovery
    ld de,magic
    ld b,4
magic_loop:
    ld a,(de)
    cp a,(hl)
    jp nz,failed
    inc de
    inc hl
    djnz magic_loop
    ld a,(hl)
    cp a,1
    jp nz,failed
    inc hl
    ld a,(hl)
    cp a,1
    jp c,failed
    inc hl
    ld a,(hl)
    cp a,46
    jp c,failed
    ld de,7
    add hl,de
    ld de,tx_open+1
    ld b,9
install:
    push bc
    ld bc,3
    ldir
    inc de
    pop bc
    djnz install
    inc hl
    inc hl
    inc hl
    ld hl,(hl)
    ld (tx_diag_take+1),hl
    ld a,1
    ld (api_ready),a
    ld hl,setup
    ld bc,setup_end-setup
    rst.lil 18h
    call reset_gp
    ld hl,mismatch_probe
    ld bc,mismatch_probe_end-mismatch_probe
    rst.lil 18h
    call wait_gp
    cp a,1
    jp nz,failed
    call reset_gp
    ld hl,match_probe
    ld bc,match_probe_end-match_probe
    rst.lil 18h
    call wait_gp
    or a,a
    jp nz,failed
    call tx_diag_take
    or a,a
    jp nz,failed
    ld a,l
    ld (baseline_rx),a
    ld hl,setup_pass
    ld bc,setup_pass_end-setup_pass
    rst.lil 18h
    ld hl,records
    ld (record_ptr),hl
    xor a,a
    ld (case_index),a
case_loop:
    ld a,2
    ld (stage),a
    xor a,a
    ld (failure_code),a
    ld (packet_index),a
    ld (reply_count),a
    ld (busy_replies),a
    ld (ticket_slot),a
    ld hl,0
    ld (accepted_total),hl
    ld (wire_bytes),hl
    ld (last_accepted),hl
    ld (packets_completed),hl
    ld (tickets),hl
    ld (tickets+3),hl
    ld (tickets+6),hl
    ld a,(case_index)
    and a,1
    ld (mode),a
    ld a,(case_index)
reduce_case:
    cp a,6
    jr c,reduced
    sub a,6
    jr reduce_case
reduced:
    srl a
    ld (kind),a
    call progress_case
    call checkpoint
    call tx_diag_take
    or a,a
    jp nz,failed
    call reset_gp
    ld hl,case_clear
    ld bc,case_clear_end-case_clear
    rst.lil 18h
    ld hl,poll_ready
    ld bc,4
    rst.lil 18h
    call wait_gp
    or a,a
    jp nz,failed
    call clock_read
    ld (started),hl
    ld (due),hl
    ld (last_progress),hl
    ld a,(mode)
    or a,a
    jr z,send_loop
    call tx_open
    or a,a
    jp nz,failed
send_loop:
    ld a,(packet_index)
    and a,7
    jr nz,select_packet
    call checkpoint
select_packet:
    ld a,(kind)
    or a,a
    ld hl,bulk_packet
    ld bc,bulk_packet_end-bulk_packet
    jr z,packet_selected
    cp a,1
    jr nz,paced_wait
    ; Each token lives in a separate immutable packet: never modify a header
    ; still borrowed by an ACTIVE descriptor merely because its reply arrived.
    ld a,(packet_index)
    ld hl,0
    ld l,a
    push hl
    pop de
    add hl,hl
    add hl,de
    add hl,hl
    add hl,hl
    ld d,a
    ld e,0
    add hl,de
    ld de,duplex_packets
    add hl,de
    ld bc,268
    jr packet_selected
paced_wait:
    call clock_read
    ld de,(due)
    or a,a
    sbc hl,de
    jr c,paced_wait
    ld hl,(due)
    ld de,2
    add hl,de
    ld (due),hl
    ld hl,small_packet
    ld bc,small_packet_end-small_packet
packet_selected:
    ld (source),hl
    ld (source_size),bc
    ld a,(packet_index)
    add a,16
    ld (wanted_token),a
    ld a,(kind)
    cp a,1
    call z,reset_gp
    ld a,(mode)
    or a,a
    jr nz,async_send
    ld hl,(source)
    ld bc,(source_size)
    rst.lil 18h
    ld hl,(accepted_total)
    ld de,(source_size)
    add hl,de
    ld (accepted_total),hl
    jr sent
async_send:
    call slot_address
    ld de,(hl)
    call ticket_zero
    jr z,slot_available
    call reap_ticket
slot_available:
    call tx_reserve
    or a,a
    jp nz,failed
    ld (new_ticket),hl
    push hl
    call slot_address
    pop de
    ld (hl),de
    ld hl,(source_size)
    push hl
    call size_address
    pop de
    ld (hl),de
    ld de,(new_ticket)
    ld hl,(source)
    ld bc,(source_size)
    call tx_publish
    or a,a
    jp nz,failed
    ld a,(ticket_slot)
    inc a
    cp a,3
    jr c,slot_selected
    xor a,a
slot_selected:
    ld (ticket_slot),a
sent:
    ld hl,(wire_bytes)
    ld de,(source_size)
    add hl,de
    ld (wire_bytes),hl
    ld a,(kind)
    cp a,1
    call z,wait_token
    ld a,(packet_index)
    inc a
    ld (packet_index),a
    ld hl,0
    ld l,a
    ld (packets_completed),hl
    ld b,64
    ld a,(kind)
    or a,a
    jr z,packet_limit
    ld b,32
packet_limit:
    ld a,(packet_index)
    cp a,b
    jp c,send_loop
    ld a,(mode)
    or a,a
    jr nz,drain
    call tx_open
    or a,a
    jp nz,failed
drain:
    call tx_poll_drain
    cp a,1
    jr nz,drained
    call monitor_progress
    jr drain
drained:
    or a,a
    jp nz,failed
    ld a,(mode)
    or a,a
    jr z,reaped
    xor a,a
    ld (ticket_slot),a
reap_all:
    call slot_address
    ld de,(hl)
    call ticket_zero
    call nz,reap_ticket
    ld a,(ticket_slot)
    inc a
    ld (ticket_slot),a
    cp a,3
    jr c,reap_all
reaped:
    call tx_close
    or a,a
    jp nz,failed
    call clock_read
    ld de,(started)
    or a,a
    sbc hl,de
    ld (elapsed),hl
    ld hl,(accepted_total)
    ld de,(wire_bytes)
    or a,a
    sbc hl,de
    jp nz,failed
    ld a,3
    ld (stage),a
    call checkpoint
    ld hl,verifying
    ld bc,verifying_end-verifying
    rst.lil 18h
    call verify_payload
    or a,a
    jp nz,failed
    call tx_diag_take
    or a,a
    jp nz,failed
    ld a,l
    ld (case_rx),a
    or a,a
    jp nz,failed
    ld iy,(record_ptr)
    ld a,(mode)
    ld (iy+0),a
    ld a,(kind)
    ld (iy+1),a
    ld a,(case_index)
    ld (iy+2),a
    ld a,(case_rx)
    ld (iy+3),a
    ld a,(kind)
    cp a,1
    ld a,0
    jr nz,no_replies_expected
    ld a,32
no_replies_expected:
    ld (iy+4),a
    ld a,(reply_count)
    ld (iy+5),a
    ld a,(busy_replies)
    ld (iy+6),a
    ld a,(failure_code)
    ld (iy+7),a
    ld hl,(elapsed)
    ld (iy+8),hl
    ld hl,(wire_bytes)
    ld (iy+11),hl
    ld hl,(accepted_total)
    ld (iy+14),hl
    ld hl,(packets_completed)
    ld (iy+17),hl
    ld hl,8192
    ld (iy+20),hl
    ld (iy+23),1
    ld de,24
    add iy,de
    ld (record_ptr),iy
    ld a,(case_index)
    inc a
    ld (case_index),a
    ld (completed),a
    ld a,4
    ld (stage),a
    call checkpoint
    ld hl,case_pass
    ld bc,case_pass_end-case_pass
    rst.lil 18h
    ld a,(record_count)
    ld b,a
    ld a,(case_index)
    cp a,b
    jp c,case_loop
    ld hl,cleanup
    ld bc,cleanup_end-cleanup
    rst.lil 18h
    xor a,a
    ld (stage),a
    call checkpoint
    ld hl,result_name
    call save_report
    ld hl,success
    ld bc,success_end-success
    rst.lil 18h
finish:
    ld sp,(saved_sp)
    pop iy
    pop ix
    pop hl
    pop de
    pop bc
    pop af
    ld hl,0
    ret
slot_address:
    ld hl,tickets
slot_offset:
    ld a,(ticket_slot)
    ld de,0
    ld e,a
    add hl,de
    add hl,de
    add hl,de
    ret
ticket_zero:
    push hl
    push de
    ex de,hl
    ld de,0
    or a,a
    sbc hl,de
    pop de
    pop hl
    ret
size_address:
    ld hl,ticket_sizes
    jr slot_offset
reap_ticket:
    ld (waiting_ticket),de
reap_wait:
    ld de,(waiting_ticket)
    call tx_status
    or a,a
    jp nz,failed
    ld (last_accepted),hl
    ld a,b
    cp a,4
    jr z,ticket_released
    call tx_poll_drain
    cp a,2
    jp nc,failed
    call monitor_progress
    jr reap_wait
ticket_released:
    push hl
    call size_address
    ld de,(hl)
    pop hl
    or a,a
    sbc hl,de
    jp nz,failed
    ld hl,(accepted_total)
    add hl,de
    ld (accepted_total),hl
    ld de,(waiting_ticket)
    call tx_reap
    or a,a
    jp nz,failed
    call slot_address
    ld de,0
    ld (hl),de
    call clock_read
    ld (last_progress),hl
    ret
; A receive reply is observed before another GP request is admitted.
wait_token:
    call clock_read
    ld (reply_started),hl
token_wait:
    ld ix,(sysvars)
    ld a,(ix+037h)
    cp a,0feh
    jr z,token_not_ready
    ld b,a
    ld a,(wanted_token)
    cp a,b
    jp nz,reply_failed
    ld a,(reply_count)
    inc a
    ld (reply_count),a
    ld a,(mode)
    or a,a
    ret z
    call tx_poll_drain
    cp a,1
    ret nz
    ld a,(busy_replies)
    inc a
    ld (busy_replies),a
    ret
token_not_ready:
    ld a,(mode)
    or a,a
    jr z,token_time
    call tx_poll_drain
    cp a,2
    jp nc,failed
token_time:
    call reply_deadline
    jr token_wait
wait_gp:
    call clock_read
    ld (reply_started),hl
gp_wait:
    ld ix,(sysvars)
    ld a,(ix+037h)
    cp a,0feh
    ret nz
    call reply_deadline
    jr gp_wait
reply_deadline:
    call clock_read
    ld de,(reply_started)
    or a,a
    sbc hl,de
    ld de,1200
    or a,a
    sbc hl,de
    ret c
reply_failed:
    ld a,3
    ld (failure_code),a
    jp failed
; Detect absence of ticket accepted-byte changes; never free an active source.
monitor_progress:
    ld a,(mode)
    or a,a
    ret z
    call slot_address
    ld de,(hl)
    call ticket_zero
    ret z
    call tx_status
    or a,a
    jp nz,failed
    ld de,(monitor_accepted)
    or a,a
    sbc hl,de
    jr z,monitor_time
    add hl,de
    ld (monitor_accepted),hl
    call clock_read
    ld (last_progress),hl
    ret
monitor_time:
    call clock_read
    ld de,(last_progress)
    or a,a
    sbc hl,de
    ld de,6000
    or a,a
    sbc hl,de
    ret c
    ld a,6
    ld (failure_code),a
    jp retain_failure
reset_gp:
    push ix
    ld ix,(sysvars)
    ld (ix+037h),0feh
    pop ix
    ret
progress_case:
    ld a,(case_index)
    call print_hex_byte
    ld hl,case_label
    ld bc,case_label_end-case_label
    rst.lil 18h
    ld a,(mode)
    add a,'0'
    rst.lil 10h
    ld a,'/'
    rst.lil 10h
    ld a,(kind)
    add a,'0'
    rst.lil 10h
    ld a,13
    rst.lil 10h
    ld a,10
    rst.lil 10h
    ret
; Save complete report with truncate/write/close. Preserve interrupted caller.
checkpoint:
    push af
    push bc
    push de
    push hl
    push ix
    push iy
    call clock_read
    ld (checkpoint_clock),hl
    ld hl,progress_name
    call save_report
    pop iy
    pop ix
    pop hl
    pop de
    pop bc
    pop af
    ret
save_report:
    ld c,00ah
    ld a,00ah
    rst.lil 08h
    or a,a
    jp z,sd_failed
    ld (save_handle),a
    ld c,a
    ld hl,report
    ld de,report_end-report
    ld a,01bh
    rst.lil 08h
    ld hl,report_end-report
    or a,a
    sbc hl,de
    push af
    ld a,(save_handle)
    ld c,a
    ld a,00bh
    rst.lil 08h
    pop af
    jp nz,sd_failed
    ret
sd_failed:
    ; Do not recursively attempt another failed save or abandon borrowed RAM.
    halt
    jr sd_failed
failed:
    ld a,(failure_code)
    or a,a
    jr nz,failure_marked
    ld a,1
    ld (failure_code),a
failure_marked:
    ld a,(api_ready)
    or a,a
    jr z,fail_saved
    call tx_poll_drain
    cp a,1
    jr z,retain_failure
    call tx_close
fail_saved:
    ld hl,failure_name
    call save_report
    call checkpoint
    ld hl,failure_message
    ld bc,failure_message_end-failure_message
    rst.lil 18h
    ld sp,(saved_sp)
    pop iy
    pop ix
    pop hl
    pop de
    pop bc
    pop af
    ld hl,1
    ret
retain_failure:
    ld hl,failure_name
    call save_report
    call checkpoint
    ; Reporting must not block behind the receiver. Retain all RAM until reset.
retain_loop:
    halt
    jr retain_loop
    INCLUDE "helpers.inc"
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
tx_diag_take: jp 0
magic: DB "UTX1"
api_ready: DB 0
saved_sp: DB 0,0,0
sysvars: DB 0,0,0
record_ptr: DB 0,0,0
source: DB 0,0,0
source_size: DB 0,0,0
new_ticket: DB 0,0,0
waiting_ticket: DB 0,0,0
tickets: DB 0,0,0,0,0,0,0,0,0
ticket_sizes: DB 0,0,0,0,0,0,0,0,0
monitor_accepted: DB 0,0,0
accepted_total: DB 0,0,0
reply_started: DB 0,0,0
started: DB 0,0,0
due: DB 0,0,0
elapsed: DB 0,0,0
mode: DB 0
kind: DB 0
packet_index: DB 0
ticket_slot: DB 0
reply_count: DB 0
busy_replies: DB 0
wanted_token: DB 0
case_rx: DB 0
save_handle: DB 0
file_handle: DB 0
blocks: DB 0
groups: DB 0
check_ptr: DB 0,0,0
report: DB "URXHOST1",1
stage: DB 1
record_count: DB 6
completed: DB 0
case_index: DB 0
report_repeats: DB 1
failure_code: DB 0
baseline_rx: DB 0
checkpoint_clock: DB 0,0,0
last_progress: DB 0,0,0
last_accepted: DB 0,0,0
packets_completed: DB 0,0,0
wire_bytes: DB 0,0,0
    DS 1
records: DS 24*24
report_end:
checks_name: DB "checks.bin",0
intro: DB 22,0,12,"UART0 STOCK-VDP RECEIVER RECOVERY TEST",13,10
    DB "Short: six cases, allow about two minutes (hardware timing unmeasured).",13,10
    DB "Extended: 24 cases, allow eight minutes. No progress for 2 minutes: reset.",13,10
    DB "A stall is FAIL. Keep the last line and return the card even after PASS.",13,10
    DB "Mode 0 stock-style blocking; mode 1 experimental per-byte async.",13,10
    DB "Kind 0 sustained bulk; 1 full duplex; 2 paced transitions.",13,10
intro_end:
setup_pass: DB "Setup PASS: mismatch rejected, matching byte accepted.",13,10
setup_pass_end:
case_label: DB " case (hex), mode/kind "
case_label_end:
verifying: DB "  TX drained; verifying every byte of the final 8192-byte buffer...",13,10
verifying_end:
verify_label: DB "  Receiver verification "
verify_number: DB '1'
    DB "/4 complete",13,10
verify_label_end:
case_pass: DB "  Case PASS; progress saved.",13,10
case_pass_end:
success: DB "UART0 RECOVERY CAMPAIGN PASS",13,10
    DB "This run completed; a rare hardware race is not ruled out.",13,10
success_end:
failure_message: DB "UART0 RECOVERY CAMPAIGN FAIL; preserve reports and return card.",13,10
failure_message_end:
    INCLUDE "packets.inc"
check_buffer: DS 3840
    END
