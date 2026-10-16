; Native AgonDev source derived from official MOS v3.0.2: src/gpio.asm
; Upstream ancestry and changes: docs/upstream-origin.md and docs/deviations.md.
;
; Title:	AGON MOS - gpio code
; Author:	Dean Belfield
; Created:	15/07/2022
; Last Updated:	24/07/2022
;
; Modinfo:
; 24/07/2022:	Moved SWITCH_A to misc.asm

			.include "macros.inc"
			.include "equs.inc"

			.assume adl=1

			; zds2gas: DEFINE .STARTUP, SPACE = ROM
			.section .STARTUP,"ax",@progbits

			.global	GPIOB_SETMODE
			.extern	SWITCH_A

;  A: Mode
;  B: Pins
;
GPIOB_SETMODE:		call	SWITCH_A
			dw	GPIOB_M0	; Output
			dw	GPIOB_M1	; Input
			dw	GPIOB_M2	; Open Drain IO
			dw	GPIOB_M3	; Open Source IO
			dw	GPIOB_M4	; Interrupt, Dual Edge
			dw	GPIOB_M5	; Alt Function
			dw	GPIOB_M6	; Interrupt, Active Low
			dw	GPIOB_M7	; Interrupt, Active High
			dw	GPIOB_M8	; Interrupt, Falling Edge
			dw	GPIOB_M9	; Interrupt, Rising Edge

; Output
;
GPIOB_M0:		RES_GPIO PB_DDR,  B
			RES_GPIO PB_ALT1, B
			RES_GPIO PB_ALT2, B
			ret

; Input
;
GPIOB_M1:		SET_GPIO PB_DDR,  B
			RES_GPIO PB_ALT1, B
			RES_GPIO PB_ALT2, B
			ret

; Open Drain IO
;
GPIOB_M2:		RES_GPIO PB_DDR,  B
			SET_GPIO PB_ALT1, B
			RES_GPIO PB_ALT2, B
			ret

; Open Source IO
;
GPIOB_M3:		SET_GPIO PB_DDR,  B
			SET_GPIO PB_ALT1, B
			RES_GPIO PB_ALT2, B
			ret

; Interrupt, Dual Edge
;
GPIOB_M4:		SET_GPIO PB_DR,   B
			RES_GPIO PB_DDR,  B
			RES_GPIO PB_ALT1, B
			RES_GPIO PB_ALT2, B
			ret

; Alt Function
;
GPIOB_M5:		SET_GPIO PB_DDR,  B
			RES_GPIO PB_ALT1, B
			SET_GPIO PB_ALT2, B
			ret

; Interrupt, Active Low
;
GPIOB_M6:		RES_GPIO PB_DR,   B
			RES_GPIO PB_DDR,  B
			SET_GPIO PB_ALT1, B
			SET_GPIO PB_ALT2, B
			ret


; Interrupt, Active High
;
GPIOB_M7:		SET_GPIO PB_DR,   B
			RES_GPIO PB_DDR,  B
			SET_GPIO PB_ALT1, B
			SET_GPIO PB_ALT2, B
			ret


; Interrupt, Falling Edge
;
GPIOB_M8:		RES_GPIO PB_DR,   B
			SET_GPIO PB_DDR,  B
			SET_GPIO PB_ALT1, B
			SET_GPIO PB_ALT2, B
			ret

; Interrupt, Rising Edge
;
GPIOB_M9:		SET_GPIO PB_DR,   B
			SET_GPIO PB_DDR,  B
			SET_GPIO PB_ALT1, B
			SET_GPIO PB_ALT2, B
			ret
