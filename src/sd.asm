; Native AgonDev source derived from official MOS v3.0.2: src/sd.asm
; Upstream ancestry and changes: docs/upstream-origin.md and docs/deviations.md.
;
; Title:	AGON MOS - SD card low level assembly language
; Author:	Leigh Brown
; Created:	26/05/2023
; Last Updated:	26/05/2023

; Modinfo
;

		.include "ez80f92.inc"
		.include "equs.inc"
		.include "sd.inc"
		.include "macros.inc"

.equiv SD_CS, 4; Bit 4 of Port B

.equiv SD_SUCCESS, 0
.equiv SD_ERROR, 1
.equiv SD_READY, 0

.equiv SD_INIT_CYCLES, 10

.equiv SD_START_TOKEN, 0xFE
.equiv SD_ERROR_TOKEN, 0x00

.equiv SD_DATA_ACCEPTED, 0x05
.equiv SD_DATA_REJECTED_CRC, 0x0B
.equiv SD_DATA_REJECTED_WRITE, 0x0D

.equiv SD_BLOCK_LEN, 512

.equiv SD_CMD_LEN, 6

		.global		_SD_init
		.global		_SD_readBlocks
		.global		_SD_writeBlocks

		.extern		_spi_transfer
		.extern		_spi_read_one
		.extern		_spi_read
		.extern		_spi_write
		.extern		_sdcardDelay

		.assume adl=1


; BYTE SD_init(void)
;
; Local variables
;	IX-6..IX-2	BYTE res[5]
;

		; zds2gas: SCOPE

_SD_init:
		; Function prologue
		push		IX
		ld		IX,0
		add		IX,SP

		; Make space for local variables
		ld		HL,-6
		add		HL,SP
		ld		SP,HL

		; Off we go
		call		_SD_powerUpSeq

		; Command card to idle
		ld		B,10
.LSD_init_loop1:		push		BC
		call		_SD_goIdleState
		pop		BC
		ld		(IX-6),A
		cp		A,0x01
		jr		Z,.LSD_init_success1
		djnz		.LSD_init_loop1

		; Failed after 10 attempts
		jr		.LSD_init_out_error

		; Send interface conditions
.LSD_init_success1:	pea		IX-6
		call		_SD_sendIfCond
		pop		BC

		; Check first byte of response is 0x01
		ld		A,(IX-6)
		cp		A,1
		jr		NZ,.LSD_init_out_error

		; Check fifth byte of response is 0xAA
		ld		A,(IX-2)
		cp		A,0xAA
		jr		NZ,.LSD_init_out_error

		; Attempt to initialize card

		; Repeat up to 100 times
		ld		B,100
.LSD_init_loop2:		push		BC
		call		_SD_sendApp
		cp		A,2		; is res[0] < 2 ?
		jr		NC,.LSD_init_wait2
		call		_SD_sendOpCond
		cp		A,SD_READY
		jr		Z,.LSD_init_success2

		; Wait 10ms before we try again
.LSD_init_wait2:		DELAY_MS	10
		pop		BC
		djnz		.LSD_init_loop2

		; Timeout: error
		jr		.LSD_init_out_error

.LSD_init_success2:	pea		IX-6
		call		_SD_readOCR
		pop		BC
		ld		A,(IX-5)
		rla
		jr		C,.LSD_init_out_success
		; Fall through to $out_error

.LSD_init_out_error:	ld		A,SD_ERROR
		jr		.LSD_init_exit

.LSD_init_out_success:	xor		A,A	; LD A,LD_SUCCESS
.LSD_init_exit:		ld		SP,IX
		pop		IX
		ret


; BYTE SD_readBlocks(DWORD addr, BYTE *buf, WORD count)
;		     IX+6        IX+12      IX+15
;
; Local variables:
;	IX-3/IX-2	Reserved for SD_readSingleBlock
;	IX-1		token

		; zds2gas: SCOPE

_SD_readBlocks:
		; Function prologue
		push		IX
		ld		IX,0
		add		IX,SP
		push		BC	; 3 bytes for local variables

		; sign-extend count (it's unsigned, so set top byte to 0)
		ld		(IX+17),0

		; HL := count, then jump to the check for zero
		ld		HL,(IX+15)
		jr		.LSD_readBlocks_start

		; Read current block
.LSD_readBlocks_loop:		call		SD_readSingleBlock

		; Exit with SD_ERROR if res1 >= 2
		cp		A,2
		jr		NC,.LSD_readBlocks_err_exit

		; or if token != SD_DATA_ACCEPTED
		ld		A,(IX-1)
		cp		A,0xFE
		jr		NZ,.LSD_readBlocks_err_exit

		; Update sector, buf and count
		; HL is set to the updated value of count
		call		SD_updateIOVars
.LSD_readBlocks_start:		ld		A,H
		or		A,L
		jr		NZ,.LSD_readBlocks_loop

		; Finished, return SD_SUCCESS (which happens to be zero)
.LSD_readBlocks_done:		xor		A,A
.LSD_readBlocks_exit:		ld		SP,IX
		pop		IX
		ret

		; Error exit, slow path so can save a couple of bytes
.LSD_readBlocks_err_exit:	ld		A,SD_ERROR
		jr		.LSD_readBlocks_exit

; Delay by 30ms. Roughly how long an old 5.25" disk takes to read 512 bytes
SD_delayDisc:
		ld		A, (_sdcardDelay)
		or		A
		ret		Z

		push	HL
		push	DE

		ld		DE, 1
		ld		HL, 81000
		; 81000 * 6 cycles per loop
.LSD_readBlocks_loop4:	and		A
		sbc		HL, DE
		jr		NZ, .LSD_readBlocks_loop4

		pop		DE
		pop		HL
		ret


; SD_readSingleBlock

; This does not use the C calling-convention.
; It uses the stack frame pointer and local space set up by _SD_readBlocks
;
; Output: A := res1

		; zds2gas: SCOPE

SD_readSingleBlock:
		call	SD_delayDisc
		ld		(IX-3),CMD17     | 0x40
		ld		(IX-2),CMD17_CRC | 0x01

		call		SD_sendIOCmd	; Sets *token to 0xFF too
		push		AF		; Save res1 to be returned
		cp		A,0xFF
		jr		Z,.LSD_readSingleBlock_out3

		; Wait for a response token (timeout = 100ms)
		TIMER_SET	0,100
		TIMER_START	0

.LSD_readSingleBlock_loop1:		call		_spi_read_one
		ld		B,A		; Move byte read to B
		cp		A,0xFF
		jr		NZ,.LSD_readSingleBlock_out1

		; Continue until the timer expires
		TIMER_EXP	0		; (clobbers just A)
		jr		NC,.LSD_readSingleBlock_loop1

.LSD_readSingleBlock_out1:		TIMER_RESET	0		; (clobbers just A)

		; Check if card response is SD_START_TOKEN

		; *token = read
		ld		(IX-1),B

		; If response token is 0xFE then read the sector
		ld		A,SD_START_TOKEN
		cp		A,B
		jr		NZ,.LSD_readSingleBlock_out3

		; Read the sector
		ld		BC,SD_BLOCK_LEN
		push		BC
		ld		BC,(IX+12)	; buf
		push		BC
		call		_spi_read
		pop		BC
		pop		BC

		; Read and discard the two CRC bytes
		call		_spi_read_one
		call		_spi_read_one

		; Deassert chip select
.LSD_readSingleBlock_out3:		call		_SD_CS_disable

		; Restore res1 to return to caller
		pop		AF
		ret


; BYTE SD_writeBlocks(DWORD addr, BYTE *buf, WORD count)
;		     IX+6        IX+12      IX+15
;
; Local variables:
;	IX-3/IX-2	Reserved for SD_writeSingleBlock
;	IX-1		token

		; zds2gas: SCOPE

_SD_writeBlocks:
		; Function prologue
		push		IX
		ld		IX,0
		add		IX,SP
		push		BC	; 3 bytes for local variables

		; sign extend count (it's unsigned, so set top byte to 0)
		ld		(IX+17),0

		; HL := count, then jump to the check for zero
		ld		HL,(IX+15)
		jr		.LSD_writeBlocks_start

.LSD_writeBlocks_loop:		call		SD_writeSingleBlock

		; Exit with SD_ERROR if res1 != 0x00
		or		A,A
		jr		NZ,.LSD_writeBlocks_err_exit

		; or if token != SD_DATA_ACCEPTED
		ld		A,(IX-1)
		cp		A,SD_DATA_ACCEPTED
		jr		NZ,.LSD_writeBlocks_err_exit

		; Update sector, buf and count
		; HL is set to the updated value of count
		call		SD_updateIOVars
.LSD_writeBlocks_start:		ld		A,H
		or		A,L
		jr		NZ,.LSD_writeBlocks_loop

		; Finished, return SD_SUCCESS (which happens to be zero)
.LSD_writeBlocks_done:		xor		A,A
.LSD_writeBlocks_exit:		ld		SP,IX
		pop		IX
		ret

		; Error exit, slow path so can save a couple of bytes
.LSD_writeBlocks_err_exit:	ld		A,SD_ERROR
		jr		.LSD_writeBlocks_exit


; SD_writeSingleBlock

; This does not use the C calling-convention.
; It uses the stack frame pointer set up by _SD_writeBlocks
;
; Output: A := res1

		; zds2gas: SCOPE

SD_writeSingleBlock:
		call	SD_delayDisc
		ld		(IX-3),CMD24     | 0x40
		ld		(IX-2),CMD24_CRC | 0x01

		call		SD_sendIOCmd	; Sets *token to 0xFF too
		push		AF		; Save res1 to be returned
		cp		A,SD_READY
		jp		NZ,.LSD_writeSingleBlock_out3 ; [DEV-006: ZDS relaxes this long JR; GNU requires explicit JP.]

		; Send start token
		ld		C,SD_START_TOKEN
		push		BC
		call		_spi_transfer
		pop		BC

		; Write buffer to card
		ld		BC,SD_BLOCK_LEN
		push		BC
		ld		BC,(IX+12)
		push		BC
		call		_spi_write
		pop		BC
		pop		BC

		; Wait for a response token (timeout = 250ms)
		TIMER_SET	0,250
		TIMER_START	0

.LSD_writeSingleBlock_loop1:		call		_spi_read_one
		ld		B,A		; Save byte read
		cp		A,0xFF
		jr		NZ,.LSD_writeSingleBlock_gotit1

		; Continue until the timer expires
		TIMER_EXP	0		; (clobbers just A)
		jr		NC,.LSD_writeSingleBlock_loop1

		; Timeout - just fall through

.LSD_writeSingleBlock_gotit1:	TIMER_RESET	0		; (clobbers just A)

		; If data accepted
		ld		A,0x1F
		and		A,B
		cp		A,5
		jr		NZ,.LSD_writeSingleBlock_out3

		; *token = 0x05 (conveniently left in register A)
		ld		(IX-1),A

		; Wait for write to finish (timeout = 250ms)
		TIMER_SET	0,250
		TIMER_START	0

.LSD_writeSingleBlock_loop2:		call		_spi_read_one
		cp		A,0x00
		jr		NZ,.LSD_writeSingleBlock_gotit2

		; Continue until the timer expires
		TIMER_EXP	0
		jr		NC,.LSD_writeSingleBlock_loop2

		; Timeout, skip over setting token
		jr		.LSD_writeSingleBlock_notgot

.LSD_writeSingleBlock_gotit2:	; Success: set token to 0x00
		xor		A,A
		ld		A,(IX-1)

.LSD_writeSingleBlock_notgot:	; Reset the timer
		TIMER_RESET	0

		; Deassert chip select
.LSD_writeSingleBlock_out3:		call		_SD_CS_disable

		; Restore res1 to return to caller
		pop		AF
		ret


; SD_sendIOCmd
;
; This does not use the C calling-convention.
; It uses the stack frame pointer set up by _SD_readBlocks/_SD_writeBlocks
;
; Input:
; Taken from stack frame and local variables of _SD_readBlocks/_SD_writeBlocks
;
; Output:
; A: response
;
		; zds2gas: SCOPE

SD_sendIOCmd:
		; Set token to none
		ld		(IX-1),0xFF

		; Assert chip select
		call		_SD_CS_enable

		; Push arguments on to stack first
		ld		HL,SD_CMD_LEN
		push		HL
		ld		HL,sd_cmd_buffer
		push		HL

		; buf[0] := command
		ld		B,(IX-3)
		ld		(HL),B
		inc		HL

		; buf[1..4] := address (big endian so swap bytes around)
		ld		BC,(IX+8)
		ld		(HL),B
		inc		HL
		ld		(HL),C
		inc		HL
		ld		BC,(IX+6)
		ld		(HL),B
		inc		HL
		ld		(HL),C
		inc		HL

		; buf[5] : = CRC
		ld		B,(IX-2)
		ld		(HL),B

		; Send contents of sd_cmd_buffer
		call		_spi_write
		pop		HL
		pop		HL

		; res1 = SD_readRes1();
		jp		_SD_readRes1


; SD_updateIOVars
;
; This does not use the C calling-convention
; It uses the stack frame pointer set up by _SD_readBlocks/_SD_writeBlocks
;
; Inputs:	None
; Outpus:	HL := updated value of count

		; zds2gas: SCOPE

SD_updateIOVars:
		; sector++
		ld		HL,(IX+6)
		ld		BC,1
		xor		A,A
		add		HL,BC
		adc		A,(IX+9)
		ld		(IX+6),HL
		ld		(IX+9),A

		; buf += SD_BLOCK_LEN
		ld		HL,(IX+12)
		ld		DE,SD_BLOCK_LEN	; Use DE here so that BC can
		add		HL,DE		; be re-used below
		ld		(IX+12),HL

		; --count
		ld		HL,(IX+15)
		or		A,A
		sbc		HL,BC		; BC still set to 1 from above
		ld		(IX+15),HL
		ret


; BYTE SD_readRes1(void)
;

		; zds2gas: SCOPE

_SD_readRes1:	ld		B,9
.LSD_readRes1_loop:		push		BC	; save B over call to _spi_read_one
		call		_spi_read_one
		pop		BC
		cp		A,0xFF
		jr		NZ,.LSD_readRes1_out
		djnz		.LSD_readRes1_loop
.LSD_readRes1_out:		ret


; void SD_readRes7(BYTE *res)
;

		; zds2gas: SCOPE

_SD_readRes7:	; Function prologue
		push		IX
		ld		IX,0
		add		IX,SP

		call		_SD_readRes1
		ld		HL,(IX+6)

		; Restore IX now, so we can "RET NC" later
		; No local variables so no need to restore SP
		pop		IX

		; Save byte read into res[0]
		ld		(HL),A

		; Exit if byte read is >1 (in other words, >= 2)
		cp		A,2
		ret		NC

		; Otherwise read the next four bytes
		ld		BC,4
		push		BC
		inc		HL
		push		HL
		call		_spi_read
		pop		HL
		pop		BC
		ret


; NB: The following functions all jump to SD_sendCmdReadRes1
;
; _SD_goIdleState
; _SD_sendApp
; _SD_sendOpCond

; BYTE SD_goIdleState(void);
;

		; zds2gas: SCOPE

_SD_goIdleState:
		ld		BC,cmd0_string
		jr		SD_sendCmdReadRes1


; UINT8 SD_sendApp(void)
;

_SD_sendApp:
		ld		BC,cmd55_string
		jr		SD_sendCmdReadRes1


; UINT8 SD_sendOpCond(void)
;
_SD_sendOpCond:
		ld		BC,acmd41_string
		; Fallthrough instead of JR SD_sendCmdReadRes1

SD_sendCmdReadRes1:
		ld		DE,SD_CMD_LEN
		push		DE		; push arguments to _spi_write
		push		BC		; (also saves them around the
						; call to _SD_CS_enable)
		call		_SD_CS_enable

		call		_spi_write
		pop		BC
		pop		BC

		call		_SD_readRes1

		push		AF
		call		_SD_CS_disable
		pop		AF

		ret


; The following commands jump to SD_sendCmdReadRes7
; _SD_sendIfCond
; _SD_readOCR

; BYTE SD_sendIfCond(BYTE *res);
;

		; zds2gas: SCOPE

_SD_sendIfCond:
		ld		BC,cmd8_string
		jr		SD_sendCmdReadRes7


; void SD_readOCR(BYTE *res);
;

_SD_readOCR:
		ld		BC,cmd58_string
		; Fallthrough instead of JR SD_sendCmdRead7

SD_sendCmdReadRes7:
		; Function prologue on behalf of the function who jumped here
		push		IX
		ld		IX,0
		add		IX,SP

		; Push the arguments to _spi_write, also saves them around the
		; call to _SD_CS_enable
		ld		DE,SD_CMD_LEN
		push		DE
		push		BC

		call		_SD_CS_enable

		call		_spi_write
		pop		BC
		pop		BC

		ld		HL,(IX+6)
		push		HL
		call		_SD_readRes7
		pop		HL
		push		AF
		call		_SD_CS_disable
		pop		AF

		; Function epilogue
		pop		IX
		ret


; void SD_powerUpSeq(void)
;

		; zds2gas: SCOPE

_SD_powerUpSeq:
		call		_SD_CS_disable_raw
		DELAY_MS	10
		call		_spi_read_one
		call		_SD_CS_disable_raw

		ld		B,SD_INIT_CYCLES
.LSD_powerUpSeq_loop:		push		BC
		call		_spi_read_one
		pop		BC
		djnz		.LSD_powerUpSeq_loop
		ret


; void SD_CS_enable();
;

		; zds2gas: SCOPE

_SD_CS_enable:
		call		_spi_read_one
		in0		A,(PB_DR)
		res		SD_CS,A
		out0		(PB_DR),A
		jp		_spi_read_one


; void SD_CS_disable();
;

		; zds2gas: SCOPE

_SD_CS_disable:
		call		_spi_read_one
		in0		A,(PB_DR)
		set		SD_CS,A
		out0		(PB_DR),A
		jp		_spi_read_one


; void SD_CS_disable_raw();
;

		; zds2gas: SCOPE

_SD_CS_disable_raw:
		in0		A,(PB_DR)
		set		SD_CS,A
		out0		(PB_DR),A
		ret


		.section .text

cmd0_string:	db		CMD0 | 0x40
		db		CMD0_ARG >> 24 & 0xFF
		db		CMD0_ARG >> 16 & 0xFF
		db		CMD0_ARG >>  8 & 0xFF
		db		CMD0_ARG       & 0xFF
		db		CMD0_CRC | 0x01

cmd8_string:	db		CMD8 | 0x40
		db		CMD8_ARG >> 24 & 0xFF
		db		CMD8_ARG >> 16 & 0xFF
		db		CMD8_ARG >>  8 & 0xFF
		db		CMD8_ARG       & 0xFF
		db		CMD8_CRC | 0x01

cmd55_string:	db		CMD55 | 0x40
		db		CMD55_ARG >> 24 & 0xFF
		db		CMD55_ARG >> 16 & 0xFF
		db		CMD55_ARG >>  8 & 0xFF
		db		CMD55_ARG       & 0xFF
		db		CMD55_CRC | 0x01

acmd41_string:	db		ACMD41 | 0x40
		db		ACMD41_ARG >> 24 & 0xFF
		db		ACMD41_ARG >> 16 & 0xFF
		db		ACMD41_ARG >>  8 & 0xFF
		db		ACMD41_ARG       & 0xFF
		db		ACMD41_CRC | 0x01

cmd58_string:	db		CMD58 | 0x40
		db		CMD58_ARG >> 24 & 0xFF
		db		CMD58_ARG >> 16 & 0xFF
		db		CMD58_ARG >>  8 & 0xFF
		db		CMD58_ARG       & 0xFF
		db		CMD58_CRC | 0x01

		.section .bss,"aw",@nobits
sd_cmd_buffer:	.skip 6
