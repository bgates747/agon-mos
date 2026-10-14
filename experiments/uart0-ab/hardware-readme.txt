UART0 A/B - CONSOLE8 HARDWARE COMPARISON

The active entry remains /test/mos-uart0/test.bin. At MOS:
  CD /test/mos-uart0
  LOAD test.bin
  RUN
Choose 8 for the controlled A/B test. Use 0 only if you also want the earlier
baseline tests. Firmware is unchanged: keep the existing UART0 candidate MOS
and stock VDP 2.16.0. No flash is required if those are still installed.
The menu prints installed MOS CRC32; expected ROM128K CRC32 is 239097B7.
Stock boot should say VDP 2.16.0, WITHOUT "UART0 CTS diagnostic".

Allow about one minute; if it takes longer than TWO MINUTES, something is wrong.
Record the last repeat/mode/phase line, reset and return the card for inspection.
A stall is FAIL, not PASS. The test clears the screen and prints each phase.
Modes: 0 blocking MOS, 1 current async, 2 grouped CTS scalar, 3 chunk accounting,
4 OTIRX chunk copying. Phase 0 sends bulk bytes; phase 1 paces735-byte payloads.
There are30 phases: three passes, with reverse mode order in the middle pass.

Expected: UART0 A/B PASS, TEST 8 PASS, Run NNNN: PASS, then a key returns to menu.
Q returns to MOS. Each selection reserves a new sequential run number, using
the existing runs.log. Results are Axxxx.dat; failure dump Xxxxx.dat; journal
Rxxxx.log. If a stall prevents saving, the reserved journal remains incomplete.
Do not delete runs.log or numbered reports. Repeated selections use new names.

WHY THIS TEST: Flexe reproduced a VDP receive-driver recovery race that can
leave RX interrupts disabled. This is an explicitly requested physical
comparison, not a claim that the emulator problem has been repaired. The
emulator failure and a possible hardware failure are separate observations.
The same kernels/workload are used; only relocation and menu reporting changed.
Return the card even if the screen reports PASS so all30 records can be checked.

Reports contain raw MOS ticks, useful-work counts, IRQ counts and late feeds.
Ticks are uncalibrated until independent timing is supplied; they are not exact
CPU cycles. Receiver checks cover735 bytes at each phase end, not every bulk
byte. No audio playback or physical CTS margin is measured by this test.
Required firmware copies/notices are beside this README for manual recovery;
menu9 remains available, but do not flash just to run this comparison.
Menu7 is the separate diagnostic receiver experiment:9/2 installs its
diagnostic VDP and9/4 restores stock. Neither is needed for option8.
