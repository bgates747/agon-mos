#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
build=build/uart0-stress
(cd build/uart0-mos/runtime && sha256sum --check --quiet ../../../experiments/uart0-mos/runtime.sha256)
cp experiments/uart0-stress/{stress.asm,stress.linkcmd} "$build/"
(
    cd "$build"
    ~/.local/bin/agon-zds ez80asm -list -listmac -quiet -NOsdiopt -warn -debug -NOigcase -cpu:eZ80F92 stress.asm
    ~/.local/bin/agon-zds eZ80link @stress.linkcmd
    objcopy -I ihex -O binary --gap-fill 0 stress.hex test.bin
)
.venv/bin/python -B experiments/uart0-stress/profile.py
for engine in jit interp; do
    .venv/bin/python -B experiments/uart0-stress/qualify.py "$engine"
done
for control in sequence payload; do
    .venv/bin/python -B experiments/uart0-stress/profile.py --controls
    .venv/bin/python -B experiments/uart0-stress/qualify.py jit "$control"
done
