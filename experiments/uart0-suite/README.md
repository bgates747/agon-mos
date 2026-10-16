# Reusable UART0 qualification suite

The suite collects the accepted UART0 software checks behind a numbered C menu,
with individual selections, run-all, sequential evidence and explicit staged
firmware choices. MOS and native fixtures retain the ZDS II build. The Author
allowed AgonDev specifically for this menu. Automated qualification and human
review are recorded separately in results.json. Physical baseline and receiver
experiment campaigns pass; stock-threshold observed reserve is 62 FIFO slots,
with electrical timing/worst-case qualification still unmeasured.

## Operator use

Keep the active hardware entry at `/test/mos-uart0/test.bin`. Follow readme.txt
beside it: `CD /test/mos-uart0`, `LOAD test.bin`, `RUN`. Keys 1–6 select baseline checks, 7 selects the diagnostic receiver experiment,
0 runs all in order 1,6,2,3,4,5, 9 opens firmware/backup choices, Q exits.
A completed selection returns to the menu after a keypress. Individual compiled
checks also support `RUN . 1` through `RUN . 7`; `RUN . auto` runs everything
with calibration honestly marked unmeasured. Firmware is excluded from run-all.

The staged MOS and official VDP 2.16.0 are unchanged from the passing standalone
campaign. The firmware submenu checks and displays image CRC32, then dispatches
the actual upstream flash utility at B0000, with its target/header checks and
Y/N question. N cancels. MOS updates can reset the machine; the request is
journaled as a pending handoff before files are closed. On return, the suite
records UNVERIFIED for zero or FAIL for a nonzero/load error. Agon Flash v1.9
can return zero after VDP updater rejection or cancellation, so zero cannot
certify success. An updater error means failure; completed updates require
readback verification. A reset leaves the handoff pending. Menu 9/3 saves a full
128 KiB MOS backup. Read firmware.txt before relying on a backup or flashing.
No physical firmware access or flashing is performed by build/deployment tools.

Human review exposed `esp_ota_begin` error 258 (ESP_ERR_INVALID_ARG) when the
VDP update was attempted. The frozen app-only emulator VDP has no qualified
OTA target/update path. Its generated review/automatic profiles now configure
`vdp_flash=0`; menu 9/2 logs SKIP without launching the updater. Hardware uses
`vdp_flash=1` and retains the explicit choice. The disposable key harness alone
enables dispatch to test the actual upstream N cancellation, then reloads with
the disabled capability to prove that no updater is launched. No successful
emulated VDP flash or hardware test of this suite is claimed. Preserved review
evidence and its limits are in human-review-failure.json.

## What the tests establish

| Key | Check | Interpretation |
| --- | --- | --- |
| 1 | Entry, before-mode, after-mode/GP, after-VSYNC/GP RX epochs | Historical flags stay separate; fresh trial RX errors fail |
| 2 | Four alternating blocking/async pairs, fixed foreground checksum, eight complete 8192-byte receiver comparisons | Raw tick and recovered-work evidence; stopwatch reference still needed |
| 3 | Pauses of 0/1/4/8 frames; 32 acknowledged replies and 8192 receiver bytes per case | Ordered full-duplex delivery and at least one reply while TX is BUSY; no physical reserve claim |
| 4 | MOS ticks against an operator stopwatch over 10–600 seconds | Manual-key calibration, with raw ticks and external milliseconds saved |
| 5 | Passive capture instructions and remaining CTS limits | PENDING until a separate capture and receiver reserve establish headroom |
| 6 | Ordering, masked-IFF output, callback exclusion, queued application return, ADL=0 | Original installed-MOS integration checks adapted for numbered reports |

MOS exposes GP replies through one last-value byte, not a reply queue. Dense
replies can all reach its RX ISR while foreground polling misses intermediate
values. The suite therefore permits one outstanding GP request: each request
precedes its 256-byte buffer write, and the next round is published only after
that reply is observed and the prior source reaches TEMT. All 32 distinct
values are required; at least one must be observed while transmission remains
BUSY. The accepted dense standalone fixture and its physical evidence remain in
experiments/uart0-stress. The throughput benchmark is unchanged. This revised
workload does not claim maximum reply-rate coverage.

The first attempt to pace dense replies with a VSYNC command after every block
stalled the frozen interpreter during qualification. That version was not
staged. The acknowledged-round design needs only the original initial pause
commands. Failed traces stay in build/uart0-suite, with the causal distinctions
recorded in observer-diagnosis.json.

Source memory is retained until queue completion and UART TEMT, including
ordinary failure cleanup. A permanent CTS blockage can therefore require a
manual reset. Ordinary missing-file or receiver-mismatch failures return to the
menu and preserve earlier evidence; they do not flush FIFOs or steal callbacks,
UART registers, vectors, timers or interrupt ownership.

## Evidence and numbering

Report format version 1 uses R0001.log and an append-only runs.log. A selection
reserves its log before tests begin. The counter takes the highest journaled
run number, skips existing run/result/backup names and stops at 9999. It uses no
RTC value. Completed stages close/reopen files to commit FAT data and directory
lengths. Interrupted runs remain visibly incomplete and keep their numbers.
A firmware handoff interrupted by reset remains PENDING until verified.
Old evidence is never overwritten. Retain runs.log even after moving reports.

B/N/F are benchmark result/baseline/failure; S/P/G are stress equivalents;
D is phased diagnostics; I/J integration result/failure; C calibration text;
M full installed-MOS backup. Run-all shares one number across all checks.
Binary benchmark/stress reports are also embedded in the journal. Headers
record the source build ID, API version, installed full-ROM CRC32 and explicit
operator hardware/VDP labels. VDP labels are not auto-detected. The full-ROM
CRC32 normally differs from the shorter candidate-file CRC32.

Run `ruby experiments/uart0-suite/analyze.rb COPIED_DIRECTORY` on the host.
Keep bench.json and stress.json with results. Packaged analyze.rb carries the
same readers and can be run directly from a copied package. PASS validates a
particular check; a complete run-all normally ends PENDING because CTS margin
needs an external measurement. SKIP distinguishes unavailable APIs/manual work.
Calibration and a passive electrical measurement are not invented by emulation.

For another target, set truthful board/VDP labels in suite.cfg. Feature detection
skips async checks when API 1.1 is absent. Firmware filenames are configurable;
prepare and qualify a package containing any replacement images before staging
them. The current package intentionally supplies the already accepted images.

## Reproduction and memory map

From this checkout, `bash experiments/uart0-suite/build.sh` prepares local
inputs, builds only on Oryx, runs headless qualification serially, prepares a
stopped human-review profile and retrieves evidence. Its project-local AgonDev
v0.22 archive is SHA256-pinned by bootstrap.sh; no global SDK installation or
MOS toolchain migration is involved. Native sources use ZDS II 5.3.5 under Wine.
The frozen MOS-owned Flexe runtime hashes remain unchanged. It executes a Golem
VDP snapshot reporting 2.16.0 with stock command APIs, rather than claiming
emulation of the exact official release binary staged for hardware.

The MOS entry at 040000 copies the C image to 090000, with stack at 0A8000.
Children run at 080000. The upstream flash utility runs at 0B0000; its MOS
buffer occupies 050000–06FFFF and VDP chunk buffer starts at 070000. The menu
and its stack therefore survive the real utility's load, CRC checks and N
cancellation. No `-model:L` compiler experiment is used.

Automated coverage runs two complete suites plus an individual diagnostic
selection on each JIT/interpreter engine, verifies numbered files/journal,
receiver bytes, exact replies, runtime pins, zero overruns/drops/backend faults
and final MOS prompt. A separate input-only SDL shim exercises real menu key
handling, simulated stopwatch input, verified MOS backup, both upstream N
cancellations, unverified-zero logging, a disabled emulator VDP choice, a missing
flash utility after handoff, missing/corrupt children, skipped orphan IDs and
monotonic numbering after individual old reports are removed. It never sends Y. The shim
is confined to the disposable headless profile; the human profile is unmodified.

Create the off-device bundle with package.rb after qualification; it refuses
receipts from different fixture binaries. deploy.py rechecks the removable FAT
UUID, refuses duplicate UUIDs and requires the exact previous manifest and
recognized test.bin before updating the stable folder. It verifies a complete
workspace backup before writing, retains operator files/numbered evidence,
installs test.bin last and verifies copied hashes. It creates no SD history
folder and does not modify root /MOS.bin or other projects. Rediscover the
mount immediately before deployment: another card may be attached or removed.

Human review remains a separate gate. On Oryx use the stopped profile:

```bash
cd ~/Agon/mystuff/agon-mos/.emulator/uart0-suite
./flexe-agon-emulator --precise-interrupts
```

Review numbered selections, run-all (ESC may skip timing), progress, final
status/menu and Q returning to the MOS prompt. Menu 9/3 can verify backup; use
N if inspecting the MOS flash prompt. The VDP choice should report SKIP in this
emulator profile. Changes stay uncommitted until the Author
has reviewed the emulator behavior and explicitly approved committing.

## Credits

This work builds on Agon MOS/VDP and the Agon developers, including Dean
Belfield, Lennart Benschop and the contributors credited by the inherited
sources. AgonDev is maintained by Jeroen Venema and builds on Paul Cawte's AgDev,
CE Programming's toolchain and runtime, LLVM and GNU binutils. Its CRT credits
Paul Cawte, CE Toolchain and Dean Belfield; its printf implementation credits
Charles Nicholson's nanoprintf. The staged flash utility is Jeroen Venema's
Agon Flash v1.9. The test emulator derives from Tom Morton's Fab emulator;
Flexe and the Golem VDP execution backend retain their own source credits.
Preserve the supplied MOS, VDP and flash notices; CREDITS.txt retains the
nanoprintf notice. These credits do not relicense upstream components.
