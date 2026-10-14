#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
# Model build must already have supplied generated/qualified kernel sources.
ruby experiments/uart0-ab/prepare_native.rb
tar -czf build/uart0-ab/native-inputs.tar.gz experiments/uart0-ab build/uart0-ab/native
scp -q -o BatchMode=yes build/uart0-ab/native-inputs.tar.gz oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-ab/
ssh -o BatchMode=yes oryx-linuxlite 'cd ~/Agon/mystuff/agon-mos && tar -xzf build/uart0-ab/native-inputs.tar.gz && bash experiments/uart0-ab/native_remote.sh && .venv/bin/python -B experiments/uart0-ab/profile.py --auto && .venv/bin/python -B experiments/uart0-ab/qualify.py jit && .venv/bin/python -B experiments/uart0-ab/profile.py --auto && .venv/bin/python -B experiments/uart0-ab/qualify.py interp && tar -czf build/uart0-ab/native-final-evidence.tar.gz -C build/uart0-ab native evidence-jit evidence-interp' > build/uart0-ab/native-final.log 2>&1
scp -q -o BatchMode=yes oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-ab/native-final-evidence.tar.gz build/uart0-ab/
tar -xzf build/uart0-ab/native-final-evidence.tar.gz -C build/uart0-ab
