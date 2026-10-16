; Native AgonDev source derived from official MOS v3.0.2: src/sd.inc
; Upstream ancestry and changes: docs/upstream-origin.md and docs/deviations.md.
; DEV-009: guard repeated includes; SDK hardware aliases are checked by the build.
.ifndef AGON_MOS_SRC_SD_INC
.set AGON_MOS_SRC_SD_INC,1
;
; Title:	AGON MOS - Low level SD card assembler defines
; Author:	Leigh Brown
; Created:	28/05/2023
; Last Updated:	28/05/2023
;
; Modinfo:


.equiv CMD0, 0
.equiv CMD0_ARG, 0x00000000
.equiv CMD0_CRC, 0x94

.equiv CMD8, 8
.equiv CMD8_ARG, 0x0000001AA
.equiv CMD8_CRC, 0x86;(1000011 << 1)

.equiv CMD17, 17
.equiv CMD17_CRC, 0x00

.equiv CMD24, 24
.equiv CMD24_CRC, 0x00

.equiv CMD55, 55
.equiv CMD55_ARG, 0x00000000
.equiv CMD55_CRC, 0x00

.equiv CMD58, 58
.equiv CMD58_ARG, 0x00000000
.equiv CMD58_CRC, 0x00

.equiv ACMD41, 41
.equiv ACMD41_ARG, 0x40000000
.equiv ACMD41_CRC, 0x00


.endif
