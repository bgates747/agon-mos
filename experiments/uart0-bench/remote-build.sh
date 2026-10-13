#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
build=build/uart0-bench
(cd build/uart0-mos/runtime && sha256sum --check --quiet ../../../experiments/uart0-mos/runtime.sha256)
cp experiments/uart0-bench/{bench.asm,bench.linkcmd} "$build/"
(
    cd "$build"
    ~/.local/bin/agon-zds ez80asm -list -listmac -quiet -NOsdiopt -warn -debug -NOigcase -cpu:eZ80F92 bench.asm
    ~/.local/bin/agon-zds eZ80link @bench.linkcmd
    objcopy -I ihex -O binary --gap-fill 0 bench.hex test.bin
)
.venv/bin/python -B experiments/uart0-bench/profile.py
for engine in jit interp; do
    .venv/bin/python -B experiments/uart0-bench/qualify.py "$engine"
done
