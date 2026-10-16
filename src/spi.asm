; Native AgonDev source derived from official MOS v3.0.2: src/spi.asm
; Upstream ancestry and changes: docs/upstream-origin.md and docs/deviations.md.
;
; Title:	AGON MOS - SPI low level assembly language
; Author:	Leigh Brown
; Created:	26/05/2023
; Last Updated:	26/05/2023

; Modinfo
;

; The approach taken to maximise performance is:
; 1) Minimise the time between receiving the response from the current request
;    and sending the next request.
; 2) Getting as much done whilst the byte is being shifted out/in

		.include "ez80f92.inc"
		.include "macros.inc"

.equiv SPI_ENA_DELAY, 50

.equiv SD_CS, 4; Bit 4

.equiv SPI_MOSI, 7; PB7
.equiv SPI_MISO, 6; PB6
.equiv SPI_CLK, 3; PB3

		.global	_init_spi
		.global	_spi_transfer
		.global	_spi_read_one
		.global	_spi_read
		.global	_spi_write

		.assume adl=1


; void spi_init(void);

		; zds2gas: SCOPE

_init_spi:	;
		; SS must remain high for SPI to work properly
		;

		; PB_DR   |=  BIT(2);
		in0		A,(PB_DR)
		set		2,A
		out0		(PB_DR),A

		; PB_ALT1 &= ~BIT(2);
		in0		A,(PB_ALT1)
		res		2,A
		out0		(PB_ALT1),A

		; PB_ALT2 &= ~BIT(2);
		in0		A,(PB_ALT2)
		res		2,A
		out0		(PB_ALT2),A

		; PB_DDR  &= ~BIT(2);
		in0		A,(PB_DDR)
		res		2,A
		out0		(PB_DDR),A

		;
		; Enable the chip select outputs and deselect
		;

		; PB_DR   |=  BIT(SD_CS);
		in0		A,(PB_DR)
		set		4,A
		out0		(PB_DR),A

		; PB_ALT1 &= ~BIT(SD_CS);
		in0		A,(PB_ALT1)
		res		4,A
		out0		(PB_ALT1),A

		; PB_ALT2 &= ~BIT(SD_CS);
		in0		A,(PB_ALT2)
		res		0x4,A
		out0		(PB_ALT2),A

		; PB_DDR  &= ~BIT(SD_CS);
		in0		A,(PB_DDR)
		res		0x4,A
		out0		(PB_DDR),A

		;
		; Set port B pins 7 (MOSI), 6 (MISO), 3 (SCK), 2 (/SS) to SPI
		;

		; PB_ALT1 &= ~(BIT(SPI_MOSI) | BIT(SPI_MISO) | BIT(SPI_CLK))
		in0		A,(PB_ALT1)
		and		A,~((1<<SPI_MOSI)|(1<<SPI_MISO)|(1<<SPI_CLK))
		out0		(PB_ALT1),A

		; PB_ALT2 |=  (BIT(SPI_MOSI) | BIT(SP_MISO) | BIT(SPI_CLK))
		in0		A,(PB_ALT2)
		or		A,(1<<SPI_MOSI)|(1<<SPI_MISO)|(1<<SPI_CLK)
		out0		(PB_ALT2),A

		;
		; Disable SPI
		;

		xor		A,A
		out0		(SPI_CTL),A

		;
		; Set SPI baud rate generator divisor registers
		;

		ld		BC,3		; I changed from 4 to 3
		out0		(SPI_BRG_H),B
		out0		(SPI_BRG_L),C

		;
		; Enable SPI as master
		;

		ld		A,0x30
		out0		(SPI_CTL),A

		; Delay for `SPI_ENA_DELAY' milliseconds
		;

		DELAY_MS	SPI_ENA_DELAY

		; All done
		ret


; unsigned char spi_read_one(void);
;
		; zds2gas: SCOPE
_spi_read_one:
		ld		C,0xFF		; Kick SPI into action before
		out0		(SPI_TSR),C	; anything else...
		pop		HL		; Pop return address for later
		jr		spi_wait

; unsigned char spi_transfer(unsigned char d);
;
_spi_transfer:
		pop		HL		; Pop return address for later
		pop		DE		; Transmit the byte ASAP...
		out0		(SPI_TSR),E
		push		DE
		; fall through (no need for JR spi_wait)

; Both _spi_read_one and _spi_transfer use spi_wait to complete the operation

spi_wait:	ld		B,0
.Lspi_read_one_loop:		in0		A,(SPI_SR)
		rla
		jr		C,.Lspi_read_one_done
		djnz		.Lspi_read_one_loop
.Lspi_read_one_done:		in0		A,(SPI_RBR)
		jp		(HL)		; Faster than RET if we have HL


; void spi_read(char *buf, unsigned int len);
;

		; zds2gas: SCOPE
_spi_read:
		; Request the first byte - do first to minimise delay
		ld		C,0xFF
		out0		(SPI_TSR),C

		; Function prologue
		push		IX
		ld		IX,0
		add		IX,SP

		; DE := destination address
		ld		DE,(IX+6)

		; HL := number of bytes to read
		ld		HL,(IX+9)

		; Decrement the count of bytes
.Lspi_read_mainloop:	ld		BC,1
		or		A,A
		sbc		HL,BC

		; If this is the last, break out of loop
		jr		Z,.Lspi_read_waitlast

		; Wait for byte to arrive then store it
.Lspi_read_waitnext:	ld		B,0		; (256 iterations)
		ld		C,0xFF		; pre-load C with dummy byte
.Lspi_read_loopnext:	in0		A,(SPI_SR)
		rla
		jr		C,.Lspi_read_gotnext
		djnz		.Lspi_read_loopnext
		; TODO: detect errors

		; Minimise delay from receiving to requesting the next byte
.Lspi_read_gotnext:	in0		A,(SPI_RBR)
		out0		(SPI_TSR),C
		ld		(DE),A
		inc		DE
		jr		.Lspi_read_mainloop

.Lspi_read_waitlast:	; Do function epilogue now, we have time
		ld		SP,IX
		pop		IX

		; Now wait for last byte
		ld		B,0		; (256 iterations)
.Lspi_read_looplast:	in0		A,(SPI_SR)
		rla
		jr		C,.Lspi_read_gotlast
		djnz		.Lspi_read_looplast
		; TODO: detect errors

.Lspi_read_gotlast:	in0		A,(SPI_RBR)
		ld		(DE),A
		ret


; void spi_write(char *buf, unsigned int len);

		; zds2gas: SCOPE
_spi_write:
		push		IX
		ld		IX,0
		add		IX,SP

		; DE := source address
		ld		DE,(IX+6)

		; Write the first byte as soon as we can
		ld		A,(DE)
		out0		(SPI_TSR),A
		inc		DE

		; HL := number of bytes to write
		ld		HL,(IX+9)

		; Decrement the count of bytes
.Lspi_write_mainloop:	ld		BC,1
		or		A,A
		sbc		HL,BC

		; If this is the last, break out of loop
		jr		Z,.Lspi_write_waitlast

		; Wait for the write to complete
.Lspi_write_waitnext:	ld		B,0		; (256 iterations)
		ld		A,(DE)		; pre-load C with byte to write
		ld		C,A
		inc		DE

.Lspi_write_loopnext:	in0		A,(SPI_SR)
		rla
		jr		C,.Lspi_write_sentnext
		djnz		.Lspi_write_loopnext
		; TODO: detect errors

		; Minimise delay from send complete to sending the next octet
.Lspi_write_sentnext:	; Don't bother reading the dummy byte (IN0 A,(SPI_RBR))
		out0		(SPI_TSR),C
		jr		.Lspi_write_mainloop

.Lspi_write_waitlast:	; Do function epilogue now, whilst the last byte is transferring
		ld		SP,IX
		pop		IX

		ld		B,0		; (256 iterations)
.Lspi_write_looplast:	in0		A,(SPI_SR)
		rla
		jr		C,.Lspi_write_sentlast
		djnz		.Lspi_write_looplast
		; TODO: detect errors

.Lspi_write_sentlast:	; Don't bother reading the dummy byte (IN0 A,(SPI_RBR))
		ret

