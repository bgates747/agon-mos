"""Minimal repair of the audited IDF4.4.6 UART receive-full slow path."""
import hashlib

ORIGINAL_SHA256='0a90ac006b6a0cadaac4c47ab035a54c782fb6171fda82e9dd059a3d84c4b0be'
BEFORE='''                    p_uart->rx_buffer_full_flg = true;
                    UART_ENTER_CRITICAL_ISR(&(uart_context[uart_num].spinlock));
'''
AFTER='''                    UART_ENTER_CRITICAL_ISR(&(uart_context[uart_num].spinlock));
                    // Publish full and mask RX together against reader recovery.
                    // The reader clears this flag under the same UART lock.
                    p_uart->rx_buffer_full_flg = true;
'''

def repair(source):
    assert hashlib.sha256(source.encode()).hexdigest()==ORIGINAL_SHA256
    assert source.count(BEFORE)==1
    return source.replace(BEFORE,AFTER)
