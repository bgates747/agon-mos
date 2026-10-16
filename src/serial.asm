; Native AgonDev source derived from official MOS v3.0.2: src/serial.asm
; Upstream ancestry and changes: docs/upstream-origin.md and docs/deviations.md.
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

			.ASSUME	ADL = 1
			
			; zds2gas: DEFINE .STARTUP, SPACE = ROM
			.section .STARTUP,"ax",@progbits
			
			XDEF	UART0_serial_TX
			XDEF	UART0_serial_RX
			XDEF	UART0_serial_GETCH
			XDEF	UART0_serial_PUTCH 

			XDEF	UART1_serial_TX
			XDEF	UART1_serial_RX
			XDEF	UART1_serial_GETCH
			XDEF	UART1_serial_PUTCH 

			XDEF	_putch
			XDEF	_getch 
			
			XDEF	putch 		
			XDEF	getch 

			XREF	_serialFlags	; In globals.asm
				
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
UART0_wait_CTS:		IN0		A, (UART0_REG_MSR)
			BIT		4, A			; check inverted CTS bit, 1 = CTS, 0 = NOT CTS (clear to send)
			JR		Z, UART0_wait_CTS
			RET

UART1_wait_CTS:		zds_GET_GPIO	PC_DR, 8		; Check Port C, bit 3 (CTS)
			JR		NZ, UART1_wait_CTS
			RET

; Write a character to UART0
; Parameters:
; - A: Data to write
; Returns:
; - F: C if written
; - F: NC if timed out
;
UART0_serial_TX:	PUSH		BC			; Stack BC
			PUSH		AF 			; Stack AF
			LD		BC,TX_WAIT		; Set CB to the transmit timeout
UART0_serial_TX1:	IN0		A,(UART0_REG_LSR)	; Get the line status register
			AND 		UART_LSR_ETH		; Check for TX hold register empty
			JR		NZ, UART0_serial_TX2	; If set, then TX is empty, goto transmit
			DEC		BC
			LD		A, B
			OR		C
			JR		NZ, UART0_serial_TX1
			POP		AF			; We've timed out at this point so
			POP		BC			; Restore the stack
			OR		A			; Clear the carry flag and preserve A
			RET	
UART0_serial_TX2:	POP		AF			; Good to send at this point, so
			OUT0		(UART0_REG_THR),A	; Write the character to the UART transmit buffer
			POP		BC			; Restore BC
			SCF					; Set the carry flag
			RET 

; Write a character to UART1
; Parameters:
; - A: Data to write
; Returns:
; - F: C if written
; - F: NC if timed out
;
UART1_serial_TX:	PUSH		BC			; Stack BC
			PUSH		AF 			; Stack AF
			LD		BC,TX_WAIT		; Set CB to the transmit timeout
UART1_serial_TX1:	IN0		A,(UART1_REG_LSR)	; Get the line status register
			AND 		UART_LSR_ETH		; Check for TX hold register empty
			JR		NZ, UART1_serial_TX2	; If set, then TX is empty, goto transmit
			DEC		BC
			LD		A, B
			OR		C
			JR		NZ, UART1_serial_TX1
			POP		AF			; We've timed out at this point so
			POP		BC			; Restore the stack
			OR		A			; Clear the carry flag and preserve A
			RET	
UART1_serial_TX2:	POP		AF			; Good to send at this point, so
			OUT0		(UART1_REG_THR),A	; Write the character to the UART transmit buffer
			POP		BC			; Restore BC
			SCF					; Set the carry flag
			RET 

; Read a character from UART0
; Returns:
; - A: Data read
; - F: C if character read
; - F: NC if no character read
;
UART0_serial_RX:	IN0		A,(UART0_REG_LSR)	; Get the line status register
			AND 		UART_LSR_RDY		; Check for characters in buffer
			RET		Z			; Just ret (with carry clear) if no characters
			IN0		A,(UART0_REG_RBR)	; Read the character from the UART receive buffer
			SCF 					; Set the carry flag
			RET

; Read a character from UART1
; Returns:
; - A: Data read
; - F: C if character read
; - F: NC if no character read
;
UART1_serial_RX:	IN0		A,(UART1_REG_LSR)	; Get the line status register
			AND 		UART_LSR_RDY		; Check for characters in buffer
			RET		Z			; Just ret (with carry clear) if no characters
			IN0		A,(UART1_REG_RBR)	; Read the character from the UART receive buffer
			SCF 					; Set the carry flag
			RET

; Read a character from UART0 (blocking)
; Returns:
; - A: Data read
; - F: C if read
; - F: NC if UART not enabled
;
UART0_serial_GETCH:	PUSH		AF 
			LD		A, (_serialFlags)
			TST		0x01
			JR		Z, UART_serial_NE
			POP		AF
.Lzds_src_serial_asm_ee44dd47_a0001:			CALL 		UART0_serial_RX
			JR		NC,.Lzds_src_serial_asm_ee44dd47_a0001
			RET 

; Read a character from UART1 (blocking)
; Returns:
; - A: Data read
; - F: C if read
; - F: NC if UART not enabled
;
UART1_serial_GETCH:	PUSH		AF 
			LD		A, (_serialFlags)
			TST		0x10
			JR		Z, UART_serial_NE
			POP		AF
.Lzds_src_serial_asm_ee44dd47_a0002:			CALL 		UART1_serial_RX
			JR		NC,.Lzds_src_serial_asm_ee44dd47_a0002
			RET 

; Write a character to UART0 (blocking)
; Parameters:
; - A: Character to write out
; Returns:
; - F: C if written
; - F: NC if UART not enabled
;
UART0_serial_PUTCH:	PUSH	AF
			LD	A, (_serialFlags)		; Get the serial flags
			TST	0x01				; Check UART is enabled
			JR	Z, UART_serial_NE		; If not, then skip
			TST	0x02				; If hardware flow control enabled then
			CALL	NZ, UART0_wait_CTS		; Wait for clear to send signal
			POP	AF
.Lzds_src_serial_asm_ee44dd47_a0003:			CALL	UART0_serial_TX			; Send the character
			JR	NC, .Lzds_src_serial_asm_ee44dd47_a0003				; Repeat until sent
			RET

; Write a character to UART1 (blocking)
; Parameters:
; - A: Character to write out
; Returns:
; - F: C if written
; - F: NC if UART not enabled
;
UART1_serial_PUTCH:	PUSH	AF
			LD	A, (_serialFlags)		; Get the serial flags
			TST	0x10				; Check UART is enabled
			JR	Z, UART_serial_NE		; If not, then skip (reuses UART0 routine here)
			TST	0x20				; If hardware flow control enabled then
			CALL	NZ, UART1_wait_CTS		; Wait for clear to send signal
			POP	AF			
.Lzds_src_serial_asm_ee44dd47_a0004:			CALL	UART1_serial_TX			; Send the character
			JR	NC, .Lzds_src_serial_asm_ee44dd47_a0004				; Repeat until sent
			RET

; Called by UART0 and UART1 PUTCH and GETCH if the UART is not enabled
;
UART_serial_NE:		POP	AF				; Tidy up the stack
			OR	A 				; Clear the carry flag
			RET
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
putch:			PUSH	IY				; Standard C prologue
			LD	IY, 0
			ADD	IY, SP	

			LD	A, (IY+6)			; INT ch (least significant byte)
			LD	HL, 0				; HLU: The return value
			LD	L, A 
			CALL	UART0_serial_PUTCH		; Output the character

			LD 	SP, IY				; Standard epilogue
			POP	IY
			RET

; INT getch(VOID);
;
; Read a character out to the UART - waits for character input
; Returns:
; - The character read
;
_getch:
getch:			PUSH	IY				; Standard C prologue
			LD	IY, 0
			ADD	IY, SP	

			CALL	UART0_serial_GETCH		; Read the character
			LD	HL, 0				; HLU: The return value
			LD	L, A

			LD 	SP, IY				; Standard epilogue
			POP	IY
			RET
