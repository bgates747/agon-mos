# Fix UART receive recovery race when the receive buffer fills

The ESP-IDF 4.4.6 UART driver used by VDP 2.16.0 can leave reception disabled
after its software receive buffer fills. The interrupt handler sets
`rx_buffer_full_flg` before taking the UART lock. Another core can clear that
flag and re-enable reception before the handler takes the lock and disables
reception again, leaving the flag clear and reception disabled.

Move the flag assignment inside the existing critical section that disables
receive interrupts. This serializes both updates with reader-side recovery;
it adds no lock or per-byte processing.
The pinned SDK's driver is supplied as a local C object so the fix does not
require modifying an installed SDK.

Proposed change to ESP-IDF's `components/driver/uart.c`:

```diff
--- a/uart.c
+++ b/uart.c
@@ -988,8 +988,10 @@
                 //If we fail to push data to ring buffer, we will have to stash the data, and send next time.
                 //Mainly for applications that uses flow control or small ring buffer.
                 if (pdFALSE == xRingbufferSendFromISR(p_uart->rx_ring_buf, p_uart->rx_data_buf, p_uart->rx_stash_len, &HPTaskAwoken)) {
+                    UART_ENTER_CRITICAL_ISR(&(uart_context[uart_num].spinlock));
+                    // Publish full and mask RX together against reader recovery.
+                    // The reader clears this flag under the same UART lock.
                     p_uart->rx_buffer_full_flg = true;
-                    UART_ENTER_CRITICAL_ISR(&(uart_context[uart_num].spinlock));
                     uart_hal_disable_intr_mask(&(uart_context[uart_num].hal), UART_INTR_RXFIFO_TOUT | UART_INTR_RXFIFO_FULL);
                     UART_EXIT_CRITICAL_ISR(&(uart_context[uart_num].spinlock));
                     if (uart_event.type == UART_PATTERN_DET) {
```

Tested on Heber Agon Console8 using diagnostic firmware that deliberately widens
the timing window. The unpatched driver stalled with 66 bytes pending in the
FIFO and required diagnostic rescue. The patched driver received both 4,096-byte
payloads with matching CRCs, no receive errors and no rescue. Normal-command
compatibility tests also passed. Natural failure frequency was not measured.

The [reproduction ZIP](https://github.com/bgates747/agon-vdp/releases/download/uart-rx-race-reproducer-2026-11-02/uart-rx-race-reproducer.zip) contains matching custom MOS/VDP sources and binaries, test-fixture source and binary, a README with build/run instructions, and raw Console8 results.
