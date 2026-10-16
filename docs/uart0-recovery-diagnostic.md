# Controlled Console8 receiver diagnostic

2026-10-15 follow-through: matched hardware baseline R0012 reproduces the fault;
repaired R0014 recovers both4096-byte payloads without rescue or receive errors.
Candidate R0017 passes all five compatibility phases. The Author confirms the
normal stock VDP2.16.0 reboot banner after R0018 restoration. HW-002 and
RX-001..RX-003 are complete; see uart0-receiver-sync-fix.md and
experiments/uart0-repair/physical-results.json. The following R0010 preparation
and earlier status descriptions are historical; stock restoration is closed.

Physical result: R0010 passes. The no-trigger case recovers normally; the
forced-window case captures the actual core0 reader recovery followed by core1
ISR RX-disable, with RX interrupts masked, full flag false, software buffers
empty and66 FIFO bytes pending. Diagnostic rescue restores RX; both4096-byte
payloads match CRC87897582 with no receive errors. The final report and progress
checkpoint agree, and detail/running journals record physical_target=1.
This confirms the diagnostic-induced mechanism on Console8, not its natural
stock-image frequency and not a verified synchronization repair. See
experiments/uart0-race/physical-results.json. The Author confirms the keyboard
repair works and the diagnostic VDP remains installed; stock restoration is
still pending. AB-006 now owns the receiver correction and matched hardware
regression. Do not move a diagnostic wait under the UART lock while fixing
flag publication/masking order.

Previous failed return and fixture repair:
Latest return: the Author's physical R0009 run hung in its first case. Its
progress checkpoint has stage1, two cases and zero completed records. The
checkpoint is reused before ARM and after publication/before drain, so it
does not distinguish those locations. The diagnostic handshake succeeded, but
there is no completed receiver-state record from which to infer a race.
Raw return is preserved in build/uart0-race/hardware-return-001. Investigation
reproduces the fixture's second SAVE failing with CREATE_NEW under actual MOS
FatFS. The corrected fixture uses overwrite/write/close and excludes all
disk/screen I/O during ARM-to-DONE, because FAT timestamps emit VDP RTC bytes.
Both-engine real-FatFS native and full FAT-menu checks pass; negative storage,
payload and handshake controls pass. See uart0-checkpoint-failure.md.
The corrected receiver test and UI-001 repair are staged together for one
substantive8/4 retry. No new firmware is needed if the recovery diagnostic VDP
is still installed. Stock restoration confirmation remains outstanding.

The real Console8 passed our short and extended traffic tests. We still need
to know whether the receiving firmware can enter the stuck state captured in
Flexe. This test will observe the receiver on the physical ESP32 and deliberately
widen the suspected timing window. It should give us evidence about the actual
ordering, rather than ask for more identical stress runs. A forced diagnostic
failure will not be reported as a naturally occurring stock-firmware failure.

## Ownership and prerequisites

The Author clarified that this MOS agent owns the VDP firmware work as well as
the MOS workload, menu, reporting and packaging. Flexe owns emulator execution,
models and regression tests. Earlier documents assigning receiver firmware to
Flexe are superseded by this instruction; immutable mail remains historical.
No other project's working source or shared runtime is to be modified.

HW-002 in the sole TODO owns preparation and manual-return analysis. Existing
HW-001 baseline is R0006/R0007:30 cases,245760 final-buffer bytes, no case RX
errors or stalls. Retain installed experimental MOS API1.1/CRC239097B7 to avoid
introducing batching changes. Export pinned stock VDP2.16.0 into this project's
build workspace, with pinned Arduino/IDF libraries and preserved licenses.
Audit the exact compiled driver's full-flag, RX-mask and lock ordering first;
do not assume source similarity proves the physical implementation matches the
emulator trace. Record driver source hashes and linked symbol/disassembly evidence.

## Experiment and evidence

Use real UART driver ISR and reader paths. Record full-condition publication,
reader recovery and RX-mask changes with core identity and bounded event
storage. A trigger may briefly delay the ISR between publishing full and taking
the UART lock, while a reader on the other core performs normal recovery.
Preserve the ordering being tested, UART ownership, flow control and payload
memory lifetime. All timing hooks must be opt-in, bounded and inactive at boot;
the original compiled driver ordering must remain identifiable.

First run a no-trigger control with the same traffic and instrumentation. Then
run the widened-window case. Require proof of the intended competing-core
ordering and inspect FIFO occupancy, enabled/raw interrupt causes, software
buffer/stash state and recovery flag. Directly masking RX and calling that a
race reproduction is insufficient. An unobserved or unattained interleaving is
INCONCLUSIVE, not PASS. Preserve the pre-recovery evidence before any intervention.

Use a bounded diagnostic escape to restore receive wakeups only after capture,
so the host can drain safely and retrieve the report without throwing away
borrowed sources. This intervention is not a production fix. Count/check all
raw diagnostic payload bytes and CRC after drain, check RX error epochs, and
separate capture validity, expected-trigger outcome and post-recovery integrity.
Include corrupt-payload, missing-reply and invalid-evidence controls. Report
timeouts with checkpoints; a memory-retaining reset hold remains valid when
safe return cannot be established.

## Integration and qualification

Keep the numbered suite at /test/mos-uart0/test.bin, sequential report allocation
and runs.log, earlier tests and firmware/backup operations. Give the diagnostic
an explicit menu choice, clear its screen, show case/phase breadcrumbs, state
duration expectations and save progress before operations that can stall.
Never include diagnostic firmware flashing in run-all. Refuse the diagnostic
unless its version/identity handshake succeeds; stock VDP must not be mistaken
for an instrumented receiver. Supply diagnostic and official stock restoration
files, identity metadata, notices and hardware-readable readme.txt together.

Build native code with ZDS II/Wine on Oryx; the C menu may use AgonDev. Build VDP
on Oryx using the pinned ESP32 toolchain. Use an isolated frozen emulator profile
for protocol/integrity/reporting qualification, keeping emulator timing/model
limitations explicit. Exercise the compiled firmware path where supported and
retain any failures. A host test or scheduling model cannot substitute for
physical ESP32 evidence. Do not declare hardware readiness if the actual
instrumented driver has not linked or protocol/reporting checks are incomplete.

Package and verify off-device first. Rediscover uniquely mounted Console8 card
UUID8658-1C23 immediately before staging, recognize its owned manifest, archive
prior contents off-card and preserve reports/root MOS. The Author performs all
physical flashing, reset and execution. No probes, Olimex wiring or unattended
bench actions are involved.

## Interpretation and follow-through

A no-trigger pass plus a controlled physical ordering/failure capture would
establish that the suspected mechanism is feasible in the diagnostic firmware
on actual hardware. It would not establish its natural frequency or claim a
stock-image reproduction. Only then prepare the minimal receiver synchronization
repair and repeat the identical diagnostic/load checks before and after on
hardware, with byte integrity and no-trigger behavior. AB-006 retains repair,
Flexe regression coordination and the wider release-qualification gate.

## Prepared result and stop point

The initial outstanding work and this plan were committed/pushed as0e01958
before implementation. Private VDP and copied IDF driver compile/link on Oryx;
audit confirms the original archive uart.c object is excluded and the diagnostic
driver defines the actual receiver functions. Original binary disassembly
retains the flag-before-lock and later RX-mask store ordering. ZDS II native
protocol and AgonDev/ZDS menu are compiled and checked against that firmware.

JIT/interpreter native protocol checks pass9.040s/9.335s; menu checks pass
14.053s/14.303s. The compiled diagnostic captures the controlled other-core
recovery-before-disable sequence and recovers both4096-byte payloads with
matching CRCs. Corruption, missing end marker and missing handshake controls
are rejected. Independent oracle controls reject intact payloads accompanied
by same-core, RX-still-enabled or full-flag-still-set evidence. Real SDL menu
input passes16.335s, allocates around an orphan result and blocks emulator
flashing. These are Oryx times; physical duration remains unmeasured.

The bundle is hash-verified at /test/mos-uart0/test.bin on uniquely identified
Console8 UUID8658-1C23. All22 report/journal files and root MOS are preserved,
with full prior contents archived off-card on Oryx. Diagnostic VDP file is
vdp-race-diag.bin,1081344bytes,CRC3039EE5C; its boot subtitle is UART0 recovery
diagnostic. Menu9/2 offers manual installation,8/4 the test,9/4 official stock
restoration. Firmware identities and readme.txt accompany the tests.

The Author requested notes then stop. No diagnostic physical flash/run has
occurred, no receiver repair is implemented, and new work remains uncommitted.
HW-002 retains manual hardware execution, restoration and return analysis.
The subsequent archive-only follow-up completed a full raw evidence/source/SD-
backup archive on Oryx and Pi: build/uart0-race-evidence-20261014.tar.gz,
SHA2562e3b701c79218b68d869d39a1ca886bdfb774a752afd256552025319fc13e37e.
The missing Oryx instruction/ownership files and latest notes were copied before
creation; the user's incomplete archive remains preserved. No hardware or test
work resumed. See experiments/uart0-race/results.json.
