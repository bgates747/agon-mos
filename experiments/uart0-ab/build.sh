#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
ruby experiments/uart0-ab/prepare.rb
mkdir -p build/uart0-ab/runner/src
cp build/uart0-ab/framework.rs build/uart0-ab/runner/src/main.rs
cat experiments/uart0-ab/bench.rs >> build/uart0-ab/runner/src/main.rs
cp experiments/uart0-async/runner/Cargo.lock build/uart0-ab/runner/
cat > build/uart0-ab/runner/Cargo.toml <<'TOML'
[package]
name="mos-uart0-async-qualification"
version="0.1.0"
edition="2021"
publish=false
[dependencies]
ez80={path="../../uart0-async/ez80-model"}
TOML
tar -czf build/uart0-ab/inputs.tar.gz experiments/uart0-ab build/uart0-ab/{default,grouped,chunk,otirx,runner,source.json} experiments/uart0-async/read-map.rb
ssh -o BatchMode=yes oryx-linuxlite 'mkdir -p ~/Agon/mystuff/agon-mos/build/uart0-ab'
scp -q -o BatchMode=yes build/uart0-ab/inputs.tar.gz oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-ab/
ssh -o BatchMode=yes oryx-linuxlite 'cd ~/Agon/mystuff/agon-mos && tar -xzf build/uart0-ab/inputs.tar.gz && bash experiments/uart0-ab/remote.sh' > build/uart0-ab/build.log 2>&1 || { tail -35 build/uart0-ab/build.log; exit 1; }
scp -q -o BatchMode=yes oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-ab/results.tar.gz build/uart0-ab/
tar -xzf build/uart0-ab/results.tar.gz -C build/uart0-ab
ruby experiments/uart0-ab/analyze.rb > build/uart0-ab/analysis.json
