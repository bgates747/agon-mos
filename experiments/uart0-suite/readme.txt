UART0 QUALIFICATION SUITE v1

The current entry is always /test/mos-uart0/test.bin. At MOS:
  CD /test/mos-uart0
  LOAD test.bin
  RUN

Press one menu key (no ENTER needed):
  1  Firmware/API fingerprint and phased RX diagnostics
  2  Legacy/async benchmark: four alternating pairs
  3  Bounded VDP pauses / full-duplex replies / receiver byte checks
  4  MOS ticks measured against your independent stopwatch
  5  Passive CTS capture preparation and remaining limits
  6  API ordering, masked-IFF output, callbacks, return fence, ADL=0
  0  Run all tests (order 1,6,2,3,4,5)
  9  Staged firmware menu / installed-MOS backup
  Q  Return to MOS

For test 4, start your stopwatch with ENTER, then stop both with ENTER after
10-600 seconds. Enter the measured seconds, such as 30.125, and press ENTER.
ESC skips that measurement. It is manual key timing, not precision timing.
It does not use the Agon's RTC as the reference or assume a tick frequency.
Test 5 needs a separate passive capture; its software status is PENDING.
Read capture.txt before attempting any probe connection. No probes are
required for tests 1,2,3,4,6. Test 3 acknowledges each GP reply before
requesting the next: MOS exposes only the latest reply in one byte. Each
request precedes a 256-byte write, and replies during TX are required. This
is not a maximum reply-rate test. The original dense test stays in workspace.

Allow about three minutes for all automatic checks, plus your stopwatch
measurement. Individual tests 2/3 should finish within two minutes each.
Progress lines identify the test, case and verification quarters. If a test
stalls beyond that expectation, report its last line and reset manually.
A permanent CTS blockage retains borrowed RAM; the suite will not flush
UART FIFOs or abandon an active source to escape the stall.

PASS means that check passed. FAIL stops run-all and retains earlier results.
PENDING/SKIP means a measurement or required API is unavailable. Run-all may
finish PENDING while every software check passes, because CTS capture is
still outstanding or stopwatch calibration was skipped. After a completed
selection, press any key to return to the menu; choose another test or Q.

Results use sequential run numbers, never dates or the Agon's clock.
R0001.log is the per-run journal; runs.log is the running log across runs.
B/N/F = benchmark result/baseline/failure. S/P/G = stress equivalents.
D = phased RX diagnostics, I/J = integration result/failure, C = calibration,
M = installed-MOS backup. The four-digit run number belongs to the selection;
run-all shares one number across its tests. Report format version is 1;
the journal also records a source build ID, MOS fingerprint and target labels.
Interrupted runs retain their reserved number. Old report filenames are not
reused even after copying individual reports away, while runs.log is retained.
Do not delete/edit runs.log while the suite is in use. If numbers reach 9999,
return the card so results can be preserved and a new series started on host.

Default firmware is unchanged from the passing standalone tests:
  MOS candidate: CRC32 7E66FD09
  Stock VDP 2.16.0: CRC32 FFFBFADE
The installed-MOS fingerprint is over the full 128 KiB, so it normally differs
from the candidate-file CRC. No reflashing is required if these are installed.
Menu 9 offers 1 MOS, 2 VDP, 3 save/verify installed MOS, 0 back.
Flashing is NEVER part of run-all. The utility shows target/file/CRC and asks
Y/N; choose N to cancel. Read firmware.txt for backup, recovery and VDP update
restrictions before choosing Y. A MOS update normally resets the machine.
A firmware request is logged as PENDING, not falsely reported as flashed.
If the utility returns, zero means UNVERIFIED, not a successful update.
Any displayed updater error means FAIL. A completed update needs readback
verification. A load/command error is logged as FAIL. A reset leaves a
pending handoff in the journal, since the suite cannot certify its outcome.
VDP flashing is unavailable in the Flexe review profile: that frozen
app-only VDP snapshot has no qualified OTA update path. Menu 9/2 reports
SKIP and sends no update command there. Hardware keeps the explicit option.
The numbered M backup must be copied and validated in workspace before it is
relied on for restoration. A backup covers MOS only, not the VDP.

For another hardware/firmware combination, edit suite.cfg target labels.
Replacement firmware needs a qualified package containing those images and
matching configured filenames. VDP labels are operator supplied, not detected.
API 1.1 is feature-detected;
unsupported async tests are skipped, and no private UART driver is installed.
The vdp_flash setting records this profile capability (0 disables, 1 enables).
Keep the packaged firmware copies, readme.txt and fixtures together.

Power down and return the SD card for host inspection after the campaign.
The host copies results/history to workspace; deployments keep this active
path stable and do not create history directories on the SD card by default.
