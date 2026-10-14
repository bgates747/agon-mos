; Isolated RAM experiment; restores UART vector before any MOS output/SD I/O.
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
    ld a,8
    rst.lil 08h
    ld (sysvars),ix
    ld hl,intro
    ld bc,intro_end-intro
    xor a,a
    rst.lil 18h
    ld hl,setup
    ld bc,setup_end-setup
    call mos_send
    call reset_gp
    ld hl,mismatch_probe
    ld bc,mismatch_probe_end-mismatch_probe
    call mos_send
    ld a,1
    call wait_gp
    call reset_gp
    ld hl,match_probe
    ld bc,match_probe_end-match_probe
    call mos_send
    xor a,a
    call wait_gp
    ld hl,records
    ld (record_ptr),hl
    xor a,a
    ld (repeat),a
round:
    xor a,a
    ld (case_index),a
case_loop:
    ld a,(case_index)
    ld b,a
    ld a,(repeat)
    and a,1
    ld a,b
    jr z,forward
    ld a,4
    sub a,b
forward:
    ld (mode),a
    xor a,a
    ld (kind),a
phase:
    ld a,(repeat)
    add a,'1'
    ld (progress_repeat),a
    ld a,(mode)
    add a,'0'
    ld (progress_mode),a
    ld a,(kind)
    add a,'0'
    ld (progress_kind),a
    ld hl,progress
    ld bc,progress_end-progress
    call mos_send
    call select_driver
    call install
    xor a,a
    ld (work),a
    ld (work+1),a
    ld (work+2),a
    ld (irqs),a
    ld (irqs+1),a
    ld (irqs+2),a
    ld (late),a
    call clock
    ld (started),hl
    ld (due),hl
    ld a,(kind)
    or a,a
    jr nz,paced
    ld a,3
    ld (remaining),a
bulk:
    ld hl,bulk_packet
    ld bc,bulk_packet_end-bulk_packet
    call send_packet
    ld a,(remaining)
    dec a
    ld (remaining),a
    jr nz,bulk
    call drain
    jr measured
paced:
    ld a,60
    ld (remaining),a
paced_next:
    call clock
    ld de,(due)
    or a,a
    sbc hl,de
    jr c,pace_work
    ld de,2
    or a,a
    sbc hl,de
    jr c,pace_ready
    ld a,(late)
    inc a
    ld (late),a
pace_ready:
    ld hl,pace_packet
    ld bc,pace_packet_end-pace_packet
    call send_packet
    call drain
    ld hl,(due)
    ld de,2
    add hl,de
    ld (due),hl
    ld a,(remaining)
    dec a
    ld (remaining),a
    jr nz,paced_next
pace_finish:
    call clock
    ld de,(due)
    or a,a
    sbc hl,de
    jr nc,measured
    call useful
    jr pace_finish
pace_work:
    call useful
    jr paced_next
measured:
    call clock
    ld de,(started)
    or a,a
    sbc hl,de
    ld (elapsed),hl
    call get_error
    ld (errors),a
    call api_close
    or a,a
    jp nz,failed
    call restore
    ; Integrity work is outside the measured interval.
    call verify_receiver
    ld ix,(record_ptr)
    ld a,(repeat)
    ld (ix+0),a
    ld a,(mode)
    ld (ix+1),a
    ld a,(kind)
    ld (ix+2),a
    ld hl,(elapsed)
    ld (ix+3),hl
    ld hl,(work)
    ld (ix+6),hl
    ld hl,(irqs)
    ld (ix+9),hl
    ld a,(late)
    ld (ix+12),a
    ld a,(errors)
    ld (ix+13),a
    or a,a
    jp nz,failed
    ld hl,(record_ptr)
    ld de,16
    add hl,de
    ld (record_ptr),hl
    ld a,(kind)
    xor a,1
    ld (kind),a
    jp nz,phase
    ld a,(case_index)
    inc a
    ld (case_index),a
    cp a,5
    jp c,case_loop
    ld a,(repeat)
    inc a
    ld (repeat),a
    cp a,3
    jp c,round
    ld hl,cleanup
    ld bc,cleanup_end-cleanup
    call mos_send
    ld hl,result_name
    ld de,report
    ld bc,report_end-report
    ld a,2
    rst.lil 08h
    or a,a
    jp nz,failed
    ld hl,success
    ld bc,success_end-success
    call mos_send
    ld sp,(saved_sp)
    pop iy
    pop ix
    pop hl
    pop de
    pop bc
    pop af
    ld hl,0
    ret
; One immutable packet outstanding; reap only after queue and wire drain.
send_packet:
    ld a,(mode)
    or a,a
    jp z,mos_send
    push hl
    push bc
    call api_reserve
    or a,a
    jp nz,failed
    ld (ticket),hl
    ex de,hl
    pop bc
    pop hl
    call api_publish
    or a,a
    jp nz,failed
    ; For bulk, keep one packet outstanding while CPU does useful work.
    jp drain
drain:
    ld a,(mode)
    or a,a
    ret z
wait_drain:
    call useful
    call api_drain
    or a,a
    jr nz,wait_drain
    ld hl,(ticket)
    ld de,0
    or a,a
    sbc hl,de
    ret z
    ld de,(ticket)
    call api_reap
    or a,a
    jp nz,failed
    ld hl,0
    ld (ticket),hl
    ret
useful:
    push bc
    ld b,32
work_loop:
    ld hl,(work)
    inc hl
    ld (work),hl
    djnz work_loop
    pop bc
    ret
clock:
    ld a,i
    push af
    di
    ld ix,(sysvars)
    ld hl,(ix+0)
    pop af
    jp po,clock_done
    ei
clock_done:
    ret
select_driver:
    di
    ld a,(mode)
    or a,a
    jr nz,driver_index
    inc a
driver_index:
    dec a
    ld hl,driver_table
    ld de,24
    or a,a
    jr z,table_ready
select_next:
    add hl,de
    dec a
    jr nz,select_next
table_ready:
    ld de,api_open+1
    ld b,7
copy_pointer:
    push bc
    ld bc,3
    ldir
    inc de
    pop bc
    djnz copy_pointer
    ld de,get_error+1
    ld bc,3
    ldir
    ei
    ret
api_open: jp 0
api_reserve: jp 0
api_publish: jp 0
api_drain: jp 0
api_reap: jp 0
api_close: jp 0
irq_jump: jp 0
get_error: ld a,(0)
    ret
install:
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
    call api_open
    or a,a
    jp nz,failed
    ret
restore:
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
    ret
counted_isr:
    push hl
    ld hl,(irqs)
    inc hl
    ld (irqs),hl
    pop hl
    jp irq_jump
mos_send:
    xor a,a
    rst.lil 18h
    ret
verify_receiver:
    ld hl,verify_reset
    ld bc,verify_reset_end-verify_reset
    call mos_send
    ld hl,verify_data
    ld (check_ptr),hl
    ld a,184
    ld (check_groups),a
verify_group:
    ld bc,60
    ld a,(check_groups)
    cp a,1
    jr nz,verify_send
    ld bc,45
verify_send:
    push bc
    ld hl,(check_ptr)
    call mos_send
    pop bc
    ld hl,(check_ptr)
    add hl,bc
    ld (check_ptr),hl
    call reset_gp
    ld hl,verify_reply
    ld bc,verify_reply_end-verify_reply
    call mos_send
    xor a,a
    call wait_gp
    ld a,(check_groups)
    dec a
    ld (check_groups),a
    jr nz,verify_group
    ret
check_ptr: DB 0,0,0
check_groups: DB 0
reset_gp:
    ld ix,(sysvars)
    ld (ix+037h),0feh
    ret
wait_gp:
    ld (wanted),a
    ld bc,0ffffffh
wait_reply:
    ld ix,(sysvars)
    ld a,(wanted)
    cp a,(ix+037h)
    ret z
    dec bc
    push bc
    pop hl
    ld de,0
    or a,a
    sbc hl,de
    jr nz,wait_reply
    jp failed
failed:
    ld hl,failure_name
    ld de,report
    ld bc,report_end-report
    ld a,2
    rst.lil 08h
hold:
    halt
    jr hold
saved_sp: DB 0,0,0
saved_vector: DB 0,0,0
saved_ier: DB 0
sysvars: DB 0,0,0
record_ptr: DB 0,0,0
ticket: DB 0,0,0
started: DB 0,0,0
due: DB 0,0,0
elapsed: DB 0,0,0
work: DB 0,0,0
irqs: DB 0,0,0
repeat: DB 0
case_index: DB 0
mode: DB 0
kind: DB 0
remaining: DB 0
late: DB 0
errors: DB 0
wanted: DB 0
report: DB "UAB1",1,30,16,0
records: DS 30*16
report_end:
result_name: DB "ab.dat",0
failure_name: DB "ab-fail.dat",0
intro: DB 12,"UART0 controlled A/B: blocking, default, grouped, chunk, OTIRX",13,10
    DB "30 phases; allow two minutes. If stalled, report the last phase.",13,10
intro_end:
progress: DB "A/B repeat "
progress_repeat: DB '0'
    DB " mode "
progress_mode: DB '0'
    DB " phase "
progress_kind: DB '0',13,10
progress_end:
success: DB "UART0 A/B PASS",13,10
success_end:
    INCLUDE "native-packets.inc"
    INCLUDE "native-table.inc"
    END
