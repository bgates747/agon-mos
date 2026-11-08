; AgonDev C -> core boundary. The core owns both register banks while running.
.assume adl=1
.section .text,"ax",@progbits
.include "core_exports.inc"
.global _emu_reset,_emu_run,_emu_step,_trace_char
.global _emu_reset_cmos,_emu_run_cmos,_emu_step_cmos
.global _emu_reset_apple,_emu_run_apple
_emu_reset_apple:
    ld hl,CORE_APPLE_RESET
    jp core_call
_emu_run_apple:
    ld hl,CORE_APPLE_RUN
    jp core_call
_emu_reset:
    ld hl,CORE_RESET
    jp core_call
_emu_run:
    ld hl,CORE_RUN
    jp core_call
_emu_step:
    ld hl,CORE_STEP
    jp core_call
_emu_reset_cmos:
    ld hl,CORE_CMOS_RESET
    jp core_call
_emu_run_cmos:
    ld hl,CORE_CMOS_RUN
    jp core_call
_emu_step_cmos:
    ld hl,CORE_CMOS_STEP
core_call:
    push af              ; ADL24 OK: F,A,00, private host stack frame.
    ld a,i               ; P/V captures host IFF2 for restoration.
    di
    push af
    ld a,mb
    push af
    ld a,8
    ld mb,a
    push bc              ; ADL24 OK: each pair occupies low,high,upper bytes.
    push de
    push hl
    push ix
    push iy
    push hl
    pop ix               ; Target entry address; original IX remains saved.
    exx
    push bc
    push de
    push hl
    exx
    ex af,af'
    push af
    ex af,af'
    call call_ix
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
    pop hl
    pop de
    pop bc
    pop af
    ld mb,a
    pop af
    jp po,was_disabled
    ei
was_disabled:
    pop af
    ret
call_ix:
    jp (ix)

; Physical-only VDP printer diagnostic; C argument is a24-bit int.
_trace_char:
    push ix
    ld ix,0
    add ix,sp
    ; Physical-only diagnostics: print one character to USB, no screen write.
    ; Foreground only after renderer completion. Printer is off at entry/exit.
    ld a,2
    rst.lil 0x10
    ld a,1
    rst.lil 0x10
    ld a,(ix+6)
    rst.lil 0x10
    ld a,3
    rst.lil 0x10
    pop ix
    ret

.global _disk_cache_ready
_disk_cache_ready:
    ld hl,661018
    jp core_call

.global _native_decode_track
_native_decode_track:
    push af
    push bc
    push de
    push hl
    push ix
    push iy
    call 0x0a7004
    pop iy
    pop ix
    pop hl
    pop de
    pop bc
    pop af
    ret
