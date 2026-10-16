CONSOLE8: ORIGINAL A/B WORKLOAD WITH THE REPAIRED VDP RECEIVER

The matched receiver repair tests already passed. This session checks the
original 30-phase workload against the repaired receiver, then repeats the
compatibility and full final-buffer checks. It is experimental qualification,
not a production release or a test of the new MOS batching API.

Same entry point throughout:
  CD /test/mos-uart0
  LOAD test.bin
  RUN

Leave the installed experimental MOS unchanged (menu CRC32 239097B7).
Do not flash MOS or root /MOS.bin for this session.

C8-001 [ ] In menu 9 choose 7 to flash vdp-rx-fixed.bin.
Require no updater error, reboot, and confirm the subtitle:
  UART0 RX sync candidate
Utility return code 0 alone does not prove a successful update.
Reload the same test.bin after reboot.

C8-002 [ ] Choose menu 8 then 1: original controlled A/B comparison.
Expect 30 progress lines, alternating bulk and paced sending across five
modes and three repeats. Allow TWO MINUTES for this selection.
Mode 0 is stock-style blocking output; modes 1-4 are experimental comparison
mechanisms, ending with OTIRX. This fixture supplies those comparisons and
does not require reflashing MOS with the off-device ABI1.2 candidate.
Require PASS. Run this selection THREE TIMES, returning to the menu each time.
Each selection gets a new sequential report number. Never overwrite reports.

C8-003 [ ] Choose menu 8 then 7: candidate compatibility campaign.
Allow THREE MINUTES. Five phases cover RX diagnostics, API/legacy behavior,
benchmark, pause/full-duplex, and six receiver cases with final-buffer byte
checks. Require CANDIDATE COMPATIBILITY PASS.

C8-004 [ ] Choose menu 9 then 4 to restore vdp-2.16.0.bin.
Require no updater error, reboot, and confirm the normal stock VDP 2.16.0
banner WITHOUT any UART diagnostic/candidate subtitle. Leave MOS unchanged.

If any selection exceeds its limit, record the last progress line, reset
manually, and preserve the card. A stall is FAIL, never PASS. Restore stock
VDP using C8-004 if possible. Return the card even if a run fails.

The screen/menu already uses the hardware-confirmed keypress fix. Existing
reports and runs.log remain. Axxxx.dat contains A/B results, Xxxxx.dat a saved
failure when available, and Rxxxx.log/runs.log identify each numbered run.
Report the observed candidate banner, outcomes, and stock restoration banner.

Limits: this repeats the original workload; its A/B result checks reply samples,
not every bulk byte. The compatibility campaign checks every final buffer byte,
not every intermediate overwrite. MOS ticks/useful work are not exact CPU-cycle
or electrical CTS-margin measurements. No new test code or firmware was built.
