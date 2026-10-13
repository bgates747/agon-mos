#!/usr/bin/env bash
# Off-device preparation only: native build and isolated headless tests on Oryx.
set -euo pipefail
cd "$(dirname "$0")/../.."
build=build/uart0-bench
mkdir -p "$build"
ruby experiments/uart0-bench/packets.rb "$build"
# Freeze the already accepted ROM, not a new firmware candidate.
ruby -rjson -rdigest -e 'r=JSON.parse(File.read("experiments/uart0-mos/results.json")); abort "Accepted ROM mismatch" unless Digest::SHA256.file("build/uart0-mos/MOS.bin").hexdigest==r.fetch("rom_sha256")'
cp build/uart0-mos/{MOS.bin,MOS.map} "$build/"
ssh -o BatchMode=yes oryx-linuxlite 'mkdir -p ~/Agon/mystuff/agon-mos/experiments/uart0-bench ~/Agon/mystuff/agon-mos/build/uart0-bench'
scp -q -o BatchMode=yes experiments/uart0-bench/{bench.asm,bench.linkcmd,profile.py,qualify.py,remote-build.sh} \
    oryx-linuxlite:Agon/mystuff/agon-mos/experiments/uart0-bench/
scp -q -o BatchMode=yes ../agon-dev-env/scripts/setup_emulator.py \
    "$build"/{MOS.bin,MOS.map,packets.inc,checks.bin,expected-packet.bin,expected.json} \
    oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-bench/
ssh -o BatchMode=yes oryx-linuxlite 'cd ~/Agon/mystuff/agon-mos && bash experiments/uart0-bench/remote-build.sh && tar -cf build/uart0-bench/qualification.tar -C build/uart0-bench bench.bin bench.hex bench.map bench.lst evidence-jit evidence-interp' \
    > "$build/build.log" 2>&1 || { tail -35 "$build/build.log" >&2; exit 1; }
scp -q -o BatchMode=yes oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-bench/qualification.tar "$build/"
tar -xf "$build/qualification.tar" -C "$build"
