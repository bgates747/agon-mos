# Console8 UART0 qualification fixture

Executive summary: this off-device tranche prepares the accepted MOS candidate,
paired blocking/async work and a Console8 rollback procedure. Physical
qualification remains TX-006. The Author performs manual flashing/testing and
authorized staging on the Oryx SD card; agent access to the board or its USB
ports still needs a fresh explicit bench grant. The fixture uses public MOS calls
and the existing VDP protocol. Its results do not establish receiver headroom.

## Reproduce and review

From this checkout, `bash experiments/uart0-bench/build.sh` stages a native ZDS II
assembly/link under Wine and two headless Flexe runs on Oryx. It preserves the
accepted production profile and uses `.emulator/uart0-bench` instead. Runtime
binaries are the previously accepted cached copies pinned by
`experiments/uart0-mos/runtime.sha256`; no other owner's emulator is rebuilt.
Evidence and binary artifacts live under ignored `build/uart0-bench`.
The delivered run is recorded in `results.json`: 42.802 seconds JIT and
56.132 seconds interpreter, excluding initial setup/build/retrieval. Both
compare 65,536 receiver bytes. These wall times are review-duration guidance,
not physical performance results. The offline tools pass 14 negative controls.

For TX-012, run locally on Oryx after automated qualification:

```bash
cd ~/Agon/mystuff/agon-mos/.emulator/uart0-bench
./flexe-agon-emulator --precise-interrupts
```

Expect `UART0 BENCH FIXTURE PASS`, `UART0 BENCH RETURN PASS` and `/uart0 *`.
Type `ECHO UART0 KEYBOARD PASS` and confirm the response and normal prompt,
then exit. The wrapper removes only this emulated fixture's prior report files.
The agent does not launch graphical instances. The Author passed TX-012 on
2026-10-13, supplying the expected PASS markers and prompt, successfully typing
`ECHO UART0 BENCH FIXTURE PASS`, then confirming "looks like pass to me".
TX-011/TX-012 are accepted; physical qualification remains pending.

## What the application measures

Four pairs alternate blocking/async order. Each timed case transmits the same
8,210-byte packet, performs the same 131,072 arithmetic iterations and waits
for TEMT. The blocking case begins with a closed session and uses legacy RST18;
the async case reserves/publishes through the installed API. Both include one
session open. Timer readings use an atomic snapshot of the existing MOS clock;
no UART/vector/timer is taken over. Close, receiver checks and SD I/O are untimed.
Elapsed values are modulo-24-bit raw MOS ticks, without seconds calibration.

The async overlap count covers only complete 256-iteration chunks whose ending
poll still reports BUSY. It is a conservative work-overlap observation, not a
measurement of all recovered CPU cycles. Low-resolution clock results can tie.
The fixture does not force CTS, inject keyboard packets or qualify every
full-duplex workload.

The VDP holds an 8,192-byte reference and compares every received byte using
buffer-to-buffer conditional calls. A mismatch sets a sticky byte; the reply
returns that byte through the normal MOS GP parser. A deliberate bad-byte probe
must fail, followed by a good-byte probe that must pass. Verification is paced
with a receiver-execution reply after each group of four comparisons. This keeps
the untimed verification stream separate from the measured transmission.
Scratch buffer IDs are 0x6af0 through 0x6af4; they are cleared at start/end.
Do not run alongside an application using those IDs. Immediate-byte comparisons
are avoided for compatibility with the VDP source's signed accumulator behavior.

Development runs with unpaced / 256-command comparison groups stalled the
pinned interpreter during closed-session legacy output. Four-command groups
pass both engines; the underlying cause is not established. The timed packet
is unchanged. No MOS or emulator source fix is claimed by this pacing choice.

`bench.dat` is a 148-byte binary report: eight-byte `UART0BN1` magic, version1,
stage0, record-count8, error0, then eight 17-byte records. Record fields are mode,
pair, elapsed-u24, checksum-u24, overlap-iterations-u24, accepted-u24, RX errors,
modem deltas and receiver result. Nonzero stage, incomplete records or
`failure.dat` indicate a failed run, never usable measurements. `SAVE` creates
new files; on physical repeat runs retain/rename previous reports before running.

```bash
ruby experiments/uart0-bench/analyze.rb report build/uart0-bench/evidence-jit/bench.dat build/uart0-bench/expected.json
ruby experiments/uart0-bench/check-tools.rb
```

## Frozen package and preparation boundary

The off-device package contains the diagnostic-epoch candidate (110,695 bytes, SHA-256
`e7fc0732fba1ba6f94a30cc4bdab7e740c51a2b066cc35259f2abfc101fa848a`),
its map, bench/check files, hardware-readable `readme.txt`, evidence readers,
headless receipts, original MIT notices, stock VDP 2.16.0, a manifest with
CRC32/hashes, and the pinned official
[agon-flash v1.9](https://github.com/AgonPlatform/agon-flash/releases/tag/v1.9).
Flash binary SHA-256 is
`480b476703b798cf8d93294cac42d77cad93f7747003b061520b86685c75eb57`.
Package creation refuses an existing output and refuses changed/unqualified
artifacts. It does not copy to SD, rewrite autoexec or invoke flashing.

`vdp-2.16.0.bin` is the official stock release image, SHA-256
`b807beef35823b13a0a056f11b7464cd1b1c6356dce0e4098b78ebe059ded35f`,
1,077,840 bytes, CRC32 FFFBFADE. No Golem module loader or Extender firmware is
required by this fixture. The accepted emulator used a Golem-built VDP snapshot
reporting 2.16.0, SHA-256 `31d25eec...`, rather than this release binary; the
stock image's physical qualification remains pending. See the official
[2.16.0 release](https://github.com/AgonPlatform/agon-vdp/releases/tag/v2.16.0).

```bash
bash experiments/uart0-bench/fetch-flash.sh
bash experiments/uart0-bench/fetch-vdp.sh
ruby experiments/uart0-bench/package.rb build/uart0-bench/console8-manual-20261013
cd build/uart0-bench/console8-manual-20261013
sha256sum --check SHA256SUMS
```

For the Author's manual workflow, stage this new package under
`/test/mos-uart0` on the SD card. On the Console8, use
`CD /test/mos-uart0` then `TYPE readme.txt`. The text includes separate stock-VDP
and candidate-MOS flash commands, CRCs, backup, expected manual PASS output,
repeat-run report preservation, restoration and result collection. The manual
test does not print the emulator autoexec's BENCH RETURN marker.

Run the physical-only deployment tool with the Oryx project `.venv`, an exact
mounted-card path and UUID. It verifies the package, requires a removable FAT
device with the matching UUID, refuses an existing destination, copies only
that new directory, flushes and verifies hashes, and writes a host receipt.
It never flashes firmware or modifies emulator profiles. A `--dry-run` mode
performs the same preflight checks without writing. The card identity is
recorded in the deployment receipt, not baked into a reusable script.

## Lease-dependent backup, installation and rollback

For agent-operated physical work, the lease must identify this Console8, its SD card and exclusive bench ownership,
permitted MOS writes/reset, the return condition and an agreed expiry. Record
installed MOS/VDP versions and board identity before changing anything. Check
firmware compatibility against the official
[update guidance](https://agonplatform.github.io/agon-docs/Updating-Firmware/),
including the flash-tool issues listed for VDP 2.8.0, 2.12.0 and 2.13.0.
If versions are unknown or affected, resolve that before any flash.
For VDP 2.15.0, the official 2.16.0 release notes require disabling its sprite
text cursor with `VDU 23 0 &0A 15` before using the flash tool.

Console8 dead-MOS recovery needs an external ESP32 with at least 4 MB of flash
and three jumpers to ZDI, following the official
[Console8 recovery instructions](https://github.com/AgonPlatform/agon-recovery).
Have the correct external programmer and verified connection plan available
before candidate installation. Do not repurpose or reflash the internal VDP.
USB recovery and any programmer wiring need the same explicit bench authority.

After the grant, validate the exact mounted card against the agreed identity,
then copy the package to a **new** `/test/mos-uart0` directory. Stop if it exists;
preserve existing `/mos/flash.bin`, root firmware, autoexec and application trees.
Host `SHA256SUMS` validation applies to this new directory. Eject cleanly.
The Author's 2026-10-13 manual-workflow instruction separately authorizes SD
staging on Oryx; it does not authorize agent-operated board/firmware access.

Before flashing, at the existing MOS prompt:

```text
SAVE /test/mos-uart0/incoming-mos.bin &0 &20000
```

Return the card cleanly to the host, inventory the exact 128 KiB installed-ROM
dump, save a second host copy with board/version/SD identity and timestamp, and
inspect its provenance. The offline reader rejects blank/wrong-length dumps;
it cannot prove that a dump belongs to this board. Never replace this backup
with a stock release download.

```bash
ruby analyze.rb backup incoming-mos.bin
```

Once the backup, recovery availability and lease are verified, return the card.
The packaged flash utility is linked for the MOSlet address; explicit loading
avoids overwriting the installed utility or relying on MOSlet search paths:

```text
LOAD /test/mos-uart0/flash.bin &B0000
RUN &B0000 MOS /test/mos-uart0/mos-candidate.bin
```

Confirm only the named MOS file after checking its displayed CRC32 against the
manifest. Do not use `all`, `vdp`, `batch` or `-f`. After reboot, record boot
versions and save `candidate-readback.bin` with the same 128 KiB SAVE command.
On the host, `ruby analyze.rb candidate candidate-readback.bin mos-candidate.bin`
requires an exact candidate prefix; unused flash tail is not asserted.
Then run the fixture manually with `CD /test/mos-uart0`, `LOAD test.bin`, `RUN`.
Collect `bench.dat`, screen/keyboard evidence and any passive capture. Stop on a
failure; a retained-memory CTS stall requires an explicit reset under the lease.

Unless the Author's lease explicitly requests retaining the candidate, restore
the **installed** backup before handing back the bench:

```text
LOAD /test/mos-uart0/flash.bin &B0000
RUN &B0000 MOS /test/mos-uart0/incoming-mos.bin
```

After reboot, independently `SAVE /test/mos-uart0/restored-mos.bin &0 &20000`.
On the host, `ruby analyze.rb restore restored-mos.bin incoming-mos.bin`
requires all 128 KiB to match. Confirm original boot versions and keyboard/prompt
behavior; retain evidence and hand back the lease. If MOS will not boot, use
the agreed external ZDI recovery route to regain access, then restore the same
installed-ROM backup and verify it. No firmware operation in this procedure
has been performed by preparing this package.

## Passive CTS evidence

Use a separately authorized high-impedance capture on Console8 MOS-TX, MOS-RX
and the physical CTS input. Confirm connector/pin/voltage details against the
actual board revision; no Olimex pin assumptions. Decode both UART directions
at 1.152 Mbaud, 8N1. Export normalized CSV with this header:

```text
kind,time_s,end_s,value
cts,0,,1
tx,0.000010,0.000018680555556,23
cts,0.000014,,0
rx,0.000020,0.000028680555556,128
cts,0.000030,,1
```

`cts` values are logical ready: 1 means the active-low pin is asserted. Include
an initial ready sample and final ready sample bracketing all frames; byte
`time_s` is the start bit and `end_s` the end of the stop bit. Sort by start/edge
time. Byte values are decimal. Remove no framing-error events; reject and
investigate such a capture. Keep original analyzer files and calibration/sample
rate alongside this normalized export.

`ruby analyze.rb trace capture.csv` inventories frames completed/started while
CTS is blocked and their observed tail. It rejects malformed timing, incomplete
CTS intervals and unknown/framing-error rows. This is **observed tail**, not
proof of receiver reserve. TX-006 still needs independent receive-headroom
bounds, controlled stop/restart and full-duplex tests. Do not force or short
CTS electrically as part of this passive procedure. A buffer size in source or
a successful run alone does not establish the required physical margin.

## Progress fixture revision (TX-014)

The loadable fixture is now `test.bin`. Startup clears the screen and states
that more than two minutes indicates a problem. Untimed breadcrumbs show setup,
each pair/mode, transmission drain, four receiver-verification quarters per
case, case completion and report saving. A detected failure prints FAIL before
holding for reset. These changes do not implement an unsafe drain timeout.
The revised fixture requires a new human emulator review before commit.

TX-015 corrects diagnostic attribution. The original fixture checked flags
accumulated since MOS boot, so prior 0x98 alone could reject a clean first case.
That defect is reproduced against the originally accepted ROM. The new MOS
API 1.1 operation atomically returns/clears diagnostic latches while the async
session is closed. No hardware FIFO/parser is flushed. The app saves setup
flags in three-byte `baseline.dat`, prints them, and establishes independent
case intervals. Repeated fresh occurrences of the same bits still fail.
This fixture requires the new MOS image (CRC32 7E66FD09); the API 1.0 image is
rejected with an explicit installation message. The electrical origin/timing
of the original break/framing flags cannot be recovered from that old report.
The SD belongs to the Author's other test and is not accessed for this revision.

Physical SD refresh archives the entire previous owned directory before staging
the new package. `deploy.py --archive-existing <sibling-directory>
--previous-manifest-sha256 <old-manifest-hash>` permits only a recognized prior
deployment; a pre-existing `test.bin` is reported as a collision and never
replaced. Old measurement/failure reports stay in the archive, while other
operator files (such as the installed-MOS backup) are copied forward.
