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

D83-002 [x] Extender and MechAgon's existing timing helper select one private,
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

## Shared timing-helper proposal review

Read MechAgon's `irq-timing-contract/PROPOSAL.md`, SHA256
`c3a486bb24abeed8231c70fea4db9f1384265a6425c5b45bb6bd24070e28088d`,
and its source/map decoder report for consumer83. The proposal retains the
required preceding/current observed spans, first already-read LSR, STOP/drain
context, single-owner timer, same-epoch descending counts and explicit expiry.
Its partial coverage, quantization and omitted-tail limits are appropriate.
The decoder's retired renderer RUN191 is a cleanup-time fact, not a first-OE
UART0-idle proof. Owner recovery reports actual83 released with a25f restored.

One concrete rearm binding needs resolution: no pending NM operation does not
prove the receive wire is quiet. Unsolicited keys, a queued reply or an in-flight
tail can still arrive. The proposed up-to256-sample timer readiness loop must
not create an unmeasured DI blackout while UART1 advertises READY. Extender
must select STOP/receive-service/atomic epoch publication or another supported
safe sequence, and bound/account its cost. Do not introduce EI mid-publication
or guess that asserting STOP instantly empties the peer/wire. Failed timer
readiness should invalidate the diagnostic, without inventing transport drain.
This concern applies only to the new diagnostic; actual83 was uninstrumented.

Generic code need not be rewritten for markers: UART0's existing entry/TX-RX
branch and final exit cover its copy/flag callback; the owner UART1 clean-empty
service boundary surrounds the app hook/core/emitter with STOP already asserted.
The U1 emitter remains an ordinary bounded CALL under owner exclusion, not an
ISR entry or a separate place to sample LSR. Tag its cost inside the outer
owner span. First/last RBR markers belong to the owner's existing drain, using
its retained B/count and saved LSR; they do not belong inside generic u1_step.
No extra IRQ ownership or timing API is implied. Extender chooses concrete
hooks/association/fit and the existing helper supplies the record implementation.

No runtime, compiler or bench action was performed for this source-only review.

## Selected owner binding, before implementation

Source of truth: Extender
[`EMOS-ASYNC-RX-DIAGNOSTIC-R01.md`](../../../../agon-extender/docs/tasks/NET-004/EMOS-ASYNC-RX-DIAGNOSTIC-R01.md)
and durable mail
`2026-11-07_07-39-55_linux-extender_u1-owner-diagnostic-marker-binding-r01`.
This closes D83-002's source-mechanism selection only; D83-003..005 still need
implementation, exact source/linked checks and any separately selected execution.

* Private diagnostic OPEN is seven bytes: operation0, service entry LE24,
  independent marker entry LE24. Existing ordinal and seven-byte reply remain.
  Four-byte OPEN supplies the NULL-marker control; baseline8de66 refuses seven.
  Both code entries need app-range validation. Marker and service association
  share lifetime; refused close retains both. Reset clears pointers without
  erasing the retained app record. No generic U1 service-event ABI changes.
* Marker code and128-byte MGIRQ001 record live in app RAM. Extender prepares
  reusable observer code and small opt-in firmware bridges; the existing helper
  and consumer integrate that binding. UART does not create a second recorder.
  Marker entry is ordinary bounded assembly under DI/ADL, preserving all
  primary/index/alternate registers and upper bytes plus incoming IFF. No EI,
  RETI, C call, transport I/O, wait or logging. Only admitted PRT1 and its own
  bounded record are accessed; parser context is copied immediately, not kept.
* Inputs: A event; D sampled PC_DR; E RX-hold; HL owner six-byte parser prefix.
  B drain-remaining/C sample are meaningful only at their defined RX points.
  In particular C at first-read is DATA; only first-error interprets C as
  acknowledging error LSR. Do not reinterpret the first-read value as status.
* Events: outer begins0x01..05 and ends0x81..85 for UART0 RX/TX, UART1 drain,
  VBlank and foreground owner; app critical0x06/86. Inner packet0x10/90 and
  clean-empty service0x11/91 are context, not additive CPU spans. Point events:
  first-RBR0x20, cap0x21, clean-empty0x22, first-error0x40. Unsampled last-RBR
  validity remains clear. Missing OPEN/CLOSE edges, hooks and tails are unknown.
* Rearm atomically disarms timer reads while raw first-error capture remains
  active. Readiness loop stays IRQ-enabled, with bounded individual register
  operations. Publish a ready epoch atomically only after source/drain/span and
  frozen-state rechecks. Arrivals in the gap remain retained/unknown. Rearm
  never clears a first-fault freeze. This addresses the readiness-loop concern
  above at contract level; instruction-level evidence is still pending.
* Stopped decoding derives durations/gaps only from valid same-epoch descending
  raw endpoints. Uncomputed native zero fields must not look like measured
  zero elapsed time. No exclusive CPU or physical STOP-tail claim follows.

No material register/rearm conflict is identified in this selected interface.
That is a source-contract finding, not a fit, linked ABI or runtime pass. Exact
wrapper saves/context injection, marker cost, NULL control and575-byte ROM fit
remain the owner's build gates. No new hardware reservation or installation is
selected, and no acknowledgement-only reply is needed.

## Checked diagnostic r01 artifact: active-fault endpoint gap

Read `2026-11-07_08-14-14_linux-extender_u1-diagnostic-r01-checked-source-artifact-agon-mos`.
Independently rehashed184789-byte package0a9e85ac and every contained manifest
file, and compared the retained identity-matched OFF binary against954e's raw
baseline: exact130497 bytes/SHA368b00b2. Diagnostic ON is owner1727fa19,
fullROM80fe2359, raw130896/free176, bridge delta399ROM/+3BSS. Standalone app
1620text/166BSS is owner-linked evidence, not consumer incremental size or
executed interrupt/register proof. Compiler362 controls were read, not rerun.
Evidence: `retry-r01/diagnostic-r01-package-review.json`.

D83-CURRENT-ENDPOINT: `observer.s::first_fault` marks the current span active
at fault and stores raw fault count/control at92..94, but does not populate
that span's end count/control at70/71/75 or set END_CAPTURED. A normal active
span's flags therefore change0x03 to0x13, whereas `observer.h`'s documented
decoder requires PRESENT|START_CAPTURED|END_CAPTURED (0x07) and valid endpoints.
Even a valid running timer cannot yield the current masked span's elapsed time
under that rule. This is a diagnostic attribution gap, not a transport fault;
the raw fault timestamp is retained and an honest decoder returns unknown.

Return this material mismatch to Extender and the consumer. Minimal options:
copy the SAME already-captured fault count/control into the active span's end
fields and set endpoint-captured, or explicitly specify/test how a stopped
decoder substitutes the separate fault timestamp for an ACTIVE_AT_FAULT span.
No extra timer/LSR read, runtime duration arithmetic or generic driver change
is needed. Require source controls for active+ready, disarmed/expired/no-active
fault and immutable first freeze; invalid timing must remain unknown.

Schema2/raw parser/remaining context, absent RBR hooks, reserved query/gaps,
register save/restore source and IRQ-enabled rearm remain bounded review facts.
No new owner source edit, compilation or native/hardware execution was performed.
Separate uninstrumented R04 admission and working8de66 are unaffected.
