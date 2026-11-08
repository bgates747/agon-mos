; SPDX-License-Identifier: MIT
; Original application leaf. Ordinary AgonDev C CALL, BYTE result A.
; Three-byte stack slots: after push IX, first argument is at IX+6.
; ADL1 caller; OFF has no I/O/MOS/PRT or callback invocation.
; ON calls only the pinned owner app recorder; no new leaf scratch or direct I/O.
 .assume adl=1
 .section .text
 .global _aw_begin,_aw_wait
; Optional owner recorder; undefined/default0 emits the original leaf only.
 .ifndef AW_CPU_ACCOUNTING
 .set AW_CPU_ACCOUNTING,0
 .endif
 .if AW_CPU_ACCOUNTING
 .extern _agon_cpu_entry,_agon_cpu_foreground
 .endif
_aw_begin:
 ld a,1
 jr entry
_aw_wait:
 xor a
entry:
 push ix
 ld ix,0
 add ix,sp
 push bc
 push de
 push hl
 ld b,a
 ld ix,(ix+6)
 ; Validate before DI. A maskable IRQ here returns to the same foreground IFF.
 ld a,i
 jp po,refused
 ld a,mb
 or a
 .if AW_CPU_ACCOUNTING
 jp nz,refused                ; enabled hooks exceed original JR range
 .else
 jr nz,refused
 .endif
 lea hl,ix+0
 ld de,0
 or a
 sbc hl,de
 .if AW_CPU_ACCOUNTING
 jp z,refused                 ; preserve default-OFF original JR bytes
 .else
 jr z,refused
 .endif
 ld hl,(ix+6)
 or a
 sbc hl,de
 jr z,refused
 di
 ld a,b
 or a
 jr z,wait_pass
begin_pass:
 xor a
 ld (ix+1),a
 ld (ix+0),a
 ld a,(hl)
 ld (ix+2),a
 inc hl
 ld a,(hl)
 ld (ix+3),a
 inc hl
 ld a,(hl)
 ld (ix+4),a
 inc hl
 ld a,(hl)
 ld (ix+5),a
 ld (ix+1),1
 ld a,1
 jr enabled_return
wait_pass:
 ld a,(ix+1)
 or a
 jr z,refused_enabled
 xor a
 ld (ix+1),a                 ; one wait consumes this pass; NOT the event
 ld a,(ix+0)
 or a
 jr nz,work
 ld a,(hl)
 cp (ix+2)
 jr nz,work
 inc hl
 ld a,(hl)
 cp (ix+3)
 jr nz,work
 inc hl
 ld a,(hl)
 cp (ix+4)
 jr nz,work
 inc hl
 ld a,(hl)
 cp (ix+5)
 jr nz,work
sleep_return:
 .if AW_CPU_ACCOUNTING
 ld a,6                       ; ACP_HALT_TAKEN, existing DI before restores
 call _agon_cpu_entry
 .endif
 pop hl
 pop de
 pop bc
 pop ix
 ld a,3
 ei
 halt                         ; must be the instruction immediately after EI
 .if AW_CPU_ACCOUNTING
 push af                      ; retain ordinary AW_HALTED result and flags
 ld a,0x86                    ; native A-event ABI, NOT a C argument
 call _agon_cpu_foreground    ; preserves actual incoming return-path IFF
 pop af
 .endif
 ret
work:
 .if AW_CPU_ACCOUNTING
 ld a,7                       ; ACP_AW_WORK, raw branch, existing DI
 call _agon_cpu_entry
 .endif
 ld a,2
 jr enabled_return
refused_enabled:
 xor a
enabled_return:
 pop hl
 pop de
 pop bc
 pop ix
 ei
 ret
refused:
 xor a
 pop hl
 pop de
 pop bc
 pop ix
 ret                          ; no EI: preserves both refused entry IFF states
