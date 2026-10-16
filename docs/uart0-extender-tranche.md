# Unattended UART qualification through Agon Extender

The Author wants the relevant Console8 tests repeated without bench visits,
followed by the next CPU-headroom and throughput comparisons. Extender can
coordinate input, file transfer, observation and recovery, but those facilities
depend on EMOS. The sender must therefore work inside real EMOS at least in
Legacy mode. Replacing it with this project's MOS image would remove the remote
services; a RAM-only experiment cannot establish the requested integration.
EMOS flash space is a prerequisite to measure before choosing an implementation.

The native-build assessment is now complete and stopped for Author review.
The existing installed image leaves2450 bytes, while this ZDS-built baseline
exceeds flash by3442 bytes before UART integration. The generic sender module
is2497 bytes; a simple addition suggests about6KiB of space work, but an actual
integrated link must account for the existing code it replaces and the hooks
it adds. Hardware was not changed or tested. The recommendation is to retain
ZDS II and first measure an EMOS ROM-compaction plan, beginning with the owner's
existing diagnostic MOSlets, while preserving input, SD and routing. Their
backport saving has not been measured, so it is not yet a promised solution.
No compiler exception or new compaction implementation is selected merely
because the Author cannot yet choose between the alternatives.

The Author assigned this work on2026-10-15 and explicitly allowed adapting test
suites for unattended operation. EX-001..EX-004 in the sole TODO own this work;
existing AB/BT tasks retain final MOS qualification, application and release
requirements. New experimental tests do not promote firmware to production.
Console8 remains a separate manual target with its own retained evidence.

## Controlling research

The newly accepted [test appliance and suite lifecycle](../../agon-extender/docs/procedures/test-appliances.md)
was found/read and linked to the Author, who confirmed it is the intended file.
It requires a Pi Python coordinator, explicitly invoked individual appliances,
conditional mode changes, at least one second for monitors to settle, and
restoration of entry modes/routes and a visible responsive CLI. Runners and
deployment helpers must never change /autoexec.txt or use reset to launch tests.
Interrupted runs stop dispatch and cannot automatically replay at the new CLI.

The [operation index](../../agon-extender/docs/procedures/README.md),
[test execution](../../agon-extender/docs/procedures/test-execution.md),
[bench constraints](../../agon-extender/docs/qualification/bench-constraints.md),
[existing installation guide](../../agon-extender/docs/using-extender.md),
[keyboard guide](../../agon-extender/docs/remote-keyboard.md),
[foreground SD guide](../../agon-extender/docs/mainboard-sd.md),
[reset protocol](../../agon-extender/docs/bench-reset.md),
[installation guide](../../agon-extender/docs/installing.md), and
[MOS recovery](../../agon-extender/docs/mos-recovery.md) govern hardware work.
Private bench identity, exact devices/reservation and endpoints remain in the
Extender machine-local record, not in this document. Network access remains
owned by agon-dev-env. Current production selection is not evidence of what
is installed on a development bench.

## EMOS baseline and size gate

The latest saved installed-ROM receipt identifies EMOSv0.1.24,
build2026-10-07-23-11-33Z, sourcecf10f0b1848346bc5d04056e4663bbbc166b2480.
Its128KiB saved physical readback matches SHA256
6f83bc21558ea7dcb665b60c18aa3a5c3030367f901e3e32ccbbf99eaf7f4019.
Image extent128622 leaves2450 erased trailing bytes. This is a verified saved
baseline, not a fresh bench query or an estimate of ZDS-generated size. The
later EMOS HEAD contains ExExt experiments and is not substituted automatically.
The full sender and compatibility hooks need actual native link measurements;
do not assume2450 bytes is enough, silently remove services, or spill into RAM
owned by EMOS utilities without auditing the memory contract.

ZDS-oriented source remains owned by an isolated agon-emos checkout. Native
ZDS II/Wine compilation runs on Oryx; no mos-agondev build is selected for this
work. EMOS OWNERSHIP.md permits direct ZDS builds. Its older test-mode-autoexec
instruction is superseded for these suites by the Author-confirmed Extender
lifecycle. Preserve component-owner baud, UART1 isolation, keyboard, console,
utility-region and route contracts when establishing native-build checks.
Unexpected source changes in other checkouts must be preserved.

Native C and assembly now compile after two isolated compatibility changes:
structure-copy initialization becomes explicit memcpy, and command fallback
declarations move before executable statements. The link still fails its
overlap/range guard; no installable native EMOS image was produced. These
source changes are exploratory, uncommitted and not behavior-qualified.

| Saved baseline/build | ROM bytes used | Capacity | Space left / overflow |
| --- | ---: | ---: | ---: |
| ZDS speed-oriented baseline | 138752 | 131072 | 7680 over |
| ZDS size-oriented baseline | 134514 | 131072 | 3442 over |
| Previously installed EMOS readback | 128622 | 131072 | 2450 free |

Explicit size optimization and additional documented optimization flags give
the same134514-byte result; switches alone have not resolved the overflow.
The compiled sender module measure includes its generic ROM wrapper; final
EMOS hook/replacement costs remain unmeasured. The owner's existing extraction
of UARTFLOW/UARTTEST/VDPPOLL is in commitsc98f80e and8f06429, with utilities
under agon-emos/projects/uartflow and projects/uartprobe. Neither those later
changes nor their compiler/build results are silently substituted for the
verified installed source. Evidence and a reproducible reader are in
experiments/uart0-extender/budget-results.json and summarize-budget.py; raw
attempts and source snapshots are under build/uart0-extender.

Legacy uses the mainboard VDP on UART0. Extender input uses its admitted UART1
path, so UART0 interrupt ownership and parser changes must preserve that input
and EMOS transport policy. Async opening must refuse routes/reservations that
cannot safely share the sender. API results, blocking compatibility barriers,
borrowed source lifetime, callback exclusion and application-return fencing
must have the same explicit contracts as the generic MOS sender. ExCom/ExExt
support is outside this first acceptance target; preserve their existing
behavior or explicitly refuse the async session, rather than bypass routing.

## Test composition and evidence

Reuse the individual versioned appliances and independent report readers.
Relevant replay includes receive diagnostics, API/session/legacy/callback/
masked-IFF/exit/ADL0 behavior, complete payload CRC/byte checks, ordered full
duplex under receiver pauses, and the receiver baseline/fixed comparison.
Receiver firmware is the same MOS-owned family already tested on Console8.
The first new performance work is original30-phase A/B replay against the
repaired receiver, then matched complete-payload paced/unpaced comparisons.
Exact physical cycles, natural race frequency and electrical CTS margin remain
separate claims. Keep stock-style blocking and each experimental sender named.

A CLI argument or finite batch selects an existing test without requiring menu
keypresses. The Pi coordinator invokes explicitly, records case/target/mode,
firmware and fixture hashes, start/completion/elapsed host times, raw reports
and restoration. Host elapsed time includes named setup/collection portions
separately; Agon tick counts remain uncalibrated unless independently measured.
Report IDs use sequential numbering and the existing running journal, without
depending on Agon wall-clock dates. Failed/inconclusive/aborted tests stop the
dependent sequence and retain evidence; keyboard acceptance is not completion.

Fixtures stay under the established /test/mos-uart0 application directory;
Extender support/evidence follow its SD layout. Preserve unknown files and
existing results. Firmware switches are explicit bounded host operations
between appliances, never hidden inside a command file or startup. Each switch
requires incoming backup, exact target, independent readback and verified boot.
Restore the incoming compatible firmware and actual CLI/input/SD state at the
end. Do not erase NVS/OTA metadata or reset after a guessed flash delay.

## Bench observation and stop boundary

The latest Extender local entry records a stopped scrolling readiness attempt,
unreviewed terminal state, and a setup-only143-byte mode8 startup. Historical
handbacks do not prove the bench is idle now. No live bench query, keyboard,
transfer, reset, flash or test was performed during this initial research.
Establish positive ownership/CLI handback before operational use. Preserve
inherited startup exactly; this test runner has no startup-repair authority.
No installed EMOS/VDP/P4 image is changed merely to establish a build baseline.

The Author subsequently confirmed idle CLI, inserted SD and bench availability.
Three read-only HTTP snapshots showed admitted neutral input, an offline idle
SD service, and P4 mode0/single buffering with zero HDMI fault counters. These
do not identify the mainboard's active video mode or independently prove CLI
execution. No keyboard command, transfer, reset, flash, startup write or test
followed. The temporary bench reservation is released at this review stop;
future operational work needs fresh ownership and state checks. All native
build processes have ended. The Author's final instruction is to finish the
interrupted assessment and stop, not to continue into integration or tests.
