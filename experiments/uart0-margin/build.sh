#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
b=build/uart0-margin
ruby experiments/uart0-margin/prepare.rb "$b"
ruby experiments/uart0-margin/packets.rb "$b"
cp experiments/uart0-margin/{host.asm,host.linkcmd} "$b/"
tar -czf "$b/inputs.tar.gz" experiments/uart0-margin "$b"/{firmware,source.json,host.asm,host.linkcmd,cases.inc,expected.json}
scp -q -o BatchMode=yes "$b/inputs.tar.gz" oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-margin/
ssh -o BatchMode=yes oryx-linuxlite 'cd ~/Agon/mystuff/agon-mos && tar -xzf build/uart0-margin/inputs.tar.gz && ~/.platformio/penv/bin/pio run -d build/uart0-margin/firmware -j 6 && cd build/uart0-margin && ~/.local/bin/agon-zds ez80asm -list -listmac -quiet -NOsdiopt -warn -debug -NOigcase -cpu:eZ80F92 host.asm && ~/.local/bin/agon-zds eZ80link @host.linkcmd && objcopy -I ihex -O binary --gap-fill 0 host.hex margin.bin && cd ../.. && .venv/bin/python -B experiments/uart0-margin/profile.py && .venv/bin/python -B experiments/uart0-margin/qualify.py jit && .venv/bin/python -B experiments/uart0-margin/qualify.py interp && .venv/bin/python -B experiments/uart0-margin/qualify.py jit badcrc && .venv/bin/python -B experiments/uart0-margin/qualify.py jit noend && tar -czf build/uart0-margin/qualified.tar.gz -C build/uart0-margin margin.bin host.lst host.map firmware/.pio/build/esp32dev/firmware.bin firmware/.pio/build/esp32dev/firmware.elf evidence-jit evidence-interp evidence-jit-badcrc evidence-jit-noend' > "$b/build-final.log" 2>&1 || { tail -30 "$b/build-final.log" >&2;exit 1; }
scp -q -o BatchMode=yes oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-margin/qualified.tar.gz "$b/"
tar -xzf "$b/qualified.tar.gz" -C "$b"
for engine in jit interp; do ruby experiments/uart0-margin/analyze.rb "$b/evidence-$engine/margin.dat" "$b/expected.json" > "$b/analysis-$engine.json"; done
