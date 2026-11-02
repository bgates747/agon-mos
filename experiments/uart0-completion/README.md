# Opt-in queued RST18 and completion callback experiment — UX-001

Applications can now test a simpler write call and optional completion
notifications, or explicitly enable copying RST18 so they may reuse their source
buffer immediately. Default RST18 and ordinary async open retain their prior
behavior. This is an experimental branch build, not a replacement for the
Console8/Jukebox-qualified ABI1.2 candidate.

Console8 has now passed all four standalone cases, including immediate reuse of
the application's copied-write source and one callback per logical write. Every
one of32768payloadbytes matched at the receiver. This establishes that the
simpler caller interface works on hardware; its real-application CPU cost and
benefit still need a matched comparison. See the hardware return below.

The borrowed convenience path avoids copying. The copying mode buys simpler
source ownership using768bytes of fixed MOS RAM, with backpressure when full.
A callback tells the application that MOS has finished reading that logical
write's source; it does not promise UART wire drain or VDP execution. The
copying mode's callback refers to consumption of the owned copies, since the
original caller buffer was already reusable at return.

## Build and qualification

MOS uses ZDS II/Wine on Oryx through `tools/zds/build.sh`. Original fixture and
application wrappers use AgonDev. Final linked image and raw results are in
`build/uart0-completion/run005/`. The preserved startup-safe baseline remains
`build/uart0-startup-safe/run005/`. The later explicitly authorized Console8
deployment and return are recorded below; Jukebox application files were not changed.

The implementation is `src/uart0_completion.inc`, included by the MOS adapter.
The existing driver has release hooks and a private copied-buffer publication
entry; no payload heap, new wire protocol or VDP modification was added.
Five protected upstream startup/UART/interrupt source files still match v3.0.2
byte for byte. The new image has a distinct write-mode EXPERIMENTAL banner.

Reproduce in a fresh build directory, using canonical Oryx SSH and FIFO rules:

```sh
UART0_BUILD_DIR=build/uart0-completion/NEW bash tools/zds/build.sh
ruby experiments/uart0-mos/symbols.rb build/uart0-completion/NEW
python3 experiments/uart0-startup-safe/source_guard.py build/uart0-completion/NEW
python3 experiments/uart0-completion/prepare_cpu.py build/uart0-completion/NEW
python3 experiments/uart0-completion/prepare_regression.py build/uart0-completion/NEW
.venv/bin/python experiments/uart0-completion/prepare_fixture.py build/uart0-completion/NEW
```

Stage those outputs to the same project-relative Oryx path, build Rust harnesses
there with the existing frozen CPU crate, and build the original app using
`bash experiments/uart0-startup-safe/remote_fixture.sh BUILD`. Native actual-ROM
and real-VDP emulator execution requires a shared FIFO lease. Real-VDP runner:
`UART0_ORYX_LEASE=TOKEN .venv/bin/python -B experiments/uart0-completion/qualify_flexe.py BUILD jit --fixture fixture --attempt UNIQUE`;
repeat with interp. The runner asserts ownership immediately before launch and
stops only its own frontend. Do not run models on the Pi or bypass the FIFO.

## Tentative appended ABI1.3

Require UTX1, major1, minor>=3, length>=69 and flags bit4. Offsets0..53 keep their
meaning, including batch selection. New entries are ADL=1, MBASE0 register-ABI
pointers, not C stack functions. They preserve IX/IY, shadow registers and
incoming foreground IFF. Primary registers are scratch except listed results.

| Offset | Entry | Inputs / results |
|---|---|---|
|54|tx_write_config|B=0 borrowed convenience / stockRST18, B=1 copiedRST18; C=0 take foreground events, C=1 direct notification/automatic retirement; HL=direct callback or0, DE=context. A=status.|
|57|tx_write_query|A=status, B bits0..3=mode, bit4=direct delivery; HL=callback, DE=context.|
|60|tx_write_last|A=status, HL=last successfully accepted logical write ID. Used after copied RST18; check submission status for borrowed calls.|
|63|tx_completion_take|A=OK, HL=id, DE=context, B=kind(1borrowed/2copied); BUSY if no event. Frees the completion's private descriptor.|
|66|tx_write_borrowed|HL=source, BC=positive length<=65535; A=status, HL=opaque logical write ID on success. Automatic reaping; no manual reserve/publish/status/reap.|

Call open and select batch16 separately. Configuration requires all descriptors
free, no sync scope/barrier/active copied write, and TEMT. A null direct callback
is valid and gives automatic retirement without notification. A non-null direct
callback must be ordinary application RAM code. Copied mode requires C=1: letting
unconsumed foreground events occupy all copy slots could deadlock a large RST18
call that itself must return before its caller can consume those events. This
prototype rejects that combination rather than silently discarding events.

The borrowed source range remains[040000h,0BC000h), entirely contained. Opaque
convenience IDs are not low-level cancel/reap tickets; applications needing
transaction cancellation continue using the original API. Failed borrowed
attempts can consume an ID; do not assume consecutive accepted IDs after errors.
ID allocation is24-bit, nonpersistent, and this prototype does not establish
indefinite wraparound handling. Do not promote this experimental ABI allocation
into EMOS or upstream without owner agreement.

## Callback and caller rules

Direct callback inputs: A=RELEASED(4), HL=logical write ID, DE=registered context.
It may run during the initial foreground submission/pump or later from the UART
ISR, with interrupts disabled and public API reentry rejected as CONTEXT. It
must preserve ADL/MBASE, leave interrupts disabled, return normally and only
post bounded application state. MOS saves both primary/shadow register banks
and indexes. No SD calls, rendering, recursive output, waiting or work scheduling
inside the callback. Completion may precede return from the write call.

For ordinary foreground work, configure event-taking mode for borrowed writes,
call take periodically, then invoke an application/library callback AFTER take
returns, with normal foreground interrupts. That is explicit foreground dispatch,
not an automatically invoked interrupt callback. The event records are bounded
by three descriptor slots and stay ordered across descriptor reuse.

The original AgonDev wrappers in `library/uart_write.src` hide discovery,
open/batch setup and indirect register calls. They are assembly register-ABI
helpers; C needs an explicit shim. Existing public calls remain the fallback.
The standalone C fixture includes a shim and a minimal flag/count callback.

Copied RST18 uses three256-byte buffers. Fixed-length writes use LDIR into free
slots, publishing through the existing ordered interrupt sender. Larger writes
wait for room and proceed in chunks; no source is retained after return. Each
logical call gets one ID and at most one callback, independent of chunks and
16-byte refills. Delimited mode is supported. Nonzero-MBASE callers retain the
existing synchronous compatibility path, with no new callback/ID for that call.
Calls made with IFF disabled use the existing bounded foreground pump, preserving
IFF; this does not turn app ISRs into supported API producers.

Normal close requires completion records reaped/taken and wire drained, then
clears mode/callback state. OSCLI/application return clears callback references
before draining accepted sources and restores stock dispatch. Undelivered
notifications are suppressed on this teardown. Reset clears BSS/mode; no callbacks
after reset. This adds no recovery machinery beyond scoped feature cleanup.

## Evidence and limits

Actual linked-ROM tests cover borrowed lengths1/15/16/17/255/256/257/1024 with
both IFF states and both delivery paths; copied fixed writes through65535bytes,
with/without callback, both IFF states and immediate source overwrite; delimiter
and empty calls;24 successive writes with ordered IDs; completion FIFO reuse;
CTS stop/resume with real GP receive parsing; invalid configurations, return
cleanup and callback API reentry. Existing27 production integration scenarios,
538 batch-control cases and stock/mixed-mode RST18 tests pass. Reset/boot tests
reach stock VDP handshake without entering experimental driver code.

A matched modeled paced comparison used30feeds of743bytes,307200 assumed cycles
per feed, and32-cycle synthetic useful-work units. This is an instruction/UART
model, not calibrated hardware CPU or application performance:

| Interface | Useful units | Maximum ISR instruction steps |
|---|---:|---:|
|Original borrowed reserve/publish/reap|263494|196|
|Borrowed convenience / foreground events|262974|210|
|Borrowed convenience / direct RET callback|263127|266|
|Copied RST18 / direct RET callback|258497|272|

Relative to that same-image baseline, useful-work units fall about0.20%,0.14%
and1.90% respectively. The initial scalar-copy prototype scored205710units;
block copies recovered most of that loss. This does not establish physical
latency, a max-throughput winner or real Jukebox benefit. Callback execution
adds ISR work even with RET alone; keep larger callback work in foreground.

Final image SHA256cb1d0f4e066395533a2f07c7454246fa3a1ed46134bf155b883bb8c6e8353128,
112777bytes; updater file CRC6E17923C, installed erased-tail ROM CRCFA47120E.
ROM growth1538bytes and BSS/RAM growth837bytes versus accepted startup-safe image.
Of837bytes,768are copy buffers; the remainder is metadata/scratch. Whole-image
RAM3956bytes. This is not an EMOS fit approval. The linked application wrapper
object contributes245bytes of text and3bytes of BSS in the fixture map, separately
from MOS cost. The fixture executes its C shim; the assembly convenience wrappers
are assembled/linked examples, not yet a released, separately runtime-qualified
library.

The standalone fixture validates a negative/positive receiver comparator then
checks all8192payloadbytes in each of four cases: borrowed/direct, borrowed/event,
32copiedRST18 calls/direct, and one8448byte copiedRST18/no callback. It logs
progress and sequential reports. Its times are frame ticks for transfer cases,
not a fair application-level performance A/B. Firmware and fixture identities
are pinned; the VDP remains the already repaired matched diagnostic image.
The standalone hardware return below passes; useful paced/bulk application
comparisons remain pending.
Do not deploy over the active Jukebox trial without explicit Author direction.

RX parser injection remains deferred: the combined MOS handler already feeds
that parser, and this interface has no demonstrated need for a public injection
syscall. Shared semantic coordination with Extender is recorded separately in
`../agon-dev-env/cross-agent/parallel_uart_async/contract.md`; it grants no binary
ABI, hardware ownership or EMOS size acceptance.

Final both-engine application results: JIT36.819seconds, interpreter49.635seconds;
32768payloadbytes compared in each, zero reported frontend faults/TX drops/RX
overruns. Raw evidence archive SHA256
97fb941d7a102ad8b7bde6d8cbb248daad9f313e614cddebf5bb9d30051eb771,
`build/uart0-completion-evidence005.tar.gz`, verified on Pi. The original raw
archive retains an obsolete SAFE_BUILD entry inside metadata.identities; the
actual identity.h, report build8c194fd8e65367aa and metadata.build_id agree. The
preparation generator and local metadata mirror are corrected; binaries unchanged.

Workspace-only appliance: `build/uart0-completion/run005/appliance/`, newtest.bin
SHA256749e7dc103ba9e8522e07254dbdc7f8aaedbebe75f9b3ecf4c6c917b33dd691e.
At that milestone it was ready to stage; the later authorized deployment is
recorded below. Emulator lease generation94 released, no waiter.

## Clean SD deployment, 2026-11-02

The Author selected hardware testing and requested removal of old-test files.
The active AGONC8 directory is /test/mos-uart0, with16 required files and no
historic reports/fixtures. Predeployment117files are preserved on Oryx and Pi
in build/uart0-completion/card-deploy001/before.tar.gz; archive SHA256
c97d45b425c6c8e96c30803f9fdbbfe6ed51d1b960e8a76e12dbea58ab6dd6c9.

The installed standard flash MOSlet was verified; no duplicate updater, debug
map or agent manifest was left on-card. Root files and other projects were
untouched. Exact run005 MOS and matched VDP retained. Test application changed
only to persist its next report number in next.txt, allowing reports to start
at R0039 after clearing archived history. Source main.c and its ASM shim are
byte-identical to the qualified fixture; report allocation was host-tested and
the original app rebuilt with AgonDev. No additional full emulator run was
performed for that logging-only change; the optional FIFO request was withdrawn
rather than wait on another owner's long session. Firmware code unchanged.

Deployed test SHA256af07f6a0d7d808ce7d9b5a4486476554c3ccdc22d476527ae41aece1694ffe83,
build71715a9860ae7f56. Deployment receipt and exact package scripts are in
build/uart0-completion/card-deploy001/. On-card readme contains standard flash
commands and automatic four-case protocol. Physical qualification was pending
at deployment; the completed return follows.

## Console8 hardware return, 2026-11-02

Report R0039/build71715a9860ae7f56 ends `END CALLBACK SUITE PASS`. Both comparator
controls pass, and all8192payloadbytes in each case match at the receiver.

| Interface | Notifications recorded | Transfer frame ticks | Receiver comparison |
|---|---:|---:|---|
|Borrowed write / direct callback|1|10|8192bytes PASS|
|Borrowed write / foreground event|1|10|8192bytes PASS|
|32copied RST18 writes / callback|32|10|8192bytes PASS|
|One large copied RST18 / no callback|0|8|8192bytes PASS|

The copied cases overwrite the caller source immediately after each call
returns. Full byte comparison therefore verifies the caller can reuse that
memory. Direct callback status, registered context and consecutive callback IDs
are checked by the compiled fixture; case3 confirms one notification per logical
write rather than per buffer slot or UART refill. Case4 exceeds all three copy
slots combined and confirms backpressure and automatic retirement without a
callback. These are physical correctness results, not a matched throughput or
CPU-headroom benchmark. They do not select a new Jukebox interface by themselves.

Archive `build/uart0-completion/card-return001/before.tar.gz`, SHA256
7c43733b6228db3baaaa3ca6e80199db71949a958c4f318769dd0c49246b0c3b,
contains19files verified on Pi and retained on Oryx. Recheck with
`.venv/bin/python build/uart0-completion/card-return001/analyze.py`; its
`analysis.json` records identities, cases and limits. All14immutable appliance
files match deployment, including the fixture, MOS, VDP and byte comparator.
The MOS/API entry guard passed; this report does not independently record the
installed VDP hash or post-return CLI responsiveness. The journal is exactly its
original compact seed plus R0039, with next.txt40. Root MOS.bin is unchanged;
autoexec selects /test/mos-uart0 rather than /test/jukebox/. The agent performed
no SD writes, board flashing or emulator execution and left the card mounted.

The hardware fixture portion of UX-002 is complete. Matched application benefit
and the separate EMOS size decision remain open. This experimental interface is
ready for that application comparison; it is not stock MOS or release approval.
