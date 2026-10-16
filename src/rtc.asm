; Native AgonDev source derived from official MOS v3.0.2: src/rtc.asm
; Upstream ancestry and changes: docs/upstream-origin.md and docs/deviations.md.
;
; Title:	AGON MOS - RTC
; Author:	Dean Belfield
; Created:	09/03/2023
; Last Updated:	05/06/2023
;
; Modinfo:
; 05/06/2023:	System variable rtc_enable now set

			.include "macros.inc"
			.include "equs.inc"

			.ASSUME	ADL = 1

			; zds2gas: DEFINE .STARTUP, SPACE = ROM
			.section .STARTUP,"ax",@progbits
			
			XDEF	__init_rtc
			XDEF	_init_rtc

			XREF	_rtc_enable

; Initialise the real time clock registers
;
__init_rtc:
_init_rtc:		
			PUSH	AF
			LD	A, 1
			LD	(_rtc_enable), A
			POP	AF
			RET

