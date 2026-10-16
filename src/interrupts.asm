; Native AgonDev source derived from official MOS v3.0.2: src/interrupts.asm
; Upstream ancestry and changes: docs/upstream-origin.md and docs/deviations.md.
;
; Title:	AGON MOS - Interrupt handlers
; Author:	Dean Belfield
; Created:	03/08/2022
; Last Updated:	29/03/2023
;
; Modinfo:
; 09/03/2023:	No longer uses timer interrupt 0 for SD card timing
; 29/03/2023:	Added support for UART1
; 10/11/2023:	Added support for I2C

			.include "macros.inc"
			.include "equs.inc"
			.include "ez80f92.inc"
			.include "i2c.inc"

			.assume adl=1

			; zds2gas: DEFINE .STARTUP, SPACE = ROM
			.section .STARTUP,"ax",@progbits

			.global	_vblank_handler
			.global	_uart0_handler
			.global	_i2c_handler

			.extern	_clock
			.extern	_vdp_protocol_data

			.extern	UART0_serial_RX
			.extern	UART0_serial_TX
			.extern	mos_api
			.extern	vdp_protocol

			.extern	_i2c_slave_rw
			.extern	_i2c_error
			.extern	_i2c_role
			.extern	_i2c_msg_ptr
			.extern	_i2c_msg_size

; AGON Vertical Blank Interrupt handler
;
_vblank_handler:	di
			push		AF
			SET_GPIO 	PB_DR, 2		; Need to set this to 2 for the interrupt to work correctly
			push		BC
			push		DE
			push		HL
			ld 		HL, (_clock)		; Increment the 32-bit clock counter
			ld		BC, 2			; By 2, effectively timing in centiseconds
			add		HL, BC
			ld		(_clock), HL
			ld		A, (_clock + 3)
			adc		A, 0
			ld		(_clock + 3), A
			pop		HL
			pop		DE
			pop		BC
			pop		AF
			ei
			reti.l

; AGON UART0 Interrupt Handler
;
_uart0_handler:		di
			push		AF
			push		BC
			push		DE
			push		HL
			call		UART0_serial_RX
			ld		C, A
			ld		HL, _vdp_protocol_data
			call		vdp_protocol
			pop		HL
			pop		DE
			pop		BC
			pop		AF
			ei
			reti.l

; AGON I2C Interrupt handler
;
_i2c_handler:
			di
			push	AF
			push	HL
			push	DE
			in0		A, (I2C_SR)				; input I2C status register - switch case to this status value
			and		0b11111000				; cancel lower 3 bits, so we can use RRA. This will save 1 T-state
			rra
			rra
			rra								; bits [7:3] contain the jumpvector
			call	i2c_handle_sr_vector
			; and switch on the vectors in this table
			dw		i2c_case_buserror		; 00h
			dw		i2c_case_master_start	; 08h
			dw		i2c_case_invalid		; 10h
			dw		i2c_case_aw_acked		; 18h
			dw		i2c_case_aw_nacked		; 20h
			dw		i2c_case_db_acked		; 28h
			dw		i2c_case_db_nacked		; 30h
			dw		i2c_case_arblost		; 38h
			dw		i2c_case_mr_ar_ack		; 40h
			dw		i2c_case_mr_ar_nack		; 48h
			dw		i2c_case_mr_dbr_ack		; 50h
			dw		i2c_case_mr_dbr_nack	; 58h
			dw		i2c_case_toimplement	; 60h - slave
			dw		i2c_case_toimplement	; 68h - slave
			dw		i2c_case_toimplement	; 70h - slave
			dw		i2c_case_toimplement	; 78h - slave
			dw		i2c_case_toimplement	; 80h - slave
			dw		i2c_case_toimplement	; 88h - slave
			dw		i2c_case_toimplement	; 90h - slave
			dw		i2c_case_toimplement	; 98h - slave
			dw		i2c_case_toimplement	; A0h - slave
			dw		i2c_case_toimplement	; A8h - slave
			dw		i2c_case_toimplement	; B0h - slave
			dw		i2c_case_toimplement	; B8h - slave
			dw		i2c_case_toimplement	; C0h - slave
			dw		i2c_case_toimplement	; C8h - slave
			dw		i2c_case_toimplement	; D0h - 10bit I2C address
			dw		i2c_case_toimplement	; D8h - 10bit I2C address
			dw		i2c_case_invalid		; E0h
			dw		i2c_case_invalid		; E8h
			dw		i2c_case_invalid		; F0h
			dw		i2c_case_invalid		; F8h - Should never produce an interrupt

i2c_handle_sr_vector:
			ex		(SP), HL	; Swap HL with the contents of the top of the stack
			add		A, A		; Multiply A by two
			add		A, L
			ld		L, A
			adc		A, H
			sub		L
			ld		H, A		; Add 8bit A to HL
			ld		A, (HL)		; Fetch vector adress from the table
			inc		HL
			ld		H, (HL)
			ld		L, A
			ex		(SP), HL	; Swap this new address back, restores HL
			ret					; Return program control to this new address

i2c_case_buserror: ; 00h
			ld		A, RET_BUS_ERROR
			ld		(_i2c_error),A

			; perform software reset of the bus
			xor		A
			out0	(I2C_SRR),A
			ld		HL, _i2c_role
			ld		A, I2C_IDLE	; READY state
			ld		(HL),A

			pop		DE
			pop		HL
			pop		AF
			ei
			reti.l

i2c_case_master_start:		; 08h
i2c_case_master_repstart:	; 10h
			ld		A, (_i2c_slave_rw)		; load slave address and r/w bit
			out0	(I2C_DR), A		; store to I2C Data Register
			ld		A, I2C_CTL_IEN | I2C_CTL_ENAB | I2C_CTL_AAK
			out0	(I2C_CTL),A		; set to Control register

			pop		DE
			pop		HL
			pop		AF
			ei
			reti.l

i2c_case_aw_acked:	; 18h
i2c_case_db_acked:	; 28h
			; Check size and size--
			ld		A, (_i2c_msg_size)
			or		A
			jr		Z, i2c_sendstop
			dec		A
			ld		(_i2c_msg_size), A

			; load pointer
			ld		HL, _i2c_msg_ptr
			push hl
			pop de
			ld		HL, (HL)

			; Load indexed byte from buffer
			ld		A, (HL)

			out0	(I2C_DR), A		; store to I2C Data Register
			ld		A, I2C_CTL_IEN | I2C_CTL_ENAB | I2C_CTL_AAK
			out0	(I2C_CTL),A		; set to Control register

			inc		HL				; pointer++
			ex		DE, HL
			ld		(HL), DE

			pop		DE
			pop		HL
			pop		AF
			ei
			reti.l

i2c_case_aw_nacked:	; 20h
i2c_case_mr_ar_nack: ; 48h
			ld		A, RET_NORESPONSE
			ld		(_i2c_error),A
			jp		i2c_sendstop

i2c_case_db_nacked:	; 30h
			ld		A, RET_DATA_NACK
			ld		(_i2c_error),A
			jp 		i2c_sendstop

i2c_case_arblost:	; 38h
			ld		A, RET_ARB_LOST
			ld		(_i2c_error),A
			jp 		i2c_sendstop

i2c_case_mr_dbr_ack: ; 50h
			; calculate offset address into i2c_mbuffer
			ld		HL, _i2c_msg_ptr
			push hl
			pop de
			ld		HL, (HL)

			in0		A,(I2C_DR)		; load byte from I2C Data Register
			ld		(HL),A			; store in buffer at calculated index

			inc		HL				; pointer++
			ex		DE, HL
			ld		(HL), DE
;			; intentionally falling through to next case
i2c_case_mr_ar_ack: ; 40h
			ld		A, (_i2c_msg_size)
			cp		1					; last byte to receive?
			jr		Z, 1f

			ld		A, I2C_CTL_IEN | I2C_CTL_ENAB | I2C_CTL_AAK	; reply with ACK
			jr		.Lvblank_handler_end
1:
			ld		A, I2C_CTL_IEN | I2C_CTL_ENAB				; reply without ACK
.Lvblank_handler_end:		out0	(I2C_CTL),A		; set to Control register
			; size--
			ld		A, (_i2c_msg_size)
			dec		A
			ld		(_i2c_msg_size), A

			pop		DE
			pop		HL
			pop		AF
			ei
			reti.l

i2c_case_mr_dbr_nack: ; 58h
			; load pointer
			ld		HL, _i2c_msg_ptr
			ld		HL, (HL)

			in0		A,(I2C_DR)			; load byte from I2C Data Register
			ld		(HL),A				; store in buffer at calculated index

			jr		i2c_sendstop

i2c_case_invalid:
i2c_case_toimplement:
i2c_sendstop:
			; send stop first to go to idle state
			ld		A, I2C_CTL_ENAB | I2C_CTL_STP
			out0	(I2C_CTL),A		; set to Control register
1:
			in0		A,(I2C_CTL)
			and		I2C_CTL_STP		; STP bit still in place?
			jr		NZ, 1b

			; Release control of the bus
			xor		A				; all bits of I2C_CTL to 0
			out0	(I2C_CTL),A		; set to Control register I2C_CTL
			ld		HL, _i2c_role
			ld		A, I2C_IDLE	; IDLE state
			ld		(HL),A

			pop		DE
			pop		HL
			pop		AF
			ei
			reti.l

			; zds2gas: END
