# RX006 — Small consumer trials after the own hardware pass

Brandon's clarified scope requires actual selected-owner code trials, not just
the already affirmative source reviews. UART first completes its own Olimex
integrity and matched legacy/counting benchmark. Only after that pass and review
of its attributable measurements does UART send the exact tested tuple and
findings to the selected owners for finite trials. This document is preparation,
not a prototype handoff or permission to begin a target run now.

The source reviews remain under their original limits. Owners keep all their
current work, paused tasks and bench requests. UART edits no application code;
VDPlet edits no application code. Extender owns any actual EMOS/native firmware
installation, current keyboard/routing admission and exact restoration.

## Rally: retained post-race exporter

Use the retained TIM-002 `timingDumpBuffer` seam identified in Rally's
`docs/consultations/mos-rx006/REVIEW.md`. Prefer an isolated invocation of its
actual export helper over running a race or changing the current game. Its
ordinary single-block source buffer stays frozen across the complete export;
the existing file bytes and legacy management/error callback remain the oracles.
The helper itself does not validate telemetry header/identity; its isolated
harness checks the retained header and exact file readback. These stats contain
no game-generation field:4503 belongs to the pinned originating state.bin,
so generation is provenance, not an invented live stats oracle.
One bounded retained export or representative slice suffices.
Do not require the complete65448B export if a smaller exact helper trial proves
the seam. The owner selects and reports the precise trial scope.

Keep the old path as a matched control where practical, with the same source
bytes and file oracle. Compare complete-operation duration/request count only;
this is a post-race export, so no rendered FPS or physics claim follows.

Rally's substantive `rx006-rally-small-helper-conditional-outline-two` chooses
the pinned584B native-stats.bin, replayed into ordinary single-block buffer50307.
Invoke the actual helper in an isolated harness, keeping256B file chunking:
three counted pulls256/256/72 replace292 READ16 calls. Keep the original helper
untouched as control and use a separate trial copy with persistent guarded256B
receive storage. No race/module setup/STOP/UNLOAD is needed to replay these
retained bytes; do not label them fresh game state. Exact input SHA256:
`648abfc3547bb878767f199710ef7a817f8cfc679f70edf716f30dc427e13732`.
The owner's detailed scope and source pins are in AgonArcade's
`docs/consultations/mos-rx006/CONDITIONAL-PLAN.md` and
`CONDITIONAL-SOURCE-PINS.json`.

UART source review confirms the exact selected producer export retains
operation5 READ16 dispatch and the legacy reply path in video/vdplet_runtime.h
alongside operation8 counted replies. This is source compatibility evidence;
the consumer control still requires actual qualification after our own pass.
Our own legacy8-byte benchmark is distinct from Rally's2-byte READ16 control.

## 6502: retained ESP32-hosted disk export seam

Use the retained `drain_disk`/BRClient source described in
`docs/tasks/IO-003/RX-006-ADOPTION-R01.md`. Do not migrate the current eZ80-local
persistence, which already owns its bytes and needs no UART return. The owner
chooses a small isolated trial of its actual adapter: a40B descriptor and512B
payload are sufficient to exercise the concrete receive seam. Preserve descriptor
identity/length validation and, if persistence is exercised, its unchanged
write/sync/reopen/readback-before-ACK rule. Do not require a game boot or a new
VDP machine implementation to prove the receive helper.

The existing BRClient accepts only operations1..6. A local counted branch must
use the actual26h completion result rather than expect a legacy success packet.
Keep legacy management/error delivery separate. A tagged source ERROR leaves
the receive arm live; do not translate it into an ordinary safe storage retry.

## Shared evidence and stop rule

Each owner records exact tested source/app/firmware identities, the real invoked
helper and input, announced/stored counts, exact bytes/guards or existing file
oracle, positive lifetime retirement and normal cleanup. One outstanding receive,
live destination/code and IRQ service apply. Source release, receive completion
and durable persistence are separate events. No timeout reuses a live arm.

Use the own-suite results to select a modest meaningful transfer size. Aggregate
tiny transfers only when needed for clock resolution; do not create a new large
matrix or chase millisecond gains. A finite actual pass plus the owner's concrete
judgment of simpler code or a useful modest gain completes that consumer's role.
Retain failures, correct attributable integration errors, and avoid blind replay.
Normal fresh FIFO admission is required for any target action.

If the proposed retained seam is no longer practical, obtain the owner's concrete
small alternative before building. Do not quietly substitute another source-only
approval for execution. After own hardware and the selected finite trials pass,
collate the evidence and stop the goal; broad adoption/release remains separate.

## Planning dispatch

The corrected sequence and this bounded outline were sent before execution,
with no build/run/prototype request, in durable mails
`2026-11-08_00-28-21_agon-mos_rx006-conditional-rally-code-trial-eight` and
`2026-11-08_00-28-22_agon-mos_rx006-conditional-6502-code-trial-eight`.
Immediate Pi-native alerts were accepted (`turn/start` for Rally and
`turn/steer` for6502); acceptance does not prove either owner read or agreed.
Rally returned the concrete584B outline above; the later selected-execution
section records subsequent own-pass and consumer preparation results.

## Own pass and selected execution dispatch

Actual132 passes the full own synthetic suite and complete return/witness chain.
The [tested handoff](CONSUMER-HANDOFF.md) now supplies exact artifacts/API and
coarse measured findings. OnNovember8 UART sent substantive task/implementation
requests to Rally11:11:53UTC and6502 11:12:10UTC, then immediate accepted
`turn/start` notifications. [Dispatch records](consumer-dispatch/status.json)
retain exact messages and limits. Earlier planning-only gates are superseded
for these two small isolated helper tasks by Brandon's explicit RX006 direction.
Unrelated paused goals, current games/persistence and normal source/commit gates
remain unchanged. Source preparation may proceed, but physical trials require
clean132 handback, their prepared contracts and normal fresh admission. Both
consumers have now returned source/build preparation below; neither
physical consumer trial has completed in this snapshot.

Rally returned prepared RX6-HLP build17f8fefe/app16392B/595f73c2, requestcaeae97c57d6.
UART read the complete helper/callback/26h adapter/result/batch contract and
independently rehashed all23 prepared and11 immutable source/input/tuple files;
[review](consumer-dispatch/rally-prepared/uart-review.json). No material ABI or
lifetime objection or additional code/build/case requested. Stats have no game-
generation field;4503 is originating state provenance and current notes now
state that explicitly. Extender returned the concrete existing-client execution
procedure and requested Rally pin its own foreground host controller before
its normal turn. Current Mech133, then FSIMf7ba, precede Rally; no consumer
physical result or grant is claimed.

6502 returned RX-001 helper18f3c207/20518B and manifest1586f6fd. UART read
the complete client/counting branch, main/callback/assembly/descriptor decoder
and offline oracle, then independently rehashed all37 pins;
[review](consumer-dispatch/6502-prepared/uart-review.json). No material ABI,
count or lifetime objection and no additional build/case requested. Historical
40B descriptor+512B payload use real BRClient/persist_decode ordering,69 old
pulls versus2 counted pulls, without game/persistence/ACK changes. Legacy ERROR
or timeout leaves counted_live and owned storage/code intact; only positive MOS
terminal state permits local retirement. Fresh consumer-specific host controller,
owner installation/restoration budget binding and normal FIFO remain before its
one physical trial. Proposed1200 whole/350 cleanup must be reconciled with the
proven1800 whole/540 install/600 cleanup before freezing; never extend an active
run or weaken restoration. No reservation, target access or physical result yet.

Rally subsequently returned its concrete foreground host runner: host kit3c0503df,
33 execution/input pins plus8 preparation files independently rehashed exactly,
with nine retained fake-SDK controls matching expected outcomes. UART read its
actual handoff/stage/one-EXEC/120s-wait/four-file/analyzer/EXIT/exception flow;
[review](consumer-dispatch/rally-runner/uart-review.json). No material source
incompatibility or additional code/build/case requested. Extender still binds
actual fresh installation evidence, original actor registration/exit/join and
restoration budget at Rally's normal FIFO turn. Fake controls are not hardware
results; the consumer physical trial remains pending.

6502's final controller kit e0c2516e closes the requested execution preparation.
All37 original,14 host and2 payload files rehash exactly; UART read the actual
controller, live SDK adapter, supervisor, batch and operating contract. Retained
eight fake-IO and two native lifecycle checks pass. Extender selected original
1800/540/420/600 bounds with1020 entry/780 EXEC floors before freeze, superseding
the historical proposal above. [Review](consumer-dispatch/6502-controller/uart-review.json)
finds no material incompatibility and requests no new code/build/case. Normal
request dfcc5d90a252 follows its protected predecessors; physical trial and
restoration remain pending. Neither unbound template nor source qualification
claims actual grant, installed state or device result.

Rally actual135 was entirely UNRUN. Installed observation expired during chat
session recovery before accepted steering delivery; first consumer read was
309s old against the unchanged120s limit. Zero runner launches, staged commands,
EXECs, arms or target I/O; [no-launch record](consumer-dispatch/rally-actual135/ACTUAL135-UNRUN.md).
Original remaining989s was below1020 entry floor, so Extender selected exact
restoration only;6502's next turn stays protected. This is a handoff delivery
failure, not an observed transport/app failure or consumer pass. UART selects
correction of handoff readiness/session preparation before a new normal FIFO
for the same uninvoked helper. Keep120s actual-evidence freshness and original
budgets, never restamp/extend. Wake/confirm the consumer is ready before the
final installed-state observation; owner should account for delivery time and
obtain a genuine new observation only within the original admitted margin. No
app/firmware change or extra case selected.

The old Rally host runner hardcodes requestcaeae, so a new real FIFO ID cannot
pass it. UART selected only the necessary isolated host admission change: required
explicit expected-request binding checked against the actual handoff, with new
runner/kit identity and stopped argv bound to the new reservation. Old runner,
kit and135 evidence remain unchanged. Focused wrong/old request refusal controls
are sufficient; no app/SD-file/firmware/physical-case change. The agreed
PREPARE-DISPATCH/actualREADY sequence precedes the owner's final genuine fresh
observation. Rally may finish this concrete preparation and requeue normally
without another UART signoff unless a material conflict appears.

Rally completed the narrow corrected host without changing app595f73c2 or either
staged file. Host kitf2de4f3e binds new request19e9824cf0fe;13 preparation files
and all host inputs independently rehash exactly. Twelve retained offline
controls passed and671 was released. The [readiness snapshot](consumer-dispatch/rally-delivery-correction/r02/READINESS-R02.md)
retains exact argv and actualREADY/final genuine observation sequence. Normal
new FIFO is submitted; no further UART review gate or target result is implied.
One real helper pass and exact owner handback remain required.

6502 actual136 completes the selected real adapter trial with a physical PASS.
UART independently verifies the retained584B report/exact descriptor+payload,
40/40/512/512 counts, callbacks2, state3 witness, callback0/mode0/route0 and
original0 exit/joined groups; [evidence](consumer-dispatch/6502-actual136/README.md).
The owner judges69 tagged requests replaced by2 counted requests suitable and
simpler for its actual BRClient/persist_decode seam. No further6502 case is
selected. Coarse8 versus0 ticks do not resolve a speed ratio or CPU/FPS benefit;
20.85s includes host staging and retrieval. No game/persistence/ACK/new exporter
coverage. Same136 exact restoration/fullhandback/release remains pending with
Extender. Rally135 is separately restored/released12:14:18UTC but entirely UNRUN;
its corrected19e9824cf0fe physical helper trial remains required before goal
closure. UART has no live target actor or checkout.

Actual136 restoration closure subsequently received: native85f9 FIRST and full
readback, originala25f/full131072B readback, fresh full CLI/files/input/idle/free
ports handback, all installer/consumer/cleanup actors joined, clean normal
release12:30:43.327754UTC. UART independently rehashed the complete returned
ROM to originala25f and checked release/actor receipts, retained with the
[consumer evidence](consumer-dispatch/6502-actual136/README.md).6502's selected
slice is complete; no additional consumer test is selected. ProtectedMech9267
remains next through normal admission; Rally19e physical trial still outstanding.
