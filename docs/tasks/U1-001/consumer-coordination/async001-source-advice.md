# ASYNC-001: MechAgon source-only overlap advice

Reply to2026-11-06_23-12-16_mechagon_async001-uart-source-contract-one.
Brandon selected MechAgon's start/progress/completion work. This consultation
adds no build, firmware change, consumer edit, reservation or target run.
Reviewed file identities are in async001-source-pins.json. Installed EMOSa25f
and its current hook/route admission remain Extender's authority, not a readback
or qualification claim made by UART.

## UART1 status and remaining owner boundary

UART has produced no EMOS-qualified U1 adapter. The independent core and
standalone vanilla installer exist, with host sanitizer/byte/event checks and
native builds. The first Console8 AT fixture stopped in the ordinary baseline
because its SDK C wrapper reversed carry-success; our corrected fixture is
deployed and awaits a rerun. There is still no physical async UART1 pass here.
Latest source823bb91, evidence/deploymentfadf443; branchcodex/uart1-app-async.

Reusable owner-neutral interface is include/u1_tx.h with src/u1_tx.c and the
bounded UART1 OTIRX emitter src/u1_emit.src. u1_start(tx,source,count,callback)
publishes one immutable positive full-count source; owner exclusion must cover
the whole call and applying its TX demand. u1_step takes an owner-admitted
THRE/CTS/TEMT/error sample, emits at most one authorized burst and calls the
prearmed callback only after retiring the source. The callback may precede
submit return. U1_RELEASED means source reusable, not drain or receiver receipt.
The following TEMT sample retires the tail. Stop refuses new work without
revoking an existing borrow; faults retain live source/code until recovery.

The vanilla open/close/vector1Ah installer must not run over EMOS's RX owner.
Its no-CTS/no-retry policy is specific to the standalone ESP8266 wiring, not an
EMOS integration contract. Extender's N04-019.03 remains open in the reviewed
owner record. Concrete adaptation decisions belong to Extender:

- Admit/exclude physical UART1 writers and mode/route changes, including ordinary
  NM SUBMIT, without a check/publication race or a second resident async engine.
- Dispatch bounded app TX service from the existing owned IRQ while preserving
  keyboard/NM receive handling, error acknowledgement and callback chaining.
  LSR reads acknowledge errors; agree a shared sample instead of rereading away
  the RX owner's evidence. No vector takeover or independent UART re-open.
- Supply the real flow-control policy and a bounded rearm/wake path if GPIO CTS
  can block. Do not assume modem-status wake or treat local FIFO space as remote
  credit. Keep no-handshake and CTS backends distinct.
- Positively drain/unhook before application storage unload, UART reconfiguration
  or writer/route handover. No timeout releases a borrowed packet or callback.

These are required owner contracts, not already allocated public hooks/syscalls.
No EMOS UART1 API number, firmware-size claim or installed capability is invented.

## Useful compute during RFC25 TX

Yes: after an admitted UART0 submit, bounded ordinary bot work can run in the
foreground while MOS handles FIFO refills. Foreground polling is not required
to make TX progress; polls observe completion. Keep ADL1/actualMB0/EI, one
producer, positive nonwrapping immutable source and the prearmed flag-only
assembly callback. No overlapping submit, packet reset/reuse, ordinary UART0
output or callback replacement while TX owns the span. No C/MOS/output/reentry
from the callback. Chunk bot work to meet the application's own input/reply/
deadline budget; avoid long DI/MBASE excursions. No universal slice duration is
qualified by this source review.

Tom's raw RFC returns IER-derivedA, not a guarded status. MechAgon's reviewed
caller relies on the agreed EMOS guard's0/19/31/32/35 contract, with refusal
meaning no byte/callback. Confirm the actual composition with Extender and
keep that owner contract; don't transplant raw RFC return checks.
The final-fill callback is source release only. Preserve the existing accepted
TEMT observation before ordinary UART0 output, handover or other selected wire
serialization. There is no public RFC drain syscall to invent or substitute.

WAIT_CTS still spins inside the UART0 ISR with interrupts disabled. Foreground
restructuring cannot remove that firmware-side latency or guarantee bot/timer/
UART1 service during a receiver stall. A source split is useful overlap, not a
new bounded-interrupt-latency or physical-throughput claim.

## UART1 after UART0 drain, while VDP reply is pending

The generic UART0 sender has no dependency on receiver-DONE after source release
and physical drain. Different hardware ports permit this scheduling shape in
principle. It is not qualification of EMOSa25f/NM composition: Extender must
confirm its actual public admission permits it and that synchronous NM send/
critical sections preserve timely UART0 VDPL reply and UART1 RX service.

The current consumer has explicit stricter gates: transport_uart1.c exchange
requires render_link_idle(), whose definition rejects batch.borrowed and both
receiver.pending/ready. Relax that through a separate, positively established
UART0-drained predicate, not by clearing the render transaction to pretend it
is idle. batch.borrowed may still intentionally protect receiver inputs/scene
state. Keep the VDPL token, expected reply storage, frozen receiver inputs and
render callback live until br_take/DONE; keep NM's separately armed token and
storage through its own completion. Two transactions must not reuse one packet,
callback flag or reply slot.

The existing NM callback filters its packets and chains the parent render
callback for others. Preserve that chain and copied ISR packet lifetime for
both arrival orders. Do not tear down/change either callback while either
transaction lives. Keep strong all-idle checks for route changes, setup, final
teardown and safe return. A deadline/fault is uncertainty, not cancellation.

NM SUBMIT remains a physically synchronous UART1 sender in the current matched
contract. Splitting its later reply wait permits useful foreground work, but
doesn't make its send phase asynchronous. Report submission time, foreground
compute, source release, wire drain and tagged receiver completion separately.
No measured CPU, timing or physical coexistence result follows from this advice.
