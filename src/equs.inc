; Native AgonDev source derived from official MOS v3.0.2: src/equs.inc
; Upstream ancestry and changes: docs/upstream-origin.md and docs/deviations.md.
.ifndef AGON_MOS_SRC_EQUS_INC
.set AGON_MOS_SRC_EQUS_INC,1
;
; Title:	AGON MOS - Equs
; Author:	Dean Belfield
; Created:	15/07/2022
; Last Updated:	08/06/2023
;
; Modinfo:
; 24/07/2022:	Added TMR2_CTL
; 03/08/2022:	Added UART0_BUFFERLEN
; 20/08/2022:	Added some VDP protocol flags
; 18/09/2022:	Added VDPP_FLAG_MODE
; 09/03/2023:	Renamed TMR2_CTL to TMR0_CTL
; 15/03/2023:	Added VDPP_FLAG_RTC
; 19/03/2023:	Fixed TMR0_RR_H to point to correct register
; 08/06/2023:	Add MASTERCLOCK to permit clock delay calculations

; System clock speed in Hz
.equiv MASTERCLOCK, 18432000

; MOS specific
;
.equiv VDPP_BUFFERLEN, 16; VDP Protocol Buffer Length
	
.equiv VDPP_FLAG_CURSOR, 0b00000001
.equiv VDPP_FLAG_SCRCHAR, 0b00000010
.equiv VDPP_FLAG_POINT, 0b00000100
.equiv VDPP_FLAG_AUDIO, 0b00001000
.equiv VDPP_FLAG_MODE, 0b00010000
.equiv VDPP_FLAG_RTC, 0b00100000
.equiv VDPP_FLAG_MOUSE, 0b01000000
; VDPP_FLAG_BUFFERED:	EQU		10000000b

; For GPIO
; PA not available on eZ80F92
;
.equ PA_DR, 0x96
.equ PA_DDR, 0x97
.equ PA_ALT1, 0x98
.equ PA_ALT2, 0x99
.equ PB_DR, 0x9A
.equ PB_DDR, 0x9B
.equ PB_ALT1, 0x9C
.equ PB_ALT2, 0x9D
.equ PC_DR, 0x9E
.equ PC_DDR, 0x9F
.equ PC_ALT1, 0xA0
.equ PC_ALT2, 0xA1
.equ PD_DR, 0xA2
.equ PD_DDR, 0xA3
.equ PD_ALT1, 0xA4
.equ PD_ALT2, 0xA5
	
.equiv GPIOMODE_OUT, 0; Output
.equiv GPIOMODE_IN, 1; Input
.equiv GPIOMODE_DIO, 2; Open Drain IO
.equiv GPIOMODE_SIO, 3; Open Source IO
.equiv GPIOMODE_INTD, 4; Interrupt, Dual Edge
.equiv GPIOMODE_ALTF, 5;	; Alt Function
.equiv GPIOMODE_INTAL, 6; Interrupt, Active Low
.equiv GPIOMODE_INTAH, 7; Interrupt, Active High
.equiv GPIOMODE_INTFE, 8; Interrupt, Falling Edge
.equiv GPIOMODE_INTRE, 9; Interrupt, Rising Edge
	
; For interrupts.asm
;

;UARTs
;
.equ UART0_IVECT, 0x18
.equ UART1_IVECT, 0x1A

;Ports
;
.equiv PB0_IVECT, 0x30; AGON ITRP Interrupt   (Pin 28/IO17 of the ESP32)
.equiv PB1_IVECT, 0x32; AGON VBLANK Interrupt (Pin 23/IO15 of the ESP32)
.equiv PB2_IVECT, 0x34
.equiv PB3_IVECT, 0x36
.equiv PB4_IVECT, 0x38
.equiv PB5_IVECT, 0x3A
.equiv PB6_IVECT, 0x3C
.equiv PB7_IVECT, 0x3E
                       
.equiv PC0_IVECT, 0x40
.equiv PC1_IVECT, 0x42
.equiv PC2_IVECT, 0x44
.equiv PC3_IVECT, 0x46
.equiv PC4_IVECT, 0x48
.equiv PC5_IVECT, 0x4A
.equiv PC6_IVECT, 0x4C
.equiv PC7_IVECT, 0x4E
                       
.equiv PD0_IVECT, 0x50
.equiv PD1_IVECT, 0x52
.equiv PD2_IVECT, 0x54
.equiv PD3_IVECT, 0x56
.equiv PD4_IVECT, 0x58
.equiv PD5_IVECT, 0x5A
.equiv PD6_IVECT, 0x5C
.equiv PD7_IVECT, 0x5E

; For vectors16.asm
;
.equ TMR0_CTL, 0x80
.equ TMR0_DR_L, 0x81
.equ TMR0_RR_L, 0x81
.equ TMR0_DR_H, 0x82
.equ TMR0_RR_H, 0x82

.endif
