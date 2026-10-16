; Native AgonDev source derived from official MOS v3.0.2: src_startup/vectors16.asm
; Upstream ancestry and changes: docs/upstream-origin.md and docs/deviations.md.
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

			XREF 	__init
			XREF 	__low_rom
			
			XDEF 	_reset
			XDEF 	__default_nmi_handler
			XDEF 	__default_mi_handler
			XDEF 	__nvectors
			XDEF 	_init_default_vectors
			XDEF 	__init_default_vectors
			XDEF 	_set_vector
			XDEF	__set_vector
			XDEF	__2nd_jump_table
			XDEF	__1st_jump_table
			XDEF	__vector_table
			
			XREF	_on_crash
			XREF	mos_api
			XREF	UART0_serial_PUTCH 
			XREF	SET_AHL24

.equiv NVECTORS, 48; Number of interrupt vectors

; Save Interrupt State
;
.macro zds_SAVEIMASK
			LD	A, I		; Sets parity bit to value of IEF2
			PUSH	AF
			DI			; Disable interrupts while loading table 
			.endm

; Restore Interrupt State
;
.macro zds_RESTOREIMASK
			POP	AF
			JP	PO, .+5		; Parity bit is IEF2
			EI
			.endm

; Reset and all RST nn's
;
			; zds2gas: DEFINE .RESET, SPACE = ROM
			.section .RESET,"ax",@progbits

_reset:	
_rst0:			DI
			STMIX
			JP.LIL	__init
		
_rst8:			JP.LIL	_rst_08_handler
			.skip 3, 0xff
		
_rst10:			JP.LIL	_rst_10_handler
			.skip 3, 0xff

_rst18:			JP.LIL	_rst_18_handler
			.skip 3, 0xff
		
_rst20:			RET
			.skip 7, 0xff
		
_rst28:			RET
			.skip 7, 0xff

_rst30:			RET
			.skip 7, 0xff

_rst38:			JP.LIL	__rst_38_handler
			.skip 0x29, 0xff
		
_nmi:			JP.LIL	__default_nmi_handler

;
; Startup code
;
			; zds2gas: DEFINE .STARTUP, SPACE = ROM
			.section .STARTUP,"ax",@progbits

			.ASSUME ADL=1

; Number of vectors supported
;
__nvectors:		DW NVECTORS            ; extern unsigned short _num_vectors;

;	
; AGON RST handlers
;

; Execute an API command
; Parameters
; - A: The API command to run
;
_rst_08_handler:	CALL	mos_api
			RET.L

; Output a single character to the ESP32
; Parameters:
; - A: The character
;
_rst_10_handler:	CALL	UART0_serial_PUTCH
			RET.L

; Write a block of bytes out to the ESP32
; Parameters:
; - HLU: Buffer address
; -  BC: Size of buffer
; -   A: Delimiter (only if BCU = 0)
;
_rst_18_handler:	LD	E, A 			; Preserve the delimiter
			LD	A, MB			; Check if MBASE is 0
			OR	A, A 
			CALL	NZ, SET_AHL24		; No, so create a 24-bit pointer
			LD	A, B			; Check for BC = 0
			OR	C 			; Yes, so run in delimited mode?
			JR	Z, _rst_18_handler_1
;
; Standard loop mode
;
_rst_18_handler_0:	LD 	A, (HL)			; Fetch the character
			CALL	UART0_serial_PUTCH	; Output
			INC 	HL 			; Increment the buffer pointer
			DEC	BC 			; Decrement the loop counter
			LD	A, B 			; Is it 0?
			OR 	C 
			JR	NZ, _rst_18_handler_0	; No, so loop
			RET.L
;
; Delimited mode
;
_rst_18_handler_1:	LD 	A, (HL)			; Fetch the character
			CP 	E 			; Is it the delimiter?
			RET.L	Z 			; Yes, so return
			CALL	UART0_serial_PUTCH	; Output
			INC 	HL 			; Increment the buffer pointer
			JR 	_rst_18_handler_1	; Loop

; Crash handler
__rst_38_handler:	JP	_on_crash

; Default Non-Maskable Interrupt handler
;
__default_nmi_handler:	RETN.LIL

; Default Maskable Interrupt handler
;
__default_mi_handler:	EI
			RETI.L
					
; Initialize all potential interrupt vector locations with a known
; default handler.
;
; void _init_default_vectors(void);
;
__init_default_vectors:
_init_default_vectors:	PUSH	AF
			zds_SAVEIMASK
			LD	HL, __default_mi_handler
			LD	A, 0xC3
			LD 	(__2nd_jump_table), A		; Place jp opcode
			LD 	(__2nd_jump_table + 1), HL	; __default_hndlr
			LD 	HL, __2nd_jump_table
			LD	DE, __2nd_jump_table + 4
			LD	BC, NVECTORS * 4 - 4
			LDIR
			IM	2
			LD 	A, __vector_table >> 8
			LD 	I, A				; Load interrupt vector base
			zds_RESTOREIMASK
			POP	AF
			RET

; Installs a user interrupt handler in the 2nd interrupt vector jump table
;
; void * _set_vector(unsigned int vector, void(*handler)(void));
;
__set_vector:
_set_vector:		PUSH	IY
			LD	IY, 0
			ADD	IY, SP				; Standard prologue
			PUSH	AF
			zds_SAVEIMASK
			LD	BC, 0				; Clear BC
			LD	B, 2				; Calculate 2nd jump table offset
			LD	C, (IY + 6)			; Vector offset
			MLT	BC				; BC is 2nd jp table offset
			LD	HL, __2nd_jump_table
			ADD	HL, BC				; HL is location of jp in 2nd jp table
			LD 	(HL), 0xC3			; Place jp opcode just in case
			INC	HL				; HL is jp destination address
			LD	BC, (IY + 9)			; BC is isr address
			LD 	DE, (HL)			; Save previous handler
			LD 	(HL), BC			; Store new isr address
			PUSH	DE
			POP	HL				; Return previous handler
			zds_RESTOREIMASK
			POP	AF
			LD 	SP, IY				; Standard epilogue
			POP	IY
			RET

			; zds2gas: DEFINE IVJMPTBL, SPACE = RAM
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
			; zds2gas: DEFINE .IVECTS, SPACE = ROM, ALIGN = 0x100
			.section .IVECTS,"ax",@progbits

__vector_table:		DW __1st_jump_table + 0x00
			DW __1st_jump_table + 0x04
			DW __1st_jump_table + 0x08
			DW __1st_jump_table + 0x0c
			DW __1st_jump_table + 0x10
			DW __1st_jump_table + 0x14
			DW __1st_jump_table + 0x18
			DW __1st_jump_table + 0x1c
			DW __1st_jump_table + 0x20
			DW __1st_jump_table + 0x24
			DW __1st_jump_table + 0x28
			DW __1st_jump_table + 0x2c
			DW __1st_jump_table + 0x30
			DW __1st_jump_table + 0x34
			DW __1st_jump_table + 0x38
			DW __1st_jump_table + 0x3c
			DW __1st_jump_table + 0x40
			DW __1st_jump_table + 0x44
			DW __1st_jump_table + 0x48
			DW __1st_jump_table + 0x4c
			DW __1st_jump_table + 0x50
			DW __1st_jump_table + 0x54
			DW __1st_jump_table + 0x58
			DW __1st_jump_table + 0x5c
			DW __1st_jump_table + 0x60
			DW __1st_jump_table + 0x64
			DW __1st_jump_table + 0x68
			DW __1st_jump_table + 0x6c
			DW __1st_jump_table + 0x70
			DW __1st_jump_table + 0x74
			DW __1st_jump_table + 0x78
			DW __1st_jump_table + 0x7c
			DW __1st_jump_table + 0x80
			DW __1st_jump_table + 0x84
			DW __1st_jump_table + 0x88
			DW __1st_jump_table + 0x8c
			DW __1st_jump_table + 0x90
			DW __1st_jump_table + 0x94
			DW __1st_jump_table + 0x98
			DW __1st_jump_table + 0x9c
			DW __1st_jump_table + 0xa0
			DW __1st_jump_table + 0xa4
			DW __1st_jump_table + 0xa8
			DW __1st_jump_table + 0xac
			DW __1st_jump_table + 0xb0
			DW __1st_jump_table + 0xb4
			DW __1st_jump_table + 0xb8
			DW __1st_jump_table + 0xbc

; 1st Interrupt Vector Jump Table
;  - this table must reside in the first 64K bytes of memory
;  - each 4-byte entry is a jump to the 2nd jump table plus offset
;
__1st_jump_table:	JP __2nd_jump_table + 0x00
			JP __2nd_jump_table + 0x04
			JP __2nd_jump_table + 0x08
			JP __2nd_jump_table + 0x0c
			JP __2nd_jump_table + 0x10
			JP __2nd_jump_table + 0x14
			JP __2nd_jump_table + 0x18
			JP __2nd_jump_table + 0x1c
			JP __2nd_jump_table + 0x20
			JP __2nd_jump_table + 0x24
			JP __2nd_jump_table + 0x28
			JP __2nd_jump_table + 0x2c
			JP __2nd_jump_table + 0x30
			JP __2nd_jump_table + 0x34
			JP __2nd_jump_table + 0x38
			JP __2nd_jump_table + 0x3c
			JP __2nd_jump_table + 0x40
			JP __2nd_jump_table + 0x44
			JP __2nd_jump_table + 0x48
			JP __2nd_jump_table + 0x4c
			JP __2nd_jump_table + 0x50
			JP __2nd_jump_table + 0x54
			JP __2nd_jump_table + 0x58
			JP __2nd_jump_table + 0x5c
			JP __2nd_jump_table + 0x60
			JP __2nd_jump_table + 0x64
			JP __2nd_jump_table + 0x68
			JP __2nd_jump_table + 0x6c
			JP __2nd_jump_table + 0x70
			JP __2nd_jump_table + 0x74
			JP __2nd_jump_table + 0x78
			JP __2nd_jump_table + 0x7c
			JP __2nd_jump_table + 0x80
			JP __2nd_jump_table + 0x84
			JP __2nd_jump_table + 0x88
			JP __2nd_jump_table + 0x8c
			JP __2nd_jump_table + 0x90
			JP __2nd_jump_table + 0x94
			JP __2nd_jump_table + 0x98
			JP __2nd_jump_table + 0x9c
			JP __2nd_jump_table + 0xa0
			JP __2nd_jump_table + 0xa4
			JP __2nd_jump_table + 0xa8
			JP __2nd_jump_table + 0xac
			JP __2nd_jump_table + 0xb0
			JP __2nd_jump_table + 0xb4
			JP __2nd_jump_table + 0xb8
			JP __2nd_jump_table + 0xbc

			; zds2gas: END
