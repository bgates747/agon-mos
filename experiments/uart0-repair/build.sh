#!/usr/bin/env bash
# Run on Oryx in this project's venv/toolchain environment; no physical access.
set -euo pipefail
cd "$(dirname "$0")/../.."
if [[ ! -d build/uart0-repair/before ]]; then
  .venv/bin/python -B experiments/uart0-repair/prepare.py
fi
for variant in before fixed candidate; do
  ~/.platformio/penv/bin/pio run -d "build/uart0-repair/$variant" -j 6
done
.venv/bin/python -B experiments/uart0-repair/packets.py
(cd build/uart0-repair/native && ~/.local/bin/agon-zds ez80asm -list -listmac -quiet -NOsdiopt -warn -debug -NOigcase -cpu:eZ80F92 host.asm && ~/.local/bin/agon-zds eZ80link @host.linkcmd && objcopy -I ihex -O binary --gap-fill 0 host.hex repair.bin)
bash experiments/uart0-suite/tests/menu_build.sh
cp build/uart0-ui/test.bin build/uart0-repair/test.bin
cp build/uart0-ui/identity.h build/uart0-repair/identity.h
