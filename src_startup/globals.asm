; Native AgonDev source derived from official MOS v3.0.2: src_startup/globals.asm
; Upstream ancestry and changes: docs/upstream-origin.md and docs/deviations.md.
;
; Title:	AGON MOS - Globals
; Author:	Dean Belfield
; Created:	01/08/2022
; Last Updated:	11/11/2023
;
; Modinfo:
; 09/08/2022:	Added sysvars structure, cursorX, cursorY
; 18/08/2022:	Added scrchar, scrpixel, audioChannel, audioSuccess, vdp_protocol_flags
; 18/09/2022:	Added scrwidth, scrheight, scrcols, scrrows
; 23/02/2023:	Added scrcolours, fixed offsets in sysvars comments
; 04/03/2023:	Added scrpixelIndex
; 09/03/2023:	Added vdp_protocol_count, keyascii, keydown; swapped keyascii with keycode, removed timer2
; 15/03/2023:	Added rtc
; 21/03/2023:	Added keydelay, keyrate, keyled
; 23/03/2023:	Added gp
; 29/03/2023:	Added serialFlags
; 14/04/2023:	Added scratchpad
; 19/05/2023	Added scrmode
; 05/06/2023:	Added RTC enable flag
; 03/08/2023:	Added user_kbvector
; 13/08/2023:	Added keymap
; 11/11/2023:	Added i2c

			.include "../src/equs.inc"
			
			XDEF	_sysvars
			
			XDEF 	_keycode
			XDEF	_keymods
			XDEF	_keyascii
			XDEF	_keydown
			XDEF	_keycount
			XDEF	_clock
			XDEF	_cursorX
			XDEF	_cursorY
			XDEF	_scrchar
			XDEF	_scrpixel
			XDEF	_audioChannel
			XDEF	_audioSuccess
			XDEF	_scrwidth
			XDEF	_scrheight
			XDEF	_scrcols
			XDEF	_scrrows
			XDEF	_scrcolours
			XDEF	_scrpixelIndex
			XDEF	_rtc
			XDEF	_keydelay 
			XDEF	_keyrate 
			XDEF 	_keyled
			XDEF	_scrmode
			XDEF	_rtc_enable
			XDEF	_mouseX
			XDEF	_mouseY
			XDEF	_mouseButtons
			XDEF	_mouseWheel
			XDEF	_mouseXDelta
			XDEF	_mouseYDelta

			XDEF	_errno
			XDEF 	_coldBoot
			XDEF	_gp
			XDEF	_serialFlags
			XDEF 	_callSM
			XDEF	_scratchpad
			XDEF	_keymap 

			XDEF	_vpd_protocol_flags
			XDEF	_vdp_protocol_state
			XDEF	_vdp_protocol_cmd
			XDEF	_vdp_protocol_len
			XDEF	_vdp_protocol_ptr
			XDEF	_vdp_protocol_data

			XDEF	_user_kbvector

			XDEF	_history_no
			XDEF	_history_size

			XDEF	_i2c_slave_rw
			XDEF	_i2c_error
			XDEF	_i2c_role
			XDEF	_i2c_msg_ptr
			XDEF	_i2c_msg_size

			.section .bss,"aw",@nobits; This section is reset to 0 in cstartup.asm
			
_sysvars:					; Please make sure the sysvar offsets match those in mos_api.inc
;
_clock:			.skip 4; + 00h: Clock timer in centiseconds (incremented by 2 every VBLANK)
_vpd_protocol_flags:	.skip 1; + 04h: Flags to indicate completion of VDP commands
_keyascii:		.skip 1; + 05h: ASCII keycode, or 0 if no key is pressed
_keymods:		.skip 1; + 06h: Keycode modifiers
_cursorX:		.skip 1; + 07h: Cursor X position
_cursorY:		.skip 1; + 08h: Cursor Y position
_scrchar:		.skip 1; + 09h: Character read from screen
_scrpixel:		.skip 3; + 0Ah: Pixel data read from screen (R,B,G)
_audioChannel:		.skip 1; + 0Dh: Audio channel 
_audioSuccess:		.skip 1; + 0Eh: Audio channel note queued (0 = no, 1 = yes)
_scrwidth:		.skip 2; + 0Fh: Screen width in pixels
_scrheight:		.skip 2; + 11h: Screen height in pixels
_scrcols:		.skip 1; + 13h: Screen columns in characters
_scrrows:		.skip 1; + 14h: Screen rows in characters
_scrcolours:		.skip 1; + 15h: Number of colours displayed
_scrpixelIndex:		.skip 1; + 16h: Index of pixel data read from screen
_keycode:		.skip 1; + 17h: Virtual key code from FabGL
_keydown:		.skip 1; + 18h; Virtual key state from FabGL (0=up, 1=down)
_keycount:		.skip 1; + 19h: Incremented every time a key packet is received
_rtc:			.skip 6; + 1Ah: Real time clock data
			.skip 2; + 20h: Spare, previously used by rtc
_keydelay:		.skip 2; + 22h: Keyboard repeat delay
_keyrate:		.skip 2; + 24h: Keyboard repeat rate
_keyled:		.skip 1; + 26h: Keyboard LED status
_scrmode:		.skip 1; + 27h: Screen mode
_rtc_enable:		.skip 1; + 28h: RTC enable status
_mouseX:		.skip 2; + 29h: Mouse X position
_mouseY:		.skip 2; + 2Bh: Mouse Y position
_mouseButtons:		.skip 1; + 2Dh: Mouse left+right+middle buttons (bits 0-2, 0=up, 1=down)
_mouseWheel:		.skip 1; + 2Eh: Mouse wheel delta
_mouseXDelta:		.skip 2; + 2Fh: Mouse X delta
_mouseYDelta:		.skip 2; + 31h: Mouse Y delta

_errno:			.skip 3; extern int _errno
_coldBoot:		.skip 1; extern char _coldBoot
_gp:			.skip 1; extern char _gp

; Serial Flags:
;
; - Bit 0: UART0 enabled
; - Bit 1: UART0 hardware flow control
; - Bit 4: UART1 enabled
; - Bit 5: UART1 hardware flow control
;
_serialFlags:		.skip 1; extern char _serialFlags

_callSM:		.skip 5; Self-modding code for CALL.IS (HL)
_scratchpad:		.skip 8; General purpose scratchpad RAM for use within functions

; Keyboard map
;
_keymap:		.skip 16; A bitmap of pressed keys

; VDP Protocol Flags
;
; Bit 0: Cursor packet received
; Bit 1: Screen character packet received
; Bit 2: Pixel point packet received
; Bit 3: Audio packet received
; Bit 4: Mode packet received
; Bit 5: RTC packet received
; Bit 6: Mouse packet received
; Bit 7: Unused
;
; VDP protocol variables
;
_vdp_protocol_state:	.skip 1; UART state
_vdp_protocol_cmd:	.skip 1; Command
_vdp_protocol_len:	.skip 1; Size of packet data
_vdp_protocol_ptr:	.skip 3; Pointer into data
_vdp_protocol_data:	.skip VDPP_BUFFERLEN

;
; Userspace hooks
;
_user_kbvector: 	.skip 3; Pointer to keyboard function

; I2C
;
_i2c_slave_rw:		.skip 1; 7 bit slave address + R/W bit
_i2c_error:		.skip 1; Error report to caller application
_i2c_role:		.skip 1; I2C current state
_i2c_msg_ptr:		.skip 3; Pointer to the current buffer
_i2c_msg_size:		.skip 1; The (remaining) message size

; Command history
;
_history_no:		.skip 1
_history_size:		.skip 1

			.section .data; This section is copied to RAM in cstartup.asm

			; zds2gas: END
