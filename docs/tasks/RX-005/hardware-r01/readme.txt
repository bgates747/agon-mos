RX-005: VDP -> EZ80 COUNTED RETURN TEST
Directory: /test/mos-uart0

Flash BOTH staged firmwares, VDP FIRST, using the installed flash command.
1. cd /test/mos-uart0
   flash vdp vdp-rx.bin
2. After the updater finishes/reset, return to this directory:
   cd /test/mos-uart0
   flash mos mos-rx.bin
Keep the normal updater checks; allow each update to finish.
MOS file CRC32: 3933C3ED. Its startup banner retains Eirene RC3 branding.

Only AFTER BOTH firmwares are installed, reboot if required, then run:
   cd /test/mos-uart0
   test
Your original autoexec.txt is preserved; this test does not run at boot.
The app verifies the exact RX-005 MOS before issuing its private syscall.

Do not type during the numbered cases. When this line appears:
  RX005 KEY READY: press and release A once.
press and release A ONCE promptly (within about20 seconds). Do not hold it.

Allow less than2 minutes for the run, including the keyboard step.
Expected end: RX005 SUITE PASS, then RX005 RETURN PASS and the MOS prompt.
It checks0..512 bytes, guards, callbacks, discards, rearms and real keys.
A stall or FAIL is failure. Note the last progress line; do not rerun
or continue to other tests while a failed transfer is live.

One complete pass is sufficient for this hardware round. Return the card
to Oryx for inspection. Reports start at R0067.log; repeats use higher numbers.
No performance/CPU percentage is claimed by this integrity test.

Restoration, only when wanted: flash vdp vdp-stock.bin / flash mos mos-stock.bin
Leave the test pair installed while this Console8 remains dedicated to tests.
Old UART appliances/reports are archived in the project on Pi/Oryx.
