# U1-001: MechAgon GOAL-001 owner support

Make the coordinated game's UART traffic reliable and make CPU headroom claims
measurable. The first integrated UART1 trial reported a receive overrun but did
not establish its cause. UART supplies generic driver/interrupt expertise and
timing-donor facts; Extender owns firmware/SDK/physical diagnostics and MechAgon
owns consumer/profile integration. No generic fix is assumed in advance.

Brandon's original goal and maximum-rate steering were read directly through
`codex_app.read_thread` in MechAgon thread
`01a1a883-630e-7b52-85d8-6fbc07cc0ccb`, turn
`01a1b546-5b80-7442-8645-3d70e44757bb`, human messages
`01a1b546-5bc4-7fb1-af6a-c42394c8d050` and
`01a1b547-e554-7e42-9919-5398d0c76796`.
Exact text is retained in `receipts/goal001-human-source.json`.
Assignment: mail
`2026-11-07_04-17-37_mechagon_goal001-uart-owner-async-support-one`.
The owning goal is `/Agon/mystuff/MechAgon/docs/tasks/GOAL-001.md` at046d35f.
The sole actionable project index is `TODO.md` entry U1-G01; the phases below
describe the bounded implementation/review sequence, not a competing TODO.

Scope permits focused source corrections, serial compiler qualification and
finite owner-coordinated hardware tests after actual admission. Existing queued
Wolf77/manual work finishes first; UART has no target checkout. Do not reserve
or operate another owner's serial device, install EMOS/P4, change wiring, or
restart failed kit76. Separate Console8/ESP8266/Jukebox work is not automatically
a GOAL-001 workload. Existing source-release/TEMT/reply/close, reciprocal gates
and first-error retention remain mandatory. No emulator workload/publication.

## Bounded work sequence

G1-001: Record verified scope and coordinate exact owner hooks/donor needs.
Preserve working rollback and previous failures. Existing source review is
`consumer-coordination/mechagon-first-physical-overrun.md`.

G1-002: Specify minimal shared-time IRQ/callback attribution and return existing
timer donor paths, required ownership/calibration/wrap handling, nested-accounting
rules and instrumentation limits to the owning headroom helper through MechAgon.
The helper owns new profiling code; do not implement a duplicate profiler.

G1-003: Review exact owner RX/STOP/exclusion candidate and evidence. Any concrete
generic defect gets a minimal correction and meaningful real-code regression
under the normal compiler FIFO. Otherwise report an explicit no-change finding
and the missing owner evidence, not a speculative driver rewrite.

G1-004: Return pinned source/ABI/size/results and any remaining contract gaps;
coordinate finite matched owner qualification only with actual dependency order
and checkout. CPU attribution must label partial/inclusive measurements and
must not equate submission/callback/peer reply with presentation or useful work.

## Starting state

Generic source823bb91 is unchanged. Vanilla Console8 bounded binary reception
passes in Jukebox R0003/R0004; this is not EMOS/P4 evidence. EMOS candidate043a
trial76 failed with reported RX OE after source release. Working ROMa25f was
fully restored and the bench released; the error's timing cause is unknown.
Consumer92f083f scheduling-only drain cache passed offline checks and is not a
demonstrated OE correction. No generic register mismatch is identified.

## Offline tranche result

Task/verified source/timing contract published a6c47b4. MechAgon received the
atomic all-IRQ/epoch/nesting/quantization contract and existing PRT donors;
its profiling helper retains implementation ownership. Extender received the
concrete pending-retry/IER/TEMT ownership caveat before integration.

The isolated bounded-CTS derivative on `codex/rfc25-bounded-cts` has paired native
ROM builds and source/linked/startup structural proof, +52 code/+1 BSS byte.
Eight UART structural negative controls (original plus seven broken variants)
and six startup mutations on each image are rejected. No ISR/guest/hardware
execution is claimed. Compiler318 released with all children joined; actual
Extender successor319 notified immediately. Source, patch, full private paired
sources/binaries and evidence are under `experiments/uart0-rfc-retry` and
`build/goal001-uart0-retry`; exact package receipt is `retry-r01/package.json`.

This is a generic source-level correction for the unbounded WAIT_CTS path,
not a demonstrated trial76 cure. EMOS integration must add pending-retry to its
live-ownership gate and abort/reset teardown. Extender owns that splice and
its linked size/qualification. Current installed/working release remains
unchanged. U1-G01 remains open for concrete owner feedback and coordinated
qualification, not a claim that async reliability or CPU-headroom goals are done.
