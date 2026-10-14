# Console8 receiver recovery: hardware-first test

Executive summary: we will test the unchanged VDP on Console8 before proposing a
firmware repair. The emulator has shown reception stopping permanently, but we
have not demonstrated that failure on the real board. MOS owns the initial
repeatable stress test and subsequent VDP instrumentation; the Author runs it
manually. Flexe owns emulator behavior/regressions. A passing run means that workload
completed; it cannot rule out a rare race.

## Scope and sequence

The first campaign uses official stock VDP 2.16.0 without diagnostic patches,
threshold changes or injected receive pauses. It uses the same experimental
ABI1.1 MOS image already installed for the passed R0005 comparison, rather than
introducing the new batching firmware at the same time. The package supplies
that exact MOS and official VDP/flash recovery files, but no new flash is needed
if installed identities still match. This is not a claim that experimental MOS
is stock or production-approved.

Use valid stock buffer-write/clear, buffer-compare and serialized GP reply
commands. Exercise sustained back-to-back large packets, an acknowledged
full-duplex workload and paced feed transitions with foreground progress.
Avoid arbitrary VDU spam, unbounded memory growth and multiple outstanding GP
requests (MOS GP is a last-value slot). Retain each source until MOS release,
and distinguish release from TEMT/wire drain and receiver completion.

A finite default campaign, with separately selectable extended repetition,
should provide frequent progress messages and a clear duration expectation.
Preserve every completed step and reserve a sequential run number before work
starts. Save the active stage before any operation that could stall; if output
stalls too, the SD checkpoint must still identify where progress stopped.
Never discard borrowed RAM merely to enforce a timeout. A stopped transmitter
may require the Author to reset after the stated no-progress limit. Do not call
a run PASS unless its required replies and payload checks finish.

Check all payload bytes in integrity stages using stock VDP comparisons, with
explicit coverage for any sustained stage that validates only its final stored
buffer. Keep load/stall detection separate from throughput or CPU-benefit
measurement. A failed run may implicate hardware/firmware/software but does not
identify the receive race without receiver-state evidence.

Prepare and verify the fixture headlessly on Oryx using a dedicated frozen
Flexe profile. Preserve any emulator failure rather than retrying until PASS;
known emulator failure is a separate result and cannot substitute for physical
failure. Verify the compiled fixture's reporting, bounded steps, corruption and
missing-reply rejection, and safe memory lifetime. If the known receiver fault
blocks a campaign, report exactly that limitation in the prepared hardware
package; physical execution is the Author-authorized investigation, not release
qualification of the emulator or new batching implementation.

## Packaging and execution

Keep `/test/mos-uart0/test.bin` as the entry point, the numbered menu and run-all
behavior, all earlier tests, sequential reports and `runs.log`. Add the recovery
campaign under the controlled-experiments menu rather than changing the SD
path. Put required firmware copies, identity/coverage metadata and a plain
`readme.txt` beside the tests. Preserve earlier deployments/results only in the
project workspace. Do not overwrite root `/MOS.bin` or unrelated card contents.

Prepare the complete bundle off-device first. Deploy only to the uniquely
identified Console8 card (UUID 8658-1C23) when available for this task, verifying
its prior owned manifest and preserving reports. No automatic flash, board
reset, serial-open operation, UART probe or Olimex wiring is authorized.
Manual run and observed stock VDP banner belong to the Author. Physical short
and extended runs have now completed; their result is recorded below.

## Interpretation and next owner

A passing run demonstrates successful communication for the pinned images,
workload, duration and board only. It does not rule out a rare synchronization
bug or establish an electrical CTS margin. A stall is a failed communication
run; preserve its last checkpoint, returned files, external elapsed time and
operator observations without claiming its cause from the display alone.

If natural failure occurs or the result remains inconclusive, this MOS agent
prepares a separate diagnostic VDP build that observes or deliberately
exercises the suspected competing-core ordering on physical ESP32 hardware.
Keep natural failure in unchanged firmware distinct from diagnostic-triggered
hardware failure and emulator-only reproduction. A proposed repair requires
matched hardware before/after evidence plus byte/error/progress checks and an
emulator regression. Lack of reproduction remains inconclusive.

HW-001 owned initial preparation and manual-return analysis and is now complete. AB-006
retains receiver attribution/repair and its hardware evidence gate. This plan
adds no separate unfinished-work checklist or authority over another project.

## Prepared implementation — 2026-10-14

The fixture and menu are prepared and hash-verified on the Console8 card at the
stable entry point. Menu8/2 selects six cases,8/3 selects24; previous tests and
firmware operations remain available. The required unchanged MOS/VDP files and
hardware-readable instructions sit beside test.bin. No flash was performed.
JIT/interpreter short runs, interactive short+extended, and deliberate corrupt
payload/missing-reply rejection validate the fixture off-device. Sequential
report collision avoidance and prior SD report preservation were verified.
See experiments/uart0-recovery/results.json for exact identities and coverage,
and experiments/uart0-recovery/readme.txt for manual operation.

The Author reported both physical campaigns passed and returned the card.
R0006/R0007 confirm all30 cases,245760 final-buffer bytes, zero case RX errors
and160 replies while async TX was BUSY. Binary reports, saved checkpoints and
journals agree. All deployed files and earlier reports are preserved; review
made no card writes. Stock VDP identity remains operator-labelled, not read
back. The entry RX98 history is distinct from setup/case diagnostic epochs00.

HW-001 is complete; see experiments/uart0-recovery/physical-results.json and
build/uart0-recovery-console8-r0006-r0007.tar.gz. The stall was not reproduced
on Console8 by these workloads. AB-006 remains open: controlled physical
instrumentation/interleaving is the next useful way to test the suspected race,
owned by this agent under HW-002 and docs/uart0-recovery-diagnostic.md.
This implementation neither fixes nor excludes the previously traced race.
