# MOS TODO

RX-006 [ ] **ACTIVE: FINISH THE REQUESTED OLIMEX SIZE SWEEP.** Brandon corrected
the premature source-review-only closure. Final matched app0208015a/18376B and
host runner are checked, exact temporary EMOS171c/VDP7d09 bound. Actual bench
FIFO92f38ff2f224/actual123 closed UNRUN after bootstrap display-status timeout;
exact firmware install/readbacks succeeded. Extender restored exact originals,
verified handback and released. Corrected bootstrap8pins/11hostcontrols reviewed;
new actual FIFOccb5dab78a89 queued, request-local owner closure/fresh grant needed.
Old token invalid, no test run or timing result.
Rally and 6502 explicitly accept source-grounded usefulness: retained exports
need 129 reads instead of 32,724, and two instead of 69, respectively. VDPlet
confirms existing 512B producer suffices. Prior C8 R0067 supplies physical
integrity evidence; 37 owner pins and count arithmetic rechecked. Complete the
finite short/long hardware checks and normal restoration; no game ports,
boot-script edits or performance optimization. Benchmark identical legacy
keycode-carrier/new bulk pulls (especially128/256/1024B), then coordinate small
actual consumer-code trials after the own-suite pass; source review is not enough.
[Result and limits](docs/tasks/RX-006/RESULT.md),
[task and exact human scope](docs/tasks/RX-006/README.md).

RX-005 [ ] **FIRST CONSOLE8 HARDWARE SUITE PASS; REVIEW BEFORE CONSUMER PILOT.**
R0067/build9c72616d7f4a4ef7 passes every synthetic case0..512B, guards, discards,
BUSY/invalid/source-error/rearm and real keys. Callbacks30/keys1:1/regfail0/ifffail0,
foreground progress3477. Source-derived32frames/2397payloadB include529B deliberate
discard and1868 exact copied-byte comparisons. Exact app/staged firmwares retained;
no hardware UART error-counter/throughput/CPU claim. Reports archived/verified on
Pi/Oryx; next68. Card and current autoexec read only. No consumer prototype or game
change; proposed Rally export pilot awaits Brandon review.
[Hardware result](docs/tasks/RX-005/hardware-r01/RESULT.md),
[review and patch](docs/tasks/RX-005/REVIEW.md).

U1-001 [ ] Develop the delegated application-space UART1 async/OTIRX driver,
targeting vanilla MOS by Brandon's clarified direction. Independent core and
OTIRX core plus standalone vanilla adapter pass host sanitizer/byte controls and
native linking. Console8 AT/GMR R0002 and Jukebox's receive-only binary sessions
R0003/R0004 pass; sustained audio/performance remains separate. Jukebox's230400
transition R0005 failed before TCP and has no established baud/driver diagnosis.
Extender owns its EMOS adaptation; its first consumer trial76 reported RX overrun
and was rolled back cleanly. [Task](docs/tasks/U1-001/README.md).

U1-G01 [ ] Support MechAgon GOAL-001's delegated async reliability and CPU
attribution work. Verify original human scope, return a bounded generic IRQ/
timer contract, coordinate concrete RX-service exclusion with Extender, and fix
generic code only when evidence requires it. Extender owns EMOS/P4/SDK and bench;
MechAgon owns profiling/integration. Preserve protected Wolf queue and independent
vanilla/Jukebox scope. [Owner support](docs/tasks/U1-001/goal001-owner-support.md).
Timing contract and standalone +52ROM/+1BSS bounded UART0 CTS derivative are
delivered; Extender owns pending-state guarded splice and physical qualification.
No current lease, installed change or confirmed trial76 fix is claimed.
Selected next app support is the [reusable wait leaf](docs/tasks/U1-001/wait-leaf-r01-plan.md)
under the concrete root delegation; app glue/SDK notify remain with their owners.
The163-byte app leaf/9-byte state passes native link, source/listing controls
and abstract event models; no executed CPU/IRQ/hardware acceptance is claimed.

## Eirene upstream async RFC qualification

RFC-001 [ ] Continue the reviewed syscall 25h evaluation after the completed
first transfer-validation tranche: both Flexe engines and wrong-ROM refusal
passed, with 269508 payload bytes and 36 callbacks verified. Next planned work is
finite normal CTS/input/timer latency, then performance and application cohorts.
The new RC3 latency fixture on `codex/rc3-latency-performance` completed both
model engines: JIT passes; interpreter reports16 UART RX overruns despite
byte/return checks passing. Actual hardware applicability is OPEN; see
[the finding](../eirene-mos/docs/tasks/RFC-001/latency-findings.md). A private
Console8 package is prepared in project space, not deployed. CPU/throughput
caller preparation is complete: full/short binaries compiled and a private
source/binary package was hash-verified under the overnight continuation.
Compiler236 is released; no performance target run or deployment occurred,
and responsiveness disposition remains OPEN. See
[preparation](../eirene-mos/docs/tasks/RFC-001/performance-preparation.md).
Jukebox continues its separately authorized migration task. Detailed plan:
[RFC-001](../eirene-mos/docs/tasks/RFC-001/README.md). Later performance/app
tranches, hardware deployment and release publication remain separate.

The separate startup fix was published as upstream Eirene PR #3; completion is
recorded in [IRQ-001](../eirene-mos/docs/tasks/IRQ-001/upstream-publication.json).
Startup-fixed RC1.1/RC2.1 and RFC-based RC3 are published; Jukebox was directed
to pin RC3. Completion/evidence: [RC-003](../eirene-mos/docs/tasks/RC-003/qualification.md).
The RC3 ABI is25h; RC1.1/RC2.1 retain42h/43h and are separate candidates.

## Recovery complete; remaining cleanup

Stock MOS3.0.2 recovery passed target CRC checks and the Author confirmed MOS
boots on2026-10-31. N-009 completed; evidence and disposition in today's devlog.
SDdiagnostics recovered/hashverified toPi/Oryx,257files includingR0030 and
updatedjournal; card unchanged andmounted. WROOM is CHECKEDr01, not identityv3.
No new experimental MOS deployment or performance test is authorized here.

N-010 [ ] Restore and verify the temporarily repurposed P4's original firmware
when that identified board is attached and available under its bench protocol.
Original16MiB backup remains preserved; do not interrupt another owner or infer
availability. This deferred cleanup is distinct from completed Console8 repair.

Reports: [MOS recovery](docs/c8-stock-mos-recovery-2026-10-31.md),
[SD evidence](docs/c8-sd-recovery-2026-10-31.md).

TRY-003 [ ] Test shorter GREEN/BLUE leads and improved nearby ground returns.
TRY-004 [ ] Inspect analog waveforms with an oscilloscope, if available.
TRY-006 [ ] Investigate safe temporary reuse of Console8 onboard ESP32 mouse pins.

Hardware hold: the first native MOS failed to boot on Console8. N-007 proved
and corrected the startup baud calculation off-device; its completed evidence
is in experiments/uart0-native/BOOT-FAILURE.md and the development log.
The failed image is withdrawn, and the corrected image has not been staged
or physically accepted. The Author has now authorized this agent's scoped
Oryx P4/ZDI identification under N-008 and scoped MOS repair under N-009.
Recovery is not established by a completed blind programming sequence.

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

N-008 identity checks passed; completion and evidence are in
docs/devlog-2026-10-28.md and docs/tasks/N-008.md. P4 programmer remains installed
until MOS repair is finished. N-009 completed the target repair on2026-10-31; N-010 owns deferred P4 cleanup.


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

## Stock-startup ZDS II MOS implementation

Toolchain decision,2026-10-31: deliver the upstream MOS modification with
ZDS II under Wine on Oryx. Original menu/test software may use AgonDev. The
native MOS port below is retained as historical/reference work, not the selected
firmware delivery path. Preserve upstream source/build conventions for review.

The Author's2026-10-31 requirement strengthens opt-in to preserve a proven stock
boot and UART path until explicit activation. BO-001/BO-002 are implemented and
software-qualified in the ZDS II fork; completed dispositions are in today's
development log. Candidate CRC0C5886FC and the rewritten menu/fixture are described
in experiments/uart0-startup-safe/README.md. Actual-ROM checks, both Flexe engines,
wrong-image rejection and quick-key/updater-entry controls pass. No board or SD
operation occurred. The dedicated Oryx review profile is staged stopped; reserve
through the shared FIFO for any reuse. BO-003 off-device/functional human review
now passes R0001:32768comparedbytes,128orderedreplies, allfourtests and live CLI
DIR return; no drops/overruns/frontend faults. Evidence is in the new fixture's
README and today's development log. The retained capture proves one boot, not
a separately recorded relaunch; physical reset recovery remains BO-004.
Review checkout is released and Rally was notified. The Author approved the
completed-work commit/push checkpoint on2026-11-01 before BO-004 implementation.
These gates precede N-006.

BO-004 [x] Deliberate-reset fixture developed, qualified and passed on Console8.
R0037 continuous sending and R0038 controlled mid-packet stop passed whole-board
power-cycle recovery. Valid records, operator confirmations, original handler,
fresh disabled state and stock-path VDP reply verified. Evidence:
build/uart0-reset/card-return001/analysis.json. No MOS/VDP code added.
CPU-only reset recovery is outside scope, not an automatic next task. Author
requests restraint on recovery machinery, especially given EMOS flash limits.

N-001..N-004 are delivered: pinned dependencies, native stock reproduction,
maintained OTIRX implementation, linked contracts and actual-ROM/both-engine
qualification. Evidence and disposed identifiers are in the2026-10-16 log and
experiments/uart0-native. This is software delivery, not firmware/release approval.

N-006 [ ] After recovery and Author authorization, prepare and qualify a
ZDS II MOS replacement package/menu after BO-001..BO-004. The arithmetic-only corrected
MOS ROM CRC4E326ABC/API1.2 is an off-device reference, not a package satisfying
the new stock-startup requirement. Pin the revised image identity, obtain fresh
human review and perform a minimal boot check before the larger campaign.
The former native CRC5B36B5B1 is withdrawn and must never be accepted again.
The first returned hardware campaign is now inspected: staged assets match and
R0035/R0036 each pass the full suite including batch16 byte verification and
ordered replies. Remaining BO-004 recovery acceptance still gates final closeout.
The supplied repaired VDP candidate is selected. Manual flashing/execution
remain Author actions; the pair stays installed by Author choice. No electrical
CTS-margin or release claim follows.

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

## Application convenience and completion notification

BD-001 [x] Review the [bouncing-balls demo task](docs/tasks/BD-001/README.md),
then verify the public-command flip/confirmation path and timer ownership.
Author approved execution2026-11-02 after the plan checkpoint7218650.
Source/command inspection confirms VDP-side swap waiting; ordered GP replies
confirmed every completed frame in the initial finite emulator sweeps.
PRT1/2 leave timer0 alone; only initially disabled timers are borrowed.

BD-002 [x] Implement the original C/AgonDev scene, deterministic wall/all-pairs
physics, local RGBA2222 renderer and responsive controls/HUD under BD-001.

BD-003 [x] Implement bitmap-upload/VDP-circle output crossed with standard,
async foreground-event and async direct-callback transport, preserving matched
CPU work, source ownership and non-blocking flip.

BD-004 [x] Implement raw-PRT stage metrics/equivalent FPS, separate wall-time
FPS and verified presentation confirmation; distinguish overlap, drain, source
release and measurement overhead as specified by BD-001.

BD-005 [x] Qualify deterministic output, timing/accounting and interaction;
prepare a finite matched sweep spanning transmit- and compute-bound workloads.
Completed original C build b57893f6a9450c82:192matched frames/24cases,
1,902,240UART scene bytes independently compared,20ms real SDL taps through
compiled VDP/MOS passed, normal return and PRT ratio checked. Evidence:
docs/tasks/BD-001/evidence.json. Shared lease released; no hardware claim.

BD-006 [x] Package the demo, source, identified firmware and concise operating
instructions for explicit review/deployment; archive returned physical results
and interpret measured gains/limits without implying upstream release approval.
Workspace appliance/ZIP are in build/uart0-balls/run007/. Authorized SD
deployment completed to /test/mos-uart0/balls; old root files moved to callback.
Console8 R0040 returned:511frames,24balls/bitmap, all transports and both
collision settings; analysis archived in docs/tasks/BD-001/hardware-R0040.md.
R0041 adds both output strategies/all transports with24..76balls:1,530frames,
1,528retained records verified. Results: docs/tasks/BD-001/hardware-R0041.md.
The automatic16/64-ball matrix was not run on hardware; interactive demo and
application-trial readiness are established within the recorded scope.

BD-007 [x] Replace disruptive twelve-frame interactive blocks with continuous,
user-controlled scenarios, rolling eight-frame rates and bounded recent-frame
logging only at option changes/quit. Preserve ball state across option/load
changes; R explicitly restarts. Build790222e035a1fed1 in run008 compiles on Oryx. Host controller test
passes187frames/9user-directed scenarios, preserving state and exercising
raw-ring rollover with no periodic SD writes. ASan/UBSan and independent host
replay pass. End-to-end normal interaction has now passed on Console8 in R0041; the
redundant queued emulator requestdb18783ba736 was cancelled. Author explicitly requested deployment before emulator verification; revised
binary deployed to /test/mos-uart0/balls, reports/counter41 and firmware
preserved. Receipt: build/uart0-balls/card-deploy002/deployment.json.

KI-001 [ ] Design opt-in keyboard event latching/queueing in MOS's existing
receive handler that can coexist with async UART output. Preserve stock keyboard
callbacks/default timing, account for EMOS space, and verify rapid queued taps.
Author recommendation2026-11-02; demo key-state/event-counter sampling is an
interim last-event recovery mechanism, not a guarantee to retain every event.

UX-001 [x] Develop the completion-callback and opt-in queued-RST18 experiment.
Implemented tentative ABI1.3, borrowed convenience writes, source-consumed
callbacks/events, fixed copied buffers/backpressure and scoped cleanup. Protected
stock startup remains unchanged. Linked-ROM and real-VDP application qualification
recorded in experiments/uart0-completion/README.md; original API/RST18 regressions
pass. Hardware application performance/EMOS selection are explicitly UX-002,
not claimed complete by off-device results. RX injection deferred for lack of
concrete need. Specification: docs/uart0-completion-interface.md.

UX-002 [ ] Qualify the completed UX-001 experiment on physical Console8.
Physical fixture portion PASSED on2026-11-02: R0039/build71715a9860ae7f56,
all four cases and32768receiver bytes, notification counts1/1/32/0. Exact
separately branded ABI1.3 deployment assets verified; returned archive and
reproducible analysis in build/uart0-completion/card-return001. Ordinary startup
and explicit opt-in retained; this is correctness acceptance, not release or
performance approval. Remaining application/size selection keeps this task open.
Compare callback,
foreground event and copied-RST18 convenience against the retained borrowed
baseline in matched paced/bulk application work before choosing an interface
for distribution. Review EMOS fit independently; no heap, new RX injection API
or shared Extender binary ABI is implied.
