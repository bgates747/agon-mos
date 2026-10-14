UART0 RECEIVER RECOVERY - CONSOLE8 / STOCK VDP

WHY: Flexe has shown a receiver race that can stop communication. We are
checking whether the real Console8 stalls under a finite, repeatable workload.
A PASS covers this run only. It does NOT rule out a rare race. A stall alone
does NOT identify its cause.

FIRMWARE: KEEP the previously tested experimental UART0 MOS and STOCK VDP.
No flash is needed if the MOS menu CRC32 is 239097B7 and boot shows normal
VDP 2.16.0 WITHOUT "UART0 CTS diagnostic". This test uses the existing
experimental per-byte async API; it does NOT test the new batching firmware.
The menu checks the known MOS image. The VDP label is operator confirmation,
not a flash readback. Please note the normal boot banner before running.

START (same location as previous UART tests):
  CD /test/mos-uart0
  LOAD test.bin
  RUN
Choose 8 (Controlled experiments), then:
  1 Previous A/B comparison
  2 SHORT receiver-recovery campaign: six cases
  3 EXTENDED campaign: 24 cases
  0 Previous A/B then short receiver-recovery campaign
  Q Back
Recommended first run: 8, then 2. If it passes, 8, then 3 is available.
Top-level 0 runs the previous baseline suite, A/B and short recovery campaign.
Top-level 9 retains staged firmware/backup operations; do not flash just to test.

TIME / PROGRESS:
Short: allow about TWO MINUTES; hardware duration has not yet been measured.
Extended: allow EIGHT MINUTES. If there is NO PROGRESS for TWO MINUTES,
something is wrong: record the last line, reset manually, and return the card.
For short runs over two minutes even with progress, report elapsed time and
last line; do not assume PASS. The screen clears at the child's start.
Cases are labelled in hex: short 00-05, extended 00-17.
Mode 0 = stock-style blocking output through the candidate MOS legacy path.
Mode 1 = experimental per-byte background sending.
Kind 0 = 64 back-to-back 8KB writes; kind 1 = 32 acknowledged duplex groups;
kind 2 = 32 paced groups. Four verification-quarter breadcrumbs follow each.
Source buffers remain retained during a stalled async send. A native timeout
may save failure state and hold silently for reset; that is FAIL, not PASS.

EXPECTED:
UART0 RECOVERY CAMPAIGN PASS
TEST 10 PASS (short) or TEST 11 PASS (extended)
Run NNNN: PASS
Press a key for the menu; Q returns to MOS.
A full passing short run verifies 49,152 final-buffer bytes. Extended verifies
196,608. The sustained case checks its FINAL overwritten buffer, not every
intermediate copy. This is a stall investigation, not a throughput benchmark.

REPORTS (sequential numbers; unreliable RTC is not used):
Rnnnn.log and runs.log = journal, including the start before child execution
Ynnnn.dat = completed report
Znnnn.dat = saved progress, updated before cases, within loads and verification
Cnnnn.dat = failure report if the fixture can save one
Do not delete these files or runs.log. Return the card even after PASS.
If a stall leaves only R/Z or an incomplete END, that is not a successful run.
Please report test choice, last progress line, elapsed time and stock banner.

RECOVERY FILES are beside test.bin: mos-candidate.bin, vdp-2.16.0.bin,
flash.bin and the previous optional diagnostic image. The required old MOS file
is /test/mos-uart0/mos-candidate.bin (file CRC32 7E66FD09), NOT /MOS.bin.
Root /MOS.bin is preserved. Firmware installation remains manual. If boot is
still diagnostic, restore stock VDP with the existing firmware menu 9 then 4
and reboot/confirm the normal banner before the recovery test. Do not select
9 then 2: that installs the separate margin experiment's diagnostic VDP.
No new firmware, threshold change, probe or Olimex wiring is needed here.
