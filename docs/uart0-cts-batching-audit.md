# UART0 CTS batching hardware and source audit — BT-002

Executive summary: keep the current FIFO-empty admission and 16-write service
cap. Investigate CTS intervals 1/2/4/8/16 within that cap. Under an explicitly
stated no-extra-propagation model, a stopped receiver may still see up to 17
bytes from one admitted service opportunity: 16 writes plus a prior shift-register
byte. The observed 62 spare slots support experimentation, not certification.
No production batch size or throughput gain is established by this audit.

## Primary hardware facts

The locally retained Zilog PS015317-0120 eZ80F92/F93 specification describes
separate 16-byte TX/RX FIFOs (printed p.104), a distinct transmitter shift register
(p.105), THRE indicating the holding FIFO empty and TEMT also requiring the
shift register empty (p.120), and inverted CTS level plus read-cleared delta
status in MSR (p.122). It does not establish an automatic CTS transmitter gate
for this implementation. The firmware owns the decision to write THR.

Primary reference: [Zilog specification](https://www.zilog.com/docs/ez80/ps0153.pdf),
local file `/Agon/docs/PS0153-eZ80F92-eZ80F93-Product-Specification.pdf`.
The online copy was inaccessible during this audit; facts above were checked in
the retained PDF, SHA256
`9d64cfd5e75e50b009028f75ec6a2377ee1cf3721443715d32a78a0d920a71ba`.

Stock VDP 2.16.0 source commit c7ac293d2aa81ddfa693390549bcd909069c8fc3 uses
Serial2 at 1152000 baud, 8N1, a 256-byte software RX buffer, and hardware RTS
threshold 64. The ESP32 hardware FIFO has 128 slots. The software ring must not
be counted as guaranteed hardware RTS reserve while its RX interrupt is paused.
The pinned IDF 4.4.6 register definition asserts flow control when occupancy is
more than T, so nominal free FIFO slots at threshold crossing are 128-(T+1).
References: pinned `video/agon.h`, `video/vdp_protocol.h`, and
[IDF 4.4.6 UART documentation](https://docs.espressif.com/projects/esp-idf/en/v4.4.6/esp32/api-reference/peripherals/uart.html),
[ESP32 register definitions](https://github.com/espressif/esp-idf/blob/v4.4.6/components/soc/esp32/include/soc/uart_reg.h).

## Current implementation paths

| Path | Current behavior and required invariant |
|---|---|
| `src/uart.c::open_UART0` | FCTL=07h enables/clears FIFOs; batching must not reconfigure them |
| `src/uart0_tx.inc::tx_service` | Arm modem source, read shared LSR, require THRE, set B=16; each write currently reads shared MSR |
| `publish_core`, `cancel_mark`, `kick_core` | Foreground service entry points; all must retain admission, fresh CTS check and cap |
| `tx_isr` TX/modem dispatch | At most one service per entry; return before further IIR reads after budget, preserving wakeups |
| `src/uart0_async.asm::uart0_pump` | Bounded RX then same TX service under DI; must use identical batching semantics |
| `sync_core` / `uart0_sync_put` | Drain earlier work; check CTS for the one ordinary byte; do not batch compatibility output |
| `close_core` / `uart0_return_fence` | Require TEMT; preserve sources while draining; reset session policy only after successful close |
| `read_msr` | Latches acknowledged modem deltas; skip whole calls between groups rather than using unowned raw reads |

One consumer and DI exclusion prevent a second foreground/ISR path from adding
THR writes during a service opportunity. The descriptor loop may move to the
next descriptor but shares the same B=16 counter. The physical 16-byte FIFO cap
is independent of the new N interval. The API wrapper saves IX and restores
incoming IFF; other preserved registers/shadow banks must remain untouched.

A local group counter must not reuse B, which is the remaining refill budget,
or C, which `read_msr` clobbers. Current TX loop/helper paths leave D available
and preserve it through `hl_zero`; D is scratch for these service callers and
saved by ISR/compatibility wrappers. Audit this again against assembled code
when implementing. No persistent remainder should survive a service return.
Avoid a new per-byte configuration branch in the default path if practical;
its instruction overhead belongs in the paired measurements either way.

## Conditional byte budget

Consider the instant the transmitter's sampled CTS level has become blocked
and stays blocked while receiver servicing is paused. At refill admission,
THRE establishes zero queued FIFO bytes but allows one old shift-register byte.
Only 16 new writes can occur before service returns. At any later stop point,
previous writes from that same opportunity plus its remaining writes are still
at most 16, even if some have shifted out. No new opportunity may begin writing
without a fresh clear-to-send sample. Therefore this opportunity plus its old
shift-register byte contributes at most 17 bytes after that stop point. This is
an accounting envelope; smaller N does not create a simple N-byte bound because
previously queued bytes cannot be recalled.

Receiver threshold crossing precedes observation at the eZ80. Let L account
conservatively for bytes completed during that unmeasured propagation/detection
interval. A sufficient conditional stock-FIFO budget is:

`128 - (64+1) - (16+1) - L = 46-L remaining slots`.

This is a model calculation, NOT a measured 46-slot reserve or an electrical
latency bound. At 1152000 baud, 8N1, one byte takes about 8.68us; a conservative
latency allowance can use `ceil(115200 * delay_seconds)` whole bytes. No measured
delay is currently available, so do not substitute L=0 as a hardware guarantee.
Any path that refills without THRE, increases the 16-write cap, carries allowance
across refills, or bypasses the fresh start check invalidates this argument.

Current default also has bytes in flight; the physical run measured its stock
settled occupancy 66, leaving 62 slots. That observation is not an independent
budget that can simply be added to a new unchecked interval. In particular,
62 observed spare slots do not authorize a 62-byte burst. Keep the hardware
cap fixed, qualify the altered sampling behavior, and retain a guard reserve.

## Evidence and permissible experiment range

Physical R0003 verified 42 payloads (172032 bytes), both 5/20ms pauses and three
repeats. Settled occupancies were 64→66,96→98,112→114,120→126 and 124/126/127→128.
All byte counts/CRCs and restoration checks pass; no raw UART errors appeared.
Full-FIFO values are censored and show no failure boundary. Changing thresholds
may alter hardware flow-control hysteresis/phase; do not infer a fixed tail
from the tighter-threshold values. See `experiments/uart0-margin/physical-results.json`.

Candidate sizes 1/2/4/8/16 fit the fixed 16-write service envelope. They are
permissible isolated experiments, with diagnostic receiver integrity checks;
none above 1 is qualified for production yet. Keep stock threshold 64 for the
primary comparison. Additional tight-threshold trials are controls. Reject
invalid measurement conditions and unexplained data loss. Do not require
Olimex probing or deliberately disable CTS as a prerequisite.

## Performance hypothesis and verification impact

In a full 16-write service with continuously permissive CTS, samples decrease
from 16 to `ceil(16/N)`. The present guard contains CALL, nine helper instructions
(including RET), BIT and conditional JR: twelve executed instructions per sample.
At N=16 this removes 15 guards, or 180 dynamic instructions, before new loop/control
overhead. This counts instructions, not cycles or a guaranteed net benefit.
Descriptor accounting remains and may dominate. UART line rate remains fixed;
measure useful eZ80 work recovered, service time and software-induced gaps.

Existing negative control `cts` expects a check before every byte. Keep it for
N1; add a batching-aware invariant (fresh check/group allowance and 16-total cap)
for N>1. Do not disable the control or mistake intentional batching for a
missing guard. Existing 17-byte-burst, premature release, lost modem wakeup and
TX-empty acknowledgement controls remain essential. Both scripted instruction
model and Flexe have timing/interrupt-model limits; physical receiver evidence
is still required for changed CTS behavior.

## Audit source identity

Audited production source at accepted commit a776668; no assembly changed:

| File | SHA256 |
|---|---|
| `src/uart0_tx.inc` | `2a086ac94ce28390ce8eff3266f193f75be4117f309690b29bac0543db0fe584` |
| `src/uart0_async.asm` | `8d0b9da560dc7206dc9f047137d164dd8dfbb869f470a739d322468b8e2455a1` |
| `src/serial.asm` | `9198539048cefa20bac9a7d898c417c01bcdb395f0f6a866956afd0ef866fba9` |
| `src/uart.c` | `eea52c27b6ab35ba3f8dac9fa0f95824465fe2b9c06779edd6965852e826373a` |
