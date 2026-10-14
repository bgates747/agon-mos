UART0 CTS RECEIVER EXPERIMENT - Console8, no probes required

This is experimental diagnostic VDP firmware based on stock VDP 2.16.0.
It keeps normal MOS CTS handling enabled. MOS does not need reflashing.
The Olimex is not involved.

First review this suite in the prepared Flexe diagnostic profile.
Emulator results validate the protocol, not physical FIFO/CTS margin.

HARDWARE PROCEDURE (after the diagnostic bundle has been staged)
Keep using /test/mos-uart0/test.bin. Read firmware.txt before flashing.
Menu 9 / 2 flashes the configured diagnostic VDP using the upstream utility.
Flashing and rebooting are manual. A utility return code of zero does NOT
prove that an update succeeded. Confirm the diagnostic boot subtitle and
successful receiver discovery in test 7.
Menu 7 runs the separate receiver experiment. Menu 0 runs baseline tests.
Menu 9 / 4 restores the supplied stock vdp-2.16.0.bin; reboot afterwards.
Do not interrupt an update. Retain your normal firmware recovery procedure.

WHAT TEST 7 DOES
It runs 42 trials: thresholds 64,96,112,120,124,126,127; receive-service
pauses of 5 and 20 milliseconds; three repetitions per combination.
Each trial sends 4096 known bytes, verifies count and CRC, and records
FIFO occupancy, raw UART errors and restoration of receiver settings.
Each trial prints a progress breadcrumb. Allow about one minute;
hardware timing is unmeasured. If it takes over two minutes, something
is wrong: photograph the last progress line and reset, then report it.

The firmware temporarily masks only UART2 receive interrupts; hardware
RTS/CTS remains enabled. It restores the threshold and interrupt enables
before verifying the payload. The production MOS image is unchanged.
Overflow at a deliberately small reserve is useful boundary evidence.
A CRC failure without overflow, framing errors, or invalid measurement
conditions is NOT a trustworthy CTS boundary.

REPORTS
The suite continues its running log and sequential Rnnnn.log numbering.
Hnnnn.dat holds measurements; Lnnnn.dat baseline diagnostics; Ennnn.dat
failure diagnostics when present. No date or RTC is used for numbering.
Offline: ruby margin-read.rb Hnnnn.dat margin.json --physical
In an emulator omit --physical. Neither output certifies electrical timing.

INTERPRETATION
ESP32 UART FIFO capacity is 128 bytes. RTS changes when occupancy exceeds
threshold T. At valid settled occupancy C, observed remaining space is
128-C and inferred additional bytes after threshold crossing are C-(T+1).
Stock threshold is 64. These are empirical observations for this exact
board/firmware/workload, not a worst-case guarantee or CTS edge timing.
Invalid counters must be rejected. Keep stock baseline and repetitions.
