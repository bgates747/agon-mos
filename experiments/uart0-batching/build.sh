#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
b=build/uart0-batching
ruby experiments/uart0-batching/prepare.rb
tar -czf "$b/inputs.tar.gz" experiments/uart0-batching "$b"/{otirx,scalar,runner,source,source.json} experiments/uart0-ab/read_map.py
ssh -o BatchMode=yes oryx-linuxlite 'mkdir -p ~/Agon/mystuff/agon-mos/build/uart0-batching'
scp -q -o BatchMode=yes "$b/inputs.tar.gz" oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-batching/
ssh -o BatchMode=yes oryx-linuxlite 'cd ~/Agon/mystuff/agon-mos && tar -xzf build/uart0-batching/inputs.tar.gz && bash experiments/uart0-batching/remote.sh' > "$b/build.log" 2>&1 || { tail -45 "$b/build.log";exit 1; }
scp -q -o BatchMode=yes oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-batching/results.tar.gz "$b/"
tar -xzf "$b/results.tar.gz" -C "$b"
cat "$b"/checks-*.txt
