; Native AgonDev source derived from official MOS v3.0.2: src/macros.inc
; Upstream ancestry and changes: docs/upstream-origin.md and docs/deviations.md.
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
		XREF	_timer0_delay


; Add A to HL (unsigned)
;
.macro zds_ADD8U_HL
			ADD	A, L 
			LD	L, A 
			ADC	A, H
			SUB	L
			LD	H, A 
			.endm

; Set a GPIO register
; Parameters:
; - REG: Register to set
; - VAL: Bit(s) to set (1: set, 0: ignore)
;
.macro zds_SET_GPIO REG,VAL
			IN0	A,(\REG)
			OR	\VAL
			OUT0	(\REG),A
			.endm

; Reset a GPIO register
; Parameters:
; - REG: Register to set
; - VAL: Bit(s) to reset (1: reset, 0: ignore)
;	
.macro zds_RES_GPIO REG,VAL
			PUSH	BC
			LD	A, \VAL
			CPL
			LD	C, A
			IN0	A,(\REG)
			AND	C
			OUT0	(\REG),A
			POP	BC
			.endm

; Get a GPIO register
; Parameters:
; - REG: Register to test
; - VAL: Bit(s) to test
;	
.macro zds_GET_GPIO REG,VAL
			IN0	A,(\REG)
			TST	A, \VAL
			.endm

; Set a TIMER to the value in register BC
; Parameters:
; - TIMER: Timer to set
;
.macro zds_TIMER_SET_BC TIMER
			.if	\TIMER >= 0 && \TIMER <= 5
				LD	A,0x0C
				OUT0	(TMR\TIMER\()_CTL),A
				OUT0	(TMR\TIMER\()_RR_L),C
				OUT0	(TMR\TIMER\()_RR_H),B
			.else
				.error "ZDS ERROR directive reached"
			.endif
			.endm

; Set a timer to the given *constant* value in milliseconds
; Parameters:
; - TIMER:    Timer set set
; - DELAY_MS: Constant delay in milliseconds
;
.macro zds_TIMER_SET TIMER,DELAY_MS
			.if	\DELAY_MS < 1 || \DELAY_MS > 910
				.error "ZDS ERROR directive reached"
			.endif
			LD		BC,MASTERCLOCK / 1000 / 256 * \DELAY_MS
			zds_TIMER_SET_BC	0
			.endm

;Start a timer
; Parameters:
; - TIMER: Timer to start
;
.macro zds_TIMER_START TIMER
			.if	\TIMER >= 0 && \TIMER <= 5
				IN0	A,(TMR\TIMER\()_CTL)
				OR	A,0x03
				OUT0	(TMR\TIMER\()_CTL),A
			.endif
			.endm

; Reset a timer to stop it running
; Leaves the rest of the timer configuration unchanged so it can be restarted
; Parameters:
; - TIMER: Timer to reset
;
.macro zds_TIMER_RESET TIMER
			.if	\TIMER >= 0 && \TIMER <= 5
				IN0	A,(TMR\TIMER\()_CTL)
				AND	A,0b11111100
				OUT0	(TMR\TIMER\()_CTL),A
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
.macro zds_TIMER_EXP_3f_ TIMER
			.if	\TIMER >= 0 && \TIMER <= 5
				IN0	A,(TMR\TIMER\()_CTL)
			.else
				.error "ZDS ERROR directive reached"
			.endif
			RLA
			.endm

; Wait for a timer to count down to zero
; Parameters:
; - TIMER: Timer to wait on
;
.macro zds_TIMER_WAIT TIMER
.Lzds_m_TIMER_WAIT_loop\@:			zds_TIMER_EXP_3f_	\TIMER
			JR		NC,.Lzds_m_TIMER_WAIT_loop\@
			.endm

; Delay for the given (constant) number of milliseconds using *Timer 0*
; Parameters:
; - DELAY_MS: Number of milliseconds to delay
;
; NB: Can wait between 1 and 910 milliseconds based on 18.432MHz clock
;
.macro zds_DELAY_MS DELAY_MS
			.if	\DELAY_MS < 1 || \DELAY_MS > 910
				.error "ZDS ERROR directive reached"
			.endif
			LD	BC,MASTERCLOCK / 1000 / 256 * \DELAY_MS
			PUSH	BC
			CALL	_timer0_delay
			POP	BC
			.endm

; zds2gas: END

.endif
