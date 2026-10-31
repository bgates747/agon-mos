ENTRY(app_entry)
SECTIONS { . = 0x080000; .client : { *(UART_ENTRY) } }
ASSERT(ADDR(.client) == 0x080000, "Wrong client load address")
ASSERT(SIZEOF(.client) < 0x10000, "Client exceeds loader span")
