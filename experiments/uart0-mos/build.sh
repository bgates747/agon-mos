#!/usr/bin/env bash
# Reproduce the installed-ROM tranche; all compilation/emulation is on Oryx.
set -euo pipefail
cd "$(dirname "$0")/../.."
build=build/uart0-mos
mkdir -p "$build"
started=$(ruby -e 'puts Process.clock_gettime(Process::CLOCK_MONOTONIC)')
bash tools/zds/build.sh
bash experiments/uart0-async/build.sh > "$build/shared-core-test.log" 2>&1
ruby experiments/uart0-mos/symbols.rb "$build"
ruby experiments/uart0-flexe/packets.rb "$build"
ruby experiments/uart0-async/audit-widths.rb src/uart0_async.asm > "$build/width-audit.txt"
ssh -o BatchMode=yes oryx-linuxlite 'mkdir -p ~/Agon/mystuff/agon-mos/experiments/uart0-mos'
scp -q -o BatchMode=yes experiments/uart0-mos/{app.asm,app.linkcmd,short.asm,short.linkcmd,profile.py,qualify.py,remote-qualify.sh,runtime.sha256} \
    oryx-linuxlite:Agon/mystuff/agon-mos/experiments/uart0-mos/
scp -q -o BatchMode=yes ../agon-dev-env/scripts/setup_emulator.py \
    "$build"/{MOS.bin,MOS.hex,MOS.map,symbols.txt,packets.inc,expected-tx.bin,expected-rx.bin,expected.json} \
    oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-mos/
{
    cat "$build/source.sha256"
    find experiments/uart0-mos -type f -print0 | sort -z | xargs -0 sha256sum
    sha256sum experiments/uart0-async/runner/src/main.rs "$build"/{MOS.bin,MOS.hex,MOS.map,symbols.txt,expected-tx.bin,expected-rx.bin}
} > "$build/inputs.sha256"
ssh -o BatchMode=yes oryx-linuxlite 'set -e; cd ~/Agon/mystuff/agon-mos
    build/uart0-async/target/release/mos-uart0-async-qualification build/uart0-mos/MOS.bin build/uart0-mos/symbols.txt > build/uart0-mos/production-tests.txt
    bash experiments/uart0-mos/remote-qualify.sh
    tar -cf build/uart0-mos/qualification.tar -C build/uart0-mos evidence-jit evidence-interp production-tests.txt app.bin app.hex app.map app.lst short.bin short.hex short.map short.lst' \
    > "$build/flexe.log" 2>&1 || { tail -35 "$build/flexe.log" >&2; exit 1; }
scp -q -o BatchMode=yes oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-mos/qualification.tar "$build/"
tar -xf "$build/qualification.tar" -C "$build"
sha256sum --check --quiet "$build/inputs.sha256"
ruby -rjson -e 'puts JSON.pretty_generate(elapsed_seconds: Process.clock_gettime(Process::CLOCK_MONOTONIC)-ARGV.fetch(0).to_f, scope: "native MOS build, scripted qualification, production-ROM scenarios and both headless engines; setup excluded")' "$started" > "$build/duration.json"
cat "$build/production-tests.txt" "$build/duration.json"
