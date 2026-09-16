# SDF-002-F01 reproduction kit

This kit contains the actual probe and SD-response injector used for qualification,
plus original automation and retained results. Hardware behavior/data loss are
unproven. Never run this raw-sector probe on a physical card.

## Reproduce without our bench directory layout

1. Use Fab Agon Emulator source at commit
   194a5e44c36a8bb886dae1741b01c6e7a1e5ede7 (1.2.4).
   Replace agon-ez80-emulator/src/spi_sdcard.rs with injector/spi_sdcard.instrumented.rs.
   Build with cargo build --release --locked using Fab's documented SDL3/build
   dependencies. This changes only the SD device response; CPU and timer are unchanged.
2. Supply a compatible platform VDP shared module. The tested module SHA-256 is
   bc7a8a6a28e176c9679c96de4bda16010b765074ec8ba155fccde189c1051955.
   Native libraries are host-specific and are not included.
3. Create a dedicated Fab profile with the included profile/fab-agon-emulator wrapper,
   a fab-agon-emulator.bin symlink to your instrumented executable, and an empty
   sdcard directory. Copy firmware/stock.bin to mos_platform.bin and
   firmware/stock.map to mos_platform.map. Write a descriptive .mos-release file;
   run sha256sum mos_platform.bin mos_platform.map > .mos-release.sha256.
   The wrapper uses ~/.local/lib for SDL3 when present.
4. Copy image/control-base.img to a fresh trial.img for EVERY control. This is
   a disposable MBR/FAT32 image with the probe and !boot.obey already installed.
   It writes LBA1, outside the partition starting at LBA2048. The image is NOT
   a physical-card deployment package.
5. From the profile directory run (replace absolute paths):
   MOS02_SD_MODE=busy SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./fab-agon-emulator --sdcard-img /absolute/trial.img --renderer sw --vdp /absolute/vdp_platform.so --precise-interrupts -u -d -b 0
6. At the debugger prompt enter:
   break $4020d
   break $a366
   delete $0
   c
   The busy control first stops at $A366 on the real timer-expiry path.
   Run registers: AF carry must be set. Then c to reach probe completion,
   and mem $40463 1 to read the final result. Stock returns 00 (false success).
   exit closes Fab.
7. Repeat with firmware/overlay.bin as mos_platform.bin; regenerate the profile
   hash file. The identical probe returns 01 after the same injected timeout.
8. Repeat both firmware variants with MOS02_SD_MODE=normal and reject.
   Neither reaches the timeout breakpoint. Normal returns00; rejected data returns01.
   The included original observer captures additional frame/token/SD/disk results;
   its addresses are valid ONLY for these stock/overlay images.

## Expected controls

                         normal   busy timeout   rejected data
Stock MOS 3.0.2              0       0 (bug)           1
Patched overlay             0       1                 1

MOS02_SD_MODE affects only CMD24 sector1: normal accepted05/ready, busy accepted05
then persistent00, reject0D. Fab still writes the host image eagerly before
responding in all cases. This tests firmware response handling, not card
persistence or data loss. Real timer expiry is observed, never forced.

## Source and build provenance

probe/ contains the exact C++/assembly source, Makefile, binary and map.
Its assembly adapts the released ZDS disk_write ABI at $A73F to the C++ return.
Override AGONDEV_TOOLCHAIN when rebuilding; the historical Makefile records the
bench path. Recheck addresses if any source/toolchain changes affect the probe.

firmware/overlay.bin is the exact tested instruction overlay, not a ZDS rebuild.
patch/ includes the source repair and overlay builder/window source.
The patch changes the same instruction window as the source-built correction.

historical/ contains original scripts with their bench paths/layout preserved,
not a portable installer. Dependencies used by the observer are included.
Use the manual steps above for an independent checkout; do not run setup.py
blindly on your own system.

full-source-evidence.tar.gz includes both complete AgonDev source builds, probe
sources, build/tool pins, preparation source archives, actual build provenance,
debugger traces, verification code and commands. Those builds use DIFFERENT
addresses; use their included symbol/config records, not the addresses above.
Seven full-source controls passed, including the unpatched negative control.

Stock MOS source: https://github.com/AgonPlatform/agon-mos
commit 8336409351ee5314e02801a7b72a4f1bb5282519.
MOS license is included; Fab license accompanies the injector.
SHA256SUMS inventories every supplied file except itself.
