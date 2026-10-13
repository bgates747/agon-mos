#!/usr/bin/env bash
# Run only in the isolated source staging directory on the canonical ZDS host.
set -euo pipefail
sha256sum --check --quiet source.sha256
zds_prefix=${AGON_ZDS_PREFIX:-"$HOME/.local/share/agon-zds/wineprefix"}
zds_root=${AGON_ZDS_ROOT:-"$zds_prefix/drive_c/Zilog/ZDSII_eZ80Acclaim!_5.3.5"}
sha256sum "$zds_root/bin/ez80asm.exe" "$zds_root/bin/eZ80link.exe" \
    "$HOME/.local/bin/agon-zds" > tools.sha256
{
    hostname
    wine --version
    objcopy --version | head -1
} > tools.txt
for unit in driver fixture; do
    "$HOME/.local/bin/agon-zds" ez80asm -list -listmac -name -pagelen:0 \
        -pagewidth:132 -quiet -NOsdiopt -warn -debug -NOigcase -cpu:eZ80F92 "$unit.asm"
done
"$HOME/.local/bin/agon-zds" eZ80link @uart.linkcmd
# Generic Linux binutils only package the native linker output, never assemble it.
objcopy -I ihex -O binary --gap-fill 0 driver.hex driver.bin
sha256sum --check --quiet source.sha256
head -1 driver.lst >> tools.txt
head -1 driver.map >> tools.txt
tar -cf artifacts.tar driver.bin driver.hex driver.map driver.lod driver.lst \
    fixture.lst driver.obj fixture.obj tools.sha256 tools.txt source.sha256
