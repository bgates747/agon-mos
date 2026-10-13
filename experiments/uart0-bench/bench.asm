; Console8 preparation fixture. Same accepted MOS, no private UART owner.
; All timings are raw MOS clock ticks; verification and SD I/O are untimed.
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
    ld (pair),a
pair_loop:
    xor a,a
    ld (trial),a
trial_loop:
    ld a,1
    ld (stage),a
    ld a,(trial)
    ld b,a
    ld a,(pair)
    xor a,b
    and a,1
    ld (mode),a             ; Alternate AB/BA across pairs.
    call progress_case
    ; Start a fresh observation epoch after untimed progress/setup output.
    call tx_diag_take
    or a,a
    jp nz,failed
    ld hl,0123456h
    ld (work_value),hl
    ld hl,010203h
    ld (work_seed),hl
    ld hl,512
    ld (chunks),hl
    ld hl,0
    ld (overlap),hl
    call clock_read
    ld (started),hl
    ld a,(mode)
    or a,a
    jr nz,async_send
    ; Closed-session RST18 is the existing blocking path on this same ROM.
    ld hl,packet
    ld bc,packet_end-packet
    rst.lil 18h
    ; Both modes include one open; here it permits safe TEMT observation.
    call tx_open
    or a,a
    jp nz,failed
    jr compute
async_send:
    call tx_open
    or a,a
    jp nz,failed
    call tx_reserve
    or a,a
    jp nz,failed
    ld (ticket),hl
    ex de,hl
    ld hl,packet
    ld bc,packet_end-packet
    call tx_publish
    or a,a
    jp nz,failed
compute:
    ld hl,(work_value)
    ld de,(work_seed)
    ld b,0
work_loop:
    add hl,de
    ld a,h
    xor a,l
    ld d,a
    inc e
    djnz work_loop
    ld (work_value),hl
    ld (work_seed),de
    ld a,(mode)
    or a,a
    jr z,next_chunk
    call tx_poll_drain
    or a,a
    jr z,next_chunk
    cp a,1
    jp nz,failed
    ld hl,(overlap)
    ld de,256
    add hl,de
    ld (overlap),hl
next_chunk:
    ld hl,(chunks)
    dec hl
    ld (chunks),hl
    ld a,h
    or a,l
    jr nz,compute
wait_drain:
    call tx_poll_drain
    cp a,1
    jr z,wait_drain
    or a,a
    jp nz,failed
    call clock_read
    ld de,(started)
    or a,a
    sbc hl,de              ; modulo 24-bit raw tick delta
    ld (elapsed),hl
    ld hl,packet_end-packet
    ld (accepted),hl
    ld a,(mode)
    or a,a
    jr z,close_session
    ld de,(ticket)
    call tx_status
    or a,a
    jp nz,failed
    ld a,b
    cp a,4
    jp nz,failed
    ld (accepted),hl
    ld de,(ticket)
    call tx_reap
    or a,a
    jp nz,failed
close_session:
    call tx_close
    or a,a
    jp nz,failed
    ; Every payload byte is compared in the VDP, outside the timing.
    ld hl,verifying
    ld bc,verifying_end-verifying
    rst.lil 18h
    call verify_payload
    or a,a
    jp nz,failed
    call tx_diag_take
    or a,a
    jp nz,failed
    ld (case_diagnostics),hl
    ld iy,(record_ptr)
    ld a,(mode)
    ld (iy+0),a
    ld a,(pair)
    ld (iy+1),a
    ld hl,(elapsed)
    ld (iy+2),hl
    ld hl,(work_value)
    ld (iy+5),hl
    ld hl,(overlap)
    ld (iy+8),hl
    ld hl,(accepted)
    ld (iy+11),hl
    ld a,(case_diagnostics)
    ld (iy+14),a
    ld (report_errors),a
    or a,a
    jp nz,failed
    ld a,(case_diagnostics+1)
    ld (iy+15),a
    ld (iy+16),0
    ld de,17
    add iy,de
    ld (record_ptr),iy
    ld hl,case_pass
    ld bc,case_pass_end-case_pass
    rst.lil 18h
    ld a,(trial)
    inc a
    ld (trial),a
    cp a,2
    jp nz,trial_loop
    ld a,(pair)
    inc a
    ld (pair),a
    cp a,4
    jp nz,pair_loop
    ld hl,cleanup
    ld bc,cleanup_end-cleanup
    rst.lil 18h
    xor a,a
    ld (stage),a
    ld hl,saving
    ld bc,saving_end-saving
    rst.lil 18h
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
progress_case:
    ld a,(pair)
    add a,'1'
    ld (case_number),a
    ld hl,case_label
    ld bc,case_label_end-case_label
    rst.lil 18h
    ld a,(mode)
    or a,a
    ld hl,blocking_label
    ld bc,blocking_label_end-blocking_label
    jr z,progress_send
    ld hl,async_label
    ld bc,async_label_end-async_label
progress_send:
    rst.lil 18h
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
    ei
    ld hl,failure_name
    ld de,report
    ld bc,report_end-report
    ld a,2
    rst.lil 08h
    ld hl,failure_message
    ld bc,failure_message_end-failure_message
    rst.lil 18h
    ld hl,error_label
    ld bc,error_label_end-error_label
    rst.lil 18h
    ld a,(report_errors)
    call print_hex_byte
    ld a,13
    rst.lil 10h
    ld a,10
    rst.lil 10h
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
saved_sp: DB 0,0,0
sysvars: DB 0,0,0
diagnostics: DB 0,0,0
baseline_diagnostics: DB 0,0,0
case_diagnostics: DB 0,0,0
ticket: DB 0,0,0
work_value: DB 0,0,0
work_seed: DB 0,0,0
chunks: DB 0,0,0
overlap: DB 0,0,0
started: DB 0,0,0
elapsed: DB 0,0,0
accepted: DB 0,0,0
record_ptr: DB 0,0,0
pair: DB 0
trial: DB 0
mode: DB 0
file_handle: DB 0
blocks: DB 0
groups: DB 0
check_ptr: DB 0,0,0
report: DB "UART0BN1",1
stage: DB 0
record_count: DB 8
report_errors: DB 0
records: DS 8*17
report_end:
magic: DB "UTX1"
checks_name: DB "checks.bin",0
result_name: DB "bench.dat",0
failure_name: DB "failure.dat",0
baseline_name: DB "baseline.dat",0
success: DB "UART0 BENCH FIXTURE PASS",13,10
success_end:
intro: DB 12,"UART0 TRANSMISSION TEST",13,10
    DB "Allow about one minute; hardware timing is unmeasured.",13,10
    DB "If this takes longer than 2 minutes, something is wrong.",13,10
    DB "Report the last progress line; do not count a stall as PASS.",13,10
intro_end:
preflight: DB "Setup: discover MOS API and check receiver verification...",13,10
preflight_end:
preflight_pass: DB "Setup PASS: bad-byte detection and good-byte check.",13,10
preflight_pass_end:
case_label: DB "Pair "
case_number: DB '1'
    DB "/4: "
case_label_end:
blocking_label: DB "BLOCKING - transmit, compute, drain...",13,10
blocking_label_end:
async_label: DB "ASYNC - transmit, compute, drain...",13,10
async_label_end:
verifying: DB "  Transmission drained; verifying 8192 receiver bytes...",13,10
verifying_end:
verify_label: DB "  Receiver verification "
verify_number: DB '1'
    DB "/4 complete",13,10
verify_label_end:
case_pass: DB "  Case PASS",13,10
case_pass_end:
saving: DB "All 8 cases PASS; saving bench.dat...",13,10
saving_end:
failure_message: DB "UART0 TEST FAIL - report last progress line; reset required.",13,10
failure_message_end:
baseline_label: DB "RX flags before trials (saved in baseline.dat): 0x"
baseline_label_end:
error_label: DB "RX flags observed in failed case: 0x"
error_label_end:
api_required: DB "This test requires UART0 MOS API 1.1: install the new MOS image.",13,10
api_required_end:
    INCLUDE "packets.inc"
check_buffer: DS 3840
    END
