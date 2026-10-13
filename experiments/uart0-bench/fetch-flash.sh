#!/usr/bin/env bash
# Off-device, fixed official release. No device access or firmware writes.
set -euo pipefail
cd "$(dirname "$0")/../.."
out=build/uart0-bench/upstream
mkdir -p "$out"
if [[ ! -e "$out/flash.bin" ]]; then
    curl --fail --location --silent --show-error \
        https://github.com/AgonPlatform/agon-flash/releases/download/v1.9/flash.bin \
        --output "$out/flash.bin"
fi
(cd "$out" && echo '480b476703b798cf8d93294cac42d77cad93f7747003b061520b86685c75eb57  flash.bin' | sha256sum --check --status)
# Commit pin preserves the upstream notice even if a tag is moved later.
if [[ ! -s "$out/flash-LICENSE.txt" ]]; then
    gh api 'repos/AgonPlatform/agon-flash/contents/LICENSE?ref=e670b5bd910dfe372c29aa9e896e6c24cc8530ec' --jq .content \
        | base64 --decode > "$out/flash-LICENSE.txt"
fi
(cd "$out" && echo '7f5a596f6c9f72cb9d38b53cdc33b84bfdc068baa705ff8b8f3faab41e9eff99  flash-LICENSE.txt' | sha256sum --check --status)
