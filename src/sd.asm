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

		XDEF		_SD_init
		XDEF		_SD_readBlocks
		XDEF		_SD_writeBlocks

		XREF		_spi_transfer
		XREF		_spi_read_one
		XREF		_spi_read
		XREF		_spi_write
		XREF		_sdcardDelay

		.ASSUME ADL = 1


; BYTE SD_init(void)
;
; Local variables
;	IX-6..IX-2	BYTE res[5]
;

		; zds2gas: SCOPE

_SD_init:
		; Function prologue
		PUSH		IX
		LD		IX,0
		ADD		IX,SP

		; Make space for local variables
		LD		HL,-6
		ADD		HL,SP
		LD		SP,HL

		; Off we go
		CALL		_SD_powerUpSeq

		; Command card to idle
		LD		B,10
.Lzds_src_sd_asm_45f24809_s001__24_loop1:		PUSH		BC
		CALL		_SD_goIdleState
		POP		BC
		LD		(IX-6),A
		CP		A,0x01
		JR		Z,.Lzds_src_sd_asm_45f24809_s001__24_success1
		DJNZ		.Lzds_src_sd_asm_45f24809_s001__24_loop1

		; Failed after 10 attempts
		JR		.Lzds_src_sd_asm_45f24809_s001__24_out_error
		
		; Send interface conditions
.Lzds_src_sd_asm_45f24809_s001__24_success1:	PEA		IX-6
		CALL		_SD_sendIfCond
		POP		BC

		; Check first byte of response is 0x01
		LD		A,(IX-6)
		CP		A,1
		JR		NZ,.Lzds_src_sd_asm_45f24809_s001__24_out_error

		; Check fifth byte of response is 0xAA
		LD		A,(IX-2)
		CP		A,0xAA
		JR		NZ,.Lzds_src_sd_asm_45f24809_s001__24_out_error

		; Attempt to initialize card

		; Repeat up to 100 times
		LD		B,100
.Lzds_src_sd_asm_45f24809_s001__24_loop2:		PUSH		BC
		CALL		_SD_sendApp
		CP		A,2		; is res[0] < 2 ?
		JR		NC,.Lzds_src_sd_asm_45f24809_s001__24_wait2
		CALL		_SD_sendOpCond
		CP		A,SD_READY
		JR		Z,.Lzds_src_sd_asm_45f24809_s001__24_success2

		; Wait 10ms before we try again
.Lzds_src_sd_asm_45f24809_s001__24_wait2:		zds_DELAY_MS	10
		POP		BC
		DJNZ		.Lzds_src_sd_asm_45f24809_s001__24_loop2

		; Timeout: error
		JR		.Lzds_src_sd_asm_45f24809_s001__24_out_error

.Lzds_src_sd_asm_45f24809_s001__24_success2:	PEA		IX-6
		CALL		_SD_readOCR
		POP		BC
		LD		A,(IX-5)
		RLA
		JR		C,.Lzds_src_sd_asm_45f24809_s001__24_out_success
		; Fall through to $out_error

.Lzds_src_sd_asm_45f24809_s001__24_out_error:	LD		A,SD_ERROR
		JR		.Lzds_src_sd_asm_45f24809_s001__24_exit

.Lzds_src_sd_asm_45f24809_s001__24_out_success:	XOR		A,A	; LD A,LD_SUCCESS
.Lzds_src_sd_asm_45f24809_s001__24_exit:		LD		SP,IX
		POP		IX
		RET


; BYTE SD_readBlocks(DWORD addr, BYTE *buf, WORD count)
;		     IX+6        IX+12      IX+15
;
; Local variables:
;	IX-3/IX-2	Reserved for SD_readSingleBlock
;	IX-1		token

		; zds2gas: SCOPE

_SD_readBlocks:
		; Function prologue
		PUSH		IX
		LD		IX,0
		ADD		IX,SP
		PUSH		BC	; 3 bytes for local variables

		; sign-extend count (it's unsigned, so set top byte to 0)
		LD		(IX+17),0

		; HL := count, then jump to the check for zero
		LD		HL,(IX+15)
		JR		.Lzds_src_sd_asm_45f24809_s002__24_start
		
		; Read current block
.Lzds_src_sd_asm_45f24809_s002__24_loop:		CALL		SD_readSingleBlock

		; Exit with SD_ERROR if res1 >= 2
		CP		A,2
		JR		NC,.Lzds_src_sd_asm_45f24809_s002__24_err_exit

		; or if token != SD_DATA_ACCEPTED
		LD		A,(IX-1)
		CP		A,0xFE
		JR		NZ,.Lzds_src_sd_asm_45f24809_s002__24_err_exit
		
		; Update sector, buf and count
		; HL is set to the updated value of count
		CALL		SD_updateIOVars
.Lzds_src_sd_asm_45f24809_s002__24_start:		LD		A,H
		OR		A,L
		JR		NZ,.Lzds_src_sd_asm_45f24809_s002__24_loop
		
		; Finished, return SD_SUCCESS (which happens to be zero)
.Lzds_src_sd_asm_45f24809_s002__24_done:		XOR		A,A
.Lzds_src_sd_asm_45f24809_s002__24_exit:		LD		SP,IX
		POP		IX
		RET

		; Error exit, slow path so can save a couple of bytes
.Lzds_src_sd_asm_45f24809_s002__24_err_exit:	LD		A,SD_ERROR
		JR		.Lzds_src_sd_asm_45f24809_s002__24_exit

; Delay by 30ms. Roughly how long an old 5.25" disk takes to read 512 bytes
SD_delayDisc:
		LD		A, (_sdcardDelay)
		OR		A
		RET		Z

		PUSH	HL
		PUSH	DE

		LD		DE, 1
		LD		HL, 81000
		; 81000 * 6 cycles per loop
.Lzds_src_sd_asm_45f24809_s002__24_loop4:	AND		A
		SBC		HL, DE
		JR		NZ, .Lzds_src_sd_asm_45f24809_s002__24_loop4

		POP		DE
		POP		HL
		RET


; SD_readSingleBlock

; This does not use the C calling-convention.
; It uses the stack frame pointer and local space set up by _SD_readBlocks
;
; Output: A := res1

		; zds2gas: SCOPE

SD_readSingleBlock:
		CALL	SD_delayDisc
		LD		(IX-3),CMD17     | 0x40
		LD		(IX-2),CMD17_CRC | 0x01
		
		CALL		SD_sendIOCmd	; Sets *token to 0xFF too
		PUSH		AF		; Save res1 to be returned
		CP		A,0xFF
		JR		Z,.Lzds_src_sd_asm_45f24809_s003__24_out3

		; Wait for a response token (timeout = 100ms)
		zds_TIMER_SET	0,100
		zds_TIMER_START	0
		
.Lzds_src_sd_asm_45f24809_s003__24_loop1:		CALL		_spi_read_one
		LD		B,A		; Move byte read to B
		CP		A,0xFF
		JR		NZ,.Lzds_src_sd_asm_45f24809_s003__24_out1

		; Continue until the timer expires
		zds_TIMER_EXP_3f_	0		; (clobbers just A)
		JR		NC,.Lzds_src_sd_asm_45f24809_s003__24_loop1
		
.Lzds_src_sd_asm_45f24809_s003__24_out1:		zds_TIMER_RESET	0		; (clobbers just A)

		; Check if card response is SD_START_TOKEN

		; *token = read
		LD		(IX-1),B

		; If response token is 0xFE then read the sector
		LD		A,SD_START_TOKEN
		CP		A,B
		JR		NZ,.Lzds_src_sd_asm_45f24809_s003__24_out3

		; Read the sector
		LD		BC,SD_BLOCK_LEN
		PUSH		BC
		LD		BC,(IX+12)	; buf
		PUSH		BC
		CALL		_spi_read
		POP		BC
		POP		BC

		; Read and discard the two CRC bytes
		CALL		_spi_read_one
		CALL		_spi_read_one

		; Deassert chip select
.Lzds_src_sd_asm_45f24809_s003__24_out3:		CALL		_SD_CS_disable

		; Restore res1 to return to caller
		POP		AF
		RET


; BYTE SD_writeBlocks(DWORD addr, BYTE *buf, WORD count)
;		     IX+6        IX+12      IX+15
;
; Local variables:
;	IX-3/IX-2	Reserved for SD_writeSingleBlock
;	IX-1		token

		; zds2gas: SCOPE

_SD_writeBlocks:
		; Function prologue
		PUSH		IX
		LD		IX,0
		ADD		IX,SP
		PUSH		BC	; 3 bytes for local variables

		; sign extend count (it's unsigned, so set top byte to 0)
		LD		(IX+17),0

		; HL := count, then jump to the check for zero
		LD		HL,(IX+15)
		JR		.Lzds_src_sd_asm_45f24809_s004__24_start

.Lzds_src_sd_asm_45f24809_s004__24_loop:		CALL		SD_writeSingleBlock

		; Exit with SD_ERROR if res1 != 0x00
		OR		A,A
		JR		NZ,.Lzds_src_sd_asm_45f24809_s004__24_err_exit

		; or if token != SD_DATA_ACCEPTED
		LD		A,(IX-1)
		CP		A,SD_DATA_ACCEPTED
		JR		NZ,.Lzds_src_sd_asm_45f24809_s004__24_err_exit
		
		; Update sector, buf and count
		; HL is set to the updated value of count
		CALL		SD_updateIOVars
.Lzds_src_sd_asm_45f24809_s004__24_start:		LD		A,H
		OR		A,L
		JR		NZ,.Lzds_src_sd_asm_45f24809_s004__24_loop
		
		; Finished, return SD_SUCCESS (which happens to be zero)
.Lzds_src_sd_asm_45f24809_s004__24_done:		XOR		A,A
.Lzds_src_sd_asm_45f24809_s004__24_exit:		LD		SP,IX
		POP		IX
		RET

		; Error exit, slow path so can save a couple of bytes
.Lzds_src_sd_asm_45f24809_s004__24_err_exit:	LD		A,SD_ERROR
		JR		.Lzds_src_sd_asm_45f24809_s004__24_exit


; SD_writeSingleBlock

; This does not use the C calling-convention.
; It uses the stack frame pointer set up by _SD_writeBlocks
;
; Output: A := res1

		; zds2gas: SCOPE

SD_writeSingleBlock:
		CALL	SD_delayDisc
		LD		(IX-3),CMD24     | 0x40
		LD		(IX-2),CMD24_CRC | 0x01
		
		CALL		SD_sendIOCmd	; Sets *token to 0xFF too
		PUSH		AF		; Save res1 to be returned
		CP		A,SD_READY
		JP		NZ,.Lzds_src_sd_asm_45f24809_s005__24_out3

		; Send start token
		LD		C,SD_START_TOKEN
		PUSH		BC
		CALL		_spi_transfer
		POP		BC

		; Write buffer to card
		LD		BC,SD_BLOCK_LEN
		PUSH		BC
		LD		BC,(IX+12)
		PUSH		BC
		CALL		_spi_write
		POP		BC
		POP		BC

		; Wait for a response token (timeout = 250ms)
		zds_TIMER_SET	0,250
		zds_TIMER_START	0
		
.Lzds_src_sd_asm_45f24809_s005__24_loop1:		CALL		_spi_read_one
		LD		B,A		; Save byte read
		CP		A,0xFF
		JR		NZ,.Lzds_src_sd_asm_45f24809_s005__24_gotit1

		; Continue until the timer expires
		zds_TIMER_EXP_3f_	0		; (clobbers just A)
		JR		NC,.Lzds_src_sd_asm_45f24809_s005__24_loop1

		; Timeout - just fall through

.Lzds_src_sd_asm_45f24809_s005__24_gotit1:	zds_TIMER_RESET	0		; (clobbers just A)

		; If data accepted
		LD		A,0x1F
		AND		A,B
		CP		A,5
		JR		NZ,.Lzds_src_sd_asm_45f24809_s005__24_out3

		; *token = 0x05 (conveniently left in register A)
		LD		(IX-1),A

		; Wait for write to finish (timeout = 250ms)
		zds_TIMER_SET	0,250
		zds_TIMER_START	0

.Lzds_src_sd_asm_45f24809_s005__24_loop2:		CALL		_spi_read_one
		CP		A,0x00
		JR		NZ,.Lzds_src_sd_asm_45f24809_s005__24_gotit2

		; Continue until the timer expires
		zds_TIMER_EXP_3f_	0
		JR		NC,.Lzds_src_sd_asm_45f24809_s005__24_loop2

		; Timeout, skip over setting token
		JR		.Lzds_src_sd_asm_45f24809_s005__24_notgot

.Lzds_src_sd_asm_45f24809_s005__24_gotit2:	; Success: set token to 0x00
		XOR		A,A
		LD		A,(IX-1)

.Lzds_src_sd_asm_45f24809_s005__24_notgot:	; Reset the timer
		zds_TIMER_RESET	0

		; Deassert chip select
.Lzds_src_sd_asm_45f24809_s005__24_out3:		CALL		_SD_CS_disable

		; Restore res1 to return to caller
		POP		AF
		RET


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
		LD		(IX-1),0xFF

		; Assert chip select
		CALL		_SD_CS_enable

		; Push arguments on to stack first
		LD		HL,SD_CMD_LEN
		PUSH		HL
		LD		HL,sd_cmd_buffer
		PUSH		HL

		; buf[0] := command
		LD		B,(IX-3)
		LD		(HL),B
		INC		HL

		; buf[1..4] := address (big endian so swap bytes around)
		LD		BC,(IX+8)
		LD		(HL),B
		INC		HL
		LD		(HL),C
		INC		HL
		LD		BC,(IX+6)
		LD		(HL),B
		INC		HL
		LD		(HL),C
		INC		HL

		; buf[5] : = CRC
		LD		B,(IX-2)
		LD		(HL),B

		; Send contents of sd_cmd_buffer
		CALL		_spi_write
		POP		HL
		POP		HL

		; res1 = SD_readRes1();
		JP		_SD_readRes1


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
		LD		HL,(IX+6)
		LD		BC,1
		XOR		A,A
		ADD		HL,BC
		ADC		A,(IX+9)
		LD		(IX+6),HL
		LD		(IX+9),A

		; buf += SD_BLOCK_LEN
		LD		HL,(IX+12)
		LD		DE,SD_BLOCK_LEN	; Use DE here so that BC can
		ADD		HL,DE		; be re-used below
		LD		(IX+12),HL

		; --count
		LD		HL,(IX+15)
		OR		A,A
		SBC		HL,BC		; BC still set to 1 from above
		LD		(IX+15),HL
		RET


; BYTE SD_readRes1(void)
;

		; zds2gas: SCOPE

_SD_readRes1:	LD		B,9
.Lzds_src_sd_asm_45f24809_s008__24_loop:		PUSH		BC	; save B over call to _spi_read_one
		CALL		_spi_read_one
		POP		BC
		CP		A,0xFF
		JR		NZ,.Lzds_src_sd_asm_45f24809_s008__24_out
		DJNZ		.Lzds_src_sd_asm_45f24809_s008__24_loop
.Lzds_src_sd_asm_45f24809_s008__24_out:		RET


; void SD_readRes7(BYTE *res)
;

		; zds2gas: SCOPE

_SD_readRes7:	; Function prologue
		PUSH		IX
		LD		IX,0
		ADD		IX,SP

		CALL		_SD_readRes1
		LD		HL,(IX+6)

		; Restore IX now, so we can "RET NC" later
		; No local variables so no need to restore SP
		POP		IX

		; Save byte read into res[0]
		LD		(HL),A
	
		; Exit if byte read is >1 (in other words, >= 2)
		CP		A,2
		RET		NC

		; Otherwise read the next four bytes
		LD		BC,4
		PUSH		BC
		INC		HL
		PUSH		HL
		CALL		_spi_read
		POP		HL
		POP		BC
		RET


; NB: The following functions all jump to SD_sendCmdReadRes1
;
; _SD_goIdleState
; _SD_sendApp
; _SD_sendOpCond

; BYTE SD_goIdleState(void);
;

		; zds2gas: SCOPE

_SD_goIdleState:
		LD		BC,cmd0_string
		JR		SD_sendCmdReadRes1


; UINT8 SD_sendApp(void)
;

_SD_sendApp:
		LD		BC,cmd55_string
		JR		SD_sendCmdReadRes1


; UINT8 SD_sendOpCond(void)
;
_SD_sendOpCond:
		LD		BC,acmd41_string
		; Fallthrough instead of JR SD_sendCmdReadRes1

SD_sendCmdReadRes1:
		LD		DE,SD_CMD_LEN
		PUSH		DE		; push arguments to _spi_write
		PUSH		BC		; (also saves them around the
						; call to _SD_CS_enable)
		CALL		_SD_CS_enable

		CALL		_spi_write
		POP		BC
		POP		BC

		CALL		_SD_readRes1

		PUSH		AF
		CALL		_SD_CS_disable
		POP		AF

		RET


; The following commands jump to SD_sendCmdReadRes7
; _SD_sendIfCond
; _SD_readOCR

; BYTE SD_sendIfCond(BYTE *res);
;

		; zds2gas: SCOPE

_SD_sendIfCond:
		LD		BC,cmd8_string
		JR		SD_sendCmdReadRes7


; void SD_readOCR(BYTE *res);
;

_SD_readOCR:
		LD		BC,cmd58_string
		; Fallthrough instead of JR SD_sendCmdRead7

SD_sendCmdReadRes7:
		; Function prologue on behalf of the function who jumped here
		PUSH		IX
		LD		IX,0
		ADD		IX,SP

		; Push the arguments to _spi_write, also saves them around the
		; call to _SD_CS_enable
		LD		DE,SD_CMD_LEN
		PUSH		DE
		PUSH		BC

		CALL		_SD_CS_enable

		CALL		_spi_write
		POP		BC		
		POP		BC

		LD		HL,(IX+6)
		PUSH		HL
		CALL		_SD_readRes7
		POP		HL
		PUSH		AF
		CALL		_SD_CS_disable
		POP		AF

		; Function epilogue
		POP		IX
		RET
		

; void SD_powerUpSeq(void)
;

		; zds2gas: SCOPE

_SD_powerUpSeq:
		CALL		_SD_CS_disable_raw
		zds_DELAY_MS	10
		CALL		_spi_read_one
		CALL		_SD_CS_disable_raw

		LD		B,SD_INIT_CYCLES
.Lzds_src_sd_asm_45f24809_s012__24_loop:		PUSH		BC
		CALL		_spi_read_one
		POP		BC
		DJNZ		.Lzds_src_sd_asm_45f24809_s012__24_loop
		RET


; void SD_CS_enable();
;

		; zds2gas: SCOPE

_SD_CS_enable:
		CALL		_spi_read_one
		IN0		A,(PB_DR)
		RES		SD_CS,A
		OUT0		(PB_DR),A
		JP		_spi_read_one


; void SD_CS_disable();
;

		; zds2gas: SCOPE

_SD_CS_disable:
		CALL		_spi_read_one
		IN0		A,(PB_DR)
		SET		SD_CS,A
		OUT0		(PB_DR),A
		JP		_spi_read_one


; void SD_CS_disable_raw();
;

		; zds2gas: SCOPE

_SD_CS_disable_raw:
		IN0		A,(PB_DR)
		SET		SD_CS,A
		OUT0		(PB_DR),A
		RET


		.section .text

cmd0_string:	DB		CMD0 | 0x40
		DB		CMD0_ARG >> 24 & 0xFF
		DB		CMD0_ARG >> 16 & 0xFF
		DB		CMD0_ARG >>  8 & 0xFF
		DB		CMD0_ARG       & 0xFF
		DB		CMD0_CRC | 0x01

cmd8_string:	DB		CMD8 | 0x40
		DB		CMD8_ARG >> 24 & 0xFF
		DB		CMD8_ARG >> 16 & 0xFF
		DB		CMD8_ARG >>  8 & 0xFF
		DB		CMD8_ARG       & 0xFF
		DB		CMD8_CRC | 0x01

cmd55_string:	DB		CMD55 | 0x40
		DB		CMD55_ARG >> 24 & 0xFF
		DB		CMD55_ARG >> 16 & 0xFF
		DB		CMD55_ARG >>  8 & 0xFF
		DB		CMD55_ARG       & 0xFF
		DB		CMD55_CRC | 0x01

acmd41_string:	DB		ACMD41 | 0x40
		DB		ACMD41_ARG >> 24 & 0xFF
		DB		ACMD41_ARG >> 16 & 0xFF
		DB		ACMD41_ARG >>  8 & 0xFF
		DB		ACMD41_ARG       & 0xFF
		DB		ACMD41_CRC | 0x01

cmd58_string:	DB		CMD58 | 0x40
		DB		CMD58_ARG >> 24 & 0xFF
		DB		CMD58_ARG >> 16 & 0xFF
		DB		CMD58_ARG >>  8 & 0xFF
		DB		CMD58_ARG       & 0xFF
		DB		CMD58_CRC | 0x01

		.section .bss,"aw",@nobits
sd_cmd_buffer:	.skip 6
