; Maintained native UART variant: src/misc.asm; origin: docs/uart0-native-source.md.
;
; Title:	AGON MOS - Miscellaneous helper functions
; Author:	Dean Belfield
; Created:	24/07/2022
; Last Updated: 15/04/2023
;
; Modinfo:
; 03/08/2022:	Added SET_AHL24 and SET_ADE24
; 10/08/2022:	Optimised SET_ADE24
; 08/11/2022:	Fixed return value bug in exec16
; 19/11/2022:	Added exec24 and params for exec16/24 functions
; 09/03/2023:	Added wait_timer0
; 20/03/2023:	Function exec24 now preserves MB
; 15/04/2023:	Added GET_AHL24

			.include "macros.inc"
			.include "equs.inc"

			.assume adl=1

			; Original segment placement: DEFINE .STARTUP, SPACE = ROM
			.section .STARTUP,"ax",@progbits

			.global	SWITCH_A
			.global	SET_AHL24
			.global	FIX_HLU24
			.global	FIX_HLU24_no_mb_check
			.global	SET_ADE24
			.global	SET_ABC24
			.global	SET_AIX24

			.global	__exec16
			.global	__exec24
			.global	__wait_timer0

			.global	_exec16
			.global	_exec24
			.global	_wait_timer0
			.global	_timer0_delay

			.extern	uart0_return_fence
			.extern	_callSM

; Switch on A - lookup table immediately after call
;  A: Index into lookup table
;
SWITCH_A:		ex	(SP), HL		; Swap HL with the contents of the top of the stack
			add	A, A			; Multiply A by two
			ADD8U_HL 			; Add to HL (macro)
			ld	A, (HL)			; follow the call. Fetch an address from the
			inc	HL 			; table.
			ld	H, (HL)
			ld	L, A
			ex	(SP), HL		; Swap this new address back, restores HL
			ret				; Return program control to this new address

; Set the MSB of HL (U) to A
;
SET_AHL24:		push	HL
			ld	HL, 2
			add	HL, SP
			ld	(HL), A
			pop	HL
			ret

; Optionally set MSB of HL(U) to MB, if needed
; Sets U of HLU to MB if MB != 0 and U is not already set
;
FIX_HLU24:		ld	A, MB
			or	A
			ret	Z
; Get the MSB of HLU in A (pushing HLU to the stack)
FIX_HLU24_no_mb_check:	push	HL
			ld	HL, 2
			add	HL, SP
			ld	A, (HL)
			or 	A, A
; top byte of HLU (on stack) already set so return
			jr	NZ, 1f
; set top byte of HLU (on stack) to MB
			ld	A, MB
			ld	(HL), A
1:			pop	HL
			ret

; Set the MSB of DE (U) to A
;
SET_ADE24:		ex	DE, HL
			push	HL
			ld	HL, 2
			add	HL, SP
			ld	(HL), A
			pop	HL
			ex	DE, HL
			ret

; Set the MSB of BC (U) to A
; can't use EX BC, HL as that instruction doesn't exist
SET_ABC24:		push	HL	; push current HL to stack to save it
			push	BC
			ld	HL, 2
			add	HL, SP
			ld	(HL), A
			pop	BC
			pop	HL	; restore HL
			ret

; Set the MSB of IX (U) to A
;
SET_AIX24:		push	HL
			push	IX
			ld	HL, 2
			add	HL, SP
			ld	(HL), A
			pop	IX
			pop	HL
			ret

; Execute a program in RAM
; int * _exec24(UINT24 address, char * params)
; Params:
; - address: The 24-bit address to call
; - params: 24-bit pointer to the params buffer
;
; This function will call the 24 bit address and keep the eZ80 in ADL mode
; The called function must do a RET and take care of preserving registers
;
__exec24:
_exec24:		push 	IY
			ld	IY, 0
			add	IY, SP		; Standard prologue
			push 	AF		; Stack any registers being used
			push	DE
			push	IX
			ld	A, MB 		; Preserve the MBASE register
			push	AF
			xor	A
			ld	MB, A		; Clear MBASE so API calls from this ADL binary don't identify process as Z80-mode
			ld	DE, (IY+6)	; Get the address
			ld	A, (IY+8)	; And the high byte for the code segment
			ld	HL, (IY+9)	; Load HLU with the pointer to the params
;
; Write out a short subroutine "JP (DE)" to RAM
;
			ld	IX, _callSM	; Storage for the self modified routine
			ld	(IX + 0), 0xC3	; JP llhhuu
			ld	(IX + 1), E
			ld	(IX + 2), D
			ld	(IX + 3), A
;
			jr	_execSM		; Save some bytes, jump to _exec16 to finish the call

; Execute a program in RAM
; int * _exec16(UINT24 address, char * params)
; Params:
; - address: The 24-bit address to call
; - params: 24-bit pointer to the params buffer
;
; This function will call the 24 bit address and switch the eZ80 into Z80 mode (ADL=0)
; The called function must do a RET.LIS (49h, C9h) and take care of preserving registers
;
__exec16:
_exec16:		push 	IY
			ld	IY, 0
			add	IY, SP		; Standard prologue
			push 	AF		; Stack any registers being used
			push	DE
			push	IX
			ld	A, MB		; Preserve the MBASE register
			push	AF
			ld	DE, (IY+6)	; Get the address
			ld	A, (IY+8)	; And the high byte for the code segment
			ld	MB, A		; Set the MBASE register
			ld	HL, (IY+9)	; Load HLU with the pointer to the params
;
; Write out a short subroutine "CALL.IS (DE): RET" to RAM
;

			ld	IX, _callSM	; Storage for the self modified routine
			ld	(IX + 0), 0x49	; CALL.IS llhh
			ld	(IX + 1), 0xCD
			ld	(IX + 2), E
			ld	(IX + 3), D
			ld	(IX + 4), 0xC9	; RET
;
_execSM:		call	uart0_return_fence
			call	_callSM		; Call the subroutine
;
			call	uart0_return_fence
			pop	AF		; Restore the MBASE register
			ld	MB, A
			pop	IX
			pop	DE
			pop 	AF
			ld	SP, IY          ; Standard epilogue
			pop	IY
			ret

; Wait for timer0 to hit 0
;
__wait_timer0:
_wait_timer0:		push	AF
			push	BC
			in0	A, (TMR0_CTL)	; Enable the timer
			or	3
			out0	(TMR0_CTL), A
1:			in0	B, (TMR0_DR_L)	; Fetch the counter L
			in0 	A, (TMR0_DR_H)	; And the counter H
			or	B
			jr	NZ, 1b
			pop	BC
			pop	AF
			ret

_timer0_delay:
			pop		HL
			pop		BC
			push		BC
			TIMER_SET_BC	0
			TIMER_START	0
			TIMER_WAIT	0
			jp		(HL)

; zds2gas: END
