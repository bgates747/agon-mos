# RX-006 — Rally adoption feasibility return

**Yes: I am comfortable that the current one-buffer counted interface WOULD work
for the retained post-race export and materially simplify it, with the documented
lifetime/error conditions.** No larger producer, cancellation framework, full-game
port or additional consumer benchmark is needed for this source-based judgment.
UART owns RX-006's synthetic qualification and completion decision.

This review reads the exact request, human scope, wire/receiver contract, retained
R0067 pass log and Rally sources listed in SOURCE-PINS.json. It performs no app
migration, build/test, target contact, reservation or paused-goal resumption.
MoonPatrol uses ordinary stock GP replies and is a different current task; it is
not being relabeled as this retained VDPlet bulk consumer.

1. **Smallest seam.** Replace only the inner READ16 reconstruction loop in
   TIM-002 `telemetry.hpp::timingDumpBuffer`, leaving original race/Stop/UNLOAD,
   file names, output bytes and state/generation oracles intact. This function
   already dumps ordinary buffers50306/50307 after the native module is unloaded,
   while those independently owned buffers remain allocated and its private
   control/error callback remains installed. `timingAllocate` creates each as a
   single whole buffer block; no new consolidation or module lease is needed.
   No producer writes continue during this dump. Keep those buffers/generation
   frozen until the complete logical export finishes, not merely one chunk.

2. **Concrete adapter.** Keep a persistent512B guarded writable chunk. Register
   syscall26h with capacity/count and NULL callback (foreground terminal-state
   polling suffices here), check admission, send one operation8 read, then wait
   without disabling interrupts. Observe state before terminal counts/payload;
   require success plus actual/announced counts equal the exact requested chunk
   (last chunks352B and72B). Save to the already-open file outside the IRQ. Only
   then rearm/reuse that chunk. The existing256B destination could instead stay
   unchanged, using257 reads;512B costs256B additional destination storage and
   uses129 reads. No async request sender is required for this adoption seam.
   If one is later selected, its request-source release remains independent of
   RX completion; keep that source live until its own positive release.

3. **Source-derived reduction.**900x72B+64=64864B, plus26x20B+64=584B, total65448B.
   Current read16(2B) uses32724 request/reply/wait exchanges. At512B this becomes
   127+2=129 exchanges (15x512+412 for the owner's8092B synthetic example is a
   separate logical size). Existing outer-file chunking need not dictate the
   wire maximum. These counts use the documented17B old request/12B old response
   and19B new request/3B counted header; discovery, errors and other commands
   are excluded. Exact arithmetic is retained in COUNTS.json.

   | Path | Requests | Outbound bytes | Inbound bytes | Total wire bytes |
   | --- | ---: | ---: | ---: | ---: |
   | READ16 | 32724 | 556308 | 392688 | 948996 |
   | Counted256 | 257 | 4883 | 66219 | 71102 |
   | Counted512 | 129 | 2451 | 65835 | 68286 |

   The separate406B final-state export across six existing buffers would use
   six reads instead of203. These are call/byte reductions, not measured latency,
   CPU percentage, throughput or FPS. Post-race export is outside race timing;
   faster export does not establish higher rendered FPS.

4. **What really disappears.** Per-word READ16 calls, two-byte assembly into a
   file chunk, bulk-data keycode encoding/ten-byte mailbox traffic and32724
   individual identity/wait/transcript-adapter decisions can leave this export
   path. It does NOT remove all private keyboard-vector code yet: LOAD/RUN/STOP/
   UNLOAD/control and tagged ERROR still use the old callback. Keep it for this
   bounded adoption, but bulk data no longer travels through it or clears fake
   key fields. A counted4B value could later replace two read16 calls; that later
   in-loop change is not necessary for this favorable export judgment.

5. **Identity and failure.**90h/count has no transaction ID. That suffices for
   this clean, strictly serialized one-outstanding request path with no unsolicited
   counted producer and no reuse after uncertainty. Preserve existing semantic
   header/generation/file-byte checks. Never pretend registration itself proves
   request/world/generation identity. The old tagged source error does NOT retire
   an arm: it must remain pending with live destination/callback code. Rally's
   existing fail-stop behavior (remain resident pending/reset) fits; do not free,
   rearm or return to MOS merely because a timeout or ERROR arrived. A positive
   oversize discard retires transport but does not validate data. Abort export
   rather than save incomplete bytes. No new cancellation/retry API is demanded.

6. **Keyboard/source/cleanup.** The counted parser must preserve genuine legacy
   keys/mode/GP replies; R0067 explicitly reports keys1/1,30callbacks and suitePASS.
   That is existing synthetic evidence, not a Rally run. Respect ADL1/MBASE0,
   callback ABI (or choose NULL), valid nonwrapping destination, one shared arm,
   positive terminal publication and no MOS/file work inside an RX callback.
   Use the producer's original output route/validated single-block buffer; hold
   source storage across the logical export. RX complete means received bytes,
   not VDP drawing/scanout or TX-source release. The matching opt-in MOS/VDP,
   INFO27/512 and actual lifetime contract must be selected before adoption;
   stock/frozen a50 support is not implied. These are existing binding conditions,
   not a request for more features or a new owner correctness program.

There is no uncovered correctness blocker in this bounded export use under that
contract. Exact failing/late-stream recovery beyond fail-stop remains an explicit
limit; it does not prevent the proposed finite serial adoption. Keep old fixtures
and oracles frozen and use a separately selected adapter if implementation is
later authorized. This favorable feasibility return is sufficient for my side
of RX-006's stop criterion; no millisecond chase or additional Rally run requested.
