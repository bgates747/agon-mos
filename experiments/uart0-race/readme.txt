UART0 CONTROLLED RECEIVER DIAGNOSTIC - CONSOLE8

LATEST UPDATE: REPAIRED TEST FIXTURE AND MENU, ONE HARDWARE SESSION
R0009 stopped because the fixture tried to overwrite a checkpoint using MOS
SAVE, which only creates new files. The old hang is reproduced using actual
MOS FatFS in Flexe; the repaired fixture passes that path in both engines.
Checkpoint updates now use explicit overwrite/write/close. They run only
outside the raw payload phase: FAT timestamps send VDP clock commands, which
would otherwise contaminate the data. Both receiver cases and their byte/CRC
checks are retained. This repairs the test, not the suspected receiver race.

From the SAME /test/mos-uart0 directory, LOAD test.bin then RUN. Menu choices
now echo "Selected <key>". Check 9 then 0 with single taps, then choose 8 then 4
for the actual two-case receiver test. No separate menu-only bench run needed.
Require "Setup PASS: repeated checkpoint writes" before Case 1. Case headings,
payload drained/evidence reading, and saved-case messages show progress.

MOS, VDP firmware and flash utility are unchanged from the preceding bundle.
If the VDP still shows "UART0 recovery diagnostic", NO REFLASH is needed.
If stock was restored, use 9 then 2 and confirm the diagnostic reboot banner.
After the test, restore stock with 9 then 4 and confirm its normal banner.
Return the card even after PASS; previous and new numbered reports are retained.

WHY: Short and extended stock-VDP tests passed. This separate diagnostic
widening of an ISR timing window asks whether the suspected recovery ordering
can be observed on the physical ESP32. A forced diagnostic result is NOT a
natural stock-firmware failure and NOT approval of a receiver repair.

FIRMWARE: Keep the old tested experimental MOS (menu ROM CRC32 239097B7).
THIS TEST NEEDS THE NEW DIAGNOSTIC VDP; it cannot run under stock VDP.
The agent has only staged files. YOU perform firmware flashing and reboot.

From MOS, at the SAME location as earlier tests:
  CD /test/mos-uart0
  LOAD test.bin
  RUN
Choose 9, then 2 to flash vdp-race-diag.bin with the staged flash utility.
Check its filename/CRC, confirm the utility's prompt, and require completed
update with no error. Utility return code 0 alone does not prove success.
Reboot. Require VDP 2.16.0 with subtitle "UART0 recovery diagnostic".
Do not flash root /MOS.bin; no new MOS image is needed for this test.

Then use the same CD / LOAD / RUN commands and choose 8, then 4.
The test checks its diagnostic handshake and records a sequential run number.
Case 1: no ISR timing pause; normal driver recovery is the control.
Case 2: bounded ISR pause before the UART lock allows other-core recovery.
The receiver records the actual stores/state, then performs a diagnostic
rescue after capture to let queued source data drain. Each case checks all
4096 raw payload bytes by count/CRC. Normal CTS and the 64-byte threshold stay.

ALLOW TWO MINUTES. Physical duration is not yet measured. If no progress for
two minutes, something is wrong: photograph the last line, reset manually,
and return the card. The test clears its screen and shows each case.
Captured data is saved before the test returns; safe memory retention may
require reset if transmission cannot drain. A stall is never PASS.

EXPECTED HARDWARE RESULT:
  CONTROLLED RECEIVER DIAGNOSTIC PASS
  TEST 12 PASS
  Run NNNN: PASS
This means the expected diagnostic ordering and recovery payload checks
passed on this board. It does not demonstrate a naturally occurring race.
INCONCLUSIVE / PENDING means the required ordering/state was not established.
FAIL means transport/integrity/reporting checks failed. SKIP means the needed
diagnostic firmware handshake was absent. Preserve and return the card for
any outcome. Do not repeat a failure merely to obtain a PASS.

FILES: Unnnn.dat completed evidence; Onnnn.dat progress checkpoint;
Vnnnn.dat failure if it could be saved; Lnnnn.dat pre-test RX epoch;
Rnnnn.log and runs.log contain the menu journal. Keep all prior results.
The saved run uses sequential numbers, not the unreliable Agon clock.

RESTORE STOCK VDP AFTER THE TEST:
Back in the suite, choose 9 then 4 (vdp-2.16.0.bin); require no update error.
Reboot and confirm normal VDP 2.16.0 WITHOUT the diagnostic subtitle.
Report the diagnostic banner, final test outcome/last progress line and
whether the stock banner returned. Return the card even after PASS.

Firmware and restoration files, checksums, notices and source archive are
beside test.bin. Previous baseline/A-B tests remain available. Diagnostic
flashing and this test are not included in run-all. No probes or wiring needed.
