#!/usr/bin/env bash
# Build prepared original fixtures and CPU oracles on Oryx; does not run them.
set -euo pipefail
build=$1
for unit in oracle regression boot; do
    sed -i 's@/Agon/mystuff/@/home/smith/Agon/mystuff/@g' "$build/$unit/Cargo.toml"
    "$HOME/.cargo/bin/cargo" build --offline --release --manifest-path "$build/$unit/Cargo.toml" > "$build/$unit/build.log" 2>&1
done
bash experiments/uart0-startup-safe/remote_fixture.sh "$build" > "$build/fixture-build.log" 2>&1
