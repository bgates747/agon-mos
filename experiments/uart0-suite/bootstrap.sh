#!/usr/bin/env bash
# Project-local SDK; no global installation or MOS toolchain changes.
set -euo pipefail
cd "$(dirname "$0")/../.."
cache=build/uart0-suite/toolchain
mkdir -p "$cache"
if [[ ! -f "$cache/agondev-linux_x86_64.tar.gz" ]]; then
    curl -fsSL https://github.com/AgonPlatform/agondev/releases/download/v0.22/agondev-linux_x86_64.tar.gz -o "$cache/agondev-linux_x86_64.tar.gz"
fi
(cd "$cache" && echo '99d7094094210d02e29cbc6ceb2ab2b358f7bce7fd720005928bb28caabd4856  agondev-linux_x86_64.tar.gz' | sha256sum --check --status)
if [[ ! -f "$cache/agondev/bin/ez80-none-elf-clang" ]]; then tar -xzf "$cache/agondev-linux_x86_64.tar.gz" -C "$cache";fi
