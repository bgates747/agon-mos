UART0 RECEIVER SYNCHRONIZATION REPAIR - ONE CONSOLE8 SESSION

The repair prevents the receiver from switching itself off after the other
CPU has already recovered. Its buffer-full flag and RX-disable now share the
existing UART lock. Both emulator engines pass the before/after comparison:
the baseline exposes the fault; the repaired image needs NO rescue. A separate
candidate with no timing/rescue hooks also passes normal command traffic.
These are software checks. This session is the required physical comparison.

Everything stays at the SAME path. No MOS flash or wiring is needed:
  CD /test/mos-uart0
  LOAD test.bin
  RUN

BASELINE:
Choose 9 then 6 to flash vdp-race-before.bin. Require a completed update with
no error, then reboot. Require banner subtitle "UART0 baseline diagnostic".
Reload the same test.bin and choose 8 then 5.
Expected: BASELINE DIAGNOSTIC PASS: original fault captured and rescued.
The intentional failure/recovery is expected in this baseline only.

REPAIRED DIAGNOSTIC:
Choose 9 then 5 to flash vdp-race-fixed.bin; require no error and reboot.
Require subtitle "UART0 repaired diagnostic".
Reload the same test.bin and choose 8 then 6.
Expected: REPAIRED RECEIVER PASS: all payload bytes recovered WITHOUT rescue.
Both cases must have matching CRCs, no receive errors and rescued=0.
This image has no executable diagnostic rescue function.

CANDIDATE WITHOUT TIMING/RESCUE HOOKS:
Choose 9 then 7 to flash vdp-rx-fixed.bin; require no error and reboot.
Require subtitle "UART0 RX sync candidate".
Reload the same test.bin and choose 8 then 7.
Five phases: RX diagnostics; API/legacy compatibility; legacy/async benchmark;
pause/full-duplex; six-case receiver campaign with every final buffer byte checked.
Expected: CANDIDATE COMPATIBILITY PASS: timing and rescue hooks absent.

RESTORE STOCK:
Choose 9 then 4 to flash vdp-2.16.0.bin; require no update error and reboot.
Require the normal stock VDP 2.16.0 banner without a UART diagnostic/candidate
subtitle. Leave MOS unchanged. Do not flash root /MOS.bin.

Each paired diagnostic should finish within TWO MINUTES. The five-phase
candidate campaign should finish within THREE MINUTES. Physical durations
are not yet measured; these limits allow room beyond emulator observations.
The screen clears at each native test, shows the case/phase and reports
checkpoint readiness. If progress stops beyond its limit, record the last
line, reset manually and return the card. A stall is never PASS.

The firmware submenu prints the selected file and CRC and invokes the existing
flash utility, which asks Y/N. Utility return code 0 alone does not prove an
update succeeded: any updater error is failure. Require the correct reboot
banner. Wrong diagnostic/candidate firmware makes the corresponding test SKIP.

Reports use new sequential run numbers and runs.log; no Agon clock timestamps
are needed. U/O files contain paired evidence, L the RX baseline, V failure
if savable, and R the menu journal. Existing results are retained. Return the
card even after PASS, along with outcomes/banners and stock restoration status.
No firmware flashing is included in run-all; previous tests remain available.
