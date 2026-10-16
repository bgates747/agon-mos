; Native AgonDev source derived from official MOS v3.0.2: src/i2c.inc
; Upstream ancestry and changes: docs/upstream-origin.md and docs/deviations.md.
.ifndef AGON_MOS_SRC_I2C_INC
.set AGON_MOS_SRC_I2C_INC,1
;* Return status codes to read/write caller
.equiv RET_OK, 0x00; ok - caller sets this at entry
.equiv RET_NORESPONSE, 0x01; address sent, nack received
.equiv RET_DATA_NACK, 0x02; data sent, nack received
.equiv RET_ARB_LOST, 0x04; arbitration lost
.equiv RET_BUS_ERROR, 0x08; Bus error

;* I2C ROLE STATUS
.equiv I2C_IDLE, 0x00
.equiv I2C_MTX, 0x01
.equiv I2C_MRX, 0x02
.equiv I2C_SRX, 0x04
.equiv I2C_STX, 0x08

;* I2C_CTL bits
.equiv I2C_CTL_IEN, 0b10000000
.equiv I2C_CTL_ENAB, 0b01000000
.equiv I2C_CTL_STA, 0b00100000
.equiv I2C_CTL_STP, 0b00010000
.equiv I2C_CTL_IFLG, 0b00001000
.equiv I2C_CTL_AAK, 0b00000100

.endif
