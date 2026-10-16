; Native AgonDev source derived from official MOS v3.0.2: src/mos_api.inc
; Upstream ancestry and changes: docs/upstream-origin.md and docs/deviations.md.
; DEV-009: guard repeated includes; SDK hardware aliases are checked by the build.
.ifndef AGON_MOS_SRC_MOS_API_INC
.set AGON_MOS_SRC_MOS_API_INC,1
;
; Title:	AGON MOS - API for user projects
; Author:	Dean Belfield
; Created:	03/08/2022
; Last Updated:	11/11/2023
;
; Modinfo:
; 05/08/2022:	Added mos_feof
; 09/08/2022:	Added system variables: cursorX, cursorY
; 18/08/2022:	Added system variables: scrchar, scrpixel, audioChannel, audioSuccess, vpd_pflags
; 05/09/2022:	Added mos_ren, vdp_pflag_mode
; 24/09/2022:	Added mos_getError, mos_mkdir
; 13/10/2022:	Added mos_oscli
; 23/02/2023:	Added more sysvars, fixed typo in sysvar_audioSuccess, offsets for sysvar_scrCols, sysvar_scrRows
; 04/03/2023:	Added sysvar_scrpixelIndex
; 08/03/2023:	Renamed sysvar_keycode to sysvar_keyascii, added sysvar_vkeycode
; 15/03/2023:	Added mos_copy, mos_getrtc, mos_setrtc, rtc, vdp_pflag_rtc
; 21/03/2023:	Added mos_setintvector, sysvars for keyboard status, vdu codes for vdp
; 22/03/2023:	The VDP commands are now indexed from 0x80
; 29/03/2023:	Added mos_uopen, mos_uclose, mos_ugetc, mos_uputc
; 13/04/2023:	Added FatFS file structures (FFOBJID, FIL, DIR, FILINFO)
; 15/04/2023:	Added mos_getfil, mos_fread, mos_fwrite and mos_flseek
; 19/05/2023:	Added sysvar_scrMode
; 05/06/2023:	Added sysvar_rtcEnable
; 03/08/2023:	Added mos_setkbvector
; 10/08/2023:	Added mos_getkbmap
; 11/11/2023:	Added mos_i2c_open, mos_i2c_close, mos_i2c_write and mos_i2c_read

; VDP control (VDU 23, 0, n)
;
.equiv vdp_gp, 0x80
.equiv vdp_keycode, 0x81
.equiv vdp_cursor, 0x82
.equiv vdp_scrchar, 0x83
.equiv vdp_scrpixel, 0x84
.equiv vdp_audio, 0x85
.equiv vdp_mode, 0x86
.equiv vdp_rtc, 0x87
.equiv vdp_keystate, 0x88
.equiv vdp_logicalcoords, 0xC0
.equiv vdp_terminalmode, 0xFF

; MOS high level functions
;
.equiv mos_getkey, 0x00
.equiv mos_load, 0x01
.equiv mos_save, 0x02
.equiv mos_cd, 0x03
.equiv mos_dir, 0x04
.equiv mos_del, 0x05
.equiv mos_ren, 0x06
.equiv mos_mkdir, 0x07
.equiv mos_sysvars, 0x08
.equiv mos_editline, 0x09
.equiv mos_fopen, 0x0A
.equiv mos_fclose, 0x0B
.equiv mos_fgetc, 0x0C
.equiv mos_fputc, 0x0D
.equiv mos_feof, 0x0E
.equiv mos_getError, 0x0F
.equiv mos_oscli, 0x10
.equiv mos_copy, 0x11
.equiv mos_getrtc, 0x12
.equiv mos_setrtc, 0x13
.equiv mos_setintvector, 0x14
.equiv mos_uopen, 0x15
.equiv mos_uclose, 0x16
.equiv mos_ugetc, 0x17
.equiv mos_uputc, 0x18
.equiv mos_getfil, 0x19
.equiv mos_fread, 0x1A
.equiv mos_fwrite, 0x1B
.equiv mos_flseek, 0x1C
.equiv mos_setkbvector, 0x1D
.equiv mos_getkbmap, 0x1E
.equiv mos_i2c_open, 0x1F
.equiv mos_i2c_close, 0x20
.equiv mos_i2c_write, 0x21
.equiv mos_i2c_read, 0x22
.equiv mos_unpackrtc, 0x23
.equiv mos_flseek_p, 0x24

; MOS string functions
;
.equiv mos_pmatch, 0x28
.equiv mos_getargument, 0x29
.equiv mos_extractstring, 0x2A
.equiv mos_extractnumber, 0x2B
.equiv mos_escapestring, 0x2C

; System variables and related functions
;
.equiv mos_setvarval, 0x30
.equiv mos_readvarval, 0x31
.equiv mos_gsinit, 0x32
.equiv mos_gsread, 0x33
.equiv mos_gstrans, 0x34
.equiv mos_substituteargs, 0x35
.equiv mos_evaluateexpression, 0x36; not implemented, yet
; 37h not yet used

; Path resolution functions
;
.equiv mos_resolvepath, 0x38
.equiv mos_getdirforpath, 0x39
.equiv mos_getleafname, 0x3A
.equiv mos_isdirectory, 0x3B
.equiv mos_getabsolutepath, 0x3C

; VDP Protocol apis
;
.equiv mos_clearvdpflags, 0x40
.equiv mos_waitforvdpflags, 0x41

; Function and module APIs
;
.equiv mos_getfunction, 0x50

; DEV-013: shared custom-project reservations; constants do not enable features.
.include "mos_api_reservations.inc"

; Low-level SD card functions
;
.equiv sd_getunlockcode, 0x70
.equiv sd_init, 0x71
.equiv sd_readblocks, 0x72
.equiv sd_writeblocks, 0x73

; FatFS file access functions
;
.equiv ffs_fopen, 0x80
.equiv ffs_fclose, 0x81
.equiv ffs_fread, 0x82
.equiv ffs_fwrite, 0x83
.equiv ffs_flseek, 0x84
.equiv ffs_ftruncate, 0x85
.equiv ffs_fsync, 0x86
.equiv ffs_fforward, 0x87
.equiv ffs_fexpand, 0x88
.equiv ffs_fgets, 0x89
.equiv ffs_fputc, 0x8A
.equiv ffs_fputs, 0x8B
.equiv ffs_fprintf, 0x8C
.equiv ffs_ftell, 0x8D
.equiv ffs_feof, 0x8E
.equiv ffs_fsize, 0x8F
.equiv ffs_ferror, 0x90

; FatFS directory access functions
;
.equiv ffs_dopen, 0x91
.equiv ffs_dclose, 0x92
.equiv ffs_dread, 0x93
.equiv ffs_dfindfirst, 0x94
.equiv ffs_dfindnext, 0x95

; FatFS file and directory management functions
;
.equiv ffs_stat, 0x96
.equiv ffs_unlink, 0x97
.equiv ffs_rename, 0x98
.equiv ffs_chmod, 0x99
.equiv ffs_utime, 0x9A
.equiv ffs_mkdir, 0x9B
.equiv ffs_chdir, 0x9C
.equiv ffs_chdrive, 0x9D
.equiv ffs_getcwd, 0x9E

; FatFS volume management and system configuration functions
;
.equiv ffs_mount, 0x9F
.equiv ffs_mkfs, 0xA0
.equiv ffs_fdisk, 0xA1
.equiv ffs_getfree, 0xA2
.equiv ffs_getlabel, 0xA3
.equiv ffs_setlabel, 0xA4
.equiv ffs_setcp, 0xA5

; Additional fatfs calls
;
.equiv ffs_flseek_p, 0xA6


; File access modes
;
.equiv fa_read, 0x01
.equiv fa_write, 0x02
.equiv fa_open_existing, 0x00
.equiv fa_create_new, 0x04
.equiv fa_create_always, 0x08
.equiv fa_open_always, 0x10
.equiv fa_open_append, 0x30

; System variable indexes for api_sysvars
; Index into _sysvars in globals.asm
;
.equiv sysvar_time, 0x00; 4: Clock timer in centiseconds (incremented by 2 every VBLANK)
.equiv sysvar_vpd_pflags, 0x04; 1: Flags to indicate completion of VDP commands
.equiv sysvar_keyascii, 0x05; 1: ASCII keycode, or 0 if no key is pressed
.equiv sysvar_keymods, 0x06; 1: Keycode modifiers
.equiv sysvar_cursorX, 0x07; 1: Cursor X position
.equiv sysvar_cursorY, 0x08; 1: Cursor Y position
.equiv sysvar_scrchar, 0x09; 1: Character read from screen
.equiv sysvar_scrpixel, 0x0A; 3: Pixel data read from screen (R,B,G)
.equiv sysvar_audioChannel, 0x0D; 1: Audio channel
.equiv sysvar_audioSuccess, 0x0E; 1: Audio channel note queued (0 = no, 1 = yes)
.equiv sysvar_scrWidth, 0x0F; 2: Screen width in pixels
.equiv sysvar_scrHeight, 0x11; 2: Screen height in pixels
.equiv sysvar_scrCols, 0x13; 1: Screen columns in characters
.equiv sysvar_scrRows, 0x14; 1: Screen rows in characters
.equiv sysvar_scrColours, 0x15; 1: Number of colours displayed
.equiv sysvar_scrpixelIndex, 0x16; 1: Index of pixel data read from screen
.equiv sysvar_vkeycode, 0x17; 1: Virtual key code from FabGL
.equiv sysvar_vkeydown, 0x18; 1: Virtual key state from FabGL (0=up, 1=down)
.equiv sysvar_vkeycount, 0x19; 1: Incremented every time a key packet is received
.equiv sysvar_rtc, 0x1A; 6: Real time clock data
.equiv sysvar_spare, 0x20; 2: Spare, previously used by rtc
.equiv sysvar_keydelay, 0x22; 2: Keyboard repeat delay
.equiv sysvar_keyrate, 0x24; 2: Keyboard repeat reat
.equiv sysvar_keyled, 0x26; 1: Keyboard LED status
.equiv sysvar_scrMode, 0x27; 1: Screen mode
.equiv sysvar_rtcEnable, 0x28; 1: RTC enable flag (0: disabled, 1: use ESP32 RTC)
.equiv sysvar_mouseX, 0x29; 2: Mouse X position
.equiv sysvar_mouseY, 0x2B; 2: Mouse Y position
.equiv sysvar_mouseButtons, 0x2D; 1: Mouse button state
.equiv sysvar_mouseWheel, 0x2E; 1: Mouse wheel delta
.equiv sysvar_mouseXDelta, 0x2F; 2: Mouse X delta
.equiv sysvar_mouseYDelta, 0x31; 2: Mouse Y delta
.equiv sysvar_gp, 0x37; 1: General poll packet data

; Flags for the VPD protocol
;
.equiv vdp_pflag_cursor, 0b00000001
.equiv vdp_pflag_scrchar, 0b00000010
.equiv vdp_pflag_point, 0b00000100
.equiv vdp_pflag_audio, 0b00001000
.equiv vdp_pflag_mode, 0b00010000
.equiv vdp_pflag_rtc, 0b00100000
.equiv vdp_pflag_mouse, 0b01000000
; vdp_pflag_buffered:	EQU	10000000b

;
; FatFS structures
; These mirror the structures contained in src_fatfs/ff.h in the MOS project
;
; Object ID and allocation information (FFOBJID)
;
; zds2gas: .STRUCT FFOBJID
.equiv FFOBJID.fs, 0
; zds2gas: fs:		DS	3 (3 bytes, no allocation); Pointer to the hosting volume of this object
.equiv FFOBJID.id, 3
; zds2gas: id:		DS	2 (2 bytes, no allocation); Hosting volume mount ID
.equiv FFOBJID.attr, 5
; zds2gas: attr:		DS	1 (1 bytes, no allocation); Object attribute
.equiv FFOBJID.stat, 6
; zds2gas: stat:		DS	1 (1 bytes, no allocation); Object chain status (b1-0: =0:not contiguous, =2:contiguous, =3:fragmented in this session, b2:sub-directory stretched)
.equiv FFOBJID.sclust, 7
; zds2gas: sclust:		DS	4 (4 bytes, no allocation); Object data start cluster (0:no cluster or root directory)
.equiv FFOBJID.objsize, 11
; zds2gas: objsize:	DS	4 (4 bytes, no allocation); Object size (valid when sclust != 0)
.equiv FFOBJID_SIZE, 15
; zds2gas: .ENDSTRUCT FFOBJID (15 bytes)
;
; File object structure (FIL)
;
; zds2gas: .STRUCT FIL
.equiv FIL.obj, 0
; zds2gas: obj:		.TAG	FFOBJID (15 bytes, no allocation); Object identifier
.equiv FIL.flag, 15
; zds2gas: flag:		DS	1 (1 bytes, no allocation); File status flags
.equiv FIL.err, 16
; zds2gas: err:		DS	1 (1 bytes, no allocation); Abort flag (error code)
.equiv FIL.fptr, 17
; zds2gas: fptr:		DS	4 (4 bytes, no allocation); File read/write pointer (Zeroed on file open)
.equiv FIL.clust, 21
; zds2gas: clust:		DS	4 (4 bytes, no allocation); Current cluster of fpter (invalid when fptr is 0)
.equiv FIL.sect, 25
; zds2gas: sect:		DS	4 (4 bytes, no allocation); Sector number appearing in buf[] (0:invalid)
.equiv FIL.dir_sect, 29
; zds2gas: dir_sect:	DS	4 (4 bytes, no allocation); Sector number containing the directory entry
.equiv FIL.dir_ptr, 33
; zds2gas: dir_ptr:	DS	3 (3 bytes, no allocation); Pointer to the directory entry in the win[]
.equiv FIL_SIZE, 36
; zds2gas: .ENDSTRUCT FIL (36 bytes)
;
; Directory object structure (DIR)
;
; zds2gas: .STRUCT DIR
.equiv DIR.obj, 0
; zds2gas: obj:		.TAG	FFOBJID (15 bytes, no allocation); Object identifier
.equiv DIR.dptr, 15
; zds2gas: dptr:		DS	4 (4 bytes, no allocation); Current read/write offset
.equiv DIR.clust, 19
; zds2gas: clust:		DS	4 (4 bytes, no allocation); Current cluster
.equiv DIR.sect, 23
; zds2gas: sect:		DS	4 (4 bytes, no allocation); Current sector (0:Read operation has terminated)
.equiv DIR.dir, 27
; zds2gas: dir:		DS	3 (3 bytes, no allocation); Pointer to the directory item in the win[]
.equiv DIR.fn, 30
; zds2gas: fn:		DS	12 (12 bytes, no allocation); SFN (in/out) {body[8],ext[3],status[1]}
.equiv DIR.blk_ofs, 42
; zds2gas: blk_ofs:	DS	4 (4 bytes, no allocation); Offset of current entry block being processed (0xFFFFFFFF:Invalid)
.equiv DIR_SIZE, 46
; zds2gas: .ENDSTRUCT DIR (46 bytes)
;
; File information structure (FILINFO)
;
; zds2gas: .STRUCT FILINFO
.equiv FILINFO.fsize, 0
; zds2gas: fsize:		DS 	4 (4 bytes, no allocation); File size
.equiv FILINFO.fdate, 4
; zds2gas: fdate:		DS	2 (2 bytes, no allocation); Modified date
.equiv FILINFO.ftime, 6
; zds2gas: ftime:		DS	2 (2 bytes, no allocation); Modified time
.equiv FILINFO.fattrib, 8
; zds2gas: fattrib:	DS	1 (1 bytes, no allocation); File attribute
.equiv FILINFO.altname, 9
; zds2gas: altname:	DS	13 (13 bytes, no allocation); Alternative file name
.equiv FILINFO.fname, 22
; zds2gas: fname:		DS	256 (256 bytes, no allocation); Primary file name
.equiv FILINFO_SIZE, 278
; zds2gas: .ENDSTRUCT FILINFO (278 bytes)

;
; Macro for calling the API
; Parameters:
; - function: One of the function numbers listed above
;
.macro MOSCALL function
			ld	A, \function
			rst.lis	0x08
			.endm

.endif
