; Native AgonDev source derived from official MOS v3.0.2: src_startup/init_params_f92.asm
; Upstream ancestry and changes: docs/upstream-origin.md and docs/deviations.md.
;
; Title:	AGON MOS - C Startup Code
; Author:	Copyright (C) 2005 by ZiLOG, Inc.  All Rights Reserved.
; Modified By:	Dean Belfield
; Created:	10/07/2022
; Last Updated: 01/08/2022
;
; Modinfo:
; 14/07/2022:	Added coldBoot detection, exec16 function
; 15/07/2022:	Added further hardware/firmware initialisation in __init
; 24/07/2022:	Added timer2 global variable and moved exec_16 to misc.asm
; 26/07/2022:	Added _tmpLHU
; 01/08/2022:	Moved global variables to globals.asm

			.include "../src/macros.inc"
			.include "../src/equs.inc"

			.include "ez80f92.inc"

			.extern	__stack
			.extern	__init_default_vectors
			.extern	__c_startup
			.extern	__cstartup
			.extern	_main
			.extern	__CS0_LBR_INIT_PARAM
			.extern	__CS0_UBR_INIT_PARAM
			.extern	__CS0_CTL_INIT_PARAM
			.extern	__CS1_LBR_INIT_PARAM
			.extern	__CS1_UBR_INIT_PARAM
			.extern	__CS1_CTL_INIT_PARAM
			.extern	__CS2_LBR_INIT_PARAM
			.extern	__CS2_UBR_INIT_PARAM
			.extern	__CS2_CTL_INIT_PARAM
			.extern	__CS3_LBR_INIT_PARAM
			.extern	__CS3_UBR_INIT_PARAM
			.extern	__CS3_CTL_INIT_PARAM
			.extern	__CS0_BMC_INIT_PARAM
			.extern	__CS1_BMC_INIT_PARAM
			.extern	__CS2_BMC_INIT_PARAM
			.extern	__CS3_BMC_INIT_PARAM
			.extern	__FLASH_CTL_INIT_PARAM
			.extern	__FLASH_ADDR_U_INIT_PARAM
			.extern	__RAM_CTL_INIT_PARAM
			.extern	__RAM_ADDR_U_INIT_PARAM

			.global	__init
			.global	_abort
			.global	__exit
			.global	_exit

			.extern	__exec16
			.extern	_exec16

			.extern	GPIOB_SETMODE

			.extern 	_coldBoot
			.extern 	_keycode
			.extern 	_timer2
			.extern 	_callSM
			.extern 	_tmpLHU
;
; Startup code
;
			; zds2gas: DEFINE .STARTUP, SPACE = ROM
			.section .STARTUP,"ax",@progbits

			.assume adl=1

; Minimum default initialization
;
; Disable internal peripheral interrupt sources
; -- this will help during a RAM debug session --
;
__init:			ld a, 0xFF
			out0 (PB_DDR), a         ; GPIO
			out0 (PC_DDR), a         ;
			out0 (PD_DDR), a         ;
			ld a, 0x00
			out0 (PB_ALT1), a        ;
			out0 (PC_ALT1), a        ;
			out0 (PD_ALT1), a        ;
			out0 (PB_ALT2), a        ;
			out0 (PC_ALT2), a        ;
			out0 (PD_ALT2), a        ;
			out0 (TMR0_CTL), a       ; timers
			out0 (TMR1_CTL), a       ;
			out0 (TMR2_CTL), a       ;
			out0 (TMR3_CTL), a       ;
			out0 (TMR4_CTL), a       ;
			out0 (TMR5_CTL), a       ;
			out0 (UART0_IER), a      ; UARTs
			out0 (UART1_IER), a      ;
			out0 (I2C_CTL), a        ; I2C
			out0 (FLASH_IRQ), a      ; Flash
			ld a, 0x04
			out0 (SPI_CTL), a        ; SPI
			in0 a, (RTC_CTRL)        ; RTC, Writing to the RTC_CTRL register also
			and a, 0xBE               ;      resets the RTC count prescaler allowing
			out0 (RTC_CTRL), a       ;      the RTC to be synchronized to another time source
;
; Configure external memory/io
;
			ld a, __CS0_LBR_INIT_PARAM
			out0 (CS0_LBR), a
			ld a, __CS0_UBR_INIT_PARAM
			out0 (CS0_UBR), a
			ld a, __CS0_BMC_INIT_PARAM
			out0 (CS0_BMC), a
			ld a, __CS0_CTL_INIT_PARAM
			out0 (CS0_CTL), a

			ld a, __CS1_LBR_INIT_PARAM
			out0 (CS1_LBR), a
			ld a, __CS1_UBR_INIT_PARAM
			out0 (CS1_UBR), a
			ld a, __CS1_BMC_INIT_PARAM
			out0 (CS1_BMC), a
			ld a, __CS1_CTL_INIT_PARAM
			out0 (CS1_CTL), a

			ld a, __CS2_LBR_INIT_PARAM
			out0 (CS2_LBR), a
			ld a, __CS2_UBR_INIT_PARAM
			out0 (CS2_UBR), a
			ld a, __CS2_BMC_INIT_PARAM
			out0 (CS2_BMC), a
			ld a, __CS2_CTL_INIT_PARAM
			out0 (CS2_CTL), a

			ld a, __CS3_LBR_INIT_PARAM
			out0 (CS3_LBR), a
			ld a, __CS3_UBR_INIT_PARAM
			out0 (CS3_UBR), a
			ld a, __CS3_BMC_INIT_PARAM
			out0 (CS3_BMC), a
			ld a, __CS3_CTL_INIT_PARAM
			out0 (CS3_CTL), a
;
; Enable internal memory
;
			ld a, __FLASH_ADDR_U_INIT_PARAM
			out0 (FLASH_ADDR_U), a
			; Change the flash control register to zero wait states
			; NB using a constant here as I couldn't work out how __FLASH_CTL_INIT_PARAM is set
			; ld a, __FLASH_CTL_INIT_PARAM
			ld a, 0x08
			out0 (FLASH_CTRL), a

			ld a, __RAM_ADDR_U_INIT_PARAM
			out0 (RAM_ADDR_U), a
			ld a, __RAM_CTL_INIT_PARAM
			out0 (RAM_CTL), a
;
; Setup Stack Pointer
;
			ld sp, __stack

;
; Detect preserved ram
;
			ld de, __warmboot_magic	; If warm boot, __warmboot_magic (pushed by 'call _main') will
			ld hl, (0x0bfffa)	; be the int24 at __stack-6 (ie 0bfffah)
			or a
			sbc hl,de
			jr z, __skip_memclr
; Cold boot: wipe external 512k RAM (initialize to $ff (rst $38))
			ld hl, 0x40000
			ld de, 0x40001
			ld bc, 0x80000 - 1
			ld (hl), 0x0ff
			ldir
; Cold boot: wipe internal SRAM
			ld hl, 0x0b7e000
			ld de, 0x0b7e001
			ld bc, 0x2000 - 1
			ld (hl), 0x0ff
			ldir
__skip_memclr:

;
; Detect hardware reset
;
			ld a, i			; Register I should be 0 on cold boot
			or a, a
			ld a, 1			; Set to 1 if cold boot
			jr z, 1f
			dec a			; Otherwise set to 0
1:			push af 		; Stack AF, will store later as __c_startup clears globals area

;
; Initialize the interrupt vector table
;
			call __init_default_vectors
;
; Further hardware/firmware initialisation
;
			ld	A, GPIOMODE_INTRE
			ld	B, 2
			call	GPIOB_SETMODE

; Protect flash pages by default

			ld        A, 0xb6    ; unlock
			out0    (0xF5), A
			ld        A, 0x49
			out0    (0xF5), A
			ld        A, 0xff    ; protect all pages
			out0    (0xFA), A

;
; Start application
;
			ld a, __cstartup
			or a, a
			jr z, __no_cstartup
			call __c_startup

			pop af			; Pop the coldboot value
			ld (_coldBoot), a	; And store

__no_cstartup:		ld hl, 0                ; hl = NULL
			push hl                 ; argv[0] = NULL
			ld ix, 0
			add ix, sp              ; ix = &argv[0]
			push ix                 ; &argv[0]
			pop hl
			ld de, 0                ; argc = 0
			call _main              ; int main(int argc, char *argv[]))
__warmboot_magic:	pop de			; clean the stack

__exit:
_exit:
_abort:			jr .                	; If we return from main loop forever here

; Define global constants
;
			.extern _SYS_CLK_FREQ
			.global _SysClkFreq

_SysClkFreq:		d32 _SYS_CLK_FREQ

			; zds2gas: END
