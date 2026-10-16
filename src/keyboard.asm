; Native AgonDev source derived from official MOS v3.0.2: src/keyboard.asm
; Upstream ancestry and changes: docs/upstream-origin.md and docs/deviations.md.
;
; Title:	AGON MOS - Keyboard routines
; Author:	Dean Belfield
; Created:	13/08/2023
; Last Updated:	13/08/2023
;
; Modinfo:
			.include "macros.inc"
			.include "equs.inc"

			.ASSUME	ADL = 1

			; zds2gas: DEFINE .STARTUP, SPACE = ROM
			.section .STARTUP,"ax",@progbits

			XDEF	keyboard_handler

			XREF	_keymods 			; In globals.asm
			XREF	_keyascii
			XREF	_keycode
			XREF	_keymap

; Agon keyboard routines
;  C: Keydown state (1 = pressed 0 = depressed)
;  B: Virtual keycode
;
keyboard_handler:	LD	A, B
			OR	A
			CALL	NZ, keyboard_map
			JP	keyboard_reset

; Write key up and down states to the keymap
;  C: Keydown state (1 = pressed 0 = depressed)
;  A: Virtual keycode
;
keyboard_map:		DEC	A 				;  A: Virtual keycode - 1
			LD	DE, keyboard_lookup		; DE: Address of keyboard lookup table
			LD	HL, 0
			LD	L, A 
			ADD	HL, HL 
			ADD	HL, HL				; HL: Virtual keycode x 4
			ADD	HL, DE				; HL: Address of key data in keyboard lookup
			LD	A, (HL)				;  A: Bit to set
			OR	A				; Check for empty entry
			RET	Z				; Yep, nothing to set here, so return
			INC	HL
			LD	HL, (HL)			; HL: Address to set into
			BIT 	0, C				; Is the key down or up?
			JR	NZ, .Lzds_src_keyboard_asm_cae44684_a0001 				; It is down so jump to the code that sets a bit
			CPL					; It is up so complement the bit
			AND	(HL)				; Then AND it with the keymap entry
			LD	(HL), A
			RET 
;
.Lzds_src_keyboard_asm_cae44684_a0001:			OR	(HL)				; OR with the keymap entry
			LD	(HL), A
			RET 
;			
; Now check for CTRL+ALT+DEL
;
keyboard_reset:		LD	A, B				; Get the virtual key code
			CP	130				; Check for DEL (cursor keys)
			JR	Z, .Lzds_src_keyboard_asm_cae44684_a0002
			CP	131				; Check for DEL (no numlock)
			JR	Z , .Lzds_src_keyboard_asm_cae44684_a0002
			CP	88				; And DEL (numlock)
			RET	NZ
.Lzds_src_keyboard_asm_cae44684_a0002:			LD	A, (_keymods)			; DEL is pressed so check CTRL + ALT
			AND	0x05				; Bit 0 and 2
			CP	0x05
			RET	NZ				; Exit if not pressed
;
; Here we're just waiting for the key to go up
;
			LD	A, C				; Get key down
			DEC	A				; Check for 0 (key up)
			JP	NZ, 0				; Yes so reset
			LD	(_keyascii), A			; Otherwise clear the keycode so no interaction with console 
			LD	(_keycode), A 
			RET

; Lookup table to convert virtual keycodes to physical keys (BBC BASIC specification)
; Uses the macro KEY to store each key as an index and a bit
; Four bytes of data per key
; - 1 byte:  The bit data to set into the keymap
; - 3 bytes: The address to set (precalculated)
;
.macro zds_KEY VKEYCODE
			.if	\VKEYCODE = 0
			d32 	0
			.else
			DB	1 << ((\VKEYCODE - 1) & 0b00000111)
			d24	_keymap + (((\VKEYCODE - 1) & 0b11111000) >> 3)
			.endif 
			.endm
;
keyboard_lookup:	zds_KEY 099; VK_SPACE
			zds_KEY 040; VK_0
			zds_KEY 049; VK_1
			zds_KEY 050; VK_2
			zds_KEY 018; VK_3
			zds_KEY 019; VK_4
			zds_KEY 020; VK_5
			zds_KEY 053; VK_6
			zds_KEY 037; VK_7
			zds_KEY 022; VK_8
			zds_KEY 039; VK_9
			zds_KEY 107; VK_KP_0
			zds_KEY 108; VK_KP_1
			zds_KEY 125; VK_KP_2
			zds_KEY 109; VK_KP_3
			zds_KEY 123; VK_KP_4
			zds_KEY 124; VK_KP_5
			zds_KEY 027; VK_KP_6
			zds_KEY 028; VK_KP_7
			zds_KEY 043; VK_KP_8
			zds_KEY 044; VK_KP_9
			zds_KEY 066; VK_a
			zds_KEY 101; VK_b
			zds_KEY 083; VK_c
			zds_KEY 051; VK_d
			zds_KEY 035; VK_e
			zds_KEY 068; VK_f
			zds_KEY 084; VK_g
			zds_KEY 085; VK_h
			zds_KEY 038; VK_i
			zds_KEY 070; VK_j
			zds_KEY 071; VK_k
			zds_KEY 087; VK_l
			zds_KEY 102; VK_m
			zds_KEY 086; VK_n
			zds_KEY 055; VK_o
			zds_KEY 056; VK_p
			zds_KEY 017; VK_q
			zds_KEY 052; VK_r
			zds_KEY 082; VK_s
			zds_KEY 036; VK_t
			zds_KEY 054; VK_u
			zds_KEY 100; VK_v
			zds_KEY 034; VK_w
			zds_KEY 067; VK_x
			zds_KEY 069; VK_y
			zds_KEY 098; VK_z
			zds_KEY 066; VK_A
			zds_KEY 101; VK_B
			zds_KEY 083; VK_C
			zds_KEY 051; VK_D
			zds_KEY 035; VK_E
			zds_KEY 068; VK_F
			zds_KEY 084; VK_G
			zds_KEY 085; VK_H
			zds_KEY 038; VK_I
			zds_KEY 070; VK_J
			zds_KEY 071; VK_K
			zds_KEY 087; VK_L
			zds_KEY 102; VK_M
			zds_KEY 086; VK_N
			zds_KEY 055; VK_O
			zds_KEY 056; VK_P
			zds_KEY 017; VK_Q
			zds_KEY 052; VK_R
			zds_KEY 082; VK_S
			zds_KEY 036; VK_T
			zds_KEY 054; VK_U
			zds_KEY 100; VK_V
			zds_KEY 034; VK_W
			zds_KEY 067; VK_X
			zds_KEY 069; VK_Y
			zds_KEY 098; VK_Z              
			zds_KEY 046; VK_GRAVEACCENT
			zds_KEY 000; VK_ACUTEACCENT
			zds_KEY 072; VK_QUOTE
			zds_KEY 000; VK_QUOTEDBL
			zds_KEY 094; VK_EQUALS
			zds_KEY 024; VK_MINUS
			zds_KEY 060; VK_KP_MINUS
			zds_KEY 094; VK_PLUS
			zds_KEY 059; VK_KP_PLUS
			zds_KEY 092; VK_KP_MULTIPLY
			zds_KEY 000; VK_ASTERISK
			zds_KEY 000; VK_BACKSLASH
			zds_KEY 075; VK_KP_DIVIDE
			zds_KEY 105; VK_SLASH
			zds_KEY 077; VK_KP_PERIOD
			zds_KEY 104; VK_PERIOD
			zds_KEY 073; VK_COLON
			zds_KEY 103; VK_COMMA
			zds_KEY 088; VK_SEMICOLON
			zds_KEY 000; VK_AMPERSAND
			zds_KEY 000; VK_VERTICALBAR
			zds_KEY 000; VK_HASH
			zds_KEY 072; VK_AT  
			zds_KEY 025; VK_CARET
			zds_KEY 000; VK_DOLLAR
			zds_KEY 000; VK_POUND
			zds_KEY 000; VK_EURO
			zds_KEY 000; VK_PERCENT
			zds_KEY 000; VK_EXCLAIM
			zds_KEY 000; VK_QUESTION
			zds_KEY 000; VK_LEFTBRACE
			zds_KEY 000; VK_RIGHTBRACE
			zds_KEY 057; VK_LEFTBRACKET
			zds_KEY 089; VK_RIGHTBRACKET
			zds_KEY 000; VK_LEFTPAREN
			zds_KEY 000; VK_RIGHTPAREN
			zds_KEY 103; VK_LESS
			zds_KEY 104; VK_GREATER
			zds_KEY 096; VK_UNDERSCORE
			zds_KEY 000; VK_DEGREE
			zds_KEY 000; VK_SECTION
			zds_KEY 046; VK_TILDE
			zds_KEY 024; VK_NEGATION
			zds_KEY 004; VK_LSHIFT
			zds_KEY 007; VK_RSHIFT
			zds_KEY 006; VK_LALT
			zds_KEY 009; VK_RALT
			zds_KEY 005; VK_LCTRL
			zds_KEY 008; VK_RCTRL
			zds_KEY 126; VK_LGUI
			zds_KEY 127; VK_RGUI
			zds_KEY 113; VK_ESCAPE
			zds_KEY 033; VK_PRINTSCREEN
			zds_KEY 000; VK_SYSREQ
			zds_KEY 062; VK_INSERT
			zds_KEY 062; VK_KP_INSERT
			zds_KEY 090; VK_DELETE
			zds_KEY 076; VK_KP_DELETE
			zds_KEY 048; VK_BACKSPACE
			zds_KEY 063; VK_HOME
			zds_KEY 063; VK_KP_HOME
			zds_KEY 106; VK_END 
			zds_KEY 106; VK_KP_END
			zds_KEY 000; VK_PAUSE
			zds_KEY 045; VK_BREAK
			zds_KEY 032; VK_SCROLLLOCK
			zds_KEY 078; VK_NUMLOCK
			zds_KEY 065; VK_CAPSLOCK
			zds_KEY 097; VK_TAB 
			zds_KEY 074; VK_RETURN
			zds_KEY 061; VK_KP_ENTER
			zds_KEY 128; VK_APPLICATION
			zds_KEY 064; VK_PAGEUP
			zds_KEY 064; VK_KP_PAGEUP
			zds_KEY 079; VK_PAGEDOWN
			zds_KEY 079; VK_KP_PAGEDOWN
			zds_KEY 058; VK_UP  
			zds_KEY 058; VK_KP_UP
			zds_KEY 042; VK_DOWN
			zds_KEY 042; VK_KP_DOWN
			zds_KEY 026; VK_LEFT
			zds_KEY 026; VK_KP_LEFT
			zds_KEY 122; VK_RIGHT
			zds_KEY 122; VK_KP_RIGHT
			zds_KEY 000; VK_KP_CENTER
			zds_KEY 114; VK_F1  
			zds_KEY 115; VK_F2  
			zds_KEY 116; VK_F3  
			zds_KEY 021; VK_F4  
			zds_KEY 117; VK_F5  
			zds_KEY 118; VK_F6  
			zds_KEY 023; VK_F7  
			zds_KEY 119; VK_F8  
			zds_KEY 120; VK_F9  
			zds_KEY 031; VK_F10 
			zds_KEY 029; VK_F11 
			zds_KEY 030; VK_F12 
			zds_KEY 000; VK_GRAVE_a
			zds_KEY 000; VK_GRAVE_e
			zds_KEY 000; VK_GRAVE_i
			zds_KEY 000; VK_GRAVE_o
			zds_KEY 000; VK_GRAVE_u
			zds_KEY 000; VK_GRAVE_y
			zds_KEY 000; VK_ACUTE_a
			zds_KEY 000; VK_ACUTE_e
			zds_KEY 000; VK_ACUTE_i
			zds_KEY 000; VK_ACUTE_o
			zds_KEY 000; VK_ACUTE_u
			zds_KEY 000; VK_ACUTE_y
			zds_KEY 000; VK_GRAVE_A
			zds_KEY 000; VK_GRAVE_E
			zds_KEY 000; VK_GRAVE_I
			zds_KEY 000; VK_GRAVE_O
			zds_KEY 000; VK_GRAVE_U
			zds_KEY 000; VK_GRAVE_Y
			zds_KEY 000; VK_ACUTE_A
			zds_KEY 000; VK_ACUTE_E
			zds_KEY 000; VK_ACUTE_I
			zds_KEY 000; VK_ACUTE_O
			zds_KEY 000; VK_ACUTE_U
			zds_KEY 000; VK_ACUTE_Y
			zds_KEY 000; VK_UMLAUT_a
			zds_KEY 000; VK_UMLAUT_e
			zds_KEY 000; VK_UMLAUT_i
			zds_KEY 000; VK_UMLAUT_o
			zds_KEY 000; VK_UMLAUT_u
			zds_KEY 000; VK_UMLAUT_y
			zds_KEY 000; VK_UMLAUT_A
			zds_KEY 000; VK_UMLAUT_E
			zds_KEY 000; VK_UMLAUT_I
			zds_KEY 000; VK_UMLAUT_O
			zds_KEY 000; VK_UMLAUT_U
			zds_KEY 000; VK_UMLAUT_Y
			zds_KEY 000; VK_CARET_a
			zds_KEY 000; VK_CARET_e
			zds_KEY 000; VK_CARET_i
			zds_KEY 000; VK_CARET_o
			zds_KEY 000; VK_CARET_u
			zds_KEY 000; VK_CARET_y
			zds_KEY 000; VK_CARET_A
			zds_KEY 000; VK_CARET_E
			zds_KEY 000; VK_CARET_I
			zds_KEY 000; VK_CARET_O
			zds_KEY 000; VK_CARET_U
			zds_KEY 000; VK_CARET_Y
			zds_KEY 000; VK_CEDILLA_c
			zds_KEY 000; VK_CEDILLA_C
			zds_KEY 000; VK_TILDE_a
			zds_KEY 000; VK_TILDE_o
			zds_KEY 000; VK_TILDE_n
			zds_KEY 000; VK_TILDE_A
			zds_KEY 000; VK_TILDE_O
			zds_KEY 000; VK_TILDE_N
			zds_KEY 000; VK_UPPER_a
			zds_KEY 000; VK_ESZETT
			zds_KEY 000; VK_EXCLAIM_INV
			zds_KEY 000; VK_QUESTION_INV
			zds_KEY 000; VK_INTERPUNCT
			zds_KEY 000; VK_DIAERESIS
			zds_KEY 000; VK_SQUARE
			zds_KEY 000; VK_CURRENCY
			zds_KEY 000; VK_MU  
			zds_KEY 000; VK_aelig
			zds_KEY 000; VK_oslash
			zds_KEY 000; VK_aring
			zds_KEY 000; VK_AELIG
			zds_KEY 000; VK_OSLASH
			zds_KEY 000; VK_ARING
			zds_KEY 000; VK_YEN
			zds_KEY 000; VK_MUHENKAN
			zds_KEY 000; VK_HENKAN
			zds_KEY 000; VK_KATAKANA_HIRAGANA_ROMAJI
			zds_KEY 000; VK_HANKAKU_ZENKAKU_KANJI
			zds_KEY 000; VK_SHIFT_0
			zds_KEY 000; VK_ASCII
