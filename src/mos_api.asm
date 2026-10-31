; Maintained native UART variant: src/mos_api.asm; origin: docs/uart0-native-source.md.
;
; Title:	AGON MOS - API code
; Author:	Dean Belfield
; Created:	24/07/2022
; Last Updated:	10/11/2023
;
; Modinfo:
; 03/08/2022:	Added a handful of MOS API calls and stubbed FatFS calls
; 05/08/2022:	Added mos_FEOF, saved affected registers in fopen, fclose, fgetc, fputc and feof
; 09/08/2022:	mos_api_sysvars now returns pointer to _sysvars
; 05/09/2022:	Added mos_REN
; 24/09/2022:	Error codes returned for MOS commands
; 13/10/2022:	Added mos_OSCLI and supporting code
; 20/10/2022:	Tweaked error handling
; 13/03/2023:	Renamed keycode to keyascii, fixed mos_api_getkey, added parameter to mos_api_dir
; 15/03/2023:	Added mos_api_copy, mos_api_getrtc, mos_api_setrtc
; 21/03/2023:	Added mos_api_setintvector
; 24/03/2023:	Fixed bugs in mos_api_setintvector
; 28/03/2023:	Function mos_api_setintvector now only accepts a 24-bit pointer
; 29/03/2023:	Added mos_api_uopen, mos_api_uclose, mos_api_ugetc, mos_api_uputc
; 14/04/2023:	Added ffs_api_fopen, ffs_api_fclose, ffs_api_stat, ffs_api_fread, ffs_api_fwrite, ffs_api_feof, ffs_api_flseek
; 15/04/2023:	Added mos_api_getfil, mos_api_fread, mos_api_fwrite and mos_api_flseek
; 30/05/2023:	Fixed mos_api_fgetc to set carry if at end of file
; 03/08/2023:	Added mos_api_setkbvector
; 10/08/2023:	Added mos_api_getkbmap
; 10/11/2023:	Added mos_api_i2c_close, mos_api_i2c_open, mos_api_i2c_read, mos_api_i2c_write


			.include "mos_api.inc"
			.assume adl=1

			; Original segment placement: DEFINE .STARTUP, SPACE = ROM
			.section .STARTUP,"ax",@progbits

			.global	mos_api

			.extern	SWITCH_A		; In misc.asm
			.extern	SET_AHL24
			.extern	FIX_HLU24
			.extern	FIX_HLU24_no_mb_check
			.extern	SET_ADE24
			.extern	SET_ABC24
			.extern	SET_AIX24

			.extern	_mos_OSCLI		; In mos.c
			.extern	_mos_EDITLINE
			.extern	_mos_LOAD_API
			.extern	_mos_SAVE_API
			.extern	_mos_CD_API
			.extern	_mos_DIR_API
			.extern	_mos_DEL
			.extern	_mos_REN_API
			.extern	_mos_FOPEN
			.extern	_mos_FCLOSE
			.extern	_mos_FGETC
			.extern	_mos_FPUTC
			.extern	_mos_FEOF
			.extern	_mos_GETERROR
			.extern	_mos_MKDIR_API
			.extern	_mos_COPY_API
			.extern	_mos_GETRTC
			.extern	_mos_UNPACKRTC
			.extern	_mos_SETRTC
			.extern	_mos_SETINTVECTOR
			.extern	_mos_GETFIL
			.extern	_mos_FREAD
			.extern	_mos_FWRITE
			.extern	_mos_FLSEEK
			.extern	_mos_FLSEEKP
			.extern	_mos_I2C_OPEN
			.extern	_mos_I2C_CLOSE
			.extern	_mos_I2C_WRITE
			.extern	_mos_I2C_READ
			.extern	_mos_mount

			.extern	_fat_tell		; In mos.c
			.extern	_fat_EOF
			.extern	_fat_size
			.extern	_fat_error
			.extern	_fat_lseek
			.extern	_fat_getfree
			.extern	_wait_VDP

			.extern	_open_UART1		; In uart.c
			.extern	_close_UART1

			.extern	UART1_serial_GETCH	; In serial.asm
			.extern	UART1_serial_PUTCH

			.extern	_keyascii		; In globals.asm
			.extern	_keycount
			.extern	_keydown
			.extern	_sysvars
			.extern	_scratchpad
			.extern	_vpd_protocol_flags
			.extern	uart0_return_fence,uart0_async_getapi
			.extern	_user_kbvector
			.extern	_keymap

			.extern	_f_open			; In ff.c
			.extern	_f_close
			.extern	_f_read
			.extern	_f_write
			.extern	_f_lseek
			.extern	_f_truncate
			.extern	_f_sync
			.extern	_f_gets
			.extern	_f_putc
			.extern	_f_puts
			.extern	_f_printf
			.extern	_f_opendir
			.extern	_f_closedir
			.extern	_f_readdir
			.extern	_f_findfirst
			.extern	_f_findnext
			.extern	_f_stat
			.extern	_f_unlink
			.extern	_f_rename
			.extern	_f_mkdir
			.extern	_f_chdir
			.extern	_f_getcwd
			.extern	_f_getlabel
			.extern	_f_setlabel

			.extern	_pmatch			; In strings.c

			.extern	_getArgument		; In mos_sysvars.c
			.extern	_extractString
			.extern	_extractNumber
			.extern	_escapeString
			.extern	_setVarVal
			.extern	_readVarVal
			.extern	_gsInit
			.extern	_gsRead
			.extern	_gsTrans
			.extern	_substituteArgs
			; XREF	_evaluateExpression

			.extern	_resolvePath		; In mos_file.c
			.extern	_getDirectoryForPath
			.extern	_getFilepathLeafname
			.extern	_isDirectory
			.extern	_resolveRelativePath

			.extern	_SD_getUnlockCode	; In sd.h
			.extern	_SD_init_API
			.extern	_SD_readBlocks_API
			.extern	_SD_writeBlocks_API
			.extern	_SD_init
			.extern	_SD_readBlocks
			.extern	_SD_writeBlocks

; Call a MOS API function
; 00h - 7Fh: Reserved for high level MOS calls
; 80h - FFh: Reserved for low level calls to FatFS
;  A: function to call
;
mos_api:		cp	0x80			; Check if it is a FatFS command
			jp	NC, 1f			; DEV-006: preserve foundation's explicit long branch.
			cp	mos_api_block1_size	; Check if out of bounds
			jp	NC, mos_api_not_implemented
			call	SWITCH_A		; Switch on this table
;
mos_api_block1_start:	dw	mos_api_getkey		; 0x00
			dw	mos_api_load		; 0x01
			dw	mos_api_save		; 0x02
			dw	mos_api_cd		; 0x03
			dw	mos_api_dir		; 0x04
			dw	mos_api_del		; 0x05
			dw	mos_api_ren		; 0x06
			dw	mos_api_mkdir		; 0x07
			dw	mos_api_sysvars		; 0x08
			dw	mos_api_editline	; 0x09
			dw	mos_api_fopen		; 0x0A
			dw	mos_api_fclose		; 0x0B
			dw	mos_api_fgetc		; 0x0C
			dw	mos_api_fputc		; 0x0D
			dw	mos_api_feof		; 0x0E
			dw	mos_api_getError	; 0x0F
			dw	mos_api_oscli		; 0x10
			dw	mos_api_copy		; 0x11
			dw	mos_api_getrtc		; 0x12
			dw	mos_api_setrtc		; 0x13
			dw	mos_api_setintvector	; 0x14
			dw	mos_api_uopen		; 0x15
			dw 	mos_api_uclose		; 0x16
			dw	mos_api_ugetc		; 0x17
			dw	mos_api_uputc		; 0x18
			dw	mos_api_getfil		; 0x19
			dw	mos_api_fread		; 0x1A
			dw	mos_api_fwrite		; 0x1B
			dw	mos_api_flseek		; 0x1C
			dw	mos_api_setkbvector	; 0x1D
			dw	mos_api_getkbmap	; 0x1E
			dw	mos_api_i2c_open	; 0x1F
			dw	mos_api_i2c_close	; 0x20
			dw	mos_api_i2c_write	; 0x21
			dw	mos_api_i2c_read	; 0x22
			dw	mos_api_unpackrtc	; 0x23
			dw	mos_api_flseek_p	; 0x24

			dw	mos_api_not_implemented	; 0x25
			dw	mos_api_not_implemented	; 0x26
			dw	mos_api_not_implemented	; 0x27

			dw	mos_api_pmatch		; 0x28
			dw	mos_api_getargument	; 0x29
			dw	mos_api_extractstring	; 0x2a
			dw	mos_api_extractnumber	; 0x2b
			dw	mos_api_escapestring	; 0x2c
			dw	mos_api_not_implemented	; 0x2d
			dw	mos_api_not_implemented	; 0x2e
			dw	mos_api_not_implemented	; 0x2f

			dw	mos_api_setvarval	; 0x30
			dw	mos_api_readvarval	; 0x31
			dw	mos_api_gsinit		; 0x32
			dw	mos_api_gsread		; 0x33
			dw	mos_api_gstrans		; 0x34
			dw	mos_api_substituteargs	; 0x35
			dw	mos_api_not_implemented	; 0x36   reserved for mos_api_evaluateexpression
			dw	mos_api_not_implemented	; 0x37   reserved for something else :)
			dw	mos_api_resolvepath	; 0x38
			dw	mos_api_getdirectoryforpath	; 0x39
			dw	mos_api_getfilepathleafname	; 0x3a
			dw	mos_api_isdirectory	; 0x3b
			dw	mos_api_getabsolutepath	; 0x3c
			dw	mos_api_not_implemented	; 0x3d
			dw	mos_api_not_implemented	; 0x3e
			dw	mos_api_not_implemented	; 0x3f

			dw	mos_api_clear_vdp_flags	; 0x40
			dw	mos_api_wait_vdp_flags	; 0x41
			dw	mos_api_not_implemented	; 0x42
			dw	mos_api_not_implemented	; 0x43
			dw	mos_api_not_implemented	; 0x44
			dw	mos_api_not_implemented	; 0x45
			dw	mos_api_not_implemented	; 0x46
			dw	mos_api_not_implemented	; 0x47
			dw	mos_api_not_implemented	; 0x48
			dw	mos_api_not_implemented	; 0x49
			dw	mos_api_not_implemented	; 0x4a
			dw	mos_api_not_implemented	; 0x4b
			dw	mos_api_not_implemented	; 0x4c
			dw	mos_api_not_implemented	; 0x4d
			dw	mos_api_not_implemented	; 0x4e
			dw	mos_api_not_implemented	; 0x4f

			dw	mos_api_getfunction	; 0x50
			dw	mos_api_not_implemented	; 0x51
			dw	mos_api_not_implemented	; 0x52
			dw	mos_api_not_implemented	; 0x53
			dw	mos_api_not_implemented	; 0x54
			dw	mos_api_not_implemented	; 0x55
			dw	mos_api_not_implemented	; 0x56
			dw	mos_api_not_implemented	; 0x57
			dw	mos_api_not_implemented	; 0x58
			dw	mos_api_not_implemented	; 0x59
			dw	mos_api_not_implemented	; 0x5a
			dw	mos_api_not_implemented	; 0x5b
			dw	mos_api_not_implemented	; 0x5c
			dw	mos_api_not_implemented	; 0x5d
			dw	mos_api_not_implemented	; 0x5e
			dw	mos_api_not_implemented	; 0x5f

			dw	mos_api_not_implemented	; 0x60
			dw	mos_api_not_implemented	; 0x61
			dw	mos_api_not_implemented	; 0x62
			dw	mos_api_not_implemented	; 0x63
			dw	mos_api_not_implemented	; 0x64
			dw	mos_api_not_implemented	; 0x65
			dw	mos_api_not_implemented	; 0x66
			dw	mos_api_not_implemented	; 0x67
			dw	mos_api_not_implemented	; 0x68
			dw	mos_api_not_implemented	; 0x69
			dw	mos_api_not_implemented	; 0x6a
			dw	mos_api_not_implemented	; 0x6b
			dw	mos_api_not_implemented	; 0x6c
			dw	mos_api_not_implemented	; 0x6d
			dw	mos_api_not_implemented	; 0x6e
			dw	mos_api_not_implemented	; 0x6f

			dw	sd_api_getunlockcode	; 0x70
			dw	sd_api_init		; 0x71
			dw	sd_api_readblocks	; 0x72
			dw	sd_api_writeblocks	; 0x73
			dw	mos_api_not_implemented	; 0x74
			dw	mos_api_not_implemented	; 0x75
			dw	mos_api_not_implemented	; 0x76
			dw	mos_api_not_implemented	; 0x77
			dw	mos_api_not_implemented	; 0x78
			dw	mos_api_not_implemented	; 0x79
			dw	mos_api_not_implemented	; 0x7a
			dw	mos_api_not_implemented	; 0x7b
			dw	mos_api_not_implemented	; 0x7c
			dw	mos_api_not_implemented	; 0x7d
			dw	mos_api_not_implemented	; 0x7e
			dw	mos_api_not_implemented	; 0x7f

.equiv mos_api_block1_size, (. - mos_api_block1_start) / 2
;
1:			and	0x7F			; Else remove the top bit
			cp	mos_api_block2_size	; Check if out of bounds
			jp	NC, mos_api_not_implemented
			call	SWITCH_A		; And switch on this table

mos_api_block2_start:	dw	ffs_api_fopen		; 0x80
			dw	ffs_api_fclose		; 0x81
			dw	ffs_api_fread		; 0x82
			dw	ffs_api_fwrite		; 0x83
			dw	ffs_api_flseek		; 0x84
			dw	ffs_api_ftruncate	; 0x85
			dw	ffs_api_fsync		; 0x86
			dw	ffs_api_fforward	; 0x87
			dw	ffs_api_fexpand		; 0x88
			dw	ffs_api_fgets		; 0x89
			dw	ffs_api_fputc		; 0x8A
			dw	ffs_api_fputs		; 0x8B
			dw	ffs_api_fprintf		; 0x8C
			dw	ffs_api_ftell		; 0x8D
			dw	ffs_api_feof		; 0x8E
			dw	ffs_api_fsize		; 0x8F
			dw	ffs_api_ferror		; 0x90
			dw	ffs_api_dopen		; 0x91
			dw	ffs_api_dclose		; 0x92
			dw	ffs_api_dread		; 0x93
			dw	ffs_api_dfindfirst	; 0x94
			dw	ffs_api_dfindnext	; 0x95
			dw	ffs_api_stat		; 0x96
			dw	ffs_api_unlink		; 0x97
			dw	ffs_api_rename		; 0x98
			dw	ffs_api_chmod		; 0x99
			dw	ffs_api_utime		; 0x9A
			dw	ffs_api_mkdir		; 0x9B
			dw	ffs_api_chdir		; 0x9C
			dw	ffs_api_chdrive		; 0x9D
			dw	ffs_api_getcwd		; 0x9E
			dw	ffs_api_mount		; 0x9F
			dw	ffs_api_mkfs		; 0xA0
			dw	ffs_api_fdisk		; 0xA1
			dw	ffs_api_getfree		; 0xA2
			dw	ffs_api_getlabel	; 0xA3
			dw	ffs_api_setlabel	; 0xA4
			dw	ffs_api_setcp		; 0xA5
			dw	ffs_api_flseek_p	; 0xA6

.equiv mos_api_block2_size, (. - mos_api_block2_start) / 2

mos_api_not_implemented:
			ld	HL, 23			; MOS_NOT_IMPLEMENTED
			ld	A, 23			; MOS_NOT_IMPLEMENTED
			ret

; Get keycode
; Returns:
;  A: ASCII code of key pressed, or 0 if no key pressed
;
mos_api_getkey:		push	HL
			ld	HL, _keycount
mos_api_getkey_1:	ld	A, (HL)			; Wait for a key to be pressed
1:			cp	(HL)
			jr	Z, 1b
			ld	A, (_keydown)		; Check if key is down
			or	A
			jr	Z, mos_api_getkey_1	; No, so loop
			pop	HL
			ld	A, (_keyascii)		; Get the key code
			ret

; Load an area of memory from a file.
; HLU: Address of filename (zero terminated)
; DEU: Address at which to load
; BCU: Maximum allowed size (bytes)
; Returns:
; - A: File error, or 0 if OK
; - F: Carry reset indicates no room for file.
;
mos_api_load:		ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, 1f		; If it is, we can assume HL and DE are 24 bit
;
; Now we need to mod HLU and DEU to include the MBASE in the U byte
;
			call	SET_AHL24
			call	SET_ADE24
;
; Finally, we can do the load
;
1:			push	BC		; UINT24   size
			push	DE		; UNIT24   address
			push	HL		; char   * filename
			call	_mos_LOAD_API	; Call the C function mos_LOAD_API
			ld	A, L		; Return value in HLU, put in A
			pop	HL
			pop	DE
			pop	BC
			scf			; Flag as successful
			ret

; Save a file to the SD card from RAM
; HLU: Address of filename (zero terminated)
; DEU: Address to save from
; BCU: Number of bytes to save
; Returns:
; - A: File error, or 0 if OK
; - F: Carry reset indicates no room for file
;
mos_api_save:		ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, 1f		; If it is, we can assume HL and DE are 24 bit
;
; Now we need to mod HLU and DEU to include the MBASE in the U byte
;
			call	SET_AHL24
			call	SET_ADE24
;
; Finally, we can do the save
;
1:			push	BC		; UINT24   size
			push	DE		; UNIT24   address
			push	HL		; char   * filename
			call	_mos_SAVE_API	; Call the C function mos_SAVE_API
			ld	A, L		; Return value in HLU, put in A
			pop	HL
			pop	DE
			pop	BC
			scf			; Flag as successful
			ret

; Change directory
; HLU: Address of path (zero terminated)
; Returns:
; - A: File error, or 0 if OK
;
mos_api_cd:		ld	A, MB		; Check if MBASE is 0
			or	A, A
;
; Now we need to mod HLU to include the MBASE in the U byte
;
			call	NZ, SET_AHL24	; If it is running in classic Z80 mode, set U to MB
;
; Finally, we can do the load
;
			push	HL		; char   * filename
			call	_mos_CD_API
			ld	A, L		; Return vaue in HLU, put in A
			pop	HL
			ret

; Directory listing
; HLU: Address of path (zero terminated)
; Returns:
; - A: File error, or 0 if OK
;
mos_api_dir:		ld	A, MB		; Check if MBASE is 0
			or	A, A
;
; Now we need to mod HLU to include the MBASE in the U byte
;
			call	NZ, SET_AHL24	; If it is running in classic Z80 mode, set U to MB
;
; Finally, we can run the command
;
			push	HL		; char * path
			call	_mos_DIR_API
			ld	A, L		; Return value in HLU, put in A
			pop	HL
			ret

; Delete a file from the SD card
; HLU: Address of filename (zero terminated)
; Returns:
; - A: File error, or 0 if OK
;
mos_api_del:		ld	A, MB		; Check if MBASE is 0
			or	A, A
;
; Now we need to mod HLU to include the MBASE in the U byte
;
			call	NZ, SET_AHL24	; If it is running in classic Z80 mode, set U to MB
;
; Finally, we can do the delete
;
			push	HL		; char   * filename
			call	_mos_DEL	; Call the C function mos_DEL
			ld	A, L		; Return vaue in HLU, put in A
			pop	HL
			ret

; Rename a file on the SD card
; HLU: Address of filename1 (zero terminated)
; DEU: Address of filename2 (zero terminated)
; Returns:
; - A: File error, or 0 if OK
;
mos_api_ren:		ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, 1f		; If it is, we can assume HL and DE are 24 bit
;
; Now we need to mod HLU and DEu to include the MBASE in the U byte
;
			call	SET_AHL24
			call	SET_ADE24
;
; Finally we can do the rename
;
1:			push	DE		; char * filename2
			push	HL		; char * filename1
			call	_mos_REN_API	; Call the C function mos_REN_API
			ld	A, L		; Return vaue in HLU, put in A
			pop	HL
			pop	DE
			ret

; Copy a file on the SD card
; HLU: Address of filename1 (zero terminated)
; DEU: Address of filename2 (zero terminated)
; Returns:
; - A: File error, or 0 if OK
;
mos_api_copy:		ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, 1f		; If it is, we can assume HL and DE are 24 bit
;
; Now we need to mod HLU and DEu to include the MBASE in the U byte
;
			call	SET_AHL24
			call	SET_ADE24
;
; Finally we can do the rename
;
1:			push	DE		; char * filename2
			push	HL		; char * filename1
			call	_mos_COPY_API	; Call the C function mos_COPY_API
			ld	A, L		; Return vaue in HLU, put in A
			pop	HL
			pop	DE
			ret

; Make a folder on the SD card
; HLU: Address of filename (zero terminated)
; Returns:
; - A: File error, or 0 if OK
;
mos_api_mkdir:		ld	A, MB		; Check if MBASE is 0
			or	A, A
;
; Now we need to mod HLU to include the MBASE in the U byte
;
			call	NZ, SET_AHL24	; If it is running in classic Z80 mode, set U to MB
;
; Finally, we can do the load
;
			push	HL		; char   * filename
			call	_mos_MKDIR_API	; Call the C function mos_MKDIR_API
			ld	A, L		; Return vaue in HLU, put in A
			pop	HL
			ret

; Get a pointer to a system variable
; Returns:
; IXU: Pointer to system variables (see mos_api.asm for more details)
;
mos_api_sysvars:	ld	IX, _sysvars
			ret

; Invoke the line editor
; HLU: Address of the buffer
; BCU: Buffer length
;   E: flags
; Returns:
;   A: Key that was used to exit the input loop (CR=13, ESC=27)
;
mos_api_editline:	ld	A, MB		; Check if MBASE is 0
			or	A, A
;
; Now we need to mod HLU to include the MBASE in the U byte
;
			call	NZ, SET_AHL24	; If it is running in classic Z80 mode, set U to MB
;
			push	DE		; UINT16  flags
			push	BC		; int 	  bufferLength
			push	HL		; char	* buffer
			call	_mos_EDITLINE
			ld	A, L		; return value, only interested in lowest byte
			pop	HL
			pop	BC
			pop	DE
			ret

; Open a file
; HLU: Filename
;   C: Mode
; Returns:
;   A: Filehandle, or 0 if couldn't open
;
; TODO: why the push/pop of HL, DE, IX and IY?
mos_api_fopen:		push	BC
			push	DE
			push	HL
			push	IX
			push	IY
;
			ld	A, MB		; Check if MBASE is 0
			or	A, A
;
; Now we need to mod HLU and DEU to include the MBASE in the U byte
;
			call	NZ, SET_AHL24	; If it is running in classic Z80 mode, set U to MB
;
			ld	A, C
			ld	BC, 0
			ld	C, A
			push	BC		; byte	  mode
			push	HL		; char	* buffer
			call	_mos_FOPEN
			ld	A, L		; Return fh
			pop	HL
			pop	BC
;
			pop	IY
			pop	IX
			pop	HL
			pop	DE
			pop	BC
			ret

; Close a file
;   C: Filehandle
; Returns
;   A: Number of files still open
;
mos_api_fclose:		push	BC
			push	DE
			push	HL
			push	IX
			push	IY
;
			ld	A, C
			ld	BC, 0
			ld	C, A
			push	BC		; byte 	  fh
			call	_mos_FCLOSE
			ld	A, L		; Return # files still open
			pop	BC
;
			pop	IY
			pop	IX
			pop	HL
			pop	DE
			pop	BC
			ret

; Get a character from a file
;   C: Filehandle
; Returns:
;   A: Character read
;   F: C set if last character in file, otherwise NC
;
mos_api_fgetc:		push	BC
			push	DE
			push	HL
			push	IX
			push	IY
;
			ld	DE, 0
			ld	E, C
			push	DE		; byte	  fh
			call	_mos_FGETC	; Read the character
			pop	DE
			ld	A, L 		; A: Character read
			srl	H 		; F: C = EOF
;
			pop	IY
			pop	IX
			pop	HL
			pop	DE
			pop	BC
			ret

; Write a character to a file
;   C: Filehandle
;   B: Character to write
;
mos_api_fputc:		push	AF
			push	BC
			push	DE
			push	HL
			push	IX
			push	IY
;
			ld	DE, 0
			ld	E, B
			push	DE		; byte	  char
			ld	E, C
			push	DE		; byte	  fh
			call	_mos_FPUTC
			pop	DE
			pop	DE
;
			pop	IY
			pop	IX
			pop	HL
			pop	DE
			pop	BC
			pop	AF
			ret

; Check whether we're at the end of the file
;   C: Filehandle
; Returns:
;   A: 1 if at end of file, otherwise 0
;
mos_api_feof:		push	BC
			push	DE
			push	HL
			push	IX
			push	IY
;
			ld	DE, 0
			ld	E, C
			push	DE		; byte	  fh
			call	_mos_FEOF
			pop	DE
;
			pop	IY
			pop	IX
			pop	HL
			pop	DE
			pop	BC
			ret

; Copy an error message
;   E: The error code
; HLU: Address of buffer to copy message into
; BCU: Size of buffer
;
mos_api_getError:	ld	A, MB		; Check if MBASE is 0
			or	A, A
			call	NZ, SET_AHL24	; If it is running in classic Z80 mode, set U to MB
;
; Now copy the error message
;
			push	BC		; UINT24 size
			push	HL		; UINT24 address
			push	DE		; byte   errno
			call	_mos_GETERROR
			pop	DE
			pop	HL
			pop	BC
			ret

; Execute a MOS command
; HLU: Pointer the the MOS command string
; DEU: Pointer to additional command structure
; BCU: Number of additional commands
; Returns:
;   A: MOS error code
;
mos_api_oscli:		call	uart0_return_fence
			ld	A, MB		; Check if MBASE is 0
			or	A, A
			call	NZ, SET_AHL24	; If it is running in classic Z80 mode, set U to MB
;
; Now execute the MOS command
;
			push	HL		; char * buffer
			call	_mos_OSCLI
			ld	A, L		; Return vaue in HLU, put in A
			pop	HL
			ret

; Fetch a RTC string
; HLU: Pointer to a buffer to copy the string to
; Returns:
;   A: Length of time
;
mos_api_getrtc:		ld	A, MB		; Check if MBASE is 0
			or	A, A
			call	NZ, SET_AHL24	; If it is running in classic Z80 mode, set U to MB
;
; Now fetch the time
;
			push	HL		; UINT24 address
			call	_mos_GETRTC
			pop	HL
			ret

; Unpack RTC data
; HLU: Pointer to a buffer to copy the RTC data to
; C: Flags (bit 0 = refresh RTC before unpacking, bit 1 = refresh RTC after unpacking)
;
mos_api_unpackrtc:	ld	A, MB		; Check if MBASE is 0
			or	A, A
			call	NZ, SET_AHL24	; If it is running in classic Z80 mode, set U to MB
			push	BC		; UINT8 flags
			push 	HL		; UINT24 address
			call	_mos_UNPACKRTC
			pop	HL
			pop	BC
			ret

; Set the RTC
; HLU: Pointer to a buffer with the time data in
;
mos_api_setrtc:		ld	A, MB		; Check if MBASE is 0
			or	A, A
			call	NZ, SET_AHL24	; If it is running in classic Z80 mode, set U to MB
;
; Now fetch the time
;
			push	HL		; UINT24 address
			call	_mos_SETRTC
			pop	HL
			ret

; Set an interrupt vector
; HLU: Pointer to the interrupt vector (24-bit pointer)
;   E: Vector # to set
; Returns:
; HLU: Pointer to the previous vector
;
mos_api_setintvector:	ld	A, E
			ld	DE, 0 		; Clear DE
			ld	E, A 		; Store the vector #
			push	HL		; void(*handler)(void)
			push	DE 		; byte vector
			call	_mos_SETINTVECTOR
			pop	DE
			pop	DE
			ret

; Set a VDP keyboard packet receiver callback
;   C: If non-zero then set the top byte of HLU(callback address)  to MB (for ADL=0 callers)
; HLU: Pointer to callback
;
mos_api_setkbvector:	call	uart0_return_fence
			push	DE
			xor	A
			or	C		; If C!=0 set top byte (bits 16:23) to MB
			jr	Z, 1f
			ld	A, MB
			call	SET_AHL24
1:			push	HL
			pop	DE
			ld	HL, _user_kbvector
			ld	(HL),DE
			pop	DE
			ret

; Get the address of the keyboard map
; Returns:
; IXU: Base address of the keymap
;
mos_api_getkbmap:	ld	IX, _keymap
			ret

; Open the I2C bus as master
;   C: Frequency ID
;
mos_api_i2c_open:	push	BC
			push	DE
			push	HL
			push	IX
			push	IY
;
			ld	HL,0
			ld	L, C
			push	HL
			call	_mos_I2C_OPEN
			pop	HL
;
			pop	IY
			pop	IX
			pop	HL
			pop	DE
			pop	BC
			ret

; Close the I2C bus
;
mos_api_i2c_close:	push	BC
			push	DE
			push	HL
			push	IX
			push	IY
;
			call	_mos_I2C_CLOSE
;
			pop	IY
			pop	IX
			pop	HL
			pop	DE
			pop	BC
			ret

; Write n bytes to the I2C bus
;   C: I2C address
;   B: Number of bytes to write, maximum 32
; HLU: Address of buffer containing the bytes to send
;
mos_api_i2c_write:	push	DE
			push	IX
			push	IY
;
			ld	A, MB		; Check if MBASE is 0
			or	A, A
			call	NZ, SET_AHL24	; If it is running in classic Z80 mode, set U to MB
;
			push	HL		; Address of buffer
			ld	HL,0
			ld	L, B
			push	HL		; Count
			ld	L, C
			push	HL		; I2C address
			call	_mos_I2C_WRITE
			pop	HL
			pop	HL
			pop	HL
;
			pop	IY
			pop	IX
			pop	DE
			ret

; Read n bytes from the I2C bus
;   C: I2C address
;   B: Number of bytes to read, maximum 32
; HLU: Address of buffer to read bytes to
;
mos_api_i2c_read:	push	DE
			push	IX
			push	IY
;
			ld	A, MB		; Check if MBASE is 0
			or	A, A
			call	NZ, SET_AHL24	; If it is running in classic Z80 mode, set U to MB
;
			push	HL		; Address of buffer
			ld	HL,0
			ld	L, B
			push	HL		; Count
			ld	L, C
			push	HL		; I2C address
			call	_mos_I2C_READ
			pop	HL
			pop	HL
			pop	HL
;
			pop	IY
			pop	IX
			pop	DE
			ret

; Open UART1
; IXU: Pointer to UART struct
;	+0: Baud rate (24-bit, little endian)
;	+3: Data bits
;	+4: Stop bits
;	+5: Parity bits
;	+6: Flow control (0: None, 1: Hardware)
;	+7: Enabled interrupts
; Returns:
;   A: Error code (0 = no error)
;
mos_api_uopen:		lea	HL, IX + 0	; HLU: Pointer to struct
			ld	A, MB 		; If in 64K segment when
			or	A, A 		; MB != 0 then
			call	NZ, SET_AHL24 	; Convert to a 24-bit absolute pointer
			push	HL		; UART * pUART
			call	_open_UART1	; Initialise the UART port
			pop	HL 		; Tidy up the stack
			ret

; Close UART1
;
mos_api_uclose:		jp	_close_UART1

; Get a character from UART1
; Returns:
;   A: Character read
;   F: C if successful
;   F: NC if the UART is not open
;
mos_api_ugetc:		jp	UART1_serial_GETCH

; Write a character to UART1
;   C: Character to write
; Returns:
;   F: C if successful
;   F: NC if the UART is not open
;
mos_api_uputc:		ld	A, C
			jp	UART1_serial_PUTCH

; Convert a file handle to a FIL structure pointer
;   C: Filehandle
; Returns:
; HLU: Pointer to a FIL struct
;
mos_api_getfil:		push	BC		; UINT8 fh
			call	_mos_GETFIL
			pop	BC
			ret

; Read a block of data from a file
;   C: Filehandle
; HLU: Pointer to where to write the data to
; DEU: Number of bytes to read
; Returns:
; DEU: Number of bytes read
;
mos_api_fread:		ld	A, MB		; Check if MBASE is 0
			or	A, A
			call	NZ, SET_AHL24
			push	DE		; UINT24 btr
			push	HL		; UINT24 buffer
			push	BC		; UINT8 fh
			call	_mos_FREAD
			ld	(_scratchpad), HL
			pop	BC
			pop	HL
			pop	DE
			ld	DE, (_scratchpad)
			ret

; Write a block of data to a file
;  C: Filehandle
; HLU: Pointer to where the data is
; DEU: Number of bytes to write
; Returns:
; DEU: Number of bytes read
;
mos_api_fwrite:		ld	A, MB		; Check if MBASE is 0
			or	A, A
			call	NZ, SET_AHL24
			push	DE		; UINT24 btr
			push	HL		; UINT24 buffer
			push	BC		; UINT8 fh
			call	_mos_FWRITE
			ld	(_scratchpad), HL
			pop	BC
			pop	HL
			pop	DE
			ld	DE, (_scratchpad)
			ret

; Move the read/write pointer in a file
;   C: Filehandle
; HLU: Least significant 3 bytes of the offset from the start of the file (DWORD)
;   E: Most significant byte of the offset
; Returns:
;   A: FRESULT
;
mos_api_flseek:		push 	DE		; UINT32 offset (msb)
			push	HL		; UINT32 offset (lsb)
			push	BC		; UINT8 fh
			call	_mos_FLSEEK	; Returns 8-bit FRESULT in A
			pop	BC
			pop	HL
			pop	DE
			ret

; Move the read/write pointer in a file, using pointer to offset value
;   C: Filehandle
; HLU: Pointer to the offset value from the start of the file (DWORD)
; Returns:
;   A: FRESULT
;
mos_api_flseek_p:	call	FIX_HLU24	; Fix the HLU to ensure it's a 24-bit pointer
			push	HL		; DWORD * offset
			push	BC		; UINT8 fh
			call	_mos_FLSEEKP
			pop	BC
			pop	HL
			ret


; MOS String functions
;
; Pattern matching
; HLU: Address of pattern (zero terminated)
; DEU: Address at string to compare against pattern (zero terminated)
; C: Flags
; Returns:
; - A: File error, or 0 if OK
;
mos_api_pmatch:
			ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, 1f		; If it is, we can assume HL and DE are 24 bit
			call	SET_AHL24
			call	SET_ADE24
1:			push	BC		; BYTE flags  (altho we'll push all 3 bytes)
			push	DE		; char * string
			push	HL		; char * pattern
			call	_pmatch		; Call the C function pmatch
			ld	A, L		; Return value in HLU, put in A
			pop	HL
			pop	DE
			pop	BC
			ret

; Extract a (numbered) argument from a string
; HLU: Pointer to source string
; BCU: Argument number
; Returns:
; - HLU: Address of the argument or zero if not found
; - DEU: Address of the next character after the argument
;
; char * getArgument(char * source, int argNo, char ** end)
mos_api_getargument:	ld	A, MB		; Check if MBASE is 0
			or	A, A
			call	NZ, SET_AHL24
			push	HL
			ld	HL, _scratchpad
			ex	(SP), HL	; char ** end
			push	BC		; UINT8 argNo
			push	HL		; char * source
			call	_getArgument	; Call the C function getArgument
			; HL now contains the argument address
			pop	BC
			pop	BC
			ex	(SP), HL
			pop	HL		; Return start of argument in HLU
			ld	DE, (_scratchpad)	; Return end of argument in DEU
			ret

; Extract a string, using a given divider
; HLU: Pointer to source string to extract from
; DEU: Pointer to string for divider matching, or 0 for default (space)
; C: Flags
; Depending on flags, the result string will be zero terminated or not
; Returns:
; - A: status code
; - HLU: Address of the result string
; - DEU: Address of next character after end of result string
;
; int extractString(char * source, char ** end, char * divider, char ** result, BYTE flags)
mos_api_extractstring:
			ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, 1f		; If it is, we can assume addresses are 24 bit
			call	SET_AHL24
			ld	A, D		; Check if DE is zero
			or	A, E
			jr	Z, 1f		; DE is zero so no need to set U to MB
			ld	A, MB
			call	SET_ADE24	; DE not zero, so set U to MB
1:			push	BC		; BYTE flags
			push	HL
			ld	HL, _scratchpad
			ex	(SP), HL	; char ** result
			push	DE		; char * divider
			push	HL
			ld	HL, _scratchpad + 3
			ex	(SP), HL	; char ** end
			push	HL		; char * source
			call	_extractString	; Call the C function extractString
			ld	A, L		; Save return value in HLU, in A
			pop	HL
			pop	HL
			pop	HL
			pop	HL
			pop 	BC		; unpop the BC
			ld	HL, (_scratchpad)	; return result in HLU
			ld	DE, (_scratchpad + 3)	; return end in DEU
			ret

; Extract a number, using given divider
; HLU: Pointer to source string to extract from
; DEU: Pointer to string for divider matching, or 0 for default (space)
; C: Flags
; Returns:
; - A: status code
; - HLU: Number extracted
; - DEU: Address of next character after end of number
;
; uint8_t	extractNumber(char * source, char ** end, char * divider, int * number, BYTE flags)
mos_api_extractnumber:
			push	BC		; BYTE flags
			ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, 1f		; If it is, we can assume addresses are 24 bit
			call	SET_AHL24
			ld	A, D
			or	A, E
			jr	Z, 1f		; DE is zero, so no need to set U to MB
			ld	A, MB
			call	SET_ADE24
1:			push	HL
			ld	HL, _scratchpad
			ex	(SP), HL	; int * number
			push	DE		; char * divider
			push	HL
			ld	HL, _scratchpad + 3
			ex	(SP), HL	; char ** end
			push	HL		; char * source
			call	_extractNumber	; Call the C function extractNumber. A will be true/false (1 or 0)
			pop	HL
			pop	HL
			pop	HL
			pop	HL
			pop 	BC		; unpop the BC
			ld	HL, (_scratchpad)	; return number in HLU
			ld	DE, (_scratchpad + 3)	; return end in DEU
			; Return value in A will be true/false
			; so we need to change to 0 for success, and 19 (invalid parameter) for failure
			or	A, A		; Was status value false?
			jr	Z, 1f		; If it is, we need to replace with 19
			ld	A, 0		; Otherwise, return 0 FR_OK
			ret
1:			ld	A, 19		; Return 19 FR_INVALID_PARAMETER
			ret

; Escape a string, converting control characters to be pipe-prefixed
; HLU: Pointer to source string
; DEU: Pointer to destination buffer (optional)
; BCU: Length of destination buffer
; Returns:
; - A: Status code
; - BCU: Length of escaped string
;
; int escapeString(char * source, char * dest, int * length)
mos_api_escapestring:
			ld	(_scratchpad), BC 	; Save the length
			ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, 1f		; If it is, we can assume addresses are 24 bit
			call	SET_AHL24
			ld	A, D
			or	A, E
			jr	Z, 1f		; DE is zero, so no need to set U to MB
			ld	A, MB
			call	SET_ADE24
1:			push	HL
			ld	HL, _scratchpad
			ex	(SP), HL	; int * length
			push	DE		; char * dest
			push	HL		; char * source
			call	_escapeString	; Call the C function escapeString
			ld	A, L		; Save return value in HLU, in A
			pop	HL
			pop	DE
			pop	BC
			ld	BC, (_scratchpad)	; Return the length
			ret

; Set a variable value
; HLU: Pointer to variable name (can include wildcards)
; IXU: Variable value (number, or pointer to zero-terminated string)
; IYU: Pointer to variable name (0 for first call)
; C: Variable type, or -1 (255) to delete the variable
; Returns:
; - A: Status code
; - C: Actual variable type
; - IYU: Pointer to variable name (for next call)
;
; int setVarVal(char * name, void * value, char ** actualName, BYTE * type);
mos_api_setvarval:
			ld	A, C
			ld	(_scratchpad + 3), A	; Save the type
			ld	(_scratchpad), IY	; Save the actualName pointer
			ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, 1f		; If it is, we can assume addresses are 24 bit
			call	SET_AHL24
			ld	A, C
			cp	1		; Is the type a number?
			jr	Z, 1f		; If it is, we don't need to set U to MB
			ld	A, MB
			call	SET_AIX24	; Only set U if type is not a number
1:			push	HL		; Temporary storage
			ld	HL, _scratchpad + 3
			ex	(SP), HL	; BYTE * type
			ld	IY, _scratchpad
			push	IY		; char ** actualName
			push	IX		; void * value
			push	HL		; char * name
			call	_setVarVal	; Call the C function setVarVal
			ld	A, L		; Save return value in HLU, in A
			pop	HL
			pop	IY		; To be replaced
			pop	IY
			pop	IY
			ld 	IY, _scratchpad
			ld	C, (IY + 3)	; Return the actual type
			ld	IY, (IY)	; Return the actual name
			ret

; Read a variable value
; HLU: Pointer to variable name (can include wildcards)
; IXU: Pointer to buffer to store the value (null/0 to read length only)
; DEU: Length of buffer
; IYU: Pointer to variable name (0 for first call)
; C: Flags (3 = expand value into string)
; Returns:
; - A: Status code
; - C: Actual variable type
; - DEU: Length of variable value
; - IYU: Pointer to variable name (for next call)
;
; int readVarVal(char * namePattern, void * value, char ** actualName, int * length, BYTE * typeFlag)
mos_api_readvarval:
			ld	A, C
			ld	(_scratchpad + 6), A	; Save the flags
			ld	(_scratchpad + 3), DE	; Save the length
			ld	(_scratchpad), IY	; Save the actualName pointer
			push ix
			pop de; move optional target buffer into DE
			ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, 1f		; If it is, we can assume addresses are 24 bit
			call	SET_AHL24
			ld	A, D		; check it target buffer is zero
			or	A, E
			jr	Z, 1f		; DE is zero, so no need to set U to MB
			ld	A, MB
			call	SET_ADE24
1:			push	HL		; Temporary storage
			ld	HL, _scratchpad + 6
			ex	(SP), HL	; BYTE * typeFlag
			push	HL
			ld	HL, _scratchpad + 3
			ex	(SP), HL	; int * length
			ld	IY, _scratchpad
			push	IY		; char ** actualName
			push	DE		; void * value
			push	HL		; char * namePattern
			call	_readVarVal	; Call the C function readVarVal
			ld	A, L		; Save return value in HLU, in A
			pop	HL		; (variable name pattern)
			pop	IX		; (value pointer)
			pop	IY		; To be replaced
			pop	IY
			pop	IY
			ld 	IY, _scratchpad
			ld	C, (IY + 6)	; Return the actual type
			ld	DE, (IY + 3)	; Return the length
			ld	IY, (IY)	; Return the actual name
			ret

; Initialise a GS Trans operation
; HLU: Pointer to source buffer to translate
; DEU: Address of pointer used to store trans info
; C: Flags
; Returns:
; - A: Status code
;
; int gsInit(void * source, t_mosTransInfo ** transInfoPtr, BYTE flags)
mos_api_gsinit:
			push	BC		; BYTE flags
			ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, 1f		; If it is, we can assume HL and DE are 24 bit
			call	SET_AHL24
			call	SET_ADE24
1:			push	DE		; t_mosTransInfo ** transInfoPtr
			push	HL		; char * source
			call	_gsInit		; Call the C function gsInit
			ld	A, L		; Return value in HLU, put in A
			pop	HL
			pop	DE
			pop	BC
			ret

; Perform a GS Trans "read" operation
; DEU: Address of pointer used to store trans info (same pointer as used with gsInit)
; Returns:
; - A: Status code
; - C: Character read
;
; int gsRead(t_mosTransInfo ** transInfo, char * read)
mos_api_gsread:
			push	HL		; preserve HL
			ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, 1f		; If it is, we can assume HL and DE are 24 bit
			call	SET_ADE24
1:			ld	HL, _scratchpad	; use scratchpad as temporary read character storage
			push	HL		; char * read
			push	DE		; t_mosTransInfo ** transInfoPtr
			call	_gsRead		; Call the C function gsRead
			ld	A, L		; Return value in HLU, put in A
			pop	DE
			pop	HL
			ld	C, (HL)		; Get the character read
			pop	HL		; Restore HL
			ret

; Perform a complete GSTrans operation from source into dest buffer
; HLU: Pointer to source buffer
; IXU: Pointer to destination buffer
; DEU: Length of destination buffer
; C: Flags
; Returns:
; - A: Status code
; - BCU: Calculated total length of destination string
;
; int gsTrans(char * source, char * dest, int destLen, int * read, BYTE flags)
mos_api_gstrans:
			push	BC		; BYTE flags
			push ix
			pop bc; move optional target buffer into BC
			ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, 1f		; If it is, we can assume addresses are 24 bit
			call	SET_AHL24
			ld	A, B		; Check if target buffer is zero
			or	A, C
			jr	Z, 1f		; target is zero, so no need to set U to MB
			ld	A, MB
			call	SET_ABC24
1:			push 	HL
			ld	HL, _scratchpad
			ex	(SP), HL	; int * read
			push	DE		; UINT24 destLength
			push	BC		; char * dest
			push	HL		; char * source
			call	_gsTrans	; Call the C function gstrans
			ld	A, L		; Return value in HLU, put in A
			pop	HL
			pop	IX
			pop	DE
			pop	BC
			pop	BC
			ld	BC, (_scratchpad)
			ret

; Substitute arguments into a string from template
; HLU: Pointer to template string
; IXU: Pointer to arguments string
; DEU: Length of destination buffer
; IYU: Pointer to destination buffer (can be null to just count size)
; C: Flags
; Returns:
; - BCU: Calculated length of destination string
;
; int substituteArgs(char * template, char * args, char * dest, int length, BYTE flags)
mos_api_substituteargs:
			push	BC		; BYTE flags (bool omitRest)
			push	DE		; UINT24 length
			push	IY		; char * dest
			ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, sub_args_contd	; If it is, we can assume addresses are 24 bit
			call	SET_AHL24
			call	SET_AIX24
			ex	(SP), HL	; Swap dest address (on stack) into HL, as it is optional
			ld	A, L
			or	A, H
			jr	Z, 1f		; HL was zero, so jump ahead
			ld	A, MB
			call	SET_AHL24	; HL (dest address) not zero, so set U to MB
1:			ex	(SP), HL	; Swap dest address back into stack
sub_args_contd:		push	IX		; char * args
			push	HL		; char * template
			call	_substituteArgs	; Call the C function substituteArgs
			ld	(_scratchpad), HL	; Save the result
			pop	HL
			pop	IX
			pop	IY
			pop	DE
			pop	BC
			ld	BC, (_scratchpad)
			ret

; Resolves a path, replacing prefixes and leafnames with actual values
; HLU: Pointer to the path to resolve
; IXU: Pointer to buffer to store the resolved path (optional - set to zero for length count only)
; DEU: Length of the resolved path buffer
; IYU: Pointer to a directory object to persist between calls (optional)
; B: Flags for file attribute matching/filtering (zero to return all matches)
; C: Index of the resolved path (zero for first call)
; Returns:
; - A: Status code
; - C: Updated index
; - DEU: Length of the resolved path
;
; int resolvePath(char * filepath, char * resolvedPath, int * length, BYTE * index, DIR * dir, BYTE flags)
mos_api_resolvepath:
			ld	(_scratchpad), BC	; Save the index
			ld	(_scratchpad + 3), DE	; Save the length
			ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, res_path_contd	; If it is, we can assume addresses are 24 bit
			call	SET_AHL24	; HL (source path) is required, so set it
			; IX(U) (destination buffer) is optional, so check if it's zero
			push ix
			pop de
			ld	A, D
			or	A, E
			jr	Z, 1f		; dest buffer is zero, so no need to set U to MB
			ld	A, MB
			call	SET_ADE24	; dest buffer not zero, so set U to MB
1:			push de
pop ix
			; IY (directory object pointer) is optional, so check if it's zero
			push iy
			pop de
			ld	A, D
			or	A, E
			jr	Z, 1f		; dir object is zero, so no need to set U to MB
			ld	A, MB
			call	SET_ADE24	; dir object not zero, so set U to MB
1:			push de
pop iy
			; OK so we should now have all the addresses set up
res_path_contd:		ld	BC, 0		; Clear BC for flags
			ld	A, (_scratchpad + 1)	; Get the flags byte
			ld	C, A		; Copy to C
			push	BC		; BYTE flags
			push	IY		; DIR * dir
			ld	IY, _scratchpad
			push	IY		; BYTE * index (scratchpad, from C on entry)
			ld	DE, 3
			add	IY, DE
			push	IY		; int * length (scratchpad + 3, from DE on entry)
			push	IX		; char * resolvedPath
			push	HL		; char * filepath
			call	_resolvePath	; Call the C function resolvePath
			ld	A, L		; Return value in HLU, put in A
			pop	HL
			pop	IX
			pop	DE		; Length (will be replaced)
			pop	BC		; Index (will be replaced)
			pop	IY
			pop	BC
			ld	BC, (_scratchpad)	; Overwrite C with new Index (also restores flags)
			ld	DE, (_scratchpad + 3)	; Returned length
			ret

; Get the directory for a given path
; String only - resolves path prefixes for the given index
; HLU: Pointer to the path to get the directory for
; IXU: Pointer to buffer to store the directory in (optional, omit for count only)
; DEU: Length of the buffer
; C: Search index
; Returns:
; - A: Status code
; - DEU: Length of the directory
;
; int getDirectoryForPath(char * srcPath, char * dir, int * length, BYTE searchIndex)
mos_api_getdirectoryforpath:
			push 	BC		; BYTE searchIndex
			ld	(_scratchpad), DE	; Save the length
			push ix
			pop de; use DE for checking optional buffer
			ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, 1f		; If it is, we can assume addresses are 24 bit
			call	SET_AHL24	; HL is required, so set it
			ld	A, D
			or	A, E
			jr	Z, 1f		; optional buffer is zero, so no need to set U to MB
			ld	A, MB
			call	SET_ADE24	; DE not zero, so set U to MB
1:			ld	BC, _scratchpad
			push	BC		; int * length
			push	DE		; char * dir
			push	HL		; char * srcPath
			call	_getDirectoryForPath	; Call the C function getDirectoryForPath
			ld	A, L		; Return value in HLU, put in A
			pop	HL
			pop	IX
			pop	DE		; Length (will be replaced)
			pop	BC
			ld	DE, (_scratchpad)
			ret

; Get the leafname for a given path
; HLU: Pointer to the path to get the leafname for
; Returns:
; - HLU: Pointer to the leafname
;
; char * getFilepathLeafname(char * filepath);
mos_api_getfilepathleafname:
			ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, 1f		; If it is, we can assume HL is 24 bit
			call	SET_AHL24	; HL is required, so set it
1:			push	HL		; char * filepath
			call	_getFilepathLeafname	; Call the C function getFilepathLeafname
			ex	(SP), HL	; Return value in HLU
			pop	HL
			ret

; Check if a given path points to a directory
; NB this does not do path resolution
; HLU: Pointer to the path to check
; Returns:
; - A: Status code
mos_api_isdirectory:
			ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, 1f		; If it is, we can assume HL is 24 bit
			call	SET_AHL24	; HL is required, so set it
1:			push	HL		; char * filepath
			call	_isDirectory	; Call the C function isDirectory
			pop	HL
			; return value is true/false, so we need to change to 0 for success, and 19 (invalid parameter) for failure
			or	A, A		; Was status value false?
			jr	Z, 1f		; If it is, we need to replace with 5
			ld	A, 0		; Otherwise, return 0 FR_OK
			ret
1:			ld	A, 5		; Return 5 FR_NO_PATH
			ret

; Get the absolute version of a (relative) path
; HLU: Pointer to the path to get the absolute version of
; IXU: Pointer to the buffer to store the absolute path in
; DEU: Length of the buffer
; Returns:
; - A: Status code
;
; int resolveRelativePath(char * path, char * resolved, int * length);
; For now, we will not support returning back length, or calculating length
mos_api_getabsolutepath:
			ld	A, MB		; Check if MBASE is 0
			or	A, A
			jr	Z, 1f		; If it is, we can assume pointers are 24 bit
			call	SET_AHL24
			call	SET_AIX24
1:			ld	(_scratchpad), DE
			ld	DE, _scratchpad
			push	DE		; int * length
			push	IX		; char * resolved
			push	HL		; char * path
			call	_resolveRelativePath	; Call the C function resolveRelativePath
			ld	A, L		; Return value in HLU, put in A
			pop	HL
			pop	IX
			pop	DE
			ld	DE, (_scratchpad)	; Return length in DEU
			ret

; Clear VDP flag(s)
; C: bitmask of flags to clear
; Returns:
; - A: vdp flags
mos_api_clear_vdp_flags:
			push	HL		; Save HL
			ld	HL, _vpd_protocol_flags
			ld	A, C
			cpl			; Invert the bitmask
			and	(HL)		; Clear the requested flags
			ld	(HL), A		; Save the new flags
			pop	HL
			ret

; Wait until VDP flag(s) are set, or timeout
; C: bitmask of flags to wait for
; Returns:
; - A = status code (0 = OK, 15 = timeout (FR_TIMEOUT))
mos_api_wait_vdp_flags:
			push	BC
			call	_wait_VDP
			pop	BC
			ret

; Open a file
; HLU: Pointer to a blank FIL struct
; DEU: Pointer to the filename (0 terminated)
;   C: File mode
; Returns:
;   A: FRESULT
;
ffs_api_fopen:		ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call 	SET_ADE24	; Convert DE to an address in segment A (MB)
			call	FIX_HLU24_no_mb_check
1:			push	BC		; BYTE mode
			push	DE		; const TCHAR * path
			push	HL		; FIL * fp
			call	_f_open
			ld	A, L 		; FRESULT
			pop	HL
			pop	DE
			pop	BC
			ret

; Close a file
; HLU: Pointer to a FIL struct
; Returns:
;   A: FRESULT
;
ffs_api_fclose:		call	FIX_HLU24
			push	HL		; FIL * fp
			call	_f_close
			ld	A, L		; FRESULT
			pop	HL
			ret

; Read data from a file
; HLU: Pointer to a FIL struct
; DEU: Pointer to where to write the file out
; BCU: Number of bytes to read
; Returns:
;   A: FRESULT
; BCU: Number of bytes read
;
ffs_api_fread:		ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call 	SET_ADE24	; Convert DE to an address in segment A (MB)
			call	FIX_HLU24_no_mb_check
1:			push	HL
			ld	HL, _scratchpad
			ex	(SP), HL	; UINT * br
			push	BC		; UINT btr
			push	DE		; void * buff
			push	HL		; FILE * fp
			call	_f_read
			ld	A, L 		; FRESULT
			pop	HL
			pop	DE
			pop	BC
			pop	BC
			ld	BC, (_scratchpad)
			ret

; Write data to a file
; HLU: Pointer to a FIL struct
; DEU: Pointer to the data to write out
; BCU: Number of bytes to write
; Returns:
;   A: FRESULT
; BCU: Number of bytes written
;
ffs_api_fwrite:		ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call 	SET_ADE24	; Convert DE to an address in segment A (MB)
			call	FIX_HLU24_no_mb_check
1:			push	HL
			ld	HL, _scratchpad
			ex	(SP), HL	; UINT * bw
			push	BC		; UINT btw
			push	DE		; void * buff
			push	HL		; FILE * fp
			call	_f_write
			ld	A, L 		; FRESULT
			pop	HL
			pop	DE
			pop	BC
			pop	BC
			ld	BC, (_scratchpad)
			ret

; Move the read/write pointer in a file
; HLU: Pointer to a FIL struct
; DEU: Least significant 3 bytes of the offset from the start of the file (DWORD)
;   C: Most significant byte of the offset
; Returns:
;   A: FRESULT
;
ffs_api_flseek:		call	FIX_HLU24
			push	BC 		; FSIZE_t ofs (msb)
			push	DE		; FSIZE_t ofs (lsw)
			push	HL		; FIL * fp
			call	_f_lseek
			ld	A, L
			pop	HL
			pop	DE
			pop	BC
			ret

; Truncate a file
; HLU: Pointer to a FIL struct
; Returns:
;   A: FRESULT
;
ffs_api_ftruncate:	call	FIX_HLU24
			push	HL		; FIL * fp
			call	_f_truncate
			ld	A, L
			pop	HL
			ret

; Flush cached information of a writing file
; HLU: Pointer to a FIL struct
; Returns:
;   A: FRESULT
;
ffs_api_fsync:
			call	FIX_HLU24
			push	HL		; FIL * fp
			call	_f_sync
			ld	A, L
			pop	HL
			ret

ffs_api_fforward:	; Not supported in our FatFS configuration
			jp mos_api_not_implemented
ffs_api_fexpand:	; Not supported in our FatFS configuration
			jp mos_api_not_implemented

; Read a string from a file
; HLU: Pointer to a FIL struct
; DEU: Pointer to target buffer to read string into
; BCU: Buffer size
; Returns:
;   DEU: Pointer to target buffer or null if error
;
ffs_api_fgets:		ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call 	SET_ADE24	; Convert DE to an address in segment A (MB)
			call	FIX_HLU24_no_mb_check
1:			push	HL		; FILE * fp
			push	BC		; UINT len
			push	DE		; void * buff
			call	_f_gets
			push hl
			pop de; Return value in DE
			pop	HL
			pop	BC
			pop	BC
			ret

; Write a character to a file
; HLU: Pointer to a FIL struct
; C: Character to write
; Returns:
;  BCU: Number of bytes written
;
ffs_api_fputc:		call	FIX_HLU24
			push	HL		; FIL * fp
			push	BC		; TCHAR c
			call	_f_putc
			push hl
			pop bc; Return value in BCU
			pop	HL
			pop	HL
			ret

; Write a string to a file
; HLU: Pointer to a FIL struct
; DEU: Pointer to the string to write out
; Returns:
;  BCU: Number of bytes written
;
ffs_api_fputs:		ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call 	SET_ADE24	; Convert DE to an address in segment A (MB)
			call	FIX_HLU24_no_mb_check
1:			push	HL		; FIL * fp
			push	DE		; const TCHAR * str
			call	_f_puts
			push hl
			pop bc; Return value in BCU
			pop	HL
			pop	HL
			ret

ffs_api_fprintf:	; Available, but hard to expose as an API
			jp mos_api_not_implemented

; Get the current read/write pointer/offset in a file
; NB if FIL is not valid, this may return junk, and DE is also not fully checked for validity
; HLU: Pointer to a FIL struct
; DEU: Pointer to a 32-bit value to store the returned pointer/offset in
; Returns:
;   A: FRESULT (FR_OK or FR_INVALID_PARAMETER)
;
ffs_api_ftell:		ld	A, MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call 	SET_ADE24	; Convert DE to an address in segment A (MB)
			call	FIX_HLU24_no_mb_check
1:			push	DE		; DWORD * offset
			push	HL		; FIL * fp
			call	_fat_tell	; FRESULT returned in A
			pop	HL
			pop	DE
			ret

; Check for EOF
; HLU: Pointer to a FILINFO struct
; Returns:
;   A: 1 if end of file, otherwise 0
;
ffs_api_feof:		call	FIX_HLU24
			push	HL		; FILEINFO * fil
			call	_fat_EOF
			pop	HL
			ret

; Return size of file in bytes from the FIL struct
; NB if FIL is not valid, this may return junk, and DE is also not fully checked for validity
; HLU: Pointer to a FIL struct
; DEU: Pointer to a 32-bit value to store the returned size in
; Returns:
;   A: FRESULT (FR_OK or FR_INVALID_PARAMETER)
;
ffs_api_fsize:		ld	A, MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call 	SET_ADE24	; Convert DE to an address in segment A (MB)
			call	FIX_HLU24_no_mb_check
1:			push	DE		; DWORD * size
			push	HL		; FIL * fp
			call	_fat_size	; FRESULT returned in A
			pop	HL
			pop	DE
			ret

; Return `err` from the FIL struct
; HLU: Pointer to a FIL struct
; Returns:
;   A: Error code
;
ffs_api_ferror:		call	FIX_HLU24
			push	HL		; FIL * fp
			call	_fat_error	; Returns err in A
			pop	HL
			ret

; Open a directory
; HLU: Pointer to a blank DIR struct
; DEU: Pointer to the directory path
; Returns:
; A: FRESULT
ffs_api_dopen:		ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call 	SET_ADE24	; Convert DE to an address in segment A (MB)
			call	SET_AHL24	; Convert HL to an address in segment A (MB)
1:
			push	DE 		; const TCHAR *path
			push    HL		; DIR *dp
			call	_f_opendir
			ld	A, L		; FRESULT
			pop	HL
			pop	DE
			ret

; Close a directory
; HLU: Pointer to an open DIR struct
; Returns:
; A: FRESULT
ffs_api_dclose:		ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call	SET_AHL24	; Convert HL to an address in segment A (MB)
1:
			push    HL		; DIR *dp
			call	_f_closedir
			ld	A, L		; FRESULT
			pop	HL
			ret

; Read the next FILINFO from an open DIR
; HLU: Pointer to an open DIR struct
; DEU: Pointer to an empty FILINFO struct
; Returns:
; A: FRESULT
ffs_api_dread:		ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call 	SET_ADE24	; Convert DE to an address in segment A (MB)
			call	SET_AHL24	; Convert HL to an address in segment A (MB)
1:
			push	DE 		; FILINFO *fno
			push    HL		; DIR *dp
			call	_f_readdir
			ld	A, L		; FRESULT
			pop	HL
			pop	DE
			ret

; Find the first file in a directory matching a pattern
; HLU: Pointer to a blank DIR struct
; DEU: Pointer to a blank FILINFO struct
; BCU: Pointer to directory path
; IXU: Pointer to matching pattern
; Returns:
;   A: FRESULT
;
ffs_api_dfindfirst:	ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call	SET_AHL24
			call	SET_ADE24
			call	SET_ABC24
			call	SET_AIX24
1:			push	IX		; const TCHAR * pattern
			push	BC		; const TCHAR * path
			push	DE		; FILINFO * fno
			push    HL		; DIR * dp
			call	_f_findfirst
			ld	A, L		; FRESULT
			pop	HL
			pop	DE
			pop	BC
			pop	IX
			ret

; Find the next file in a directory matching a pattern
; HLU: Pointer to DIR struct from f_findfirst
; DEU: Pointer to a FILINFO struct
; Returns:
;   A: FRESULT
;
ffs_api_dfindnext:	call	FIX_HLU24
			push	HL
			push de
			pop hl
			call	FIX_HLU24
			ex	(SP), HL	; First stack entry is now DEU
			push	HL		; Second arg DIR
			call	_f_findnext
			ld	A, L		; FRESULT
			pop	HL
			pop	DE
			ret

; Check file exists
; HLU: Pointer to a FILINFO struct
; DEU: Pointer to the filename (0 terminated)
; Returns:
;   A: FRESULT
;
ffs_api_stat:		ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call 	SET_ADE24	; Convert DE to an address in segment A (MB)
			call	FIX_HLU24_no_mb_check
1:			push	HL		; FILEINFO * fil
			push	DE		; const TCHAR * path
			call	_f_stat
			ld	A, L 		; FRESULT
			pop	DE
			pop	HL
			ret

; Unlink a file using a filepath
; HLU: Pointer to the path to unlink
; Returns:
;   A: FRESULT
;
ffs_api_unlink:		ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			call	NZ, SET_AHL24
			push	HL		; const TCHAR * path
			call	_f_unlink
			ld	A, L		; FRESULT
			pop	HL
			ret

; renames and/or moves a file or sub-directory
; HLU: Pointer to the old name (0 terminated)
; DEU: Pointer to the new name (0 terminated)
; Returns:
;   A: FRESULT
;
ffs_api_rename:		ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call	SET_AHL24	; Convert HL to an address in segment A (MB)
			call 	SET_ADE24	; Convert DE to an address in segment A (MB)
1:			push	DE		; const TCHAR * newname
			push	HL		; const TCHAR * oldname
			call	_f_rename
			ld	A, L		; FRESULT
			pop	HL
			pop	DE
			ret

; Currently f_chmod and f_utime are not supported in our FatFS configuration
ffs_api_chmod:
			jp mos_api_not_implemented
ffs_api_utime:
			jp mos_api_not_implemented

; Create a directory
; HLU: Pointer to the directory path to create
; Returns:
;   A: FRESULT
;
ffs_api_mkdir:		ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			call	NZ, SET_AHL24	; Convert HL to an address in segment A (MB)
			push	HL		; const TCHAR * path
			call	_f_mkdir
			ld	A, L		; FRESULT
			pop	HL
			ret

; Change the current directory
; HLU: Pointer to the directory path to change to
; Returns:
;   A: FRESULT
;
ffs_api_chdir:		ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			call	NZ, SET_AHL24	; Convert HL to an address in segment A (MB)
			push	HL		; const TCHAR * path
			call	_f_chdir
			ld	A, L		; FRESULT
			pop	HL
			ret

ffs_api_chdrive:	; Available but as we only support one drive, this is not useful
			jp mos_api_not_implemented

; Copy the current directory (string) into buffer (hl)
; HLU: Pointer to a buffer
; BCU: Maximum length of buffer
; Returns:
; A: FRESULT
ffs_api_getcwd:		ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call	SET_AHL24	; Convert HL to an address in segment A (MB)
1:
			push	BC 		; sizeof(buffer)
			push    HL		; buffer
			call	_f_getcwd
			ld	A, L		; FRESULT
			pop	HL
			pop	BC
			ret

; Mount a volume
; HLU: Pointer to a blank FATFS struct (set to NULL for default)
; DEU: Pointer to the volume path (0 terminated, set to NULL for default)
;   C: Options byte
; Returns:
;   A: FRESULT
;
; NB in MOS 3 we will ignore all arguments, and just call mos_mount
ffs_api_mount:		call	_mos_mount	; Call the mount function in MOS
			ret

ffs_api_mkfs:		; Not supported in our FatFS configuration
			jp mos_api_not_implemented
ffs_api_fdisk:		; Not supported in our FatFS configuration
			jp mos_api_not_implemented

; Get the free space information
; HLU: Path (ideally caller should set this to NULL)
; DEU: Pointer to a block of memory to store number of free clusters, 32-bit value
; BCU: Pointer to a block of memory to store cluster size, 32-bit value
; Returns:
;   A: FRESULT
; NB this differs from a plain f_getfree call which takes a pointer for a FATFS object pointer
; we return only the cluster size, as the object contents may change in future versions
;
ffs_api_getfree:	ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call	SET_ABC24
			call	SET_ADE24
			; path is optional, so check if it's zero - arguably we could/should zero it
			ld	A, H
			or	A, L
			jr	Z, 1f
			ld	A, MB
			call	SET_AHL24
1:			push	BC		; UINT32 * clusterSize
			push	DE		; UINT32 * clusters
			push	HL		; const TCHAR * path
			call	_fat_getfree
			pop	HL
			pop	DE
			pop	BC
			ret

; Get the label of a volume
; HLU: Path (ideally caller should set this to NULL)
; DEU: Pointer to a buffer to store the label in (12 bytes, 23 if we enable exfat)
; BCU: Pointer to a block of memory to store the 32-bit volume serial number
; Returns:
;   A: FRESULT
;
ffs_api_getlabel:	ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call	SET_ABC24
			call	SET_ADE24
			; path is optional, so check if it's zero - arguably we could/should zero it
			ld	A, H
			or	A, L
			jr	Z, 1f
			ld	A, MB
			call	SET_AHL24
1:			push	BC		; UINT32 * vsn
			push	DE		; TCHAR * label
			push	HL		; const TCHAR * path
			call	_f_getlabel
			ld	A, L		; FRESULT
			pop	HL
			pop	DE
			pop	BC
			ret

; Sets the label of a volume
; HLU: New label
; Returns:
;   A: FRESULT
;
ffs_api_setlabel:	call	FIX_HLU24
			push	HL		; const TCHAR * label
			call	_f_setlabel
			ld	A, L		; FRESULT
			pop	HL

ffs_api_setcp:		; Not supported in our FatFS configuration
			jp mos_api_not_implemented

; Move the read/write pointer in a file
; HLU: Pointer to a FIL struct
; DEU: Pointer to a 32-bit value for to move the file pointer/offset to
; Returns:
;   A: FRESULT
;
ffs_api_flseek_p:	ld	A, MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call 	SET_ADE24	; Convert DE to an address in segment A (MB)
			call	FIX_HLU24_no_mb_check
1:			push	DE		; DWORD * offset
			push	HL		; FIL * fp
			call	_fat_lseek	; FRESULT returned in A
			pop	HL
			pop	DE
			ret

; Expose raw SD card access APIs
;

; Get unlock code for using SD card APIs
; HLU: Pointer to store fetched 24-bit unlock code value
; Returns:
; nothing
sd_api_getunlockcode:	call	FIX_HLU24
			push	HL		; int * unlockCode
			call	_SD_getUnlockCode	; Call the C function SD_getUnlockCode
			pop	HL
			ret

; Initialise SD card interface
; HLU: Pointer to 24-bit unlock code
; Returns:
; - A: 0 if OK/Ready, 1 for error, 2 for locked
sd_api_init:		call	FIX_HLU24	; HLU: Pointer to unlock code
			push	HL
			call	_SD_init_API
			pop	HL
			ret

; Read raw blocks from SD card
; HLU: Pointer to DWORD for block address/offset, and unlock code at ptr+4
; DEU: Pointer to buffer to read into
; BC: Number of blocks to read
; Returns:
; - A: 0 if OK, 1 for error, 2 for locked
; BYTE SD_readBlocks_API(DWORD * addr, BYTE *buf, WORD count)
sd_api_readblocks:	ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call	SET_ADE24	; Convert DE to an address in segment A (MB)
			call	SET_AHL24	; Convert HL to an address in segment A (MB)
1:			push	BC		; WORD count
			push	DE		; BYTE * buf
			push	HL		; DWORD * addr
			call	_SD_readBlocks_API
			pop	HL
			pop	DE
			pop	BC
			ret

; Write raw blocks to SD card
; HLU: Pointer to DWORD for block address/offset, and unlock code at ptr+4
; DEU: Pointer to buffer to write from
; BC: Number of blocks to write
; Returns:
; - A: 0 if OK, 1 for error, 2 for locked
; BYTE SD_writeBlocks_API(DWORD * addr, BYTE *buf, WORD count)
sd_api_writeblocks:	ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			call	SET_ADE24	; Convert DE to an address in segment A (MB)
			call	SET_AHL24	; Convert HL to an address in segment A (MB)
1:			push	BC		; WORD count
			push	DE		; BYTE * buf
			push	HL		; DWORD * addr
			call	_SD_readBlocks_API
			pop	HL
			pop	DE
			pop	BC
			ret

; C calling convention functions

; Get a pointer to a system variable
; Returns:
; HLU: Pointer to system variables (see mos_api.asm for more details)
;
func_getsysvars:	ld	HL, _sysvars
			ret

; Get the address of the keyboard map
; Returns:
; HLU: Base address of the keymap
;
func_getkbmap:		ld	HL, _keymap
			ret

; Get function
; Only usable for code in ADL mode
; C: Flags (must be zero for now)
; B: Function number
; Returns:
; - A: 0 (OK), 19 (Invalid parameter), 20 (Invalid command - called from Z80 mode)
; - HL: Pointer to function (or 0 if invalid)
;
mos_api_getfunction:	ld	HL, 0		; Set HL to 0 (no function) as default
			ld	A, MB		; A: MB
			or	A, A 		; Check whether MB is 0, i.e. in 24-bit mode
			jr	Z, 1f		; It is, so skip as all addresses can be assumed to be 24-bit
			ld	A, 20		; Invalid command (called from Z80 mode)
			ret			; Return with error code 20 (Invalid command)
1:			ld	A, C		; Get flags
			or	A, A		; Check if flags are set
			jr	Z, 1f		; Only support no flags for now
			ld	A, 19		; Invalid parameter (flags set)
			ret			; Return with error code 19 (Invalid parameter)
1:			ld	A, B		; Get function number
			cp	mos_function_block_size	; Check if out of bounds
			jr	C, 1f
			ld	A, 19		; Invalid parameter (function number out of bounds)
			ret			; Return with error code 19 (Invalid parameter)
1:			; Get function address
			; first we need to triple A to get the correct offset in the function table
			push	BC		; Save BC
			push	IX		; Save IX
			ld	A, B		; Get function number
			ld	BC, 0		; Set BC to 0
			ld	C, A		; Set BC to function number
			push bc
			pop ix; Copy to IX
			add	IX, IX		; IX = 2 * function number
			add	IX, BC		; IX = 3 * function number
			ld	BC, mos_function_block_start	; BC = start of function table
			add	IX, BC		; IX = address of function pointer in table
			ld	HL, (IX)	; Get function pointer from table
			pop	IX		; Restore IX
			pop	BC		; Restore BC
			ld	A, 0		; Set A to 0 (OK)
			ret			; Return with OK code

mos_function_block_start:
			d24	_SD_init	; 0x00
			d24	_SD_readBlocks	; 0x01
			d24	_SD_writeBlocks	; 0x02
			d24	0		; 0x03 (reserved for potential future _SD_status function)
			d24	0		; 0x04 (reserved for potential future _SD_ioctl function)
			d24	_f_printf	; 0x05
			d24	_f_findfirst	; 0x06
			d24	_f_findnext	; 0x07
			d24	_open_UART1	; 0x08
			d24	_setVarVal	; 0x09
			d24	_readVarVal	; 0x0A
			d24	_gsTrans	; 0x0B
			d24	_substituteArgs	; 0x0C
			d24	_resolvePath	; 0x0D
			d24	_getDirectoryForPath	; 0x0E
			d24	_resolveRelativePath	; 0x0F
			d24	func_getsysvars	; 0x10
			d24	func_getkbmap	; 0x11
			d24	0		; Retired getfunction12 tombstone
			.if (. - mos_function_block_start) / 3 != mos_function_uart0_async
			.error "UART slot disagrees with canonical reservation"
			.endif
			d24	uart0_async_getapi	; 0x13, ADL UART0 API discovery

.equiv mos_function_block_size, (. - mos_function_block_start) / 3
