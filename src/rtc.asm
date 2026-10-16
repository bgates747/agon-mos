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

			.assume adl=1

			; zds2gas: DEFINE .STARTUP, SPACE = ROM
			.section .STARTUP,"ax",@progbits

			.global	__init_rtc
			.global	_init_rtc

			.extern	_rtc_enable

; Initialise the real time clock registers
;
__init_rtc:
_init_rtc:
			push	AF
			ld	A, 1
			ld	(_rtc_enable), A
			pop	AF
			ret

