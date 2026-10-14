#!/usr/bin/env bash
set -euo pipefail
(cd build/uart0-async/ez80-model && sha256sum --check --quiet ../../../experiments/uart0-async/model.sha256)
for mode in default grouped chunk otirx; do
 (cd "build/uart0-ab/$mode" && bash remote-build.sh)
 .venv/bin/python -B experiments/uart0-ab/read_map.py "build/uart0-ab/$mode"
done
~/.cargo/bin/cargo build --locked --offline --release --manifest-path build/uart0-ab/runner/Cargo.toml --target-dir build/uart0-ab/target
build/uart0-ab/target/release/mos-uart0-async-qualification build/uart0-ab > build/uart0-ab/model.csv
# Negative controls must be rejected by the byte/ownership assertions.
for fault in corrupt no-progress; do
 if build/uart0-ab/target/release/mos-uart0-async-qualification build/uart0-ab "$fault" > "build/uart0-ab/$fault.log" 2>&1; then
  echo "Control survived: $fault"; exit 1
 fi
done
.venv/bin/python -B -c 'from pathlib import Path; p=Path("build/uart0-ab"); assert "payload byte corruption" in (p/"corrupt.log").read_text(); assert "API hung: blocking_send" in (p/"no-progress.log").read_text()'
tar -czf build/uart0-ab/results.tar.gz -C build/uart0-ab default grouped chunk otirx model.csv corrupt.log no-progress.log source.json
