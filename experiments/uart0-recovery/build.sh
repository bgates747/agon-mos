#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
b=build/uart0-recovery
ruby experiments/uart0-recovery/prepare.rb
# Build only off-device. All compilation is native ZDS II/Wine on Oryx.
tar -czf "$b/inputs.tar.gz" experiments/uart0-recovery "$b"/recovery.asm "$b"/recovery.linkcmd "$b"/helpers.inc "$b"/packets.inc "$b"/checks.bin "$b"/expected.json "$b"/bulk-packet.bin "$b"/small-packet.bin "$b"/duplex-packets.bin "$b"/identity.h experiments/uart0-suite/src/main.c experiments/uart0-suite/entry.asm experiments/uart0-suite/entry.linkcmd
ssh -o BatchMode=yes oryx-linuxlite 'mkdir -p ~/Agon/mystuff/agon-mos/build/uart0-recovery'
scp -q -o BatchMode=yes "$b/inputs.tar.gz" oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-recovery/
ssh -o BatchMode=yes oryx-linuxlite 'cd ~/Agon/mystuff/agon-mos && tar -xzf build/uart0-recovery/inputs.tar.gz && cd build/uart0-recovery && ~/.local/bin/agon-zds ez80asm -list -listmac -quiet -NOsdiopt -warn -debug -NOigcase -cpu:eZ80F92 recovery.asm && ~/.local/bin/agon-zds eZ80link @recovery.linkcmd && objcopy -I ihex -O binary --gap-fill 0 recovery.hex recovery.bin' > "$b/build.log" 2>&1 || { tail -25 "$b/build.log";exit 1; }
scp -q -o BatchMode=yes "oryx-linuxlite:Agon/mystuff/agon-mos/$b/recovery.bin" "$b/"
ssh -o BatchMode=yes oryx-linuxlite 'cd ~/Agon/mystuff/agon-mos && bash experiments/uart0-recovery/menu-build.sh' > "$b/menu-build.log" 2>&1 || { tail -25 "$b/menu-build.log";exit 1; }
scp -q -o BatchMode=yes "oryx-linuxlite:Agon/mystuff/agon-mos/$b/test.bin" "$b/"
