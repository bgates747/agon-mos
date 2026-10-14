# UART0 receiver occupancy experiment

This MOS-owned experiment implements TX-020: probe-free Console8 measurements
using a diagnostic build of stock VDP 2.16.0. Olimex probing stays deferred.
Production MOS and the shared Flexe runtime are unchanged. No physical firmware
has been flashed by the agent. Human review and physical Console8 run R0003
pass all 42 payload checks. Stock threshold 64 leaves 62 observed FIFO slots;
electrical timing and a worst-case guarantee remain unmeasured. See
[physical-results.json](physical-results.json).

See [readme.txt](readme.txt) for the operator procedure. This is separate menu
option 7; baseline run-all retains the previously qualified tests. A stock VDP
restore option accompanies the staged diagnostic image. Reports use existing
sequential numbering and the running log.

`build.sh` prepares a clean archive of upstream VDP commit
c7ac293d2aa81ddfa693390549bcd909069c8fc3, pins its libraries, builds with
PlatformIO/Arduino ESP32 2.0.14 (IDF 4.4.6), and builds the native host fixture
with ZDS II under Wine on Oryx. `source.json` in the build directory records
source and dependency identities. Upstream source directories are read-only.
The diagnostic extension retains upstream MIT attribution to Dean Belfield
and the existing VDP/library contributors. Existing upstream license notices
remain in the archived sources. New project additions are MIT, as specified
by the Author.

Private command VDU 23,0,0xE7 supplies HELLO, ARM and serialized report reads.
It deliberately avoids Golem's D8/D9 commands. ARM accepts thresholds 1..127
and pauses 1..20 ms. The fixture uses seven thresholds, two durations and
three repeats. Only UART2 receive interrupt sources are masked; hardware
flow control, transmit interrupts and system interrupts remain enabled.
The code records empty-before-arm conditions, threshold readback, hardware
flow-control state, raw errors, peak/settled FIFO occupancy and settling time.
It restores saved RX enables and the threshold before count/CRC verification.
FIFO length uses IDF's ESP32-specific pointer-aware helper.

Raw verification reads the existing IDF driver in nonblocking chunks. An
intermediate Arduino per-byte reader stalled under JIT at case 9; that
candidate was not deployed. The exact emulator cause was not established.
The replacement passed both engines and deliberate bad-CRC/missing-EOT
controls. Missing-EOT is bounded; source memory remains retained until MOS
has drained transmission. The native host also handles missing diagnostic
firmware as SKIP rather than pretending to measure stock VDP.

`analyze.rb` validates the 2028-byte versioned URMHOST1 report. It distinguishes
FIFO overflow from protocol errors, signal errors, unexplained data loss and
invalid measurement conditions. Even `--physical` reports empirical evidence
only; electrical CTS edge timing and worst-case physical qualification remain
unproven. Emulator FIFO counters are expressly unqualified.

Primary implementation references:
- https://docs.espressif.com/projects/esp-idf/en/v4.4.6/esp32/api-reference/peripherals/uart.html
- https://github.com/espressif/esp-idf/blob/v4.4.6/components/hal/esp32/include/hal/uart_ll.h
- https://github.com/espressif/esp-idf/blob/v4.4.6/components/soc/esp32/include/soc/uart_reg.h

To exercise the integrated menu after building `uart0-suite`, run on Oryx:

```sh
.venv/bin/python -B experiments/uart0-margin/profile.py --menu-auto
.venv/bin/python -B experiments/uart0-margin/qualify.py jit --menu
.venv/bin/python -B experiments/uart0-margin/profile.py --menu-auto
.venv/bin/python -B experiments/uart0-margin/qualify.py interp --menu
.venv/bin/python -B experiments/uart0-margin/profile.py --menu
```

The last command prepares a stopped human-review profile. Launch its
`flexe-agon-emulator` wrapper manually; choose 7 and then Q. VDP flashing is
blocked in the emulator. Firmware binaries and licenses are bundled off-device
with `package.rb`; physical deployment remains a separate operation that must
verify the Console8 card identity and prior manifest. Preserve `/MOS.bin` and
all numbered reports. Reuse `/test/mos-uart0/test.bin` without SD history folders.
