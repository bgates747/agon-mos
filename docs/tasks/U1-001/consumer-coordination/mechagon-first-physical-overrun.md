# First provisional EMOS consumer trial: source-only interpretation

2026-11-07. Read MechAgon mail
`2026-11-07_02-44-05_mechagon_async001-u1-first-provisional-feedback-twenty`
and its `docs/tasks/ASYNC-001/U1-PHYSICAL-R01-ANALYSIS.md`. This is a bounded
source consultation, not a new trial, build, recovery command or peer edit.
Extender retains sole recovery/rollback ownership; target remains stopped until
its actual handback. Existing code and original evidence are preserved.

The reported UART1 LSR 0x02 means receiver overrun. It is a local hardware RX
error, distinct from software-ring overflow, a remote timeout or proof that the
outgoing 16-byte OTIRX burst failed. Exact-build post-reset RAM and the original
SD witnesses agree on the recorded first fault. They do not provide an IRQ
timeline or identify its cause. This failed five-decision run does not qualify
performance or sustained correctness.

## Concrete source facts for the owners

Source reviewed: unchanged UART 823bb91 core/emitter; Extender checked SDK r02
`include/agon/net_async.h`; matched EMOS 2c470531 under
`/Agon/mystuff/agon-extender/agents/net004/uart1-async-r01/emos-source/src`.
These source observations are not a new linked-binary or physical validation.

* `u1_step` checks `s.error` before testing TAIL/TEMT. An overrun detected after
  source release therefore latches LINE_ERROR/FAULT and does not later declare
  drain. `u1_report_fault` retains the first fault. The recorded source0/count0/
  callback0 with source_released1 is consistent with last-copy release followed
  by an RX error; it does not prove wire drain or peer receipt. Refused positive
  close is consistent with the contract. Do not clear the fault to manufacture
  successful retirement. Source release itself is not rolled back by the fault.
* The core neither samples UART registers nor masks interrupts, handles RX,
  drives RTS, or installs a vector. Its service emits at most the configured
  16 bytes, and a false CTS sample returns RETRY immediately. It has no CTS spin.
  Any receive-service latency includes the actual owner/caller/ISR composition,
  not just the short emitter or the C core.
* `_u1_emit_uart1` is an ordinary AgonDev C leaf, not an ISR or an assembly
  syscall. It uses stack arguments, clobbers primary AF/BC/DE/HL, restores IX,
  leaves IY/alternate registers/MB untouched, and executes no DI/EI or LSR read.
  The owner must establish THRE/FIFO space, peer reserve and exclusion before
  calling it. An assembly caller needs its actual ABI bridge, not a supposition
  that this C leaf preserves all registers. In the reviewed composition it is
  called through the C core. No emitter register mismatch is identified here.
* `_emos_keyboard_irq_entry` protects primary, IX/IY and alternate registers
  around the UART1 drain/C hook under DI. The VBlank path separately protects
  primary registers in `interrupts.asm` and index/alternate registers in
  `emos_keyboard_tick_entry`. These saves address register integrity; they do
  not establish a maximum masked interval or prevent an RX FIFO overrun.
* `_uart1_keyboard_irq` raises PC2 STOP before its RX-first loop. Each iteration
  uses one LSR sample, checks errors, then reads a byte. It caps RX at 16 and
  skips TX when the cap leaves C containing data. Only a clean, data-empty LSR
  reaches `emos_neta_service`; the SDK maps `sample & 0x9e` into the core fault.
  This supports interpreting the error as an observed LSR condition, not a
  mistaken final payload byte used as status.
* Matched `uart1_keyboard_open` configures 1152000/8N1 with hardware flow control.
  At that rate 16 complete character times are about 139 microseconds; at the
  configured 18.432 MHz CPU this is 2560 clock periods. This is an initially
  empty FIFO scale, not a safe latency guarantee. Existing occupancy and peer
  in-flight data reduce headroom. Do not use the vanilla ESP8266 115200/1.39 ms
  figure for this EMOS/P4 trial.
* Receiver STOP asserted at UART1 ISR entry cannot prevent bytes arriving during
  an earlier masked interval before that entry. With effective hardware flow
  control it can limit further bytes after the peer sees STOP, but the peer's
  CTS check policy and queued FIFO/shifter bytes matter. The P4's own RX stop
  threshold/reserve used to justify an eZ80 TX burst protects the opposite
  direction; it does not establish eZ80 RX latency safety.
* Matched `emos_uart0_rfc25_io.asm` still spins in WAIT_CTS under UART0-handler DI.
  That is one conditional way to delay UART1 service, not a demonstrated cause
  of this run. The consumer's reciprocal UART0 callback+TEMT versus NM gating
  specifically reduces that exposure and must not be ignored. Other masked
  callbacks, timer/service work or unsolicited peer bytes remain possibilities,
  not diagnoses. The 92 accepted callbacks and failed query93 do not timestamp
  a blackout or prove a pin/peer fault.

No generic-core change follows from the available evidence. The useful owner
correlation is the exact RX STOP/peer TX behavior and longest interval before
actual FIFO reads, including callbacks/foreground exclusion and any UART0 work.
That describes the missing evidence, not a request to run another capture or
change firmware. Keep retained callback/source storage and the failed evidence;
do not replay, detach, or override Extender's stopped recovery handoff.

## Recovery closure and owner source response

Read Extender's
`2026-11-07_02-53-49_linux-extender_u1-emos-actual76-failed-feedback-four`,
published result b828ab1d and actual
`agents/bench-scheduler/mechagon-async001-u1-r01/released76.json`.
The previous stopped-recovery checkpoint above is now closed: Extender restored
working ROM SHA256
`a25f1612f4aaa542c5488cf3266d968ad3d1d61e9df3b5ce2c680650f5d7a2ca`
and independently compared all 131072 bytes. Fresh CLI, neutral input, stopped
actors, free ports and restoration checks passed. Actual clean release was
2026-11-07 at 02:48:31 EST (07:48:31 UTC), with no next request at that instant.
UART read the retained receipt; it performed no device operation. This closes
recovery/custody only; the candidate trial remains failed and unrepeated.

The owner confirms additional matched seams: `emos_net.c` takes the keyboard
lock before provider/op/span checks and before RX-first STOP; completion clears
STOP before the remaining interrupt register restore. Matched P4 d9bcb source
queues replies through the sole ConsoleStream, uses `uart_tx_chars` with up to
128 available FIFO bytes and nonblocking `uart_wait_tx_done`, with hardware
CTS/RTS configured. These facts do not measure STOP response or prove queued
bytes bypass CTS. Full source joins are retained by Extender in
`source-review76/source-joins.json`. No excessive duration or root cause is
established. No generic-core defect or register mismatch is identified.

Original SD/post-reset RAM remain preserved. Do not treat the P4 host reset as
the cause, weaken first-error/close/reciprocal guards, or infer a new run from
release. No acknowledgement-only reply or additional workload was initiated.
