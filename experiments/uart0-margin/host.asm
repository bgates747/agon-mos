; Native ZDS II borrowed-source UART0 receiver-margin experiment.
.assume adl=1
    DEFINE UART_ENTRY, SPACE=ROM
    SEGMENT UART_ENTRY
    XDEF app_entry
app_entry:
    jp start
    DS 60
    DB "MOS",0,1,"UTC1"
result_name: DB "margin.dat",0
    DS 5
baseline_name: DB "margin-base.dat",0
failure_name: DB "margin-fail.dat",0
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
    ld a,0e7h
    call wait_value
    jr nc,diagnostic_ready
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
wait_drain:
    call tx_poll_drain
    cp a,1
    jr z,wait_drain
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
    cp a,48
    jr nz,field_loop
    call tx_diag_take
    or a,a
    jp nz,failed
    ld a,l
    ld hl,(record_ptr)
    dec hl
    ld (hl),a
    or a,a
    jp nz,failed
    ld a,(case_index)
    inc a
    ld (case_index),a
    cp a,42
    jp nz,case_loop
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
failed:
    ld a,(api_installed)
    or a,a
    jr z,save_failure
failed_drain:
    call tx_poll_drain
    cp a,1
    jr z,failed_drain
    call tx_close
save_failure:
    ld hl,failure_name
    ld de,report
    ld bc,report_end-report
    ld a,2
    rst.lil 08h
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
saved_sp: DB 0,0,0
sysvars: DB 0,0,0
ticket: DB 0,0,0
record_ptr: DB 0,0,0
baseline: DB 0,0,0
wait_started: DB 0,0,0
case_index: DB 0
low_nibble: DB 0
wanted: DB 0
hello: DB 23,0,0e7h,2
arm: DB 23,0,0e7h,0,64,5
query: DB 23,0,0e7h,1,0,0
report: DB "URMHOST1",1
stage: DB 0
    DB 42,0
records: DS 42*48
report_end:
intro: DB 22,0,12,"UART0 RECEIVER MARGIN EXPERIMENT",13,10
    DB "42 threshold/pause trials; allow up to two minutes.",13,10
    DB "Any longer: record the last case and reset. A stall is not PASS.",13,10
    DB "Normal CTS stays enabled; failures at tight thresholds are evidence.",13,10
intro_end:
missing: DB "SKIP: requires the staged UART0 CTS diagnostic VDP.",13,10
missing_end:
failure: DB "UART0 MARGIN TRANSPORT FAIL - returning after source drains.",13,10
failure_end:
success: DB "UART0 MARGIN DATA SAVED; inspect receiver CRC/FIFO evidence on host.",13,10
    DB "Saved data alone is not a CTS margin PASS.",13,10
success_end:
    INCLUDE "cases.inc"
    END
