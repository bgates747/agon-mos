; Isolated NMI-001 proof. Fixed synthetic guest, eight yields, then reset.
; No public ABI and no writes to a live NMI gateway from application code.
.assume adl=1
.text
.global _nmi_proof_dispatch, _nmi_proof_run, _nmi_read_watchdog
.global _nmi_proof_reset_only, _nmi_proof_state
.extern __default_nmi_handler, _clock, _nmi_proof_host

WDT_CTL .equ 0x93
WDT_RELOAD .equ 0x94
GUEST_BANK .equ 5
GUEST_BASE .equ 0x050000
GUEST_SPS .equ 0xef00
GUEST_GUARD .equ 0x05eef8
GUEST_COUNT .equ 0x05ec00
GUEST_SP_PROBE .equ 0x05ec02
WITNESS .equ 0x05ed00
STARTING .equ 1
RUNNING .equ 2
HOST .equ 3
RECOVERY .equ 4

_nmi_read_watchdog:
    in0 a,(WDT_CTL)
    ret

_nmi_proof_run:
    di
    ld (host_stack),sp
    ld a,STARTING
    ld (_nmi_proof_state),a
    ld hl,guest_code
    ld de,GUEST_BASE
    ld bc,guest_end-guest_code
    ldir
    ld hl,GUEST_GUARD
    ld de,GUEST_GUARD+1
    ld bc,15
    ld (hl),0xa9
    ldir
    ld hl,0
    ld (previous_count),hl
    ld (GUEST_COUNT),hl
    ld (GUEST_SP_PROBE),hl
    xor a
    ld (yields),a

    ld sp,proof_stack_top
    stmix
    ld a,GUEST_BANK
    ld mb,a
    ld a,0xc2                 ; F92 NMI, SCLK, 2^22 cycles.
    out0 (WDT_CTL),a
    ld a,RUNNING
    ld (_nmi_proof_state),a
    jp.sis 0

_nmi_proof_dispatch:
    push af
    ld a,(_nmi_proof_state)
    or a
    jp z,default_nmi
    cp RUNNING
    jp nz,nmi_failure
    ; IEF2 is the incoming guest IRQ enable flag. Nothing above changes it.
    ld a,i
    jp pe,nmi_failure
    ld a,mb
    cp GUEST_BANK
    jp nz,nmi_failure
    push bc
    push de
    push hl
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

    ld ix,0
    add ix,sp
    ; Ten three-byte pushes precede the CPU's three-byte mixed Z80 frame.
    ld a,(ix+30)
    cp 2
    jp nz,nmi_failure
    ld hl,0
    ld l,(ix+31)
    ld h,(ix+32)
    ld de,guest_store-guest_code
    or a
    sbc hl,de
    jr z,pc_before_store
    ld hl,0
    ld l,(ix+31)
    ld h,(ix+32)
    ld de,guest_loop-guest_code
    or a
    sbc hl,de
    jr z,pc_after_store
    ld hl,0
    ld l,(ix+31)
    ld h,(ix+32)
    ld de,guest_branch-guest_code
    or a
    sbc hl,de
    jp nz,nmi_failure
pc_after_store:
    ld de,(GUEST_COUNT)
    jr check_count
pc_before_store:
    ld de,(GUEST_COUNT)
    inc de
check_count:
    ld a,(ix+18)
    cp e
    jp nz,nmi_failure
    ld a,(ix+19)
    cp d
    jp nz,nmi_failure
    ld hl,0
    ld l,e
    ld h,d
    ld de,(previous_count)
    push hl
    or a
    sbc hl,de
    pop hl
    jp z,nmi_failure
    ld (previous_count),hl
    ld a,(ix+28)
    cp 0x7d
    jp nz,nmi_failure
    bit 0,(ix+27)
    jp z,nmi_failure
    ld a,(ix+1)
    cp 0x31
    jp nz,nmi_failure
    bit 0,(ix+0)
    jp z,nmi_failure
    ld hl,primary_checks
check_register:
    ld a,(hl)
    cp 0xff
    jr z,registers_ok
    ld de,0
    ld e,a
    push ix
    pop iy
    add iy,de
    inc hl
    ld a,(iy)
    cp (hl)
    jp nz,nmi_failure
    inc hl
    jr check_register
registers_ok:
    ld hl,(GUEST_SP_PROBE)
    ld a,l
    cp GUEST_SPS & 255
    jp nz,nmi_failure
    ld a,h
    cp GUEST_SPS >> 8
    jp nz,nmi_failure
    ld hl,GUEST_GUARD
    ld b,16
guard_byte:
    ld a,(hl)
    cp 0xa9
    jp nz,nmi_failure
    inc hl
    djnz guard_byte

    ld (parked_stack),sp
    ld a,HOST
    ld (_nmi_proof_state),a
    xor a
    ld mb,a
    ld sp,(host_stack)
    ; Synthetic ADL NMI frame. Its continuation runs on the CLI long stack.
    ld hl,host_continuation
    push hl
    dec sp
    ld hl,0
    add hl,sp
    ld (hl),3
    di
    retn.l

default_nmi:
    pop af
    jp __default_nmi_handler

host_continuation:
    call reload_watchdog
    ld hl,(_clock)
    ld (initial_tick),hl
    ei
wait_vblank:
    halt
    ld hl,(_clock)
    ld de,(initial_tick)
    or a
    sbc hl,de
    jr z,wait_vblank
    ld a,(yields)
    inc a
    ld (yields),a
    ld hl,0
    ld l,a
    push hl
    call _nmi_proof_host
    pop bc
    di
    ld a,(yields)
    cp 8
    jr z,armed_exit
    call reload_watchdog
    ld sp,(parked_stack)
    ld a,GUEST_BANK
    ld mb,a
    ld a,RUNNING
    ld (_nmi_proof_state),a
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
    retn.l                     ; DI configured IEF2=0 before guest return.

armed_exit:
    ld hl,WITNESS
    ld (hl),'N'
    inc hl
    ld (hl),'M'
    inc hl
    ld (hl),'I'
    inc hl
    ld (hl),8
    inc hl
    ld (hl),8

nmi_failure:
    di
    ld a,RECOVERY
    ld (_nmi_proof_state),a
_nmi_proof_reset_only:
    ; May enter before RAM/stack initialization. No CALL or stack use.
    xor a
    ld mb,a
    ld a,0x83                  ; Remain enabled, select chip reset and 2^18.
    out0 (WDT_CTL),a
    ld a,0xa5
    out0 (WDT_RELOAD),a
    ld a,0x5a
    out0 (WDT_RELOAD),a
reset_pending:
    halt
    jr reset_pending

reload_watchdog:
    ld a,0xa5
    out0 (WDT_RELOAD),a
    ld a,0x5a
    out0 (WDT_RELOAD),a
    ret

primary_checks:
    .db 24,0x47,25,0xa9,21,0xc2,22,0x58
    .db 15,0x36,16,0xb7,12,0xd4,13,0x62
    .db 9,0x14,10,0xb2,6,0xa3,7,0x7d,3,0x2c,4,0x5e
    .db 0xff

.assume adl=0
guest_code:
    di
    ld sp,GUEST_SPS
    ld (GUEST_SP_PROBE-GUEST_BASE),sp
    ld bc,0xb214
    ld de,0x7da3
    ld hl,0x5e2c
    exx
    ld a,0x31
    scf
    ex af,af'
    ld bc,0xa947
    ld de,0x58c2
    ld ix,0xb736
    ld iy,0x62d4
    ld hl,0
    ld a,0x7d
    scf
guest_loop:
    inc hl
guest_store:
    ld (GUEST_COUNT-GUEST_BASE),hl
guest_branch:
    jr guest_loop
guest_end:

.bss
_nmi_proof_state: .ds 1
yields: .ds 1
previous_count: .ds 3
initial_tick: .ds 3
host_stack: .ds 3
parked_stack: .ds 3
proof_stack: .ds 256
proof_stack_top:
