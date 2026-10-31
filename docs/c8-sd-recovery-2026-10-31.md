# Console8 diagnostic SD recovery — 2026-10-31

The Author confirmed that stock MOS boots after the checked WROOM restoration.
Recovered and verified the card's UART evidence on both Oryx and Pi. The SD
card was not changed, unmounted or ejected. Four diagnostic/report files and
one startup file had no identical match in the prior loose-file evidence
index. All UART fixture files were captured, so recovery does not depend on
proving which files an older compressed archive might contain.

## Card and capture

Unique removable FAT volume AGONC8, UUID8658-1C23, mounted at
/run/media/smith/AGONC8 on Oryx. Captured five test/mos-uart0* directories,
plus relevant root MOS/startup files:257files,67,826,138bytes. Compared source
and copied hashes, re-read every archived regular member, then independently
verified archive and all257file hashes after copying/extracting on Pi. No
Agon timestamps were used to infer freshness; stored2035dates are unreliable.

Files not matched by name/size/SHA256 in earlier loose build evidence:

- test/mos-uart0/R0030.log
- test/mos-uart0/runs.log
- test/mos-uart0-before-progress/failure.dat
- test/mos-uart0-before-stress/bench.dat
- autoexec.txt

This comparison does not claim those bytes were absent from every historical
compressed archive. Complete fresh snapshot and manifests are retained anyway.

## Latest run and startup context

R0030 records suite buildca6fe00f96f33e66, firmware action, candidateMOS104658
bytes/CRC07259758 and FLASH_HANDOFF verification=PENDING. It is evidence of the
candidate flash request, not of flash completion, CRC success or boot. Preserve
it for the original incident audit; no re-run or firmware change was performed.
The old candidate file on SD remains unchanged as captured. Root MOS.bin does
match known-good stockMOS3.0.2 SHA256d564243283972690933a4554296ad6202ca4ef54572279533a942960846bebae.
Autoexec sets keyboard1, changes to/mystuff/jukebox and loads jukebox.bin; no
flash command is present in the captured startup file. Nothing was executed.

## Evidence

Both machines retain build/c8-sd-recovery-20261031/return-001/card plus manifest,
collector and checks. Snapshot archive:return-001.tar.gz,58,934,987bytes,
SHA256e462d13696c695c67b901c8a3c9adb6fc41b0e20dd14a6f15a472be9fd1634f3.
Pi-verification.json records257independent file-hash matches. Card left mounted.
MOS recovery taskN-009 is complete based on target CRC and Author-confirmed boot;
P4 original firmware restoration is a separate deferred cleanup item.
