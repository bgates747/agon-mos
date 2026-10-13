#!/usr/bin/env bash
# Lightweight staging locally; all compilation and emulation run on Oryx.
set -euo pipefail
cd "$(dirname "$0")/../.."
build=build/uart0-flexe
mkdir -p "$build"
ruby experiments/uart0-flexe/packets.rb "$build"
ssh -o BatchMode=yes oryx-linuxlite \
    'mkdir -p ~/Agon/mystuff/agon-mos/experiments/uart0-flexe ~/Agon/mystuff/agon-mos/experiments/uart0-async ~/Agon/mystuff/agon-mos/build/uart0-flexe'
scp -q -o BatchMode=yes experiments/uart0-flexe/{app.asm,app.linkcmd,reference.sha256,profile.py,qualify.py,check-profile.py,build.sh,remote-build.sh,packets.rb} \
    oryx-linuxlite:Agon/mystuff/agon-mos/experiments/uart0-flexe/
scp -q -o BatchMode=yes experiments/uart0-async/{driver.asm,fixture.asm} \
    oryx-linuxlite:Agon/mystuff/agon-mos/experiments/uart0-async/
scp -q -o BatchMode=yes src/uart0_tx.inc oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-flexe/
# Canonical profile generator snapshot; no project copy is maintained in source.
scp -q -o BatchMode=yes ../agon-dev-env/scripts/setup_emulator.py \
    "$build/packets.inc" "$build/expected-tx.bin" "$build/expected-rx.bin" "$build/expected.json" \
    oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-flexe/
ssh -o BatchMode=yes oryx-linuxlite \
    'cd ~/Agon/mystuff/agon-mos && bash experiments/uart0-flexe/remote-build.sh' \
    > "$build/build.log" 2>&1 || { cat "$build/build.log" >&2; exit 1; }
for engine in jit interp; do
    ssh -o BatchMode=yes oryx-linuxlite \
        "cd ~/Agon/mystuff/agon-mos && .venv/bin/python -B experiments/uart0-flexe/qualify.py '$engine'" \
        | tee "$build/$engine.log"
done
ssh -o BatchMode=yes oryx-linuxlite \
    'cd ~/Agon/mystuff/agon-mos && sha256sum --check --quiet build/uart0-flexe/inputs.sha256 && tar -cf build/uart0-flexe/evidence.tar -C build/uart0-flexe evidence-jit evidence-interp inputs.sha256 tools.txt uart-tests.txt check-profile.txt app.bin app.hex app.map app.lst driver.lst fixture.lst'
scp -q -o BatchMode=yes oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-flexe/evidence.tar "$build/"
tar -xf "$build/evidence.tar" -C "$build"
ruby experiments/uart0-async/audit-widths.rb experiments/uart0-flexe/app.asm > "$build/width-audit.txt"
