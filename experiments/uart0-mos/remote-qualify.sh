#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
build=build/uart0-mos
# Consume the MOS-owned cached qualified runtime; the emulator owner may be
# changing its own sources/builds concurrently. Never repin that work here.
if [[ ! -d "$build/runtime" ]]; then
    mkdir -p "$build/runtime"
    cp .emulator/runtime/flexe-agon-emulator.bin "$build/runtime/flexe-agon-emulator"
    cp .emulator/runtime/{flexe-vdp.so,esp32-firmware.bin,esp32-firmware.elf} "$build/runtime/"
fi
(cd "$build/runtime" && sha256sum --check --quiet ../../../experiments/uart0-mos/runtime.sha256)
cp experiments/uart0-mos/{app.asm,app.linkcmd,short.asm,short.linkcmd} "$build/"
(
    cd "$build"
    ~/.local/bin/agon-zds ez80asm -list -listmac -quiet -NOsdiopt -warn -debug -NOigcase -cpu:eZ80F92 app.asm
    ~/.local/bin/agon-zds eZ80link @app.linkcmd
    objcopy -I ihex -O binary --gap-fill 0 app.hex app.bin
    ~/.local/bin/agon-zds ez80asm -list -listmac -quiet -NOsdiopt -warn -debug -NOigcase -cpu:eZ80F92 short.asm
    ~/.local/bin/agon-zds eZ80link @short.linkcmd
    objcopy -I ihex -O binary --gap-fill 0 short.hex short.bin
)
(cd "$build/runtime" && sha256sum --check --quiet ../../../experiments/uart0-mos/runtime.sha256)
.venv/bin/python -B experiments/uart0-mos/profile.py
for engine in jit interp; do
    .venv/bin/python -B experiments/uart0-mos/qualify.py "$engine"
done
