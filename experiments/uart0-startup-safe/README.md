# Preserve stock MOS startup; explicitly activate background sending

The new firmware boots through the working release's startup code and keeps its
ordinary UART handler until an application explicitly opens an experimental
session. Closing the session or returning from the application restores stock
handling. Software tests now check boot recovery even with deliberately broken
experimental code present. This reduces the chance of a transport experiment
preventing access to the CLI and updater after reset. Human functional review
now passes, and the first Console8 hardware campaign also passes. The next task
is the dedicated physical run of the deployed deliberate-reset fixture. The Author chose direct hardware testing because of emulator demand; this supersedes the planned GUI review before that
hardware procedure.
Performance qualification remains separate.
This is an experimental candidate.

The earlier checkpoints were pushed before implementation: `d5268d2` and
`a45912b` on `codex/uart0-async`, and `e493d97` on
`codex/uart0-otirx-native`. The Author explicitly approved committing/pushing the completed work on
2026-11-01 before starting the deliberate-reset fixture.
BO-001..BO-003 dispositions and the remaining BO-004 gate are in the development log
and the sole unfinished-work index, [TODO.md](../../TODO.md).

## Exact candidate

| Item | Identity |
| --- | --- |
| Build | `build/uart0-startup-safe/run004` |
| MOS compiler | Upstream ZDS II under Wine on Oryx |
| MOS binary | 111,239 bytes; SHA256 `89ea8694194e0488337bf1dcbfa91e2b084b3afc75a9c3916f4acc9ae12aa42b` |
| Installed ROM CRC32 | `0C5886FC` with erased FF tail; Flexe zero-tail `16A52145` |
| MOS subtitle | `Arthur - UART0 startup-safe EXPERIMENTAL` |
| Test application | AgonDev menu; ZDS II native test children |
| Menu | SHA256 `26ed31af3f93bf2a056cab8c2da29a9efabbe45a1e2ec900c8f405f4dde39a2f`; build ID `32d6d885f3b8b8e0` |
| Compiled VDP | RX-repaired diagnostic, SHA256 `201ad8ab4af807c261cb92634286b2fbaedcf3879f140e820b60ab54cf707e2a` |
| Frozen Flexe frontend | SHA256 `412089a89a5adccb3c1c0fc4b121472da28f2d3d48c435c88a660028d7cd84d9` |
| Frozen Flexe VDP backend | SHA256 `77b3cbf76564d54628c2bb876aa96ef3834c6b363d53df4892b8a3ab4248e5cd` |

The compiled diagnostic VDP is not the official stock VDP. These results do not
approve a firmware combination for deployment or establish new performance or
electrical CTS-margin measurements.

## Startup and ownership boundary

Five files match official v3.0.2 commit
`8336409351ee5314e02801a7b72a4f1bb5282519` byte for byte, in both the working
tree and built source snapshot: `main.c`, `src/uart.c`, `src/interrupts.asm`,
`src_startup/cstartup.asm`, `src_startup/init_params_f92.asm`.
`source_guard.py` verifies this rather than relying on names or comments.
Reset/default-vector installation remains the release implementation.

The ordinary release BSS clearing disables the experimental state on cold and
retained-RAM resets. Initialization moved out of `main` into the first explicit
successful session open. Discovery does not initialize or activate it. Open
uses the release's RAM-vector setter to install the experimental handler under
interrupt exclusion, preserving line rate, FIFO contents and receiver state.
It refuses a caller-owned replacement handler and restores that handler.

Open can return BUSY while a preceding stock byte is still shifting. Applications
must retry within their own timeout rather than assume open is instantaneous.
An installed keyboard callback also excludes open; from the stock callback path
this is BUSY, without entering experimental ISR-context bookkeeping. The menu
removes its input callback before running a selected test.

Close drains accepted traffic and restores the saved handler/interrupt mask.
Application return retains the existing source-lifetime fence and restores stock
handling before the CLI. Ticket numbering stays monotonic across close/reopen;
batch selection returns to one. Legacy applications do not enable batching.

Minimal guards remain in serial/RST dispatch; the whole ROM is not identical
to the release. Disabled paths use direct stock status reads and the original
RST18 body. The active RST18 wrapper uses `CALL.LIL` to match that body's
`RET.L` frame. Reset recovers volatile transport state, but a partial VDP packet
can require resetting both processors. This is not protection against corrupt
flash, arbitrary memory corruption or an unrelated startup defect.

## Qualification completed

| Check | Result and evidence under `run004` |
| --- | --- |
| UART0/UART1 baud calculation | All seven rates each, including 1,152,000; `cpu/boot/execution.log` |
| Cold and retained-RAM startup | Reset reaches release main; data/BSS/vectors checked |
| Boot handshake and broken experiment | Four cold/warm × intact/crashed-handler controls; no experimental initializer, service or status helper entered before banner |
| Actual mixed-mode RST18 | Fixed/delimited × stock/active × both interrupt states; correct stack, bytes and IFF |
| Ownership/session controls | Discovery, rejected custom vector, takeover, lazy initialization, close/reopen and app-return restoration |
| Existing production and batching cases | 27 production + 538 batching scenarios at each of sizes 1/2/4/8/16 |
| Bad-image regression | Previous run003's incorrect RST18 call frame is rejected at runtime; `cpu/driver/negative-rst18.log` |
| Flexe JIT | Two complete suites PASS, 66.431 s; `flexe-jit-final/receipt.json` |
| Flexe interpreter | Two complete suites PASS, 93.451 s; `flexe-interp-final/receipt.json` |
| Full receiver integrity | Each engine compares 65,536 payload bytes and checks 256 ordered replies; full raw packets/reports retained |
| Wrong-image control | Menu rejects changed ROM before activation or numbered report creation; `flexe-jit-wrongrom/receipt.json` |
| Keyboard and updater entry | 20 ms taps select tests 1/2, Q returns to CLI, official FLASH prints usage, subsequent DIR works; `keys2/receipt.json` |

Both full-engine campaigns report zero frontend faults, UART TX drops and RX
overruns. The CPU fixture uses modeled registers/peer replies and actual linked
eZ80 instructions; it does not measure physical timing. Flexe runs the compiled
ESP32 firmware. No physical board or SD-card operation occurred in this tranche.
The updater check supplies no firmware arguments or confirmation: it tests entry
and return, not programming.

Earlier attempts remain in the archive. Run003 exposed a real active-RST18 stack
frame defect; the fix is included in run004 and a regression rejects run003.
The first keyboard/updater attempt loaded official FLASH at the ordinary app
address, causing an emulator panic because FLASH is linked at B0000h. The
corrected keys2 test uses that required address and passes. Earlier ZDS report
padding and profile-preparation harness errors are also retained. Failed attempts
are not acceptance evidence.

## Human review return — 2026-10-31

The Author completed the review and requested release/analysis. Numbered report
`R0001.log`, its native children and raw traffic independently confirm a clean
functional pass for the exact candidate above:

| Pause | Payload bytes compared | Replies expected / received | RX or ordering errors |
| --- | --- | --- | --- |
| 0 frames | 8,192 | 32 / 32 | 0 |
| 1 frame | 8,192 | 32 / 32 | 0 |
| 4 frames | 8,192 | 32 / 32 | 0 |
| 8 frames | 8,192 | 32 / 32 | 0 |

All four complete transmitted packets match the generated inputs. All 8,192
byte-comparison commands are present. The native reports confirm actual replies
while sending remains pending, with final payload verification in each case.
The integration child passes masked-interrupt output and queued-source exit;
the menu confirms the stock handler is restored after return. Raw traffic then
shows Q returning to the CLI, typed `dir`, a directory listing and a new prompt.
All staged test/child/check binaries match the qualified fixture hashes.

The frontend reports no faults, TX drops or RX overruns. Captured VDP replies
equal delivered replies byte for byte. The saved capture contains one boot and
one suite execution; a separate close/relaunch is not independently established
by this capture. Do not infer it or physical reset recovery from a PASS line.
The earlier linked-ROM cold/retained-RAM/crashed-handler reset controls remain
the off-device reset evidence. Real reset recovery belongs to BO-004.

This clears the functional emulator gate for a focused Console8 boot,
activation, integrity and reset check. It does not measure a new throughput or
CPU-saving result, approve a public release or authorize physical flashing.

Raw return archive on Pi/Oryx:
`build/uart0-startup-safe/run004/human-return001.tar.gz`, 298,280 bytes, SHA256
`c10d3e6308a07d076a10ca74a178f15dc40f7a71c000a038c5d91bf7630d18a2`.
All 23 files match their archived manifest after retrieval to Pi. Reproducible
offline analysis is saved alongside them as `human-return001/analyse.py` and
`analysis.json`. No further emulator was launched for analysis.

Review checkout generation48/request `c16e3260c12d` was released with fresh
whole-host idle evidence at 14:59:41 EDT. Rally's next request `5c6fe3061222`
was notified immediately through its existing chat; it subsequently checked out.
The review profile remains stopped. Reuse requires a new FIFO reservation.

## Console8 physical return — 2026-11-01

The first hardware campaign passes. R0031..R0036 are fresh reports from the
qualified menu build `32d6d885f3b8b8e0`. Every staged firmware/test asset and all
previous numbered reports still match deployment hashes. R0031/R0033/R0034
pass stock-handler discovery; R0032 passes explicit activation/close/reopen.
R0035 and R0036 each pass all four tests, including native OTIRX, masked-IFF
sending and queued-source application-return cleanup. The menu verifies stock
handler restoration rather than relying only on child return status.

| Full run | Pause frames | Payload bytes verified | Ordered replies | RX / ordering errors |
| --- | --- | --- | --- | --- |
| R0035 | 0 / 1 / 4 / 8 | 32,768 | 128 / 128 | 0 / 0 |
| R0036 | 0 / 1 / 4 / 8 | 32,768 | 128 / 128 | 0 / 0 |

All eight case records have correct transmitted command lengths and final
reply tokens. Replies arrive while sending is still pending in every case:
30/31/31/31 per run. The fixture's full receiver byte comparisons complete
successfully; baseline RX flags are zero and no new failure artifact exists.
Modem-delta flags of1 represent recorded CTS transitions, not receive errors.
The journal contains exactly the six complete new reports without collision.
Agon RTC timestamps were not used to decide freshness.

This establishes normal hardware boot/opt-in/cleanup and repeated integrity for
this experimental pair. The Author reports completing the power-cycle steps.
The fixture does not record the physical reset edge, a firmware readback or a
wire capture; installed-MOS identity is gated by the fixture's ROM check before
report creation. It does not test a deliberately crashed/partial-command reset,
measure electrical CTS margin or establish a new throughput/CPU-saving result.
BO-004 now has an implemented, off-device-qualified deliberate-reset fixture;
human review and its dedicated hardware run are next. It was not supplied for
this completed round; the Author completed all requested tests.
Broader performance/release gates remain separate.

The Author deliberately left the experimental MOS and matched test VDP installed
because Console8 will remain dedicated between tests. Stock restoration is not
pending for this run. No firmware was flashed/restored by this inspection, and
no card content, mounting state or emulator reservation was changed.

The installed `/mos/flash.bin` is byte-for-byte identical to the supplied official
updater1.9 (SHA256 `480b476703b798cf8d93294cac42d77cad93f7747003b061520b86685c75eb57`).
Future instructions should use `flash mos mos-candidate.bin` or
`flash vdp vdp-test.bin` from `/test/mos-uart0`. Loading the supplied copy at
B0000h is a fallback. The Author's decision to retain firmware supersedes the
old on-card H-005 restoration instruction for this completed campaign; inspection
leaves that historical card text unchanged.

Full read-only return snapshot on Pi/Oryx:
`build/uart0-startup-safe/card-return001.tar.gz`, 1,388,310 bytes, SHA256
`bf26310a96d97f5a6bbd45356cf307184d18ac3b234ef2f3d2bdf0c28ce399e3`.
All 113 files were verified against card reads on Oryx and independently after
Pi retrieval. `card-return001/analyse.py` and `analysis.json` retain the exact
checks and results. Six new reports and six native child files account for all
new active-directory files; only the running journal changed among deployed
files. Root stock MOS is unchanged. The returned startup file now comments out
Jukebox loading and changes to `/test/mos-uart0` after keyboard setup; it does
not run the suite or activate transport. This change predates inspection and
was preserved as found. The Author separately approved the commit checkpoint on
2026-11-01; no public release is inferred.

## Review fixture

The stopped Oryx profile is
`/home/smith/Agon/mystuff/agon-mos/.emulator/uart0-startup-safe-review`.
It opens the menu without activating experimental transport. No physical
firmware is staged by preparing this emulator profile.

| Key | Operation |
| --- | --- |
| 1 | Stock transport and discovery without activation |
| 2 | Explicit activation, ordinary output, close/reopen |
| 3 | Batch16 OTIRX; four pauses; full-duplex ordered replies and byte comparison |
| 4 | Masked-interrupt output and app exit with a queued borrowed source |
| 0 | Run all |
| Q | Return to stock MOS CLI |

Allow up to two minutes for Run all. Progress lines identify each test; a stall
is a failure. Expect `UART0 STARTUP-SAFE SUITE PASS`, fresh sequential
`Rnnnn.log`/child reports and an updated `runs.log`. No reliable clock is needed.
The fixture refuses an unexpected ROM fingerprint before reading private state.

Reserve/check out Oryx under this project's identity **when the Author is ready**,
using the canonical [scheduling procedure](../../../agon-dev-env/cross-agent/vdplet-rollout/README.md).
Keep the profile stopped until then. The Author launches the real generated
`./flexe-agon-emulator` wrapper from the profile directory; retain checkout
through review, evidence collection and verified shutdown. Do not launch while
another owner holds checkout.

## Reproduction

All builds use fresh output directories. From the Pi repository, build and check
the MOS source snapshot, then generate symbols and fixture inputs:

```bash
UART0_BUILD_DIR=build/uart0-startup-safe/runNEW bash tools/zds/build.sh
ruby experiments/uart0-mos/symbols.rb build/uart0-startup-safe/runNEW
.venv/bin/python experiments/uart0-startup-safe/source_guard.py build/uart0-startup-safe/runNEW
.venv/bin/python experiments/uart0-startup-safe/prepare_fixture.py build/uart0-startup-safe/runNEW
```

Copy that build and these scripts to the corresponding Oryx project paths using
the canonical network configuration. Preserve the frozen runtime, VDP, SDK and
UART-oracle dependencies recorded in the archive; the CPU oracle hash is
`9aa4e2011e4573f4ed92611b7ab505ca72d8ef21ef43081b7c8e1c58afb1200a`.
On Oryx, compile the original application/native children:

```bash
bash experiments/uart0-startup-safe/remote_fixture.sh build/uart0-startup-safe/runNEW
```

Before any emulation, reserve/check out a finite tranche through the shared Pi
scheduler. Set `UART0_ORYX_LEASE` on Oryx to its returned token. The test runners
assert `agon-mos` ownership against that shared authority immediately before
each emulator process. CPU harness execution also requires checkout.

```bash
.venv/bin/python experiments/uart0-startup-safe/qualify_cpu.py build/uart0-startup-safe/runNEW
.venv/bin/python experiments/uart0-startup-safe/flexe.py build/uart0-startup-safe/runNEW jit --fixture fixture --attempt final
.venv/bin/python experiments/uart0-startup-safe/flexe.py build/uart0-startup-safe/runNEW interp --fixture fixture --attempt final
.venv/bin/python experiments/uart0-startup-safe/flexe.py build/uart0-startup-safe/runNEW jit --fixture fixture --attempt wrongrom --wrong-rom
```

`qualify_cpu.py --reject-build build/uart0-startup-safe/run003` additionally
replays the retained bad-RST image as a negative control. The keyboard/updater
check requires a separate disposable profile from `prepare_review.py --name
uart0-startup-safe-keysNEW`, and the verified official `flash.bin` in the build
directory. Run `interactive.py --attempt keysNEW` with the same build argument.
The utility hash must match `480b476703b798cf8d93294cac42d77cad93f7747003b061520b86685c75eb57`.

Preserve receipts, raw output and numbered reports; verify that owned collectors
and emulators stopped; release with fresh whole-host idle evidence and steer the
next queued agent immediately. The completed runs preceded this session's notice
of the new scheduling procedure; their receipts do not claim a lease. Subsequent
launches require it. Creating a stopped profile and offline analysis need no
emulator checkout.

The verified full archive is
`build/uart0-startup-safe-20261031-r01.tar.gz`, SHA256
`f20322d4d98b0ef760ca68ea5df50cc5743456c2921f87427687983ea4ac9cd5`.
It preserves early attempts, final sources/binaries, build output, CPU runners,
raw emulator evidence and frozen runtime inputs on Pi and Oryx. The current
lease guard was added afterward; executed harness sources remain separately
preserved under `provenance/executed-harness`. Verification details are in
`build/uart0-startup-safe/archive-verification.json`.

## Deliberate-reset fixture — BO-004 implementation, 2026-11-01

The completed normal hardware campaign remains passed. This next fixture is a
new original AgonDev application in `experiments/uart0-reset`; it uses the exact
already-tested ZDS II MOS and matched VDP. No firmware change or new flash is
needed to exercise it. It extends the existing numbered suite while leaving
Run all restricted to the ordinary tests.

| Choice | Behavior |
| --- | --- |
| 5 | Sustain three queued immutable spans for a sixty-second reset window |
| 6 | Disable interrupts and halt the application partway through a VDP buffer write |
| 7 | After reboot, verify the pending run and fresh stock transport |

Preparation first observes an ACTIVE descriptor with some, but not all, source
bytes accepted. It saves a CRC-protected `reset.arm`/`Xnnnn.dat`, run number,
build/ROM identity and observed state, appends PENDING to the sequential journal,
and closes its report/metadata files. It finishes the preparation transfer before
reusing its source storage. Only then does it publish a RESET NOW display and
new traffic. During the reset window it performs no filesystem calls. No UART
register, startup routine or firmware interrupt handler is modified by the app.

Mode6 deliberately stops refills after the on-screen message and part of the
first256-byte VDP payload. The incomplete command and borrowed descriptor are
expected. A stationary screen is not PASS: the operator must power-cycle the
whole board, reopen the appliance, choose7 and confirm Y. The verifier checks
zero initialized/batch/ticket/synchronization state, the original UART vector,
a closed session, the same ROM and a successful stock GP query/reply before
committing RESET PASS. Automated tests label simulated resets separately from
physical qualification.

Mode5 cannot silently turn an unperformed reset into PASS. At expiry it drains
and restores stock output, displays DO NOT RESET, and waits for E before saving
EXPIRED. All fixture-owned writable files stay closed until that acknowledgment.
A pending/corrupt/unreset/expired record is not sufficient for PASS. New reset
runs are refused while one is pending; normal activation tests are also blocked
in the interactive menu until the pending reset is verified. Numbering does
not depend on the unreliable Agon RTC.

Physical instructions will use whole-board OFF/ON, not an assumed eZ80-only
reset: a VDP left expecting packet bytes may need its own reset. No SD writes
or firmware/programmer operations have been performed for this new fixture.
The new source remains uncommitted pending its separate human emulator review.

### Reset qualification result and next procedure

The new fixture is developed and passes automated qualification. Exact menu:
`build/uart0-reset/run003/fixture/test.bin`, build `13839d236311480e`, SHA256
`e1bc61d1f989bf3af457b8255b8b93a4caaccc6dee546bfcdbe7efce32ce27b3`.
MOS remains SHA256 `89ea8694194e0488337bf1dcbfa91e2b084b3afc75a9c3916f4acc9ae12aa42b`;
no new firmware installation is required.

Both engines pass continuous-send and partial-packet reset/restart, with actual
20 ms recovery-menu taps7/Y/Q and a working CLI afterward. The controlled-stop
captures each end47bytes into a256-byte buffer payload. Both engines also pass
the ordinary four tests. Missing, unreset, corrupt, wrong-ROM and expired controls
all refuse reset success. Sixteen process phases/eleven outcomes completed in
531.691seconds. The first capture checker matched preparation prose rather than
the actual READY title; that failed attempt is retained and the matcher fixed.

The new verifier labels simulated resets as software evidence; physical
qualification remains pending. The nominal minute window uses MOS's frame-driven
clock (7200ticks), not RTC timestamps; display refresh can affect its duration.
If expiry is reached, do not reset during the subsequent acknowledgment/save.

The stopped review profile is
`/home/smith/Agon/mystuff/agon-mos/.emulator/uart0-reset-bo004-review`.
It opens the menu without activation. Reserve/check out under the canonical FIFO
when the Author is ready; the Author launches the generated wrapper. For each
mode5then6: wait for RESET NOW, close/reopen the emulator, choose7thenY, require
UART0 RESET RECOVERY PASS, thenQandDIR. Mode6 deliberately freezes; that is the
expected trigger, not the test result. On physical Console8 the matching action
is whole-board power OFF/ON, then reopen the appliance and go straight to7/Y.
Do not run activation tests between reboot and verification. A generic stall
before RESET NOW is not a valid reset trial. Runall does not include5/6.

Reproduce from the repository on Pi with:

```bash
.venv/bin/python experiments/uart0-reset/prepare.py build/uart0-reset/runNEW
```

Transfer the fresh build and reset source to the matching Oryx project paths,
then compile there using the retained SDK and ZDS child toolchain:

```bash
bash experiments/uart0-startup-safe/remote_fixture.sh build/uart0-reset/runNEW
```

For headless qualification reserve a finite600second tranche, export its returned
`UART0_ORYX_LEASE` onOryx, then run `experiments/uart0-reset/qualify.py` with that
build argument and a fresh `--attempt` name. It asserts ownership before every
frontend launch and stops its owned processes after each phase. Prepare the
stopped review with `--attempt bo004 --review --qualified-attempt q004` (or
the chosen qualification attempt) only after its receipt matches the menu hash. No reservation is retained for offline analysis.

Full source, failed attempts, raw phases and frozen runtime are retained on both
hosts in `build/uart0-reset-q004-evidence.tar.gz`, SHA256
`0f7866e5ee497e642271a691275b0e1b4bd29305ffeb7e3ae1f041069d513d4b`.
All509ordinary files are verified onPi. New source remains uncommitted pending
human review; the completed prior tranche was pushed before this work began.

## Reset appliance hardware deployment, 2026-11-01

LATEST 2026-11-01 — RESET APPLIANCE DEPLOYED TO CONSOLE8 CARD.
Author selected direct hardware testing because the emulator is heavily demanded.
AGONC8 UUID8658-1C23, same /test/mos-uart0; 22 package files verified,
87 numbered evidence files plus runs.log retained. Next report R0037.
Existing firmware was replaced for other projects: Author must flash BOTH
mos-candidate.bin (file CRC29DCC1FC, ROM CRC0C5886FC) and vdp-test.bin
(RX sync fixed). No physical flash or execution performed by this agent.
New test.bin SHAe1bc61d1...ce27b3, build13839d236311480e.
Protocol: menu5 -> RESET NOW -> whole-board OFF/ON -> reopen7/Y;
then menu6 -> RESET NOW controlled freeze -> whole-board OFF/ON -> reopen7/Y.
Require RESET RECOVERY PASS and working CLI after each. Go straight to7 after
reboot. Expired mode5 is NOT PASS; E saves expiry before retry.
Card left mounted. Root MOS.bin/autoexec and prior reports unchanged.
Predeployment archive verified on Pi: build/uart0-reset/card-deploy001/before.tar.gz
SHA256 3c2d9dd66f773977e823102f48496ea9d0a67cdea84522715709d418b415a37a.
Deployment receipt/package scripts are in the same directory. Physical acceptance
remains pending. No emulator reservation or launch. Earlier next-GUI-review and
already-installed-pair statements are superseded for this hardware round.

## Console8 reset results and scope

2026-11-01 — Console8 deliberate-reset tests PASS; BO-004 complete.
R0037 mode5 continuous sending and R0038 mode6 controlled mid-packet stop both
have operator-Y power-cycle confirmation, valid CRC-protected VERIFIED records,
matching build13839d236311480e and installed MOS CRC0C5886FC. Each verified fresh
disabled transport state, original UART handler and successful stock-path VDP
query/reply after reboot. This establishes whole-board power-cycle recovery;
it does not establish CPU-only-reset parser recovery or precise reset timing.
All previously deployed assets/reports unchanged, journal prefix preserved.
117 returned files verified on Pi; archive build/uart0-reset/card-return001/before.tar.gz,
SHA256 ce4cb28c70325aaaa941a8ba09b74b63bae6fae80012bf5d317a9e6c5c1865fe.
Reproducible checks and results: card-return001/analyze.py and analysis.json.
Card read only and left mounted; no emulator launch or firmware flashing.

Scope decision: Author cautions against excessive recovery machinery for a hobby
computer, particularly EMOS flash pressure. This fixture added ZERO MOS/VDP code:
its pending records, CRC checks, reset menu and reports are standalone test-app
code. Do not add production crash-recovery machinery on the strength of this
edge-case test. Keep stock startup/explicit opt-in, ordinary correctness and
measured CPU/throughput benefits central. Evaluate any proposed firmware growth
against practical benefit and EMOS space cost; CPU-only reset recovery remains
outside this completed task, not an automatic next work item.
