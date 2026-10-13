UART0 TEST - HEBER AGON CONSOLE8
==============================
Manual firmware installation and test. No Extender required.

On the Console8:
  CD /test/mos-uart0
  TYPE readme.txt

MOS image: mos-candidate.bin (110611 bytes), CRC32 F7A575E8.
VDP image: vdp-2.16.0.bin (1077840 bytes), CRC32 FFFBFADE.
The VDP image is the official stock 2.16.0 Bistromathics release.
flash.bin is the official AgonPlatform flash utility v1.9.
All these files and bench.bin/checks.bin are in this directory.

BEFORE FLASHING
Record the installed MOS and VDP versions (a boot photo is useful).
Have Console8 external ESP32/ZDI recovery available for a MOS failure.
Preserve the installer/image for your current VDP if you plan to restore it.
The MOS SAVE below backs up MOS only; it does NOT back up the VDP.
If already running stock VDP 2.16.0, skip the VDP flash section.

First save the exact installed MOS:
  CD /test/mos-uart0
  SAVE incoming-mos.bin &0 &20000
This must produce 131072 bytes. Do not overwrite an existing backup.
Power down, return the SD card to Oryx, and ask for backup validation
and a separate host copy before installing the candidate MOS.

INSTALL STOCK VDP 2.16.0, IF NEEDED
Use this section only with MOS 1.04 or later and VDP 1.04RC3 or later.
For installed VDP 2.8.0, 2.12.0 or 2.13.0, the SD flash tool cannot
perform the update: stop and use the official online VDP installer.
For installed VDP 2.15.0 ONLY, first disable its sprite text cursor:
  VDU 23 0 &0A 15
Then, from the test directory:
  LOAD flash.bin &B0000
  RUN &B0000 VDP /test/mos-uart0/vdp-2.16.0.bin
Confirm the VDP target, filename and CRC32 FFFBFADE before answering Y.
Allow the update/reboot to complete. Confirm VDP Version 2.16.0.
If it is an older MOS/VDP combination, stop and ask before upgrading.

INSTALL THE UART0 MOS CANDIDATE
After the installed-MOS backup has been checked on Oryx:
  CD /test/mos-uart0
  LOAD flash.bin &B0000
  RUN &B0000 MOS /test/mos-uart0/mos-candidate.bin
Confirm the MOS target, filename and CRC32 F7A575E8 before answering Y.
Do not use ALL, BATCH or -f. Allow update/reboot to complete.
This development MOS still prints version 3.0.2; that alone does not
identify it. Save an independent flash readback for the host to check:
  CD /test/mos-uart0
  SAVE candidate-readback.bin &0 &20000

RUN THE TEST
Remain in /test/mos-uart0; checks.bin must be in the current directory.
  LOAD bench.bin
  RUN
The test performs four blocking/async pairs and verifies every payload
byte in the VDP. Give it about a minute; hardware duration is unmeasured.
Expect:
  UART0 BENCH FIXTURE PASS
and the normal MOS prompt. Then type:
  ECHO UART0 KEYBOARD PASS
Expect that text and a normal prompt. Take a photo of the result.
UART0 BENCH RETURN PASS is an emulator autoexec marker, so it is NOT
expected from this manual RUN.

bench.dat is the 148-byte measurement report. Preserve it unchanged.
If failure.dat appears, the machine hangs, or PASS is absent, report
failure. Do not interpret the raw MOS clock ticks as calibrated seconds.
A permanent CTS stall can require an explicit reset.
For repeat runs, preserve old reports first, for example:
  RENAME bench.dat bench-01.dat
Rename failure.dat too, if present. Never overwrite incoming-mos.bin.

RESTORE THE ORIGINAL MOS WHEN FINISHED
Use only the installed-MOS backup validated on Oryx:
  CD /test/mos-uart0
  LOAD flash.bin &B0000
  RUN &B0000 MOS /test/mos-uart0/incoming-mos.bin
Check the displayed CRC32 against the backup's host record, then answer Y.
After reboot:
  CD /test/mos-uart0
  SAVE restored-mos.bin &0 &20000
Confirm original MOS version and normal keyboard/prompt operation.
This restores MOS only. VDP restoration requires your previous VDP image.

RETURN RESULTS TO ORYX
Power down and put the SD card back on Oryx. Keep incoming-mos.bin,
candidate-readback.bin, bench.dat, any failure.dat and restored-mos.bin.
The host verifies the candidate prefix and exact full MOS restoration,
and decodes bench.dat. Please supply boot/result photos as well.
The passive CTS/headroom tests are a separate qualification step.

HOST / PROVENANCE NOTES
SHA256SUMS and manifest.json identify every packaged file.
The earlier emulator used a Golem-built VDP snapshot reporting 2.16.0,
not this official release binary. This test uses standard VDP commands;
the physical run qualifies the official image for this fixture.
VDP release: https://github.com/AgonPlatform/agon-vdp/releases/tag/v2.16.0
Update/recovery guidance is linked in README.md. Original license notices
are in MOS-LICENSE.txt, VDP-LICENSE.txt and FLASH-LICENSE.txt.
