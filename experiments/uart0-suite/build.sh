#!/usr/bin/env bash
# All compilation and emulation on Oryx; local Ruby stages native fixtures.
set -euo pipefail
cd "$(dirname "$0")/../.."
build=build/uart0-suite
ruby experiments/uart0-suite/prepare.rb "$build"
ruby -rjson -rdigest -e 'r=JSON.parse(File.read("experiments/uart0-mos/results.json"));abort "MOS pin mismatch" unless Digest::SHA256.file("build/uart0-suite/MOS.bin").hexdigest==r.fetch("rom_sha256")'
cp build/uart0-bench/upstream/{flash.bin,vdp-2.16.0.bin} "$build/"
cp "$build/MOS.bin" "$build/mos-candidate.bin"
cp experiments/uart0-suite/suite.cfg "$build/"
cp ../agon-dev-env/scripts/setup_emulator.py "$build/"
tar -cf "$build/inputs.tar" experiments/uart0-suite experiments/uart0-stress/capture.txt experiments/uart0-bench/analyze.rb \
    "$build"/bench/{bench.asm,bench.linkcmd,packets.inc,expected.json,expected-packet.bin} \
    "$build"/stress/{stress.asm,stress.linkcmd,packets.inc,expected.json} \
    "$build"/api/{app.asm,app.linkcmd,short.asm,short.linkcmd,packets.inc} \
    "$build"/{identity.h,MOS.bin,MOS.map,mos-candidate.bin,flash.bin,vdp-2.16.0.bin,checks.bin,suite.cfg,setup_emulator.py,margin.bin}
ssh -o BatchMode=yes oryx-linuxlite 'mkdir -p ~/Agon/mystuff/agon-mos/build/uart0-suite'
scp -q -o BatchMode=yes "$build/inputs.tar" oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-suite/
ssh -o BatchMode=yes oryx-linuxlite 'cd ~/Agon/mystuff/agon-mos && tar -xf build/uart0-suite/inputs.tar && bash experiments/uart0-suite/bootstrap.sh && bash experiments/uart0-suite/remote-build.sh && gcc -Wall -Wextra -Werror -shared -fPIC experiments/uart0-suite/tests/keys.c -ldl -o build/uart0-suite/keys.so && .venv/bin/python -B experiments/uart0-suite/profile.py --keys && .venv/bin/python -B experiments/uart0-suite/tests/interactive.py && .venv/bin/python -B experiments/uart0-suite/profile.py --auto && .venv/bin/python -B experiments/uart0-suite/qualify.py jit && .venv/bin/python -B experiments/uart0-suite/qualify.py interp && .venv/bin/python -B experiments/uart0-suite/profile.py && tar -cf build/uart0-suite/qualification.tar -C build/uart0-suite test.bin menu.bin entry.map entry.lst bench/bench.bin bench/bench.map bench/bench.lst stress/stress.bin stress/stress.map stress/stress.lst api/app.bin api/app.map api/app.lst api/short.bin api/short.map api/short.lst evidence-jit evidence-interp evidence-interactive' > "$build/build.log" 2>&1 || { tail -30 "$build/build.log" >&2;exit 1; }
scp -q -o BatchMode=yes oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-suite/qualification.tar "$build/"
tar -xf "$build/qualification.tar" -C "$build"
