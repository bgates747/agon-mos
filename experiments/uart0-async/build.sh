#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
model_source=${EZ80_MODEL_SOURCE:-/Agon/mystuff/agon-6502/build/ez80-model}
out_dir=build/uart0-async
mkdir -p "$out_dir"
if [[ ! -d "$out_dir/ez80-model" ]]; then
    cp -a "$model_source" "$out_dir/ez80-model"
fi
model_manifest="$PWD/experiments/uart0-async/model.sha256"
(cd "$out_dir/ez80-model" && sha256sum --check --quiet "$model_manifest")
# Host/account/key selection belongs to agon-dev-env's canonical SSH contract.
# Each build stages only its own sources in a fresh cache directory.
stage=$(ssh -o BatchMode=yes oryx-linuxlite \
    'mkdir -p ~/.cache/agon-mos-uart0-async && mktemp -d ~/.cache/agon-mos-uart0-async/build.XXXXXX')
[[ "$stage" =~ ^/[-a-zA-Z0-9_/.]+/build\.[a-zA-Z0-9]+$ ]] || { echo 'Invalid staging path' >&2; exit 1; }
inputs=(driver.asm fixture.asm uart.linkcmd remote-build.sh)
(cd experiments/uart0-async && sha256sum "${inputs[@]}") > "$out_dir/source.sha256"
scp -q -o BatchMode=yes "${inputs[@]/#/experiments/uart0-async/}" \
    "$out_dir/source.sha256" "oryx-linuxlite:$stage/"
ssh -o BatchMode=yes oryx-linuxlite "cd '$stage' && bash remote-build.sh" \
    > "$out_dir/zds-build.log" 2>&1 || { cat "$out_dir/zds-build.log" >&2; exit 1; }
scp -q -o BatchMode=yes "oryx-linuxlite:$stage/artifacts.tar" "$out_dir/artifacts.tar"
tar -xf "$out_dir/artifacts.tar" -C "$out_dir"
(cd experiments/uart0-async && sha256sum --check --quiet "../../$out_dir/source.sha256")
ruby experiments/uart0-async/read-map.rb "$out_dir" | tee "$out_dir/map-audit.txt"
{
    sha256sum experiments/uart0-async/{driver,fixture}.asm \
        experiments/uart0-async/runner/src/main.rs experiments/uart0-async/{build,remote-build,check-negatives}.sh \
        experiments/uart0-async/{audit-widths,read-map}.rb experiments/uart0-async/uart.linkcmd \
        experiments/uart0-async/model.sha256 experiments/uart0-async/runner/{Cargo.toml,Cargo.lock} \
        "$out_dir/driver.bin" "$out_dir/driver.hex" "$out_dir/driver.map" "$out_dir/symbols.txt" \
        "$out_dir/tools.sha256" "$out_dir/tools.txt"
    rg --files -0 "$out_dir/ez80-model/src" -g '*.rs' | sort -z | xargs -0 sha256sum
} > "$out_dir/inputs.sha256"
cargo build --locked --offline --release --manifest-path experiments/uart0-async/runner/Cargo.toml \
    --target-dir "$out_dir/target"
"$out_dir/target/release/mos-uart0-async-qualification" \
    "$out_dir/driver.bin" "$out_dir/symbols.txt" "$@" | tee "$out_dir/qualification.txt"
sha256sum --check --quiet "$out_dir/inputs.sha256"
ruby experiments/uart0-async/audit-widths.rb > "$out_dir/width-audit.txt"
experiments/uart0-async/check-negatives.sh | tee "$out_dir/negatives.txt"
