# Reproduce the VDP UART receive-recovery race

This package contains the matching custom MOS, VDP diagnostics and native test
application used for a controlled before/after test on Heber Agon Console8.
An ESP32 UART interrupt handler can disable reception after the other core has
already recovered it. The repair moves the buffer-full flag update inside the
existing UART lock, alongside disabling receive interrupts.

The unpatched diagnostic deliberately exposes the faulty ordering and then
rescues reception so the evidence can be saved. The repaired diagnostic must
receive every byte without rescue. These tests do not measure the frequency
of the fault during ordinary use.

## Contents

- `sd/firmware/`: matching MOS, before/fixed diagnostic VDP, repair-only VDP,
  official restoration images and a flash utility fallback.
- `sd/before/repair.bin` and `sd/fixed/repair.bin`: identical native fixtures in
  separate, initially empty report directories.
- `source/mos/`: complete custom MOS source and original ZDS II build recipe.
- `source/vdp/common/`, `source/vdp/variants/`, `source/vdp/manifests/`: complete
  VDP/library sources, variant differences and original source-file hashes.
- `source/fixture/`: native application source, generated payload include and
  linker inputs; `source/esp-idf/`: original/fixed UART driver and minimal patch.
- `source/vdp-stock/`: unmodified upstream VDP restoration-release source.
- `tools/`: source materializer/build helpers and independent report decoders.
- `evidence/`: physical reports, interpreted results and source/link audits.
- `licenses/`: applicable notices. `provenance.json` identifies sources/binaries.

From this extracted directory, verify package files with `sha256sum -c SHA256SUMS`.

## Run on Console8

Use a board with a working MOS prompt and its firmware update utility. These
steps replace MOS and VDP; keep the supplied restoration files available.
No Extender, extra wiring or logic analyzer is needed.

Copy the **contents** of `sd/` to `/test/mos-uart0/` on the SD card, keeping its
`firmware`, `before` and `fixed` subdirectories. Use fresh report directories:
the native test uses fixed filenames. Preserve old results elsewhere before
repeating rather than copying old reports into a new test directory.

Install the matched MOS once:

```text
CD /test/mos-uart0/firmware
flash mos mos-candidate.bin
```

Require successful verification and reboot. This is historical MOS 3.0.2 with
experimental UART API 1.1, not stock or the newer callback experiment. Updater
FILE CRC32 is `7E66FD09`; the installed 128KiB ROM CRC in the recorded hardware
run is `239097B7`. Do not substitute a different experimental MOS.

If `flash` is not installed, from the firmware directory use the supplied
fallback: `LOAD flash.bin &B0000`, then `RUN &B0000 mos mos-candidate.bin`.
For VDP use `RUN &B0000 vdp <explicit-filename>`. Retain its normal confirmation
and verification checks.

### Before the fix

```text
CD /test/mos-uart0/firmware
flash vdp vdp-race-before.bin
```

After successful verification/reboot require **UART0 baseline diagnostic**.
Then:

```text
CD /test/mos-uart0/before
LOAD repair.bin &80000
RUN &80000
```

The explicit load/run address matters: the fixture is linked at `&80000`.
It exercises ordinary recovery, then a widened interrupt/reader timing window.
Expect `UART0 RACE DATA SAVED; receiver evidence must be validated.` This
message alone is not PASS; decode the saved record as described below.

### After the fix

```text
CD /test/mos-uart0/firmware
flash vdp vdp-race-fixed.bin
```

After successful verification/reboot require **UART0 repaired diagnostic**.
Then:

```text
CD /test/mos-uart0/fixed
LOAD repair.bin &80000
RUN &80000
```

Expect the same data-saved message. This image contains no executable diagnostic
rescue routine. Both payloads must finish without rescue.

Allow **two minutes per run**. The fixture clears the screen and prints setup,
case and evidence-save progress. If it stops progressing beyond two minutes,
record the last line, reset manually and preserve the reports. A stall or SKIP
is not PASS. SKIP generally indicates the wrong diagnostic VDP is installed.

Each run directory receives `race.dat` (final 332-byte record), `race-step.dat`
(progress), `race-base.dat` (initial MOS RX flags), and `race-fail.dat` if the
failure path can save it. These native filenames differ from the historical
menu's numbered report filenames.

## Validate the result

Return the SD card to a computer with Python 3. From this extracted archive,
pass the actual paths to the saved records:

```sh
python3 tools/check_pair.py /path/to/card/test/mos-uart0/before/race.dat /path/to/card/test/mos-uart0/fixed/race.dat
```

Require `passed: true`. The decoder checks both 4,096-byte payloads per run,
CRC32 `87897582`, RX errors, different-core observations and flag/interrupt
ordering. The baseline must capture the stuck state and require rescue. The
fixed run must need no rescue and finish with RX enabled. The baseline's FIFO
occupancy may vary; the recorded Console8 test captured 66 pending bytes.
Inspect one record with `python3 tools/analyze.py <race.dat>`.

Check the supplied physical evidence without a board:

```sh
python3 tools/check_pair.py evidence/hardware/U0012.dat evidence/hardware/U0014.dat
```

R0012/R0014 are the physical before/after runs. R0017 supplies additional
normal-command compatibility evidence; that larger menu campaign is not a
separate runnable menu in this focused package. The paired native fixture and
its complete source/binary are supplied. `vdp-rx-fixed.bin` has no timing,
recording or rescue hooks, only a private identity query; it is not the paired
before/after diagnostic target.

## Restore when finished

From `/test/mos-uart0/firmware`, use `flash vdp vdp-2.16.0.bin`; require successful
verification/reboot and the normal VDP 2.16.0 Bistromathics banner without a UART
subtitle. To restore MOS, use `flash mos mos-stock.bin` and verify update/reboot.
An updater's return code alone does not prove success.

## Rebuild from source

Compilation is optional for running the supplied binaries. No proprietary
compiler or prebuilt SDK/toolchain is redistributed.

VDP uses PlatformIO `espressif32@6.6.0`, Arduino ESP32 2.0.14 / ESP-IDF 4.4.6.
Complete pinned project libraries are supplied. Install PlatformIO Core, then:

```sh
python3 tools/build_vdp.py before --output build/vdp-before
python3 tools/build_vdp.py fixed --output build/vdp-fixed
python3 tools/build_vdp.py candidate --output build/vdp-candidate
```

These commands materialize complete source, verify every file against the
original manifests, and invoke `pio run`. Outputs are each directory's
`.pio/build/esp32dev/firmware.bin`. Add `--prepare-only` to inspect without
compiling, or `--pio /path/to/pio` to select the CLI. PlatformIO downloads its
public platform/framework/toolchain. The local UART C object supplies the
repaired driver; `libdriver.a(uart.c.obj)` must not also be linked (see audits).

MOS and the native fixture use **ZDS II eZ80Acclaim! 5.3.5** and GNU binutils
`objcopy`. Obtain/install the licensed compiler separately. The included Linux
launcher needs Wine/Xvfb; install it as `~/.local/bin/agon-zds`. It defaults to
`~/.local/share/agon-zds/wineprefix` and Zilog's standard installation path.
See its `AGON_ZDS_PREFIX`/`AGON_ZDS_ROOT` settings; the historical MOS recipe also
uses the standard Zilog Windows include path.

```sh
mkdir -p build/mos
cp -a source/mos/. build/mos/
(cd build/mos && bash tools/zds/remote-build.sh)
bash tools/build_fixture.sh
```

Outputs are `build/mos/MOS.bin` and `build/fixture/repair.bin`. Both clean
rebuilds matched the supplied hardware-test binaries byte for byte. VDP sources
and binaries were audited against preserved original builds. All diagnostic
changes are included in the variant sources; the proposed production fix alone
is `source/esp-idf/uart-rx-full-lock.patch`.

Upstream/dependency notices are preserved. The ESP-IDF driver remains
Apache-2.0, not MIT. New additions are MIT; see `licenses/` and component sources.
