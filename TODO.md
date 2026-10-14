# MOS TODO

Executive summary: the goal is to free the Agon's CPU for useful work while MOS
sends data to the VDP. An earlier Console8 experiment completed about 31% more
other work during regularly scheduled sending, without increasing bulk speed
over our experimental sender that checks permission before every byte. The
app-controlled batching switch is now implemented and passes software tests.

It remains experimental. A fault in the VDP firmware used by the emulator can
stop reception permanently; later passing tests do not resolve it. We still
need complete checks of the benchmark's received data, menu integration, tests
of the new firmware on Console8 and explicit release approval. The menu's
keyboard delay also remains unexplained. Stock MOS remains the approved baseline.
This is the sole unfinished-work checklist.

Subtask IDs are immutable: a short namespace followed by a hyphen and three
zero-padded digits, then a checkbox. Reordering never renumbers an item.
Record completed/disposed IDs and evidence in the development log, remove them
here, and never reuse an identifier.

## Deployment policy

The Author lifted the SD write hold and authorized staging the suite. Multiple
cards may be attached to Oryx: rediscover the unique UUID 8658-1C23 and match
the prior UART manifest/fixture immediately before deployment. Keep the active
/test/mos-uart0 path; preserve history only in project workspace.

## Provenance

TX-016/TX-017 fixture and capture-preparation work completed on 2026-10-13.
The Author passed human emulator review; subsequent Console8 physical software
and empirical reserve campaigns pass. TX-006 qualification closeout is complete.

TX-014/TX-015 were accepted for commit on 2026-10-13 after the passing physical
benchmark and explicit commit/push instruction; emulator-review history remains
recorded accurately in the development log.


C-001/C-002, TX-001 and TX-005 were resolved/delivered on 2026-10-13; see
[the development log](docs/devlog-2026-10-13.md). Human acceptance TX-010 passed on 2026-10-13.
Earlier TX-002/TX-003/TX-004 and TX-007/TX-008/TX-009 remain completed evidence.
Console8 preparation TX-011 and human fixture acceptance TX-012 passed on 2026-10-13.
Manual Console8 SD deployment TX-013 completed on 2026-10-13.
Original ASY-001 identifiers remain valid provenance references in
[the MOS-owned task](docs/tasks/ASY-001.md).

## Opt-in CTS batching (contract, audit and initial prototypes delivered)

See [the design goal and acceptance plan](docs/uart0-cts-batching.md).
Contract: [proposed ABI](docs/uart0-cts-batching-api.md).
Budget and source review: [hardware audit](docs/uart0-cts-batching-audit.md).
BT-001/BT-002 are complete. TX-006 closeout records empirical reserve and
defers electrical/worst-case qualification; stock restoration is confirmed.

BT-003 [ ] Implement isolated grouped-scalar and bounded OTIRX candidates,
retaining stock legacy behavior, an experimental per-byte session fallback
and the 16-write service cap. Complete the versioned session API and supported
settings, including ownership, CTS wakeups, IRQ interaction and exit cleanup. Verify native block-I/O
register/count semantics, source-span bounds and per-chunk descriptor accounting;
preserve CTS admission, wakeups and lifetime/ordering fences. Experimental
ABI1.2 setter/getter and bounded OTIRX now exist off-device. Scalar and OTIRX
builds pass 23,640 scripted scenarios across sizes 1/2/4/8/16, plus fault controls
and linked-ROM checks. Native receiver evidence is in experiments/uart0-batching;
human review, the receiver-race gate and supported-combination selection remain.

BT-004 [ ] Compare stock-style blocking, experimental per-byte async, grouped-scalar
and OTIRX throughput and recovered
CPU/useful work, including
service cost and latency; establish whether batching offers a worthwhile gain.
Initial paced model result:73.75% fewer UART service cycles; unpaced throughput
does not improve. Console8 R0005 shows 31.3% more paced useful work over
experimental per-byte async; this is not an exact physical cycle count.
See experiments/uart0-ab/RESULTS.md.

BT-005 [ ] Extend menu/reporting and both-engine qualification for batching,
receiver integrity, negative controls, default regression and session cleanup.
Native CRC and acknowledged full-duplex children now use the public ABI and
fixed report-name slots. Sequential menu integration remains pending; combined
JIT testing reproduced the known receiver race despite later passing runs.

BT-006 [ ] Qualify manually on Console8 with stock threshold and diagnostic
controls; repeat near any failure boundary without Olimex probing or wiring.

BT-007 [ ] Select conservative supported options from evidence, document
compatibility/limits, and prepare a repeatable release candidate for explicit
Author approval before promotion/release. Require supported API, full receiver
integrity, legacy/session regressions and repeatable performance evidence;
defer shipping if gains do not justify the tradeoff.

## Next tranche: A/B streaming and Jukebox-shaped workload

See [the tranche specification](docs/uart0-ab-tranche.md). These identify
benchmark deliverables; BT-003..BT-007 retain the driver/qualification work and
are dependencies, not a second implementation of the same tasks.

AB-006 [ ] Close the traced intermittent native A/B stall: implement the VDP
receiver diagnostic/correction in this project's owned copies and coordinate
emulator regression with Flexe, then
repeat both-engine qualification and human review before relying on emulator
passes for release qualification. See docs/uart0-ab-tranche.md for evidence and completion gate.
Diagnosis is traced in the emulator: VDP ISR disables RX after reader recovery clears the flag;
diagnostic RX re-enable resumes TX. See docs/uart0-ab-stall.md. Receiver-owner
correction/regression and renewed qualification remain. The Author separately
authorized an exploratory Console8 comparison on2026-10-14; it does not clear
the emulator fault or production qualification gate.
The Author now requires hardware reproduction before a correction and hardware
regression afterward; emulator-only evidence cannot establish physical failure
or repair. Earlier request sent through the emulator owner's `golem` mailbox route:
`2026-10-14_03-28-03_agon-mos_uart0-recovery-hardware-one`.
The owner's task log acknowledges the request. Unchanged-VDP Console8 short
and extended campaigns R0006/R0007 now pass all30 cases with245760 final-buffer
bytes checked and zero case RX errors. HW-001 preparation/return is complete;
the emulator race remains unresolved and no physical race was reproduced.
The Author corrected ownership: MOS owns VDP firmware work, Flexe owns the
emulator. HW-002 now owns the controlled physical diagnostic preparation;
do not treat these passes as proof of a repair. See
experiments/uart0-recovery/physical-results.json. No bench lease is implied.

HW-002 [ ] Build and qualify the controlled Console8 VDP receive-recovery
diagnostic, MOS workload and numbered-suite integration. Audit/pin the actual
ESP32 driver, observe the real ISR/reader ordering, and use bounded diagnostic
scheduling hooks to exercise that ordering on hardware. Include a no-trigger
control, independently checked failure-state evidence, bounded recovery with
byte/CRC checks, versioned sequential reports, stock restoration and unchanged
MOS. Qualify compiled images and negative controls off-device, package at the
stable SD path, then analyze the Author's manual return. Distinguish natural
stock failure, diagnostic-induced physical ordering and emulator-only behavior.
See [the diagnostic plan](docs/uart0-recovery-diagnostic.md). A firmware repair
and its matched physical regression remain AB-006 work after reproduction.

AB-001 [ ] Build repeated sustained-stream comparisons: stock-style blocking, experimental per-byte async,
grouped scalar and bounded OTIRX, using identical valid VDP workloads. Initial
model and30-phase native fixtures implemented. Human review failed with a
experimental per-byte async bulk stall; its cause is now traced under AB-006.
The exploratory hardware run is complete; supported-driver comparisons and
release qualification remain pending.

AB-002 [ ] Measure fixed-payload wire-drain time and concurrent useful CPU work,
service cost and latency; alternate case order and report repeat variation.
Initial cycle campaign and native raw observations recorded in uart0-ab;
calibrated hardware rates and optimized refill latency remain pending.

AB-003 [ ] Verify byte integrity with diagnostic VDP, and measure performance
separately with stock VDP using matched commands and completion semantics.
New ABI1.2 fixtures verify complete 4096-byte raw payloads and 8192-byte stock
command buffers across all five batch sizes; no physical claim is made.
Extend these checks to the matched 16KiB A/B command workload.
Verify every bulk payload byte via count/CRC or equivalent receiver checks,
not only reply samples. Include sustained full-duplex traffic, descriptor/queue
boundaries and repeated CTS stop/resume, coordinated with BT-005/BT-006.

AB-004 [ ] Build the source-derived Jukebox-shaped fixture: 735-byte PCM feeds
at 60 Hz, two one-second VDP samples, short due-work ISR and foreground stable
packet production. Compare scalar/OTIRX with identical adapted scheduling; test
RAM feeds before SD jitter, bounded graphics, backlog and sample readiness.
Source inspection is complete; see docs/uart0-jukebox-skins-audit.md.

AB-005 [ ] Package the comparisons and integrity checks into the existing menu;
qualify headlessly before one manual Console8 hardware campaign.
Option8 and sequential A/X reports are staged for the Author-authorized
exploratory hardware comparison, retaining earlier tests/reports. Final menu
integration passed60 JIT phases across repeated runs and30 interpreter phases;
Console8 R0005 passes all30 phases; useful paced work rises31.3% with OTIRX
versus experimental per-byte async, with equal bulk ticks. Full receiver integrity and broader
qualification remain. See experiments/uart0-ab/physical-results.json.

UI-001 [ ] Diagnose the Author-reported Console8 suite menu keyboard delay.
getch uses normal blocking MOS getkey; no deliberate polling delay is present.
Compare against the MOS prompt and a minimal getkey fixture before changing
input handling. The R0005 A/B run completed; keyboard delay remains untraced.

AB-007 [ ] Scope and coordinate actual AgonJukebox skins integration after the
controlled fixtures establish benefit and integrity. Arrange explicit app-owner
authorization before changing that project. Use a short scheduling ISR, stable
foreground packet production and MOS as sole UART owner. Compare stock app
behavior with adapted scalar/OTIRX variants using matched scheduling; measure
audio continuity, feed backlog and graphics/CPU headroom. Keep scheduling gains
separate from transport gains; synthetic AB-004 alone does not close this task.
