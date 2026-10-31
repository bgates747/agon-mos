; Maintained native UART variant: src/serial.asm; origin: docs/uart0-native-source.md.
;
; Title:	AGON MOS - UART code
; Author:	Dean Belfield
; Created:	11/07/2022
; Last Updated:	29/03/2023
;
; Modinfo:
; 27/07/2022:	Reverted serial_TX back to use RET, not RET.L and increased timeout
; 08/08/2022:	Added check_CTS
; 22/03/2023:	Added serial_PUTCH, moved putch and getch from uart.c
; 23/03/2023:	Renamed serial_RX_WAIT to seral_GETCH
; 29/03/2023:	Added support for UART1

			.include "macros.inc"
			.include "equs.inc"

			.assume adl=1

			; Original segment placement: DEFINE .STARTUP, SPACE = ROM
			.section .STARTUP,"ax",@progbits

			.global	UART0_serial_TX
			.global	UART0_serial_RX
			.global	UART0_serial_GETCH
			.global	UART0_serial_PUTCH

			.global	UART1_serial_TX
			.global	UART1_serial_RX
			.global	UART1_serial_GETCH
			.global	UART1_serial_PUTCH

			.global	_putch
			.global	_getch

			.global	putch
			.global	getch

			.extern	tx_opened,uart0_sync_put,uart0_read_lsr,uart0_read_msr
			.extern	_serialFlags	; In globals.asm

.equiv UART0_PORT, 0xC0; UART0
.equiv UART1_PORT, 0xD0; UART1

.equiv UART0_REG_RBR, UART0_PORT+0; Receive buffer
.equiv UART0_REG_THR, UART0_PORT+0; Transmitter holding
.equiv UART0_REG_DLL, UART0_PORT+0; Divisor latch low
.equiv UART0_REG_IER, UART0_PORT+1; Interrupt enable
.equiv UART0_REG_DLH, UART0_PORT+1; Divisor latch high
.equiv UART0_REG_IIR, UART0_PORT+2; Interrupt identification
.equiv UART0_REG_FCT, UART0_PORT+2;	; Flow control
.equiv UART0_REG_LCR, UART0_PORT+3; Line control
.equiv UART0_REG_MCR, UART0_PORT+4; Modem control
.equiv UART0_REG_LSR, UART0_PORT+5; Line status
.equiv UART0_REG_MSR, UART0_PORT+6; Modem status
.equiv UART0_REG_SCR, UART0_PORT+7; Scratch

.equiv UART1_REG_RBR, UART1_PORT+0; Receive buffer
.equiv UART1_REG_THR, UART1_PORT+0; Transmitter holding
.equiv UART1_REG_DLL, UART1_PORT+0; Divisor latch low
.equiv UART1_REG_IER, UART1_PORT+1; Interrupt enable
.equiv UART1_REG_DLH, UART1_PORT+1; Divisor latch high
.equiv UART1_REG_IIR, UART1_PORT+2; Interrupt identification
.equiv UART1_REG_FCT, UART1_PORT+2;	; Flow control
.equiv UART1_REG_LCR, UART1_PORT+3; Line control
.equiv UART1_REG_MCR, UART1_PORT+4; Modem control
.equiv UART1_REG_LSR, UART1_PORT+5; Line status
.equiv UART1_REG_MSR, UART1_PORT+6; Modem status
.equiv UART1_REG_SCR, UART1_PORT+7; Scratch

.equiv TX_WAIT, 16384; Count before a TX times out

.equiv UART_LSR_ERR, 0x80; Error
.equiv UART_LSR_ETX, 0x40; Transmit empty
.equiv UART_LSR_ETH, 0x20; Transmit holding register empty
.equiv UART_LSR_RDY, 0x01; Data ready

; Check whether we're clear to send (UART0 only)
;
UART0_wait_CTS:		call		uart0_read_msr
			bit		4, A			; check inverted CTS bit, 1 = CTS, 0 = NOT CTS (clear to send)
			jr		Z, UART0_wait_CTS
			ret

UART1_wait_CTS:		GET_GPIO	PC_DR, 8		; Check Port C, bit 3 (CTS)
			jr		NZ, UART1_wait_CTS
			ret

; Write a character to UART0
; Parameters:
; - A: Data to write
; Returns:
; - F: C if written
; - F: NC if timed out
;
UART0_serial_TX:	push		AF
			ld		A,(tx_opened)
			or		A,A
			jr		Z,UART0_tx_legacy
			pop		AF
			call		uart0_sync_put
			scf
			ret
UART0_tx_legacy:	pop		AF
			push		BC			; Stack BC
			push		AF 			; Stack AF
			ld		BC,TX_WAIT		; Set CB to the transmit timeout
UART0_serial_TX1:	call		uart0_read_lsr	; Get the line status register
			and 		UART_LSR_ETH		; Check for TX hold register empty
			jr		NZ, UART0_serial_TX2	; If set, then TX is empty, goto transmit
			dec		BC
			ld		A, B
			or		C
			jr		NZ, UART0_serial_TX1
			pop		AF			; We've timed out at this point so
			pop		BC			; Restore the stack
			or		A			; Clear the carry flag and preserve A
			ret
UART0_serial_TX2:	pop		AF			; Good to send at this point, so
			out0		(UART0_REG_THR),A	; Write the character to the UART transmit buffer
			pop		BC			; Restore BC
			scf					; Set the carry flag
			ret

; Write a character to UART1
; Parameters:
; - A: Data to write
; Returns:
; - F: C if written
; - F: NC if timed out
;
UART1_serial_TX:	push		BC			; Stack BC
			push		AF 			; Stack AF
			ld		BC,TX_WAIT		; Set CB to the transmit timeout
UART1_serial_TX1:	in0		A,(UART1_REG_LSR)	; Get the line status register
			and 		UART_LSR_ETH		; Check for TX hold register empty
			jr		NZ, UART1_serial_TX2	; If set, then TX is empty, goto transmit
			dec		BC
			ld		A, B
			or		C
			jr		NZ, UART1_serial_TX1
			pop		AF			; We've timed out at this point so
			pop		BC			; Restore the stack
			or		A			; Clear the carry flag and preserve A
			ret
UART1_serial_TX2:	pop		AF			; Good to send at this point, so
			out0		(UART1_REG_THR),A	; Write the character to the UART transmit buffer
			pop		BC			; Restore BC
			scf					; Set the carry flag
			ret

; Read a character from UART0
; Returns:
; - A: Data read
; - F: C if character read
; - F: NC if no character read
;
UART0_serial_RX:	call		uart0_read_lsr	; Get the line status register
			and 		UART_LSR_RDY		; Check for characters in buffer
			ret		Z			; Just ret (with carry clear) if no characters
			in0		A,(UART0_REG_RBR)	; Read the character from the UART receive buffer
			scf 					; Set the carry flag
			ret

; Read a character from UART1
; Returns:
; - A: Data read
; - F: C if character read
; - F: NC if no character read
;
UART1_serial_RX:	in0		A,(UART1_REG_LSR)	; Get the line status register
			and 		UART_LSR_RDY		; Check for characters in buffer
			ret		Z			; Just ret (with carry clear) if no characters
			in0		A,(UART1_REG_RBR)	; Read the character from the UART receive buffer
			scf 					; Set the carry flag
			ret

; Read a character from UART0 (blocking)
; Returns:
; - A: Data read
; - F: C if read
; - F: NC if UART not enabled
;
UART0_serial_GETCH:	push		AF
			ld		A, (_serialFlags)
			tst		0x01
			jr		Z, UART_serial_NE
			pop		AF
1:			call 		UART0_serial_RX
			jr		NC,1b
			ret

; Read a character from UART1 (blocking)
; Returns:
; - A: Data read
; - F: C if read
; - F: NC if UART not enabled
;
UART1_serial_GETCH:	push		AF
			ld		A, (_serialFlags)
			tst		0x10
			jr		Z, UART_serial_NE
			pop		AF
1:			call 		UART1_serial_RX
			jr		NC,1b
			ret

; Write a character to UART0 (blocking)
; Parameters:
; - A: Character to write out
; Returns:
; - F: C if written
; - F: NC if UART not enabled
;
UART0_serial_PUTCH:	push	AF
			ld	A,(tx_opened)
			or	A,A
			jr	Z,UART0_putch_legacy
			pop	AF
			call	uart0_sync_put
			scf
			ret
UART0_putch_legacy:
			ld	A, (_serialFlags)		; Get the serial flags
			tst	0x01				; Check UART is enabled
			jr	Z, UART_serial_NE		; If not, then skip
			tst	0x02				; If hardware flow control enabled then
			call	NZ, UART0_wait_CTS		; Wait for clear to send signal
			pop	AF
1:			call	UART0_serial_TX			; Send the character
			jr	NC, 1b				; Repeat until sent
			ret

; Write a character to UART1 (blocking)
; Parameters:
; - A: Character to write out
; Returns:
; - F: C if written
; - F: NC if UART not enabled
;
UART1_serial_PUTCH:	push	AF
			ld	A, (_serialFlags)		; Get the serial flags
			tst	0x10				; Check UART is enabled
			jr	Z, UART_serial_NE		; If not, then skip (reuses UART0 routine here)
			tst	0x20				; If hardware flow control enabled then
			call	NZ, UART1_wait_CTS		; Wait for clear to send signal
			pop	AF
1:			call	UART1_serial_TX			; Send the character
			jr	NC, 1b				; Repeat until sent
			ret

; Called by UART0 and UART1 PUTCH and GETCH if the UART is not enabled
;
UART_serial_NE:		pop	AF				; Tidy up the stack
			or	A 				; Clear the carry flag
			ret
;
; The C wrappers
;

; INT putch(INT ch);
;
; Write a character out to the UART
; Parameters:
; - ch: The character to write (least significant byte)
; Returns:
; - The character written
;
_putch:
putch:			push	IY				; Standard C prologue
			ld	IY, 0
			add	IY, SP

			ld	A, (IY+6)			; INT ch (least significant byte)
			ld	HL, 0				; HLU: The return value
			ld	L, A
			call	UART0_serial_PUTCH		; Output the character

			ld 	SP, IY				; Standard epilogue
			pop	IY
			ret

; INT getch(VOID);
;
; Read a character out to the UART - waits for character input
; Returns:
; - The character read
;
_getch:
getch:			push	IY				; Standard C prologue
			ld	IY, 0
			add	IY, SP

			call	UART0_serial_GETCH		; Read the character
			ld	HL, 0				; HLU: The return value
			ld	L, A

			ld 	SP, IY				; Standard epilogue
			pop	IY
			ret
