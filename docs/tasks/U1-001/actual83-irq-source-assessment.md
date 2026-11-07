# GOAL-001: actual83 UART1 overrun source assessment

Actual83 still reports UART1 RX overrun with the corrected bounded-CTS/atomic
owner ROM8de66 installed. The earlier fixes did not establish sufficient service
latency or peer STOP reserve for this consumer. No new generic U1 fault is
identified here. Do not replay the same case without a discriminator.

This is the existing UART-owner source-support assignment in
`2026-11-07_07-17-22_mechagon_goal001-uart83-overrun-source-support`.
No new build, target access, instrumentation installation or physical case was
performed. Extender retains firmware/bench/cleanup ownership and MechAgon the
consumer/profiling work. Existing queues and custody remain unchanged.

## Evidence and limits

Rehashed the original1799-byte SD status2ac3ac64 and post-reset64KiB RAMeca958f2.
Selected frozen application/source/SDK/core/map inputs still match actual83's
kit5706e12a/source3ddc0496. Native43122-byte image9be4582a and map2886cb1c
were read alongside existing object disassembly. Source pins and exact retained
paths: `retry-r01/actual83-source-pins.json`. This is not a rebuild, execution or
independent decoding of every RAM field.

The SD record has13 decisions,10 acknowledged viewframes, stage9/result35,
POLLquery57,56 accepted replies/no rejects, U1phase3/fault2/error2,
source_released1/wire_idle0/progress58. `link_idle=1` is a later foreground
observation, not proof that UART0 was idle when the first OE occurred. Original
fault time, FIFO occupancy and physical CTS/STOP tail are absent. Source release
does not prove wire drain, hook retirement or absence of an earlier blackout.

## Concrete timing contributions from matched source

* `experiments/uart1-async/src/u1_tx.c::u1_step` has no wait loop. An admitted
  service emits at most16 bytes once, or returns for CTS/THRE/TEMT retry. Its
  matched application callback `agon_neta_source_done` writes one flag. The
  emitter uses OTIRX, not a wait for sixteen bytes to leave the wire. Thus the
 139us wire interval is not the CPU duration of this service.
* Matched `emos_uart0_rfc25_io.asm` samples CTS once and defers without spinning.
  The actual application's `rfc.s::render_rfc_callback` only stores a flag.
  The final UART0 TX callback is not an arbitrary C workload in this build.
  The tiny atomic ownership helper is another bounded masked interval; no
  measured duration follows from that description.
* `interrupts.asm::_uart0_handler` masks interrupts through RX protocol dispatch
  and the installed callback chain. Its byte read is nonblocking. UART0 TX
  handling and repeated RX entries also consume masked service opportunities;
  removing the CTS backedge does not remove those costs.
* `emos_keyboard_io.asm::_uart1_keyboard_irq` asserts peer STOP, then drains at
  most16 bytes. Each byte goes through the parser; a completed packet dispatches
  immediately before the drain continues. NM replies pass through
  `emos_net_packet`/`emos_reply_callback`, the application's callback router and
  `agon_net_receive`. The accepted-reply path copies13+payload bytes, up to141,
  and updates witnesses, all with interrupts masked. This is more work than the
  TX flag callback. It is not yet a measured overrun cause.
* A clean-empty UART1 drain invokes `emos_neta_service`, the application hook
  and U1 step before readiness is restored. Existing object disassembly confirms
  AgonDev frame setup, two byte-shift helper calls and a five-byte sample copy
  in this hook, in addition to the core/emitter. The16-byte RX cap therefore
  does not mean a sixteen-instruction or constant-time interrupt.
* VBlank calls `emos_keyboard_tick_entry` under DI, including controller/owner
  tick work and possible U1 progress. Foreground `neta` calls assert STOP and
  hold it through their critical section. Other application `render_guard`
  regions mask interrupts without that UART1 STOP scope. These are additional
  concrete boundaries for a delay investigation, not newly proven defects.

At18.432MHz and1152000baud8N1, one character takes160 CPU clocks/8.681us;
sixteen take2560 clocks/138.889us. This is empty-FIFO geometry, not an allowed
blackout. If occupancy is already q, only16-q byte slots remain; an in-flight
character and STOP response consume part of that reserve. A service interval
cannot be judged from FIFO size alone. No exact cycle-cost sum is claimed:
branch paths, compiler helpers, callbacks, memory waits and IRQ ordering matter.

The P4's RX reserve protects the opposite direction. Bytes accepted by
`uart_tx_chars` or a software output queue are not proof of bytes transmitted
after eZ80 STOP; queue counts cannot substitute for physical tail evidence.

## Minimum discriminating diagnostic proposed to the owners

D83-001 [x] Return the matched source findings and evidence limits. Preserve
first-error status, source/drain separation and quarantine. No generic rewrite
or new resident async engine is justified by this result.

D83-002 [ ] Extender and MechAgon's existing timing helper select one private,
small diagnostic composition. Use application-owned RAM and bounded assembly
markers, not a second profiler. Tag UART0 RX/protocol callback, UART0 TX,
UART1 drain/packet callback, VBlank and foreground critical sections. Retain
the preceding completed masked span as well as the current path; recording only
"UART1 ISR" at fault loses the blackout that preceded entry. Include duration,
sequence and timer-validity fields. Do not interpret a maximum across the whole
run as temporal proof of the failing event.

D83-003 [ ] At the existing first-error branch, before fault/reset callbacks,
freeze the ALREADY-read LSR byte (C), drain count, parser position, STOP/hold
context and recent timing record. Never add an independent LSR read: it
acknowledges evidence. Bracket first/last RBR of a drain where practical; avoid
a new general C callback or full record write for every received byte. Count
cap hits separately from clean-empty exits. The owner chooses register-safe
hooks and a supported app association; no hard-coded private RAM address or
new public syscall is requested.

D83-004 [ ] Use only an explicitly disposable admitted timer and the existing
helper's consistent epoch/expiry rules. No PRT0 takeover, blind reload restore,
or foreground scratch reader from an ISR. /256 gives13.889us resolution; it can
separate gross blackouts near139us but cannot establish fine ISR cycle costs.
/16 gives0.868us but a16-bit counter wraps in56.889ms; no silent modular reading
of a potentially longer stall. An expired/ambiguous observation is UNKNOWN.
Actual83 was unprofiled, so no timer ownership is inferred from that run.

D83-005 [ ] Before any selected physical case, account actual linked ROM fit
(575bytes free in8de66), register/IFF preservation and marker overhead; include
unmeasured save/restore tails. A fixed-size app-RAM record avoids serial/SD/log
output in the hot path. Stop once at the first fault; no automatic retry or
baud/firmware fallback. Retain the frozen diagnostic source and exact image.

Interpretation: a long measured masked span while receive readiness remained
advertised identifies a concrete service-risk path. A long time between reads
alone can also be ordinary wire silence. OE after STOP was asserted and a clean
drain narrows attention to resume ordering/peer response/reserve, but software
tags do not measure the physical peer tail. If records cannot settle that
distinction, request the owner to choose a separately bounded CTS/TX capture or
controlled peer pause/credit test; do not claim an electrical or FIFO-reserve
cause from software queue totals. All new execution remains owner-selected.
