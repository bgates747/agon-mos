# Controlled Console8 receiver diagnostic

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
