#!/usr/bin/env bash
set -euo pipefail
(cd build/uart0-async/ez80-model && sha256sum --check --quiet ../../../experiments/uart0-async/model.sha256)
for mode in scalar otirx; do
 (cd "build/uart0-batching/$mode" && bash remote-build.sh)
 .venv/bin/python -B experiments/uart0-ab/read_map.py "build/uart0-batching/$mode"
done
~/.cargo/bin/cargo build --locked --offline --release --manifest-path build/uart0-batching/runner/Cargo.toml --target-dir build/uart0-batching/target
for mode in scalar otirx; do
 for n in 1 2 4 8 16; do
  UART_BATCH_SIZE=$n build/uart0-batching/target/release/mos-uart0-async-qualification "build/uart0-batching/$mode/driver.bin" "build/uart0-batching/$mode/symbols.txt" > "build/uart0-batching/checks-$mode-$n.txt"
 done
 for fault in bad-guard burst release; do
  if UART_BATCH_SIZE=16 build/uart0-batching/target/release/mos-uart0-async-qualification "build/uart0-batching/$mode/driver.bin" "build/uart0-batching/$mode/symbols.txt" "$fault" > "build/uart0-batching/negative-$mode-$fault.log" 2>&1; then echo 'Fault control survived';exit 1;fi
  .venv/bin/python -B -c 'from pathlib import Path;import sys;expected={"bad-guard":"CTS group allowance exceeded","burst":"burst exceeds 16","release":"early source release"};assert expected[sys.argv[2]] in Path(sys.argv[1]).read_text()' "build/uart0-batching/negative-$mode-$fault.log" "$fault"
 done
done
(cd build/uart0-batching && tar -czf results.tar.gz scalar otirx source.json checks-*.txt negative-*.log)
