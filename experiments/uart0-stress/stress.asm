; Stock-VDP pause / ordered GP replies while async TX is active.
; No UART register, interrupt vector, keyboard callback or timer takeover.
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
    ld hl,intro
    ld bc,intro_end-intro
    rst.lil 18h
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
    ld de,magic
    ld b,4
magic_loop:
    ld a,(de)
    cp a,(hl)
    jp nz,failed
    inc hl
    inc de
    djnz magic_loop
    ld a,(hl)
    cp a,1
    jp nz,failed
    inc hl
    ld a,(hl)
    cp a,1
    jp c,api_missing        ; Diagnostic epochs require ABI minor >=1.
    inc hl
    ld a,(hl)
    cp a,46
    jp c,api_missing
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
    push hl
    ld hl,(hl)
    ld (diagnostics),hl
    pop hl
    inc hl
    inc hl
    inc hl
    ld hl,(hl)
    ld (tx_diag_take+1),hl
    ld a,1
    ld (api_installed),a
    ld hl,preflight
    ld bc,preflight_end-preflight
    rst.lil 18h
    ld hl,setup
    ld bc,setup_end-setup
    rst.lil 18h
    ; Prove that a deliberately bad byte yields FAIL and a good byte PASS.
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
    ; Setup and historical boot diagnostics must not be blamed on a trial.
    call tx_diag_take
    or a,a
    jp nz,failed
    ld (baseline_diagnostics),hl
    ld hl,baseline_label
    ld bc,baseline_label_end-baseline_label
    rst.lil 18h
    ld a,(baseline_diagnostics)
    call print_hex_byte
    ld a,13
    rst.lil 10h
    ld a,10
    rst.lil 10h
    ld hl,baseline_name
    ld de,baseline_diagnostics
    ld bc,3
    ld a,2
    rst.lil 08h
    or a,a
    jp nz,failed
    ld hl,preflight_pass
    ld bc,preflight_pass_end-preflight_pass
    rst.lil 18h
    ld hl,records
    ld (record_ptr),hl
    xor a,a
    ld (case_index),a
case_loop:
    ld a,1
    ld (stage),a
    ld a,(case_index)
    add a,'1'
    ld (case_number),a
    ld hl,pause_digits
    ld de,0
    ld a,(case_index)
    ld e,a
    add hl,de
    ld a,(hl)
    ld (pause_number),a
    ld hl,case_label
    ld bc,case_label_end-case_label
    rst.lil 18h
    call tx_diag_take
    or a,a
    jp nz,failed
    xor a,a
    ld (observed),a
    ld (busy_replies),a
    ld (sequence_error),a
    ld a,0feh
    ld (last_token),a
    ld ix,(sysvars)
    ld (ix+037h),a
    ld a,(case_index)
    ld hl,packet0
    ld bc,packet0_end-packet0
    ld de,0
    or a,a
    jr z,selected
    ld hl,packet1
    ld bc,packet1_end-packet1
    ld de,1
    cp a,1
    jr z,selected
    ld hl,packet2
    ld bc,packet2_end-packet2
    ld de,4
    cp a,2
    jr z,selected
    ld hl,packet3
    ld bc,packet3_end-packet3
    ld de,8
selected:
    ld (source),hl
    ld (source_size),bc
    ld a,e
    ld iy,(record_ptr)
    ld (iy+0),a
    ld (iy+1),32
    call clock_read
    ld (started),hl
    call tx_open
    or a,a
    jp nz,failed
    call tx_reserve
    or a,a
    jp nz,failed
    ld (ticket),hl
    ex de,hl
    ld hl,(source)
    ld bc,(source_size)
    call tx_publish
    or a,a
    jp nz,failed
observe:
    call observe_reply
    call tx_poll_drain
    cp a,1
    jr z,observe
    or a,a
    jp nz,failed
    ld de,(ticket)
    call tx_status
    or a,a
    jp nz,failed
    ld a,b
    cp a,4
    jp nz,failed
    ld (accepted),hl
    ld de,(source_size)
    or a,a
    sbc hl,de
    jp nz,failed
    ld de,(ticket)
    call tx_reap
    or a,a
    jp nz,failed
    call tx_close
    or a,a
    jp nz,failed
    ; Source is released and UART TEMT before a reply timeout can report FAIL.
    ; Never abandon borrowed RAM when CTS holds an open session blocked.
    call clock_read
    ld (reply_started),hl
wait_last:
    call observe_reply
    ld a,(sequence_error)
    or a,a
    jp nz,record_case
    ld a,(observed)
    cp a,32
    jr z,record_case
    call clock_read
    ld de,(reply_started)
    or a,a
    sbc hl,de
    ld de,2400
    or a,a
    sbc hl,de
    jr c,wait_last
    ld a,2
    ld (sequence_error),a
record_case:
    call clock_read
    ld de,(started)
    or a,a
    sbc hl,de
    ld iy,(record_ptr)
    ld (iy+7),hl
    ld hl,(accepted)
    ld (iy+4),hl
    ld a,(observed)
    ld (iy+2),a
    ld a,(busy_replies)
    ld (iy+3),a
    ld a,(sequence_error)
    ld (iy+12),a
    ld a,(last_token)
    ld (iy+13),a
    call tx_diag_take
    or a,a
    jp nz,failed
    ld (case_diagnostics),hl
    ld iy,(record_ptr)
    ld a,(case_diagnostics)
    ld (iy+10),a
    ld a,(case_diagnostics+1)
    ld (iy+11),a
    ld a,(sequence_error)
    or a,a
    jp nz,failed
    ld a,(busy_replies)
    or a,a
    jp z,failed
    ld a,(case_diagnostics)
    ld (report_errors),a
    or a,a
    jp nz,failed
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
    ld (report_errors),a
    or a,a
    jp nz,failed
    ld hl,case_pass
    ld bc,case_pass_end-case_pass
    rst.lil 18h
    ld iy,(record_ptr)
    ld de,16
    add iy,de
    ld (record_ptr),iy
    ld a,(case_index)
    inc a
    ld (case_index),a
    cp a,4
    jp nz,case_loop
    ld hl,cleanup
    ld bc,cleanup_end-cleanup
    rst.lil 18h
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
observe_reply:
    ld ix,(sysvars)
    ld a,(ix+037h)
    ld hl,last_token
    cp a,(hl)
    ret z
    ld (hl),a
    ld b,a
    ld a,(observed)
    add a,16
    cp a,b
    jr nz,bad_sequence
    ld a,(observed)
    cp a,32
    jr nc,bad_sequence
    inc a
    ld (observed),a
    ; Count only replies for which queue/TEMT is still BUSY afterwards.
    call tx_poll_drain
    cp a,1
    ret nz
    ld a,(busy_replies)
    inc a
    ld (busy_replies),a
    ret
bad_sequence:
    ld a,1
    ld (sequence_error),a
    ret
clock_read:
    ; An atomic snapshot; never reset or take over the MOS timer.
    ld a,i
    push af
    di
    ld ix,(sysvars)
    ld hl,(ix+0)
    pop af
    jp po,clock_masked
    ei
clock_masked:
    ret
print_hex_byte:
    push af
    rrca
    rrca
    rrca
    rrca
    and a,15
    call print_hex_digit
    pop af
    and a,15
print_hex_digit:
    add a,'0'
    cp a,':'
    jr c,print_hex_emit
    add a,7
print_hex_emit:
    rst.lil 10h
    ret
reset_gp:
    ld ix,(sysvars)
    ld (ix+037h),2
    ret
wait_gp:
    ld ix,(sysvars)
    ld bc,0ffffffh
wait_gp_loop:
    ld a,(ix+037h)
    cp a,2
    ret c
    dec bc
    push bc
    pop hl
    ld de,0
    or a,a
    sbc hl,de
    jr nz,wait_gp_loop
    jp failed
verify_payload:
    ld a,2
    ld (stage),a
    ld hl,reset_flag
    ld bc,reset_flag_end-reset_flag
    rst.lil 18h
    ld hl,checks_name
    ld c,1
    ld a,00ah
    rst.lil 08h
    or a,a
    jp z,failed
    ld (file_handle),a
    ld a,32
    ld (blocks),a
verify_block:
    ld a,(file_handle)
    ld c,a
    ld hl,check_buffer
    ld de,3840
    ld a,01ah
    rst.lil 08h
    ld hl,3840
    or a,a
    sbc hl,de
    jp nz,failed
    ld hl,check_buffer
    ld (check_ptr),hl
    ld a,64
    ld (groups),a
verify_group:
    ld hl,(check_ptr)
    ld bc,60
    rst.lil 18h
    ; Four comparisons per GP barrier keep this untimed parser workload small.
    call reset_gp
    ld hl,reply
    ld bc,reply_end-reply
    rst.lil 18h
    call wait_gp
    or a,a
    jp nz,failed
    ld hl,(check_ptr)
    ld de,60
    add hl,de
    ld (check_ptr),hl
    ld a,(groups)
    dec a
    ld (groups),a
    jr nz,verify_group
    ld a,(blocks)
    dec a
    ld (blocks),a
    ; Every eight blocks = 2,048 compared bytes, outside timed work.
    and a,7
    jr nz,verify_more
    ld a,(blocks)
    srl a
    srl a
    srl a
    ld b,a
    ld a,'4'
    sub a,b
    ld (verify_number),a
    ld hl,verify_label
    ld bc,verify_label_end-verify_label
    rst.lil 18h
verify_more:
    ld a,(blocks)
    or a,a
    jp nz,verify_block
    ld a,(file_handle)
    ld c,a
    ld a,00bh
    rst.lil 08h
    xor a,a
    ret
api_missing:
    ld hl,api_required
    ld bc,api_required_end-api_required
    rst.lil 18h
    jp failed
failed:
    ld a,(api_installed)
    or a,a
    jr z,save_failure
    ; An API failure with an open session must retain its source to TEMT.
    ; This may wait for explicit reset if CTS is permanently blocked.
    call tx_poll_drain
    cp a,1
    jr z,failed
    call tx_close
save_failure:
    ld hl,failure_name
    ld de,report
    ld bc,report_end-report
    ld a,2
    rst.lil 08h
    ld hl,failure_message
    ld bc,failure_message_end-failure_message
    rst.lil 18h
failed_hold:
    halt
    jr failed_hold

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
api_installed: DB 0
saved_sp: DB 0,0,0
sysvars: DB 0,0,0
diagnostics: DB 0,0,0
baseline_diagnostics: DB 0,0,0
case_diagnostics: DB 0,0,0
ticket: DB 0,0,0
source: DB 0,0,0
source_size: DB 0,0,0
started: DB 0,0,0
reply_started: DB 0,0,0
accepted: DB 0,0,0
record_ptr: DB 0,0,0
case_index: DB 0
observed: DB 0
busy_replies: DB 0
sequence_error: DB 0
last_token: DB 0
file_handle: DB 0
blocks: DB 0
groups: DB 0
check_ptr: DB 0,0,0
report: DB "UART0ST1",1
stage: DB 0
record_count: DB 4
report_errors: DB 0
records: DS 4*16
report_end:
magic: DB "UTX1"
checks_name: DB "checks.bin",0
result_name: DB "stress.dat",0
failure_name: DB "failure.dat",0
baseline_name: DB "baseline.dat",0
success: DB "UART0 STRESS FIXTURE PASS",13,10
    DB "Software test only: physical CTS margin remains unmeasured.",13,10
success_end:
intro: DB 22,0,12,"UART0 PAUSE / FULL-DUPLEX TEST",13,10
    DB "Allow about one minute; hardware timing is unmeasured.",13,10
    DB "If this takes longer than 2 minutes, something is wrong.",13,10
    DB "Report the last progress line; a stall is not PASS.",13,10
intro_end:
preflight: DB "Setup: discover MOS API and check receiver verification...",13,10
preflight_end:
preflight_pass: DB "Setup PASS: bad-byte detection and good-byte check.",13,10
preflight_pass_end:
case_label: DB "Case "
case_number: DB '1'
    DB "/4: pause "
pause_number: DB '0'
    DB " frames; send 8192 bytes + 32 replies...",13,10
case_label_end:
pause_digits: DB "0148"
verifying: DB "  Ordered replies PASS; TX drained; checking receiver bytes...",13,10
verifying_end:
verify_label: DB "  Receiver verification "
verify_number: DB '1'
    DB "/4 complete",13,10
verify_label_end:
case_pass: DB "  Case PASS",13,10
case_pass_end:
failure_message: DB "UART0 STRESS FAIL - reset required; return card for inspection.",13,10
failure_message_end:
baseline_label: DB "RX flags before trials (saved in baseline.dat): 0x"
baseline_label_end:
api_required: DB "Requires UART0 MOS API 1.1; install packaged MOS, not /MOS.bin.",13,10
api_required_end:
    INCLUDE "packets.inc"
check_buffer: DS 3840
    END
