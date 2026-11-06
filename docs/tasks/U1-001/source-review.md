# U1-001 initial source findings

Matched EMOS donor (read-only):
`/Agon/mystuff/agon-extender/agents/net004/emos-uart-rfc25-source`, commit
`2c79c6006d6bcb0c2b3f9d8d6aae3ef4b36c730a`.

`src/emos_net.c` validates the envelope and publishes `admitted=2` before
`emos_keyboard_send`. Forward maximum is **146 UART bytes**, not 147: four VDU
envelope bytes, fourteen NM header bytes and 128 opaque payload bytes. The local
gateway operation byte makes its input 147 bytes and is omitted from UART output.

`src/emos_keyboard_io.asm` preserves IFF around one-byte TX attempts and reads
LSR once before sampling GPIO CTS. LSR acknowledges error information. The RX
assembly drains at most 16 bytes, preserves the count across dispatch callbacks,
and shares the full saved-register `_emos_keyboard_irq_entry`. It is not a stock
unowned UART vector. A second app-side LSR read must not consume an error before
the owner's receive path records it.

`src/emos_keyboard.c` optional telemetry code masks TX-empty when GPIO CTS
blocks; its VBlank tick supplies retries. Its comment explicitly excludes modem
interrupt wakeup. `src/uart.c:uart1_keyboard_irq_done` restores receive readiness
then optionally services telemetry. These are possible owner seams, not an
existing public app-hook ABI or permission to edit this donor.

Stock `mos_setintvector` (14h) and `mos_uopen` (15h) document vector 1Ah, but do
not arbitrate an occupied EMOS port. 14h's documented preservation also has an
ADL compatibility correction in the maintained MOS API reference. The driver
must not initialize UART1 or replace the receive vector merely because those
stock calls exist.

## Integration questions sent to Extender

Is there a supported admitted app-service registration and GPIO-CTS retry
opportunity? If absent, the owner must define a minimal opt-in hook, separately
costed, which preserves NM validation/RX arming, existing RX saves and liveness,
single-writer exclusion and physical ownership through source and wire drain.
No pointer layout, opcode, address or byte cost is invented here. All engine,
state and source storage remain in the application. Current NM SUBMIT remains
synchronous until explicitly integrated by its owner.

## MechAgon source reply

Mail `2026-11-06_12-43-40_mechagon_u1001-consumer-wire-lifetime-return-one`
confirms 146-byte maximum. Its static `agon_net_client` owns `input[147]` and
`reply[142]`; `input+1` is eligible persistent wire storage only after supported
integration. Completion callback, wire drain, matching NM reply and positive
detach/RELEASE are distinct gates. SDK timeout handling must not free or reuse a
still borrowed input. Other writers include console/controller/SD-link,
telemetry and admission packets, not just a second NM submit. UART0 graphics
and UART1 RX must remain live. Bench 58 and installed firmware stay with Brandon.

Later matched benchmark: identical CONNECT/POLL and echo 1/127/128 payloads,
same pair and byte stream, synchronous versus explicit async plus a fixed compute
block. Record bytes/callbacks, first fault, source/drain/reply brackets, useful
work, RX/input liveness and cleanup. Add identical UART0 output only after the
isolated transport proof. Existing combat frame timing is not a UART1 metric.

## Independent first tranche

The C TX core uses owner-provided status and an admitted emit leaf; it never
installs a vector, touches an NM router, reads LSR, claims an interrupt source,
or assumes GPIO CTS generates an interrupt. Its configured burst is bounded by
an explicit receiver-reserve contract. A separate native OTIRX leaf is inert
until a supported adapter binds it. Host checks and native linking will qualify
this independent tranche only; operational install/IRQ/IFF/RX proof remains open.
