; Native ZDS II borrowed-source UART0 controlled receiver-recovery diagnostic.
.assume adl=1
    DEFINE UART_ENTRY, SPACE=ROM
    SEGMENT UART_ENTRY
    XDEF app_entry
app_entry:
    jp start
    DS 60
    DB "MOS",0,1,"URF1"
result_name: DB "race.dat",0
    DS 7
baseline_name: DB "race-base.dat",0
    DS 2
failure_name: DB "race-fail.dat",0
    DS 2
progress_name: DB "race-step.dat",0
    DS 2
expected_variant: DB 0ffh       ; offset137: 0 before, 1 fixed, FF CLI autodetect
start:
    push af
    push bc
    push de
    push hl
    push ix
    push iy
    ld (saved_sp),sp
    xor a,a
    ld (api_installed),a
    ld (completed),a
    ld a,8
    ld (stage),a
    ld hl,intro
    ld bc,intro_end-intro
    rst.lil 18h
    ld a,8
    rst.lil 08h
    ld (sysvars),ix
    ; Exercise replacement twice before arming the receiver or borrowing RAM.
    ; MOS SAVE creates a NEW file; it cannot update a progress checkpoint.
    call checkpoint
    call checkpoint
    ld hl,storage_ready
    ld bc,storage_ready_end-storage_ready
    rst.lil 18h
    ld bc,01300h
    ld a,050h
    rst.lil 08h
    or a,a
    jp nz,failed
    ld (discovery+1),hl
    call discovery
    ld de,magic
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
    ld (api_installed),a
    call reset_gp
    ld hl,hello
    ld bc,4
    rst.lil 18h
    ld a,0ffh
    call wait_value
    jr c,missing_diagnostic
    cp a,0d8h
    jr z,variant_ready
    cp a,0d9h
    jr nz,missing_diagnostic
variant_ready:
    sub a,0d8h
    ld (receiver_fixed),a
    ld b,a
    ld a,(expected_variant)
    cp a,0ffh
    jr z,diagnostic_ready
    cp a,b
    jr z,diagnostic_ready
missing_diagnostic:
    ld hl,missing
    ld bc,missing_end-missing
    rst.lil 18h
    ld a,3
    ld (stage),a
    ld hl,result_name
    ld de,report
    ld bc,report_end-report
    ld a,2
    rst.lil 08h
    ld hl,0
    jp finish
 diagnostic_ready:
    call tx_diag_take
    or a,a
    jp nz,failed
    ld (baseline),hl
    ld hl,baseline_name
    ld de,baseline
    ld bc,3
    ld a,2
    rst.lil 08h
    or a,a
    jp nz,failed
    ld hl,records
    ld (record_ptr),hl
    xor a,a
    ld (case_index),a
case_loop:
    ld a,1
    ld (stage),a
    call checkpoint
    ld a,(case_index)
    ld hl,0
    ld l,a
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    add hl,hl
    ld de,labels
    add hl,de
    ld bc,0
    xor a,a
    rst.lil 18h
    ld a,(case_index)
    ld de,0
    ld e,a
    ld hl,cases
    add hl,de
    add hl,de
    ld a,(hl)
    ld (arm+4),a
    inc hl
    ld a,(hl)
    ld (arm+5),a
    call tx_diag_take
    or a,a
    jp nz,failed
    call reset_gp
    ld hl,arm
    ld bc,6
    rst.lil 18h
    ld a,0e1h
    call wait_value
    jp c,failed
    ld a,4
    ld (stage),a
    ; RAM-only phase: FatFS timestamps send VDP RTC commands. No disk or
    ; screen I/O from ARM until the receiver's DONE reply is observed.
    call tx_open
    or a,a
    jp nz,failed
    call tx_reserve
    or a,a
    jp nz,failed
    ld (ticket),hl
    ex de,hl
    ld hl,payload
    ld bc,payload_end-payload
    call tx_publish
    or a,a
    jp nz,failed
    call clock_read
    ld (drain_started),hl
    ld a,5
    ld (stage),a
wait_drain:
    call tx_poll_drain
    cp a,1
    jr nz,drain_finished
    call clock_read
    ld de,(drain_started)
    or a,a
    sbc hl,de
    ld de,2400
    or a,a
    sbc hl,de
    jr c,wait_drain
    jp failed
drain_finished:
    or a,a
    jp nz,failed
    ld de,(ticket)
    call tx_status
    or a,a
    jp nz,failed
    ld a,b
    cp a,4
    jp nz,failed
    ld de,payload_end-payload
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
    ld a,0e3h
    call wait_value
    jp c,failed
    ld a,2
    ld (stage),a
    call checkpoint
    ld hl,reading
    ld bc,reading_end-reading
    rst.lil 18h
    xor a,a
    ld (query+4),a
field_loop:
    xor a,a
    ld (query+5),a
    call nibble
    jp c,failed
    ld (low_nibble),a
    ld a,1
    ld (query+5),a
    call nibble
    jp c,failed
    rlca
    rlca
    rlca
    rlca
    ld b,a
    ld a,(low_nibble)
    or a,b
    ld hl,(record_ptr)
    ld (hl),a
    inc hl
    ld (record_ptr),hl
    ld a,(query+4)
    inc a
    ld (query+4),a
    cp a,80
    jr nz,field_continue
    ld a,6
    ld (stage),a
    call checkpoint
    ld a,(query+4)
field_continue:
    cp a,160
    jr nz,field_loop
    ld hl,(record_ptr)
    ld de,97
    or a,a
    sbc hl,de                 ; record[63] must match the HELLO variant
    ld a,(receiver_fixed)
    cp a,(hl)
    jp nz,failed
    call tx_diag_take
    or a,a
    jp nz,failed
    ld a,l
    ld hl,(record_ptr)
    ld de,99
    or a,a
    sbc hl,de
    ld (hl),a
    or a,a
    jp nz,failed
    ld a,(case_index)
    inc a
    ld (case_index),a
    ld (completed),a
    ld a,7
    ld (stage),a
    call checkpoint
    ld hl,case_saved
    ld bc,case_saved_end-case_saved
    rst.lil 18h
    ld a,(case_index)
    cp a,2
    jp nz,case_loop
    xor a,a
    ld (stage),a
    call checkpoint
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
    ld hl,0
    jp finish
nibble:
    call reset_gp
    ld hl,query
    ld bc,6
    rst.lil 18h
    ld a,0ffh
    call wait_value
    ret c
    cp a,16
    jr nc,bad_nibble
    or a,a
    ret
bad_nibble:
    scf
    ret
reset_gp:
    ld ix,(sysvars)
    ld (ix+037h),0feh
    ret
wait_value:
    ld (wanted),a
    call clock_read
    ld (wait_started),hl
wait_loop:
    ld ix,(sysvars)
    ld a,(ix+037h)
    ld b,a
    ld a,(wanted)
    cp a,0ffh
    jr z,wait_nibble
    cp a,b
    jr z,wait_ok
    jr wait_time
wait_nibble:
    ld a,b
    cp a,0feh
    jr nz,wait_ok
wait_time:
    call clock_read
    ld de,(wait_started)
    or a,a
    sbc hl,de
    ld de,600
    or a,a
    sbc hl,de
    jr c,wait_loop
    scf
    ret
wait_ok:
    ld a,b
    or a,a
    ret
clock_read:
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
checkpoint:
    push af
    push bc
    push de
    push hl
    push ix
    push iy
    ld hl,progress_name
    ld c,00ah                 ; FA_WRITE | FA_CREATE_ALWAYS
    ld a,00ah                 ; MOS fopen, not MOS SAVE (CREATE_NEW)
    rst.lil 08h
    or a,a
    jp z,sd_failed
    ld (save_handle),a
    ld c,a
    ld hl,report
    ld de,report_end-report
    ld a,01bh                 ; MOS fwrite; DE returns the actual count
    rst.lil 08h
    ld hl,report_end-report
    or a,a
    sbc hl,de
    push af
    ld a,(save_handle)
    ld c,a
    ld a,00bh                 ; MOS fclose commits directory/data
    rst.lil 08h
    pop af
    jp nz,sd_failed
    pop iy
    pop ix
    pop hl
    pop de
    pop bc
    pop af
    ret
sd_failed:
    ; No recursive save attempt. Retain source RAM if a transfer is active.
    ld a,(api_installed)
    or a,a
    jr z,sd_message
    call tx_poll_drain
    cp a,1
    jr z,sd_hold
    call tx_close
sd_message:
    ld hl,storage_failure
    ld bc,storage_failure_end-storage_failure
    rst.lil 18h
    ld hl,1
    jp finish
sd_hold:
    halt
    jr sd_hold
failed:
    ld hl,failure_name
    ld de,report
    ld bc,report_end-report
    ld a,2
    rst.lil 08h
    or a,a
    jp nz,sd_failed
    call checkpoint
    ld a,(api_installed)
    or a,a
    jr z,save_failure
    call tx_poll_drain
    cp a,1
    jr z,sd_hold
    call tx_close
save_failure:
    ld hl,failure
    ld bc,failure_end-failure
    rst.lil 18h
    ld hl,1
finish:
    ld sp,(saved_sp)
    pop iy
    pop ix
    pop de
    pop de
    pop bc
    pop af
    ret
; HL is the return code; discard the originally saved HL stack slot.
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
api_installed: DB 0
save_handle: DB 0
receiver_fixed: DB 0
saved_sp: DB 0,0,0
sysvars: DB 0,0,0
ticket: DB 0,0,0
record_ptr: DB 0,0,0
baseline: DB 0,0,0
wait_started: DB 0,0,0
drain_started: DB 0,0,0
case_index: DB 0
low_nibble: DB 0
wanted: DB 0
hello: DB 23,0,0e6h,2
arm: DB 23,0,0e6h,0,0,0
query: DB 23,0,0e6h,1,0,0
report: DB "URFHOST1",1
stage: DB 0
    DB 2
completed: DB 0
records: DS 2*160
report_end:
intro: DB 22,0,12,"UART0 RECEIVER SYNCHRONIZATION REGRESSION",13,10
    DB "Two cases: no trigger, then widened ISR/reader timing window.",13,10
    DB "Allow two minutes. No progress for two minutes: record last line and reset.",13,10
    DB "Forced diagnostic failure is not a natural stock-firmware failure.",13,10
intro_end:
storage_ready: DB "Setup PASS: repeated checkpoint writes; starting receiver checks.",13,10
storage_ready_end:
storage_failure: DB "FAIL: checkpoint open/write failed; preserve the card and reports.",13,10
storage_failure_end:
reading: DB "Payload drained; reading receiver evidence (two halves)...",13,10
reading_end:
case_saved: DB "Case data saved; checking the next case or final result...",13,10
case_saved_end:
missing: DB "SKIP: expected matched baseline/repaired diagnostic VDP is not installed.",13,10
missing_end:
failure: DB "UART0 RACE TRANSPORT FAIL; preserve reports.",13,10
failure_end:
success: DB "UART0 RACE DATA SAVED; receiver evidence must be validated.",13,10
success_end:
    INCLUDE "cases.inc"
    END
