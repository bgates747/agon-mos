UART0 PAUSE / FULL-DUPLEX TEST - HEBER CONSOLE8

The current fixture always lives at /test/mos-uart0.
Previous fixtures and their results are archived before replacement.
No Extender, wiring changes or logic sniffer are needed.

MOS is unchanged from the passing diagnostic benchmark:
  mos-candidate.bin: 110695 bytes, CRC32 7E66FD09
  SHA256 e7fc0732fba1ba6f94a30cc4bdab7e740c51a2b066cc35259f2abfc101fa848a
VDP is stock Agon Platform 2.16.0, unchanged:
  vdp-2.16.0.bin: 1077840 bytes, CRC32 FFFBFADE

If these versions are already installed from the passing run, do not flash
again. The copies here identify the required firmware. /MOS.bin at the SD
root is NOT this candidate. Firmware changes are manual and separate from
running the test; use the known flash/recovery procedure if needed.
The prior bundle's firmware utility, notices and plain-text flash guide
are included here as flash.bin, *LICENSE.txt and firmware.txt.

Keep test.bin and checks.bin together. At MOS:
  CD /test/mos-uart0
  LOAD test.bin
  RUN

The test selects single-buffered mode 0 and clears the screen. Allow about
one minute; physical timing is unmeasured. If it takes longer than 2 minutes,
something is wrong. Report the last progress line; a stall is not PASS.
No keyboard input is required during the test.

Expect setup PASS, then cases 1/4 through 4/4, with pauses of 0, 1, 4 and 8
video frames. Each sends 8192 payload bytes and requests 32 ordered replies.
It requires replies before TX drains, then verifies every receiver byte.
Each case prints verification 1/4 through 4/4 complete and Case PASS.
Finally expect UART0 STRESS FIXTURE PASS and return to the MOS prompt.
Check that typing DIR still works. The test uses scratch VDP buffers
0x6AF0..0x6AF4 and clears them afterwards. It leaves display mode 0 selected.

Success creates stress.dat (76 bytes) and baseline.dat (3 bytes). Return the
card with these files. Keep a photo of the final screen. A detected failure
saves failure.dat and prints UART0 STRESS FAIL, then waits for reset.
If TX itself remains blocked, it retains source memory and may not print a
failure or return. Reset manually if the 2-minute expectation is exceeded.
It never frees borrowed memory or resets UART FIFOs to escape a CTS stall.

For a repeat run, first preserve or rename stress.dat, baseline.dat and any
failure.dat; existing report files can otherwise be stale or cause a save
failure. Return the card for inspection before overwriting test evidence.

A PASS verifies this software workload. It does not establish electrical
CTS headroom, calibrated timing or game performance. See capture.txt for
what remains measurable and why the expansion header is not a UART0 port.
