; Native AgonDev source derived from official MOS v3.0.2: src/vdp_protocol.asm
; Upstream ancestry and changes: docs/upstream-origin.md and docs/deviations.md.
;
; Title:	AGON MOS - VDP serial protocol
; Author:	Dean Belfield
; Created:	03/08/2022
; Last Updated:	26/09/2023
;
; Modinfo:
; 09/08/2022:	Added vdp_protocol_CURSOR
; 18/08/2022:	Added vpd_protocol_SCRCHAR, vpd_protocol_POINT, vdp_protocol_AUDIO, bounds checking for protocol
; 18/09/2022:	Added vdp_protocol_MODE
; 13/02/2023:	Bug fix vpd_protocol_MODE now returns correct scrheight
; 23/02/2023:	vdp_protocol_MODE now returns number of screen colours
; 04/03/2023:	Added _scrpixelIndex to vpd_protocol_POINT
; 09/03/2023:	Added FabGL virtual key data to vdp_protocol_KEY, reset is now CTRL+ALT+DEL
; 15/03/2023:	Added vdp_protocol_RTC
; 21/03/2023:	Added vdp_protocol_KEYSTATE
; 26/03/2023:	Added vdp_protocol_GP, checks DEL above cursor block for CTRL+ALT+DEL
; 19/05/2023:	Extended vdp_protocol_MODE to store scrmode
; 03/08/2023:	Added user_kbvector in vdp_protocol_KEY
; 13/08/2023:	Moved keyboard handling to keyboard.asm
; 26/09/2023:	RTC packet length reduced to 6 bytes

			.include "macros.inc"
			.include "equs.inc"

			.assume adl=1

			; zds2gas: DEFINE .STARTUP, SPACE = ROM
			.section .STARTUP,"ax",@progbits

			.global	vdp_protocol

			.extern	_keyascii
			.extern	_keycode
			.extern	_keymods
			.extern	_keydown
			.extern	_keycount
			.extern	_cursorX
			.extern	_cursorY
			.extern	_scrchar
			.extern	_scrpixel
			.extern	_audioChannel
			.extern	_audioSuccess
			.extern	_scrwidth
			.extern	_scrheight
			.extern	_scrcols
			.extern	_scrrows
			.extern	_scrcolours
			.extern	_scrpixelIndex
			.extern	_scrmode
			.extern	_rtc
			.extern	_keydelay
			.extern	_keyrate
			.extern 	_keyled
			.extern	_mouseX
			.extern	_gp
			.extern	_vpd_protocol_flags
			.extern	_vdp_protocol_state
			.extern	_vdp_protocol_cmd
			.extern	_vdp_protocol_len
			.extern	_vdp_protocol_ptr
			.extern	_vdp_protocol_data

			.extern	_user_kbvector

			.extern	keyboard_handler	; In keyboard.asm
;
; The UART protocol handler state machine
;
vdp_protocol:		ld	A, (_vdp_protocol_state)
			or	A
			jr	Z, vdp_protocol_state0
			dec	A
			jr	Z, vdp_protocol_state1
			dec	A
			jr	Z, vdp_protocol_state2
			dec	A
			jp	Z, vdp_protocol_state3 ; [DEV-006: ZDS relaxes this long JR; GNU requires explicit JP.]
			xor	A
			ld	(_vdp_protocol_state), A
			ret
;
; Wait for control byte (>=80h)
;
vdp_protocol_state0:	ld	A, C			; Wait for a header byte (bit 7 set)
			sub	0x80
			ret	C
			ld	(_vdp_protocol_cmd), A	; Store the cmd (discard the top bit)
			ld	(_vdp_protocol_ptr), HL	; Store the buffer pointer
			ld	A, 1			; Switch to next state
			ld	(_vdp_protocol_state), A
			ret

;
; Read the packet length in
;
vdp_protocol_state1:	ld	A, C			; Fetch the length byte
			cp	VDPP_BUFFERLEN + 1	; Check if it exceeds buffer length (16)
			jr	C, 1f			;
			ld	A, 3			; If it does exceed buffer length, switch to state 3 (ignore packet)
			ld	(_vdp_protocol_state), A
			ret
;
1:			ld	(_vdp_protocol_len), A	; Store the length
			or	A			; If it is zero
			jr	Z, vdp_protocol_exec	; Then we can skip fetching bytes, otherwise
			ld	A, 2			; Switch to next state
			ld	(_vdp_protocol_state), A
			ret

; Read the packet body in
;
vdp_protocol_state2:	ld	HL, (_vdp_protocol_ptr)	; Get the buffer pointer
			ld	(HL), C			; Store the byte in it
			inc	HL			; Increment the buffer pointer
			ld	(_vdp_protocol_ptr), HL
			ld	A, (_vdp_protocol_len)	; Decrement the length
			dec	A
			ld	(_vdp_protocol_len), A
			ret	NZ			; Stay in this state if there are still bytes to read
;
; When len is 0, we can action the packet
;

vdp_protocol_exec:	xor	A			; Reset the state
			ld	(_vdp_protocol_state), A
			ld	A, (_vdp_protocol_cmd)	; Get the command byte...
			cp	vdp_protocol_vesize	; Check whether the command is in bounds
			ret	NC			; Out of bounds, so just ignore
			ld	DE, vdp_protocol_vector
			ld	HL, 0			; Index into the jump table
			ld	L, A			; ...in HLU
			add	HL, HL			; Multiply by four, as each entry is 4 bytes
			add	HL, HL			; And add the address of the vector table
			add	HL, DE
			jp	(HL)			; And jump to the entry in the jump table
;
; Jump table for UART commands
;
vdp_protocol_vector:	jp	vdp_protocol_GP
			jp	vdp_protocol_KEY
			jp	vdp_protocol_CURSOR
			jp	vpd_protocol_SCRCHAR
			jp	vdp_protocol_POINT
			jp	vdp_protocol_AUDIO
			jp	vdp_protocol_MODE
			jp	vdp_protocol_RTC
			jp	vdp_protocol_KEYSTATE
			jp	vdp_protocol_MOUSE
;
.equiv vdp_protocol_vesize, (.-vdp_protocol_vector)/4

;
; Discard data (packet too long)
;
vdp_protocol_state3:	ld	A, (_vdp_protocol_len)
			dec	A
			ld	(_vdp_protocol_len), A
			ret	NZ			; Stay in this state if there are still bytes to read
			xor	A			; Reset the state
			ld	(_vdp_protocol_state), A
			ret

; General Poll
;
vdp_protocol_GP:	ld	A, (_vdp_protocol_data + 0)
			ld	(_gp), A
			ret

; Keyboard Data
; Received after a keypress event in the VPD
;
vdp_protocol_KEY:	ld	HL, (_user_kbvector)		; If a user kbvector is set, call it
			ld	DE, 0
			or	A
			sbc	HL, DE
			jr	Z, 1f
			ld	HL, 1f
			push	HL				; Push return address from user routine
			ld	HL, (_user_kbvector)
			ld	DE, _vdp_protocol_data		; Pass keyboard packet address to user routine in DE (24-bit)
			jp	(HL)
;
1:			ld	A, (_vdp_protocol_data + 0)	; ASCII key code
			ld	(_keyascii), A
			ld	A, (_vdp_protocol_data + 1)	; Key modifiers (SHIFT, ALT, etc)
			ld	(_keymods), A
			ld	A, (_vdp_protocol_data + 3)	; Key down? (1=down, 0=up)
			ld	C, A				; C: Keydown
			ld	(_keydown), A
			ld	A, (_keycount)			; Increment the key event counter
			inc	A
			ld	(_keycount), A
			ld	A, (_vdp_protocol_data + 2)	; Virtual key code
			ld	B, A 				; B: Virtual keycode
			ld	(_keycode), A
;
			jp	keyboard_handler		; Call the handle keyboard routine (in keyboard.asm)

; Cursor data
; Received after the cursor position is updated in the VPD
;
; Byte: Cursor X
; Byte: Cursor Y
;
; Sets vpd_protocol_flags to flag receipt to apps
;
vdp_protocol_CURSOR:	ld	A, (_vdp_protocol_data+0)
			ld	(_cursorX), A
			ld	A, (_vdp_protocol_data+1)
			ld	(_cursorY), A
			ld	A, (_vpd_protocol_flags)
			or	VDPP_FLAG_CURSOR
			ld	(_vpd_protocol_flags), A
			ret

; Screen character data
; Received after VDU 23,0,0,x;y;
;
; Byte: ASCII code of character
;
; Sets vpd_protocol_flags to flag receipt to apps
;
vpd_protocol_SCRCHAR:	ld	A, (_vdp_protocol_data+0)
			ld	(_scrchar), A
			ld	A, (_vpd_protocol_flags)
			or	VDPP_FLAG_SCRCHAR
			ld	(_vpd_protocol_flags), A
			ret

; Pixel value data (RGB)
; Received after VDU 23,0,1,x;y;
;
; Byte: Red component of read pixel
; Byte: Green component of read pixel
; Byte: Blue component of read pixel
; Byte: The palette index
;
; Sets vpd_protocol_flags to flag receipt to apps
;
vdp_protocol_POINT:	ld	HL, (_vdp_protocol_data+0)
			ld	(_scrpixel), HL
			ld	A, (_vdp_protocol_data+3)
			ld	(_scrpixelIndex), A
			ld	A, (_vpd_protocol_flags)
			or	VDPP_FLAG_POINT
			ld	(_vpd_protocol_flags), A
			ret

; Audio acknowledgement
; Received after VDU 23,0,5,channel,volume,frequency,duration
;
; Byte: channel
; Byte: success (1 if successful, otherwise 0)
;
; Sets vpd_protocol_flags to flag receipt to apps
;
vdp_protocol_AUDIO:	ld	A, (_vdp_protocol_data+0)
			ld	(_audioChannel), A
			ld	A, (_vdp_protocol_data+1)
			ld	(_audioSuccess), A
			ld	A, (_vpd_protocol_flags)
			or	VDPP_FLAG_AUDIO
			ld	(_vpd_protocol_flags), A
			ret

; Screen mode details
; Received after VDU 23,0,6 or VDU 17, n
;
; Word: Screen width in pixels
; Word: Screen height in pixels
; Byte: Screen width in characters
; Byte: Screen height in characters
; Byte: Number of colours
; Byte: Screen mode
;
; Sets vpd_protocol_flags to flag receipt to apps
;
vdp_protocol_MODE:	ld	A, (_vdp_protocol_data+0)
			ld	(_scrwidth), A
			ld	A, (_vdp_protocol_data+1)
			ld	(_scrwidth+1), A
			ld	A, (_vdp_protocol_data+2)
			ld	(_scrheight), A
			ld	A, (_vdp_protocol_data+3)
			ld	(_scrheight+1), A
			ld	A, (_vdp_protocol_data+4)
			ld	(_scrcols), A
			ld	A, (_vdp_protocol_data+5)
			ld	(_scrrows), A
			ld	A, (_vdp_protocol_data+6)
			ld	(_scrcolours), A
			ld	A, (_vdp_protocol_data+7)
			ld	(_scrmode), A
			ld	A, (_vpd_protocol_flags)
			or	VDPP_FLAG_MODE
			ld	(_vpd_protocol_flags), A
			ret

; RTC
; Received after VDU 23,0,7
;
; See vdp_time_t struct in clock.h for details
;
; Sets vpd_protocol_flags to flag receipt to apps
;
vdp_protocol_RTC:	ld	HL, _vdp_protocol_data
			ld	DE, _rtc
			ld	BC,  6
			ldir
			ld	A, (_vpd_protocol_flags)
			or	VDPP_FLAG_RTC
			ld	(_vpd_protocol_flags), A
			ret

; Keyboard status
; Received after VDU 23,0,8,delay;rate;led
;
; Word:	delay
; Word: rate
; Byte: led status
;
vdp_protocol_KEYSTATE:	ld	HL, _vdp_protocol_data
			ld	DE, _keydelay
			ld	BC, 5
			ldir
			ret

; Mouse data
; Received after a mouse movement event, if mouse has been activated
;
; Word: X position
; Word: Y position
; Byte: Button state
; Byte: Wheel delta
; Word: X delta
; Word: Y delta
;
vdp_protocol_MOUSE:	ld	HL, _vdp_protocol_data
			ld	DE, _mouseX
			ld	BC, 10
			ldir
			ld	A, (_vpd_protocol_flags)
			or	VDPP_FLAG_MOUSE
			ld	(_vpd_protocol_flags), A
			ret
