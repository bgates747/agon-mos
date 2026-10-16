# MOS TODO

Executive summary: the goal is to free the Agon's CPU for useful work while MOS
sends data to the VDP. An earlier Console8 experiment completed about 31% more
other work during regularly scheduled sending, without increasing bulk speed
over our experimental sender that checks permission before every byte. The
app-controlled batching switch is now implemented and passes software tests.

It remains experimental. Console8 R0010 captured a receiver synchronization
fault under forced timing. Its lock correction is now implemented in private
VDP builds and passes paired and compatibility checks in both emulator engines.
Console8 R0012/R0014 now confirm the repair under matched forced timing;
R0017 passes candidate compatibility, and stock VDP restoration is confirmed.
Complete benchmark receiver checks, batching menu integration, new MOS
qualification and release approval
remain. The keypress repair is confirmed; stock MOS remains the approved baseline.
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
The Author requested concise card text and full project-side history.
Keep readme.txt/firmware.txt short; archive a complete verified snapshot before
compacting runs.log. Preserve run numbering and individual evidence. The latest
post-compaction baseline is build/uart0-branding/deployed-card-state-20261016
(through0029; next run0030).

BR-001 [ ] Confirm the experimental banner/CRC44BC5C07/API1.1 if the Author
installs the optional branded MOS. Firmware/menu are staged in the SAME Console8
directory after its2026-10-16 return. The original sender's A/B and compatibility
campaigns pass; no full rerun is needed for branding. Leave the other-project
VDP unchanged. Evidence: experiments/uart0-branding.

## Provenance

UI-001 was accepted on physical Console8 after the R0010 session; the Author
confirms that the queued-input repair fixes submenu keypresses. Its immutable
ID and evidence are recorded in docs/devlog-2026-10-14.md.

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

EX-001 [ ] Audit Agon Extender's unattended test lifecycle, installed EMOS
flash/RAM headroom and native ZDS II build compatibility. Record the explicit
Legacy-mode integration and bench/recovery boundaries in
docs/uart0-extender-tranche.md; use the installed source baseline rather than
assuming the newest EMOS branch is on hardware.
Assessment delivered for review: saved installed headroom2450bytes; native ZDS
size build overflows3442bytes, sender module2497bytes. No integration or hardware
test yet. The Author requests stop after this assessment; see budget-results.json.

EX-002 [ ] Implement the generic UART sender in an isolated EMOS-owned
candidate, preserving Legacy routing, Extender input, SD services and return
cleanup within the128KiB ROM limit. Build with ZDS II/Wine on Oryx and verify
actual link placement, baud divisor and relevant owner checks. A RAM-only
prototype does not satisfy this integration requirement.
Prerequisite: preserve EMOS functionality while resolving the native baseline's
ROM overflow. Existing diagnostic MOSlet extraction is a research lead, with
unmeasured backport savings; no toolchain exception or feature removal approved.

EX-003 [ ] Adapt the relevant existing Console8 tests for explicit unattended
Pi coordination on Extender/Olimex: phased RX, API/legacy/callback/masked-IFF/
exit/ADL0, byte/CRC integrity, pause/full-duplex and matched receiver repair.
Preserve individual invocation, modes/routes, sequential reports and ordinary
startup. Preserve/verify incoming firmware and recovery before installation;
collect and archive evidence, then restore an actual responsive CLI.

EX-004 [ ] Run the next controlled A/B tranche on the integrated EMOS Legacy
candidate, including original30-phase replay, full matched payload verification,
paced useful work and unpaced wire-drain time. Keep these outcomes separate from
Console8 evidence and exact CPU-cycle/CTS timing claims. AB/BT tasks retain
their broader final MOS, application and release gates.

See [the tranche specification](docs/uart0-ab-tranche.md). These identify
benchmark deliverables; BT-003..BT-007 retain the driver/qualification work and
are dependencies, not a second implementation of the same tasks.

AB-006 [ ] Finish emulator regression of the original intermittent native A/B workload
against the repaired receiver, coordinate the corresponding emulator regression
with Flexe, and obtain renewed both-engine/human qualification before release
claims. The receiver defect is now reproduced and repaired on physical Console8:
R0012 captures the baseline stuck state/rescue, R0014 verifies both4096-byte
payloads without rescue, and R0017 passes the normal candidate's five-phase
compatibility campaign. Stock VDP restoration is operator-confirmed after R0018.
RX-001..RX-003 and HW-002 are complete; their evidence/disposition is recorded
in docs/devlog-2026-10-15.md and experiments/uart0-repair/physical-results.json.
Supported batching API/full receiver integrity and performance/release
qualification remain separate unfinished work.
The original workload's Console8 replay now passes R0026/R0027/R0028 (90 phases),
followed by candidate compatibility PASS R0029. Remaining AB-006 scope includes
emulator regression/coordination and renewed human qualification; do not repeat
the completed physical replay for branding alone.
The Author subsequently installed another project's VDP; leave it unchanged.
The branded MOS is optional; completed-readme.txt records the completed campaign.
MOS owns VDP firmware; Flexe owns emulator models/regressions. No natural
stock-image failure frequency, new CPU-cycle measurements or release approval
is established. Existing failed traces and raw returns remain archived.

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

AB-007 [ ] Scope and coordinate actual AgonJukebox skins integration after the
controlled fixtures establish benefit and integrity. Arrange explicit app-owner
authorization before changing that project. Use a short scheduling ISR, stable
foreground packet production and MOS as sole UART owner. Compare stock app
behavior with adapted scalar/OTIRX variants using matched scheduling; measure
audio continuity, feed backlog and graphics/CPU headroom. Keep scheduling gains
separate from transport gains; synthetic AB-004 alone does not close this task.
