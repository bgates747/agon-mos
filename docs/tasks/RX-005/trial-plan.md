# RX-005 — First synthetic counted-return trial

Brandon's2026-11-07 instruction starts an explicit goal: get a trial working
with original synthetic cases, then stop for review. UART coordinates and owns
MOS plus the fixture; VDPlet owns every VDP/VDPlet edit. Neither edits games.
No candidate is distributed to application owners before Brandon's review.
There is no physical flashing, release, upstream submission or default change.

## First slice and donor

Use a single opt-in registered receive destination/capacity and typed counted
return. Ordinary VDU requests/output and keyboard/legacy replies keep their
existing paths. Use existing application correlation where necessary; do not
add a queue, channels, automatic retries, cancellation engine or deferred executor.
A partial/uncertain transfer must not silently release or rearm storage.

Select the exact released Eirene RC3 donor97311c437093e416342a6c836cf9914f2ced027d,
tag3.1.0_uart0_rc_3: established startup fix and RFC25 TX, using Eirene's own
AgonDev toolchain. This does not migrate official ZDS II MOS. Leave the current
neighboring feature checkout and all released assets untouched; use an isolated
trial worktree/branch. Record the matched donor build and actual SDK/library
identity before attributing code-size or runtime differences.

Feature logic stays in one new MOS implementation file, with at most two small
source registration/dispatch edits. The original fixture uses AgonDev C with
small ABI/IRQ assembly wrappers as required. VDPlet selects and pins its own
trial donor, producer implementation and one-file integration, returning source,
binary/map provenance and a private synthetic operation contract. Agree the
unused reply type and counted layout before implementing either side.

The first proposal is a distinct reply type with a16-bit payload count followed
by that many bytes, copied directly into admitted application RAM. The old
16-byte MOS scratch remains the path for old packets. A small public trial
syscall arms/queries a receive and exposes pending/complete/error and actual
count; a minimal callback is optional, with explicit register/IFF rules. No
number, exact descriptor layout or callback context is frozen by this plan.
An intact oversized/unarmed frame must be discarded as a counted frame, never
reinterpreted as keyboard/legacy packets or allowed to overwrite capacity.

Pacing is a joint wire contract, not a consequence of allocating RAM. Keep
producer output serialized by whole frame and establish the real eZ80 receive
service/flow-control constraints. Do not introduce a general ring/FIFO-trigger
redesign unless the first measured trial demonstrates it is required.

## Finite synthetic qualification

Use one command-line fixture with no mandatory switches, clear screen/title,
case breadcrumbs, expected duration under two minutes and an explicit terminal
PASS/FAIL. Preserve raw reports under sequential run numbers, without clock-based
names. A timeout is failure, not completion or authority to release live memory.

1. Matched donor startup and ordinary mode/poll/keyboard controls, before opt-in.
2. Deterministic patterns including00/80/81/88/FF:0/1/2/8/16/17/127/255/256/512
   bytes, and a bounded larger chunk only if jointly supported. Verify every
   byte, exact actual count, guards and one terminal notification per admission.
3. Exact-capacity, BUSY, invalid/zero destination where applicable, unarmed and
   intact oversize frames. Verify no guard changes, no false success and normal
   legacy packet alignment after positive discard. No intentional reset/power
   fault or elaborate hostile-input framework is part of this slice.
4. Repeated positive rearm plus early-arriving reply (armed before sending),
   embedded header-like payload bytes, ordinary replies and real key down/up
   between complete frames. Verify data never becomes key events and genuine
   keys survive. Keyboard injection remains distinct from firmware byte claims.
5. Foreground useful-work counter while pending and bounded IRQ completion,
   then clean source/receive/callback/timer retirement and return to MOS. Report
   measured elapsed/CPU limits honestly; no game FPS or hardware claim from
   byte arithmetic or emulation alone.

MOS-side source/host checks cover actual parser/admission behavior and register/
IFF/lifetime edges. Native build/link checks pin code/BSS/stack changes and
startup/legacy invariants. End-to-end Flexe qualification executes matched MOS
and VDP firmware on Oryx through the actual FIFO/checkout/assert/cleanup process,
with exact byte/callback/oracle checks and both engines where practical. Do not
substitute Fab for a firmware-running VDP check. Ask Flexe only for necessary
emulator infrastructure facts/fixes; firmware ownership stays with VDPlet.

## Build and run admission

Pi compiler FIFO covers finite MOS/app builds and ordinary bounded source/link
checks: one compiler job, finite watchdog, retained logs, owned children joined,
release and immediate next-owner notification. VDPlet owns admission for its
own build jobs. Prepare/pin the full emulator runner and cleanup plan before an
Oryx request. Emulation uses Oryx exclusively; no Pi diversion. Host CPU boost
stays off. No lease is a firmware installation or physical-test authorization.

## Completion and mandatory review stop

Record agreed wire/API and ownership, exact source/binaries/toolchain/VDP pins,
diff, code/RAM costs, synthetic case results and raw evidence, known limits and
how to reproduce. Passing means the finite source/build/end-to-end synthetic
criteria pass; it is not physical qualification or application acceptance.
Once that trial passes, stop the goal's work for Brandon's review. No prototypes,
SDK adoption or migration requests to individual game/application agents.

The sole actionable checklist remains the root TODO. This plan records scope
and acceptance criteria; later agreement/results append to the running notes.
