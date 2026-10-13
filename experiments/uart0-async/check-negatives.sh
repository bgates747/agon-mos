#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
out_dir=build/uart0-async
runner="$out_dir/target/release/mos-uart0-async-qualification"
for control in cts burst rx release interleave wakeup; do
    case "$control" in
        cts) reason='CTS guard missing';;
        burst) reason='burst exceeds 16';;
        rx) reason='RX read without data';;
        release) reason='early source release';;
        interleave) reason='burst exceeds 16|ordinary output interleaved';;
        wakeup) reason='failed to drain';;
    esac
    if UART_NEGATIVE="$control" "$runner" "$out_dir/driver.bin" "$out_dir/symbols.txt" \
        > "$out_dir/negative-$control.log" 2>&1; then
        echo "FAIL: $control survived" >&2
        exit 1
    fi
    if ! rg -q "$reason" "$out_dir/negative-$control.log"; then
        cat "$out_dir/negative-$control.log" >&2
        exit 1
    fi
    echo "PASS: $control rejected ($reason)"
done
