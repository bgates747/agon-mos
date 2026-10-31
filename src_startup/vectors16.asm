; Maintained native UART variant: src_startup/vectors16.asm; origin: docs/uart0-native-source.md.
;
; Title:	AGON MOS - C Startup Code
; Author:	Copyright (C) 2005 by ZiLOG, Inc.  All Rights Reserved.
; Modified By:	Dean Belfield
; Created:	10/07/2022
; Last Updated:	29/03/2023
;
; Modinfo:
; 11/07/2022:	Added RST_10 code - TX
; 15/07/2022:	Added __vertical_blank_handler
; 24/07/2022:	Added RST_08 code - MOS API and moved Timer2 ISR into here from timer.c
; 25/07/2022:	Runs in STMIX mode
; 03/08/2022:	Added RST handlers, moved interrupt handlers to interrupts.asm
; 08/08/2022:	RST_10 now calls check_CTS before sending
; 17/03/2023:	Added RST_18 code
; 22/03/2023:	Moved putch to serial.asm, renamed serial_PUTCH
; 29/03/2023:	Added support for UART1

			.include "../src/macros.inc"
			.include "../src/equs.inc"

			.extern 	__init
			.extern 	__low_rom

			.global 	_reset
			.global 	__default_nmi_handler
			.global 	__default_mi_handler
			.global 	__nvectors
			.global 	_init_default_vectors
			.global 	__init_default_vectors
			.global 	_set_vector
			.global	__set_vector
			.global	__2nd_jump_table
			.global	__1st_jump_table
			.global	__vector_table

			.extern	_on_crash
			.extern	mos_api
			.extern	UART0_serial_PUTCH
			.extern	uart0_sync_begin,uart0_sync_end
			.extern	SET_AHL24

.equiv NVECTORS, 48; Number of interrupt vectors

; Save Interrupt State
;
.macro SAVEIMASK
			ld	A, I		; Sets parity bit to value of IEF2
			push	AF
			di			; Disable interrupts while loading table
			.endm

; Restore Interrupt State
;
.macro RESTOREIMASK
			pop	AF
			jp	PO, .+5		; Parity bit is IEF2
			ei
			.endm

; Reset and all RST nn's
;
			; Original segment placement: DEFINE .RESET, SPACE = ROM
			.section .RESET,"ax",@progbits

_reset:
_rst0:			di
			stmix
			jp.lil	__init

_rst8:			jp.lil	_rst_08_handler
			.skip 3, 0xff

_rst10:			jp.lil	_rst_10_handler
			.skip 3, 0xff

_rst18:			jp.lil	_rst_18_handler
			.skip 3, 0xff

_rst20:			ret
			.skip 7, 0xff

_rst28:			ret
			.skip 7, 0xff

_rst30:			ret
			.skip 7, 0xff

_rst38:			jp.lil	__rst_38_handler
			.skip 0x29, 0xff

_nmi:			jp.lil	__default_nmi_handler

;
; Startup code
;
			; Original segment placement: DEFINE .STARTUP, SPACE = ROM
			.section .STARTUP,"ax",@progbits

			.assume adl=1

; Number of vectors supported
;
__nvectors:		dw NVECTORS            ; extern unsigned short _num_vectors;

;
; AGON RST handlers
;

; Execute an API command
; Parameters
; - A: The API command to run
;
_rst_08_handler:	call	mos_api
			ret.l

; Output a single character to the ESP32
; Parameters:
; - A: The character
;
_rst_10_handler:	call	UART0_serial_PUTCH
			ret.l

; Write a block of bytes out to the ESP32
; Parameters:
; - HLU: Buffer address
; -  BC: Size of buffer
; -   A: Delimiter (only if BCU = 0)
;
_rst_18_handler:	call	uart0_sync_begin
			ld	E, A 			; Preserve the delimiter
			ld	A, MB			; Check if MBASE is 0
			or	A, A
			call	NZ, SET_AHL24		; No, so create a 24-bit pointer
			ld	A, B			; Check for BC = 0
			or	C 			; Yes, so run in delimited mode?
			jr	Z, _rst_18_handler_1
;
; Standard loop mode
;
_rst_18_handler_0:	ld 	A, (HL)			; Fetch the character
			call	UART0_serial_PUTCH	; Output
			inc 	HL 			; Increment the buffer pointer
			dec	BC 			; Decrement the loop counter
			ld	A, B 			; Is it 0?
			or 	C
			jr	NZ, _rst_18_handler_0	; No, so loop
			call	uart0_sync_end
			ret.l
;
; Delimited mode
;
_rst_18_handler_1:	ld 	A, (HL)			; Fetch the character
			cp 	E 			; Is it the delimiter?
			jr	Z, _rst_18_done		; Yes, so release scope
			call	UART0_serial_PUTCH	; Output
			inc 	HL 			; Increment the buffer pointer
			jr 	_rst_18_handler_1	; Loop

_rst_18_done:		call	uart0_sync_end
			ret.l

; Crash handler
__rst_38_handler:	jp	_on_crash

; Default Non-Maskable Interrupt handler
;
__default_nmi_handler:	retn.lil

; Default Maskable Interrupt handler
;
__default_mi_handler:	ei
			reti.l

; Initialize all potential interrupt vector locations with a known
; default handler.
;
; void _init_default_vectors(void);
;
__init_default_vectors:
_init_default_vectors:	push	AF
			SAVEIMASK
			ld	HL, __default_mi_handler
			ld	A, 0xC3
			ld 	(__2nd_jump_table), A		; Place jp opcode
			ld 	(__2nd_jump_table + 1), HL	; __default_hndlr
			ld 	HL, __2nd_jump_table
			ld	DE, __2nd_jump_table + 4
			ld	BC, NVECTORS * 4 - 4
			ldir
			im	2
			ld 	A, __vector_table >> 8
			ld 	I, A				; Load interrupt vector base
			RESTOREIMASK
			pop	AF
			ret

; Installs a user interrupt handler in the 2nd interrupt vector jump table
;
; void * _set_vector(unsigned int vector, void(*handler)(void));
;
__set_vector:
_set_vector:		push	IY
			ld	IY, 0
			add	IY, SP				; Standard prologue
			push	AF
			SAVEIMASK
			ld	BC, 0				; Clear BC
			ld	B, 2				; Calculate 2nd jump table offset
			ld	C, (IY + 6)			; Vector offset
			mlt	BC				; BC is 2nd jp table offset
			ld	HL, __2nd_jump_table
			add	HL, BC				; HL is location of jp in 2nd jp table
			ld 	(HL), 0xC3			; Place jp opcode just in case
			inc	HL				; HL is jp destination address
			ld	BC, (IY + 9)			; BC is isr address
			ld 	DE, (HL)			; Save previous handler
			ld 	(HL), BC			; Store new isr address
			push	DE
			pop	HL				; Return previous handler
			RESTOREIMASK
			pop	AF
			ld 	SP, IY				; Standard epilogue
			pop	IY
			ret

			; Original segment placement: DEFINE IVJMPTBL, SPACE = RAM
			.section IVJMPTBL,"aw",@nobits

; 2nd Interrupt Vector Jump Table
;  - this table must reside in RAM anywhere in the 16M byte range
;  - each 4-byte entry is a jump to an interrupt handler
;
__2nd_jump_table:	.skip NVECTORS * 4


; Interrupt Vector Table
;  - this segment must be aligned on a 256 byte boundary anywhere below
;    the 64K byte boundry
;  - each 2-byte entry is a 2-byte vector address
;
			; Original segment placement: DEFINE .IVECTS, SPACE = ROM, ALIGN = 0x100
			.section .IVECTS,"ax",@progbits

__vector_table:		dw __1st_jump_table + 0x00
			dw __1st_jump_table + 0x04
			dw __1st_jump_table + 0x08
			dw __1st_jump_table + 0x0c
			dw __1st_jump_table + 0x10
			dw __1st_jump_table + 0x14
			dw __1st_jump_table + 0x18
			dw __1st_jump_table + 0x1c
			dw __1st_jump_table + 0x20
			dw __1st_jump_table + 0x24
			dw __1st_jump_table + 0x28
			dw __1st_jump_table + 0x2c
			dw __1st_jump_table + 0x30
			dw __1st_jump_table + 0x34
			dw __1st_jump_table + 0x38
			dw __1st_jump_table + 0x3c
			dw __1st_jump_table + 0x40
			dw __1st_jump_table + 0x44
			dw __1st_jump_table + 0x48
			dw __1st_jump_table + 0x4c
			dw __1st_jump_table + 0x50
			dw __1st_jump_table + 0x54
			dw __1st_jump_table + 0x58
			dw __1st_jump_table + 0x5c
			dw __1st_jump_table + 0x60
			dw __1st_jump_table + 0x64
			dw __1st_jump_table + 0x68
			dw __1st_jump_table + 0x6c
			dw __1st_jump_table + 0x70
			dw __1st_jump_table + 0x74
			dw __1st_jump_table + 0x78
			dw __1st_jump_table + 0x7c
			dw __1st_jump_table + 0x80
			dw __1st_jump_table + 0x84
			dw __1st_jump_table + 0x88
			dw __1st_jump_table + 0x8c
			dw __1st_jump_table + 0x90
			dw __1st_jump_table + 0x94
			dw __1st_jump_table + 0x98
			dw __1st_jump_table + 0x9c
			dw __1st_jump_table + 0xa0
			dw __1st_jump_table + 0xa4
			dw __1st_jump_table + 0xa8
			dw __1st_jump_table + 0xac
			dw __1st_jump_table + 0xb0
			dw __1st_jump_table + 0xb4
			dw __1st_jump_table + 0xb8
			dw __1st_jump_table + 0xbc

; 1st Interrupt Vector Jump Table
;  - this table must reside in the first 64K bytes of memory
;  - each 4-byte entry is a jump to the 2nd jump table plus offset
;
__1st_jump_table:	jp __2nd_jump_table + 0x00
			jp __2nd_jump_table + 0x04
			jp __2nd_jump_table + 0x08
			jp __2nd_jump_table + 0x0c
			jp __2nd_jump_table + 0x10
			jp __2nd_jump_table + 0x14
			jp __2nd_jump_table + 0x18
			jp __2nd_jump_table + 0x1c
			jp __2nd_jump_table + 0x20
			jp __2nd_jump_table + 0x24
			jp __2nd_jump_table + 0x28
			jp __2nd_jump_table + 0x2c
			jp __2nd_jump_table + 0x30
			jp __2nd_jump_table + 0x34
			jp __2nd_jump_table + 0x38
			jp __2nd_jump_table + 0x3c
			jp __2nd_jump_table + 0x40
			jp __2nd_jump_table + 0x44
			jp __2nd_jump_table + 0x48
			jp __2nd_jump_table + 0x4c
			jp __2nd_jump_table + 0x50
			jp __2nd_jump_table + 0x54
			jp __2nd_jump_table + 0x58
			jp __2nd_jump_table + 0x5c
			jp __2nd_jump_table + 0x60
			jp __2nd_jump_table + 0x64
			jp __2nd_jump_table + 0x68
			jp __2nd_jump_table + 0x6c
			jp __2nd_jump_table + 0x70
			jp __2nd_jump_table + 0x74
			jp __2nd_jump_table + 0x78
			jp __2nd_jump_table + 0x7c
			jp __2nd_jump_table + 0x80
			jp __2nd_jump_table + 0x84
			jp __2nd_jump_table + 0x88
			jp __2nd_jump_table + 0x8c
			jp __2nd_jump_table + 0x90
			jp __2nd_jump_table + 0x94
			jp __2nd_jump_table + 0x98
			jp __2nd_jump_table + 0x9c
			jp __2nd_jump_table + 0xa0
			jp __2nd_jump_table + 0xa4
			jp __2nd_jump_table + 0xa8
			jp __2nd_jump_table + 0xac
			jp __2nd_jump_table + 0xb0
			jp __2nd_jump_table + 0xb4
			jp __2nd_jump_table + 0xb8
			jp __2nd_jump_table + 0xbc

			; zds2gas: END
