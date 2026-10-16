; Native AgonDev source derived from official MOS v3.0.2: src/macros.inc
; Upstream ancestry and changes: docs/upstream-origin.md and docs/deviations.md.
; DEV-009: guard repeated includes; SDK hardware aliases are checked by the build.
.ifndef AGON_MOS_SRC_MACROS_INC
.set AGON_MOS_SRC_MACROS_INC,1
;
; Title:	AGON MOS - Useful Macros
; Author:	Dean Belfield
; Created:	15/07/2022
; Last Updated:	08/06/2023
;
; Modinfo:
; 08/08/2022:	Added GET_GPIO
; 09/09/2022:	Commented
; 08/06/2023:	Add timer-related macros

; Used by macros
		.include "equs.inc"

; References to functions called by Macros
		.extern	_timer0_delay


; Add A to HL (unsigned)
;
.macro ADD8U_HL
			add	A, L
			ld	L, A
			adc	A, H
			sub	L
			ld	H, A
			.endm

; Set a GPIO register
; Parameters:
; - REG: Register to set
; - VAL: Bit(s) to set (1: set, 0: ignore)
;
.macro SET_GPIO REG,VAL
			in0	A,(\REG)
			or	\VAL
			out0	(\REG),A
			.endm

; Reset a GPIO register
; Parameters:
; - REG: Register to set
; - VAL: Bit(s) to reset (1: reset, 0: ignore)
;
.macro RES_GPIO REG,VAL
			push	BC
			ld	A, \VAL
			cpl
			ld	C, A
			in0	A,(\REG)
			and	C
			out0	(\REG),A
			pop	BC
			.endm

; Get a GPIO register
; Parameters:
; - REG: Register to test
; - VAL: Bit(s) to test
;
.macro GET_GPIO REG,VAL
			in0	A,(\REG)
			tst	A, \VAL
			.endm

; Set a TIMER to the value in register BC
; Parameters:
; - TIMER: Timer to set
;
.macro TIMER_SET_BC TIMER
			.if	\TIMER >= 0 && \TIMER <= 5
				ld	A,0x0C
				out0	(TMR\TIMER\()_CTL),A
				out0	(TMR\TIMER\()_RR_L),C
				out0	(TMR\TIMER\()_RR_H),B
			.else
				.error "ZDS ERROR directive reached"
			.endif
			.endm

; Set a timer to the given *constant* value in milliseconds
; Parameters:
; - TIMER:    Timer set set
; - DELAY_MS: Constant delay in milliseconds
;
.macro TIMER_SET TIMER,DELAY_MS
			.if	\DELAY_MS < 1 || \DELAY_MS > 910
				.error "ZDS ERROR directive reached"
			.endif
			ld		BC,MASTERCLOCK / 1000 / 256 * \DELAY_MS
			TIMER_SET_BC	0
			.endm

;Start a timer
; Parameters:
; - TIMER: Timer to start
;
.macro TIMER_START TIMER
			.if	\TIMER >= 0 && \TIMER <= 5
				in0	A,(TMR\TIMER\()_CTL)
				or	A,0x03
				out0	(TMR\TIMER\()_CTL),A
			.endif
			.endm

; Reset a timer to stop it running
; Leaves the rest of the timer configuration unchanged so it can be restarted
; Parameters:
; - TIMER: Timer to reset
;
.macro TIMER_RESET TIMER
			.if	\TIMER >= 0 && \TIMER <= 5
				in0	A,(TMR\TIMER\()_CTL)
				and	A,0b11111100
				out0	(TMR\TIMER\()_CTL),A
			.else
				.error "ZDS ERROR directive reached"
			.endif
			.endm

; Test if the given timer has expired
; Parameters:
; - TIMER: Timer to test
; Output:
; - AF: Carry Flag set or clear depending on whether timer has expired
;
.macro TIMER_EXP TIMER
			.if	\TIMER >= 0 && \TIMER <= 5
				in0	A,(TMR\TIMER\()_CTL)
			.else
				.error "ZDS ERROR directive reached"
			.endif
			rla
			.endm

; Wait for a timer to count down to zero
; Parameters:
; - TIMER: Timer to wait on
;
.macro TIMER_WAIT TIMER
.LTIMER_WAIT_loop\@:			TIMER_EXP	\TIMER
			jr		NC,.LTIMER_WAIT_loop\@
			.endm

; Delay for the given (constant) number of milliseconds using *Timer 0*
; Parameters:
; - DELAY_MS: Number of milliseconds to delay
;
; NB: Can wait between 1 and 910 milliseconds based on 18.432MHz clock
;
.macro DELAY_MS DELAY_MS
			.if	\DELAY_MS < 1 || \DELAY_MS > 910
				.error "ZDS ERROR directive reached"
			.endif
			ld	BC,MASTERCLOCK / 1000 / 256 * \DELAY_MS
			push	BC
			call	_timer0_delay
			pop	BC
			.endm

; zds2gas: END

.endif
