#!/usr/bin/env bash
# Lightweight snapshotting here; all native compilation/linking runs on Oryx.
set -euo pipefail
cd "$(dirname "$0")/../.."
out=build/uart0-mos
mkdir -p "$out"
inputs=(main.c MOS.zdsproj src src_startup src_fatfs src_umm_malloc tools/zds)
find "${inputs[@]}" -type f -print0 | sort -z | xargs -0 sha256sum > "$out/source.sha256"
tar -cf "$out/source.tar" "${inputs[@]}" -C "$out" source.sha256
stage=$(ssh -o BatchMode=yes oryx-linuxlite 'mkdir -p ~/.cache/agon-mos-native && mktemp -d ~/.cache/agon-mos-native/build.XXXXXX')
[[ "$stage" =~ ^/[-a-zA-Z0-9_/.]+/build\.[a-zA-Z0-9]+$ ]] || exit 1
scp -q -o BatchMode=yes "$out/source.tar" "oryx-linuxlite:$stage/"
ssh -o BatchMode=yes oryx-linuxlite "cd '$stage' && tar -xf source.tar && sha256sum --check --quiet source.sha256 && bash tools/zds/remote-build.sh && sha256sum --check --quiet source.sha256 && tar -cf artifacts.tar MOS.bin MOS.hex MOS.map image.sha256 tools.sha256 logs source.sha256 src/uart0_async.lst" \
    > "$out/build.log" 2>&1 || { tail -45 "$out/build.log" >&2; exit 1; }
scp -q -o BatchMode=yes "oryx-linuxlite:$stage/artifacts.tar" "$out/artifacts.tar"
tar -xf "$out/artifacts.tar" -C "$out"
sha256sum --check --quiet "$out/source.sha256"
printf '%s\n' "$stage" > "$out/oryx-stage.txt"
