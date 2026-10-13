#!/usr/bin/env bash
# Official stock VDP release for manual Console8 installation.
set -euo pipefail
cd "$(dirname "$0")/../.."
out=build/uart0-bench/upstream
mkdir -p "$out"
if [[ ! -e "$out/vdp-2.16.0.bin" ]]; then
    curl --fail --location --silent --show-error \
        https://github.com/AgonPlatform/agon-vdp/releases/download/v2.16.0/firmware.bin \
        --output "$out/vdp-2.16.0.bin"
fi
if [[ ! -s "$out/VDP-LICENSE.txt" ]]; then
    gh api 'repos/AgonPlatform/agon-vdp/contents/LICENSE?ref=c7ac293d2aa81ddfa693390549bcd909069c8fc3' --jq .content \
        | base64 --decode > "$out/VDP-LICENSE.txt"
fi
(cd "$out" && echo 'b807beef35823b13a0a056f11b7464cd1b1c6356dce0e4098b78ebe059ded35f  vdp-2.16.0.bin' | sha256sum --check --status)
(cd "$out" && echo 'fae2cacdc47dc5ed8efbd052201834108167942f0b524b8238327e9fbe13fd25  VDP-LICENSE.txt' | sha256sum --check --status)
