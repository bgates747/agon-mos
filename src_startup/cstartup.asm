; Native AgonDev source derived from official MOS v3.0.2: src_startup/cstartup.asm
; Upstream ancestry and changes: docs/upstream-origin.md and docs/deviations.md.
;
; Title:	AGON MOS - C Startup Code
; Author:	Copyright (C) 2005 by ZiLOG, Inc.  All Rights Reserved.
; Modified By:	Dean Belfield
; Created:	10/07/2022
; Last Updated:	09/08/2022
;
; Modinfo:
; 01/08/2022:	Moved _errno to globals.asm
; 09/08/2022:	Reformatted

			.global __c_startup
			.global __cstartup
			.extern _errno
			.extern _main

			.extern __low_bss         ; Low address of bss segment
			.extern __len_bss         ; Length of bss segment

			.extern __low_data        ; Address of initialized data section
			.extern __low_romdata     ; Addr of initialized data section in ROM
			.extern __len_data        ; Length of initialized data section

			.extern __copy_code_to_ram
			.extern __len_code
			.extern __low_code
			.extern __low_romcode

.equiv __cstartup, 0x1

			; zds2gas: DEFINE .STARTUP, SPACE = ROM
			.section .STARTUP,"ax",@progbits
			.assume adl=1

__c_startup:
_c_int0:
;
; Clear the uninitialized data section
;
			ld	BC, __len_bss			; Check for non-zero length
			ld	a, __len_bss >> 16
			or	A, C
			or	A, B
			jr	Z, _c_bss_done			; BSS is zero-length ...
			xor	A, A
			ld 	(__low_bss), A
			sbc	HL, HL				; hl = 0
			dec	BC				; 1st byte's taken care of
			sbc	HL, BC
			jr	Z, _c_bss_done  	        ; Just 1 byte ...
			ld	HL, __low_bss			; reset hl
			ld	DE, __low_bss + 1		; [de] = bss + 1
			ldir					; Clear this section

_c_bss_done:
;
; Copy the initialized data section
;
			ld	BC, __len_data			; [bc] = data length
			ld	A, __len_data >> 16		; Check for non-zero length
			or	A, C
			or	A, B
			jr	Z, _c_data_done			; __len_data is zero-length ...
			ld	HL, __low_romdata		; [hl] = data_copy
			ld	DE, __low_data			; [de] = data
			ldir					; Copy the data section

_c_data_done:
;
; Copy CODE (which may be in FLASH) to RAM if the
; copy_code_to_ram symbol is set in the link control file
;
			ld	A, __copy_code_to_ram
			or	A, A
			jr	Z, _copy_code_to_ram_done
			ld	BC, __len_code			; [bc] = code length
			ld	A, __len_code >> 16		; Check for non-zero length
			or	A, C
			or	A, B
			jr	Z, _copy_code_to_ram_done	; __len_code is zero-length ...
			ld	HL, __low_romcode		; [hl] = code_copy
			ld	DE, __low_code			; [de] = code
			ldir					; Copy the code section

_copy_code_to_ram_done:
;
; C environment created, continue with the initialization process
;
			ret

			; zds2gas: END
