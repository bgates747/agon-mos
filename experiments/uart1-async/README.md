# Application-space UART1 sender — U1-001 development

The independent TX core and OTIRX leaf live in application RAM. The default
adapter under development targets vanilla MOS and an otherwise unused UART1.
First hardware test: Console8/ESP8266 over TX/RX, without CTS/RTS. Extender owns
its separate EMOS adaptation and hooks; that work does not gate this driver.
No vector is installed or port initialized by the present core alone.

One positive immutable span and a prearmed flag-only assembly callback follow
the UART0 model. The callback releases source memory after the final FIFO write;
wire drain requires a later owner-provided TEMT observation, and peer execution
has its own reply. No queue, cancellation or automatic payload replay. Stop
refuses new work while continuing an admitted source. A fault retains remaining
source/code ownership and its first fault; ordinary return/unload is unsafe.

`u1_tx.h` is the original C core interface, not a new numeric MOS ABI. `u1_step`
does at most one configured burst. The backend must serialize core calls against
its ISR, preserve incoming IFF/MB/registers, service RX first, and apply returned
TX/retry effects without losing a wakeup. The core never reads LSR or acknowledges
an error. Its owner supplies one admitted sample including any acknowledged
error. A post-copy failure is uncertain, never safe cancellation.

Burst size is 1..16 and may not exceed the explicitly supplied receiver reserve.
Setting reserve=16 declares an external protocol contract; it does not prove
that headroom exists. CTS may change during OTIRX. A TX FIFO alone does not make
that safe. Without a confirmed receiver contract, do not enable large bursts.
GPIO CTS, when used, requires an actual bounded retry opportunity; it is not
assumed to generate a modem interrupt. Without CTS, ignore its unconnected input
and refill on TX-empty. Peer pacing belongs to the protocol, separately from
local FIFO capacity. The foreground may observe the wire tail; no periodic CTS
retry timer is needed in no-flow-control mode.

`u1_emit.src` is a small C-compatible UART1 copy leaf. It performs only bounded
OTIRX and returns, preserving IX/IY and not changing IFF. It has no validation or
ownership machinery: only the settled adapter may wire it to `u1_step`. Exact
register CALL entry (HL/BC/DE), install and restore are a later adapter step.
No RST number or guessed private ROM address has been allocated.

See [the task](../../docs/tasks/U1-001/README.md) for scope and integration gates.

Reproduce the bounded host/native build only after obtaining a real Pi compiler
checkout. Supply its actual token and generation; choose a new output directory
so previous attempts remain intact:

```
python3 build.py --lease ACTUAL_TOKEN --generation ACTUAL_GENERATION --out /absolute/new/output
```

The script asserts ownership before each compiler/check, runs host ASan/UBSan,
links the simulated-port example and archives the native library, disassembly,
map, source hashes and logs. It enforces the task's time/temperature/memory
limits. Release the slot after owned children stop and notify the actual next
owner, if any. It never launches the compiled guest or accesses a serial port.

The first build passed host checks and native linking. Native core text is
537 bytes and the copy leaf 30 bytes, all application code. Those counts exclude
the still-unimplemented owner/install/IRQ/retry adapters. They are not a resident
ROM cost or an operational/throughput qualification.
