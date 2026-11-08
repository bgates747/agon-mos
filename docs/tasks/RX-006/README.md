# RX-006 — Bounded bidirectional transport feasibility goal

**ACTUAL129 DATA PASS; BATCH COMPLETION BUG IDENTIFIED AND CORRECTED IN NEW KIT.**
Recovered original SD log passes all ten sizes4..8092, all36 benchmark cells
and SUITE PASS. The host timed out because UART's following SAVE batch command
used invalid unprefixed hexadecimal/address and decimal length syntax. Exact
receiving MOS source rejects that address and stops EXEC before the listener.
The absent witness and unavailable pre-reset console/RAM limits remain.
[Full evidence and diagnosis](actual129/README.md), [analysis](actual129/analysis.json).

Extender restored exact originals/full readbacks and released129 at10:10:35UTC;
all actors stopped, token invalid, FSIM8cc next requiring fresh grant. Original
123/128 installation-only UNRUN failures remain separate historical records.
No performance tuning or transport/firmware correction is needed by this finding.

[Completion confirmation r04](OLIMEX-R04.md) uses unchanged app0208015a,
EMOS171c/VDP7d09 with explicit `SAVE ... &447CF &20`, fresh targetr02 and host
physical-r04. New kit6d467b51/all49 owner input hashes match; actual normal FIFO request
`e4d3981a89ae` awaits owner binding and fresh admission behind existing owners.
Preserve populatedr01/old kit and all129 evidence. Confirm witness/return/normal
listener chain before selected consumer-code trials; no prototype pilot yet.

Equal-payload no-work batches complete about5.65x/6.49x/7.12x faster using counted
returns at128/256/1024B than tagged8B replies. This is original129's coarse public
clock application latency, including verification, not CPU utilization or pure
wire throughput. No consumer or firmware performance claim is inferred.

## Reopening after Brandon's correction

Brandon further clarified the required sequence: verify the method on hardware
and benchmark identical pulls through the existing keyboard-reply workaround
and the new counted path; then work with selected owners to test it in their
own code. In particular 128, 256 and about 1024 bytes are useful comparative
sizes, while individual four-byte operations are too short for a convincing
timing result. This is actual hardware and consumer testing, not just source
acceptance. Keep consumer trials conditional on the own-suite pass and useful
measurements; do not optimize performance or expand into full-game rewrites.

Brandon responded to the unrun-sweep statement:

> You mean that the olimex sweep is still in the queue and will be run when your slot frees up.

UART clarified that no reservation had been made and acknowledged closing too
early. Finish a finite own fixture and coordinate a supported receiving
MOS/EMOS/VDP/input/recovery tuple with Extender. Enter the actual bench FIFO
when prepared, obtain actual admission and complete the size sweep below.
Source review is already affirmative; do not repeat consultations or port games.
The existing no-optimization, finite-run and normal-restoration limits remain.
Use the current 512-byte wire replies for long logical reads; no new larger-frame
feature is needed. If integration blocks progress, report that exact preparation
dependency rather than claiming the test is already queued or passed.

Brandon selected this goal on November7 after Console8 RX-005 R0067 passed.
Prove practical adoption feasibility, not a maximum-performance result. UART
coordinates and owns MOS plus original synthetic test code; VDPlet owns VDP,
Extender owns EMOS/bench integration, and consumer owners assess their own code.
No UART/VDP owner edits game code. No boot-script changes or automatic test start.

## Direct human instructions and stop condition

In UART chat01a132e0-4787-7310-93e9-f5248ffb2ff8, Brandon said:

> i'm going down for the night. you may work with other agents to schedule bench time on the olimex for benchmarking and testing. you should probably begin with your own simple test suite to guide expectations. you'll want to send/receive short and long transactions. 4,8,16,32,64,128, 256,1024,4096,8092 bytes are probably informative transfers to try and should be very quick to loop through, and not push the hardware too hard.

He then explicitly selected the goal:

> make this a goal task. continue to work with select agents until any errors are resolved. we will not try to optimize for performance. as soon as they're comfortable that this method *would* work *if* adopted and would make life eaiser on them or at least provide a modest peformance gain, then stop the goal and report success. but do not have them grind away all night trying to squeeze millisecond gains out of kilobyte-sized transfers.

This authorizes finite own-suite preparation and coordinated Olimex testing,
correctness/integration error resolution and selected-owner consultation. It does
not authorize preempting a bench owner, changing startup, rewriting applications,
performance optimization, upstream submission or a production release. Oryx is
unavailable overnight; use ordinary Pi compiler FIFO and actual Extender custody.

Stop immediately when existing/new attributable correctness evidence and concrete
selected-owner review support that adoption would work and simplify their code or
give a modest useful benefit. Do not make a full-game port, a large benchmark
matrix, worst-case fault proof or squeezing milliseconds a completion requirement.
A completed finite check is not permission for another sweep/replay. Avoid new
firmware/protocol features when the current working interface suffices.

## Initial evidence and selected consumers

RX-005: same MOS/VDP/app passes both Flexe engines and physical Console8 R0067;
0..512-byte integrity/guards/callbacks/keyboard/discard/rearm/admission checks pass.
The published source and exact build/export pins are in RX-005/hardware-r01.
No RX-005 CPU/throughput improvement has been measured. No prototype is broadly
released by this new goal; focused technical review and test fixtures are selected.

Consult VDPlet and Extender first on exact source/lifetime and bench fit. Consult
Rally (large retained post-race export) and6502 (512-byte disk data plus descriptor)
on concrete adoption seams and whether the approach is enough to be useful.
Prefer their existing source/oracles; no game migration or new owner workload is
required for an affirmative source-grounded feasibility judgment. Respect paused
consumer goals. If one of these is unsuitable, choose another confirmed receiver
consumer rather than expanding to all projects.

## Small synthetic suite and measurement contract

Sizes are exactly4,8,16,32,64,128,256,1024,4096,8092 bytes (8092 is intentional).
Use deterministic payloads including header-looking values and surrounding guards.
Verify every valid returned payload and exact count, one outstanding source/receive,
source callback/wire drain/receiver reply as distinct endpoints, positive cleanup.
No timeout reuses live storage or manufactures cancellation; stop uncertain runs
and coordinate owner recovery without an automatic replay.

The current producer caps single wire replies at512B. For larger logical reads,
use strictly serialized chunks<=512, labeling logical total, chunk count, wire
headers/requests and complete-operation latency. An8092B logical transfer has
15x512+412B replies. Do not describe it as one8092B reply or silently change INFO27.
A larger single-frame trial is optional only if the VDP owner judges a tiny,
correctness-focused configuration change justified; it is not needed to show a
useful reduction from the old READ16 workaround. Prefer the existing512B producer.
Long sends may use ordinary existing buffered uploads and the existing async sender.

Compare matched synchronous sending with opt-in async+bounded foreground work;
compare receive busy-wait with receive+same checked work kernel if useful. Setup,
source upload, output/logging and independent readback verification stay outside
pure-TX intervals; record complete request/reply intervals for RX. Aggregate
small transactions so coarse read/loop overhead is not misrepresented as wire
speed. Keep payload versus wire byte rate and foreground capacity versus CPU
utilization distinct. No-traffic calibration is needed before any percentage
claim; omit that claim if it adds more machinery than this feasibility goal needs.
Reuse a checked inactive PRT only if the selected owner admits it, retaining
IRQ/vector/reload limitations. Public MOS counts are two per VBlank, not proof
of120 service interrupts/s. Do not steal an active timer or use emulator speed
as physical evidence.

One initial finite sweep suffices. Suggested bound: one warmup plus three short
batches; repetitions64 for<=256B,8 for1024B,4 for4096/8092B, with progress between
cells and a whole-suite two-minute target. The exact prepared shape must fit the
selected owner tuple before freeze. Per-transfer deadlines and runner finite
watchdogs are protection, not permission to free borrowed buffers or silently
repeat failed operations. Retain partial/failed evidence.

## Bench and ownership plan

Finish source/build and acquire exact tuple before declaring READY. Reserve
through the shared Olimex FIFO; Extender grants only after actual fresh custody.
At reservation,6502/120 was active; it has since released. The dated05:25UTC
November8 snapshot has MechAgon and FSIM ahead of our request, with no active
lease. Obtain fresh actual admission rather than treating this snapshot as custody.
Extender chooses the smallest admitted bench composition/launch/retrieval path:
the Olimex mainboard keyboard is unavailable, so a plain-MOS replacement must not
break its only setup/recovery interface. No casual installation of Console8 MOS
or VDP over a live EMOS/P4 pair. If EMOS integration would require substantial
new work, do not build it merely for this goal: use existing attributable evidence
and a simpler owner-supported finite proof, documenting limits.

Preserve exact incoming firmware/SD/startup/route/mode and use existing retained
rollback bytes. Test invocation is explicit CLI/runner, not autoexec/reset. Follow
Extender test-appliances/test-execution/bench constraints, fresh checkout/assert,
finite monitoring, exact restoration and prompt/neutral input handback. Resource
permission never authorizes changing P4/EMOS/VDP outside the agreed tuple.

## Completed source review and remaining hardware work

- [x] Obtain producer feasibility: exact existing 512-byte producer suffices;
      no new VDP build or large-reply feature is needed. Extender has qualified
      the temporary receiving composition and reviewed the whole fixture;
      actual installation readbacks passed, but no consumer handoff or test occurred.
- [x] Collate Rally and 6502 affirmative source reviews, source/artifact hashes,
      simplifications, caller requirements and evidence limits.
- [x] Recheck all 37 supplied source/artifact pins and transfer-count arithmetic.
- [x] Dispose of the proposed sweep honestly: initial source draft archived
      uncompiled/unrun; no passing fixture, new timing or Olimex claim.
- [x] Prepare/check the finite synthetic fixture against the actual owner tuple.
- [x] Include matched legacy keycode-carried READ_BYTES (8 bytes per reply) and
      new counted reads of the same immutable source, verifying identical bytes.
      Aggregate complete logical pulls; report tiny cases as unresolved if the
      clock lacks resolution. Include 128/256/1024-byte comparisons. Explain
      that the legacy carrier is packet 81h, not held-key-map packet 88h.
- [x] Reserve the prepared Olimex run in the real FIFO and notify Extender:
      actual request `92f38ff2f224`, no token or target access implied.
- [ ] Obtain actual fresh grant, perform finite short/long send/receive checks,
      resolve correctness failures, preserve results and restore/hand back.
- [ ] After the own hardware pass, guide selected consumer owners through small
      actual in-code trials using measured findings; preserve each owner lane
      and normal bench scheduling. Source reviews alone do not complete this.
      [Conditional trial scope](CONSUMER-TRIALS.md) keeps those checks bounded.
- [ ] Report attributable hardware evidence and limits, then stop without tuning.
