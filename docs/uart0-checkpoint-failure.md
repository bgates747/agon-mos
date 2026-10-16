# Console8 R0009 fixture hang and repair

The subsequent Console8 R0010 run passes after these fixture repairs. Both
receiver cases complete, the final/checkpoint files agree, and all8192 payload
bytes match their CRCs with zero receive errors. The Author also confirms the
keypress repair. The forced case captures the suspected receiver ordering on
physical hardware; that separate synchronization defect is the next AB-006
work. Diagnostic VDP remains installed by the Author's confirmation.

The test stopped while trying to update its own progress file. It used MOS
SAVE, which creates a new file and refuses an existing name. The fixture
treated that error as a reason to halt forever. This explains why the card
had its first checkpoint but no completed receiver record. It does not give
us evidence for or against the suspected receiving-firmware race.

The relevant code is `mos_SAVE` in src/mos.c, opening with
`FA_WRITE | FA_CREATE_NEW`, and the `FR_EXIST` branch of `f_open` in
src_fatfs/ff.c. The exact old experimental MOS build source on Oryx has the
same behavior. The original native `checkpoint` in this experiment used API2
every time, then entered `sd_hold` on any nonzero result. The second checkpoint
therefore fails deterministically on the physical FAT card.

The frozen Flexe directory-backed hostfs shortcut opens CREATE_NEW with Rust
`.create(true)`, which allows an existing file. It concealed this fixture error.
No emulator code was changed here. `fat-regression.py` uses a disposable32MiB
FAT16 image with `--sdcard-img`, exercising the actual MOS FatFS/SPI path.
The old native image reproduces the same stage1/count2/completed0 checkpoint
and missing final/failure reports as hardware R0009.

The first attempted repair exposed a second issue. FAT file creation/sync calls
`get_fattime` in src_fatfs/diskio.c, which calls `rtc_update` and sends VDP
command23,0,87h,0. A checkpoint after ARM puts those bytes into the raw payload
receiver. Captured wire data and receiver records show the first byte23 and
CRC51D16A4A, then an early zero end marker. This failed attempt is retained.
The hostfs shortcut also bypasses these timestamp requests, so checking only
directory-backed emulator files was insufficient.

The final repair changes only the native fixture; diagnostic VDP and installed
experimental MOS are unchanged. Progress uses fopen with WRITE|CREATE_ALWAYS,
checks the exact fwrite count, and closes. A double-write preflight exercises
replacement before arming the receiver. No disk or screen operations occur
between ARM and observed DONE. Final and failure reports retain separate
numbered names; the source buffer is retained if transmission cannot drain.
Storage errors before a transfer print an error and return to MOS without
recursive save attempts or an unexplained halt.

Progress stage8 means preflight;1 means before ARM;2 means receiver DONE and
before evidence retrieval;6 means halfway through the record;7 means a case
is saved;0 means complete. Stages4(armed) and5(waiting for drain) are RAM-only
while the raw receiver is active. A returned stage1 checkpoint alone cannot
separate those active phases. Persisting them would itself disturb this test.

Both-engine actual-FatFS native checks and the real-key menu integration pass
with both complete4096-byte payloads, matching CRC87897582, zero receive errors,
and valid diagnostic ordering. The menu test preserves the returned R0001–9
reports and running journal and allocates R0010. Corrupt payload, absent end
marker, absent handshake, and a checkpoint path that cannot be opened are
separate rejection controls. Evidence is under Oryx
build/uart0-race/checkpoint-fix-20261014, with a verified Pi archive after staging.
These are emulator checks of the compiled firmware, not new physical results.

One Console8 session now covers the menu repair and the receiver diagnostic:
load the same /test/mos-uart0/test.bin, use9/0 to check the firmware submenu,
then8/4 for the real two-case run. The existing diagnostic VDP can stay installed;
if it was restored, install the already staged diagnostic again. Afterward
restore stock VDP with9/4 and confirm its normal banner. Allow up to two minutes;
a stall is never PASS. Inspect the returned numbered evidence before making
any receiver repair or hardware qualification claim.
