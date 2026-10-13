#!/usr/bin/env bash
# MOS owns the native test app. Consume the separately owned qualified runtime.
set -euo pipefail
cd "$(dirname "$0")/../.."
build=build/uart0-flexe
sha256sum --check --quiet experiments/uart0-flexe/reference.sha256
../flexe-agon-emulator/build/uart-tests | tee "$build/uart-tests.txt"
cp experiments/uart0-flexe/{app.asm,app.linkcmd} experiments/uart0-async/{driver.asm,fixture.asm} "$build/"
(
    cd "$build"
    for unit in app driver fixture; do
        ~/.local/bin/agon-zds ez80asm -list -listmac -quiet -NOsdiopt -warn -debug -NOigcase -cpu:eZ80F92 "$unit.asm"
    done
    ~/.local/bin/agon-zds eZ80link @app.linkcmd
    objcopy -I ihex -O binary --gap-fill 0 app.hex app.bin
)
cp ../golem/docs/tasks/GOLEM-021/consumer/build/staged-firmware.bin "$build/esp32-firmware.bin"
cp ../golem/docs/tasks/GOLEM-021/consumer/build/staged-firmware.elf "$build/esp32-firmware.elf"
if [[ ! -x .venv/bin/python ]]; then
    bootstrap=${UART_VENV_BOOTSTRAP:-../golem/.venv/bin/python}
    "$bootstrap" -m venv .venv
fi
.venv/bin/python -B experiments/uart0-flexe/profile.py
.venv/bin/python -B experiments/uart0-flexe/check-profile.py | tee "$build/check-profile.txt"
{
    ~/.cargo/bin/rustc --version
    ~/.cargo/bin/cargo --version
    .venv/bin/python --version
    wine --version
} > "$build/tools.txt"
sha256sum experiments/uart0-flexe/{app.asm,app.linkcmd,reference.sha256,profile.py,qualify.py,check-profile.py,build.sh,remote-build.sh,packets.rb} \
    experiments/uart0-async/{driver.asm,fixture.asm} "$build/setup_emulator.py" \
    "$build/packets.inc" "$build/expected-tx.bin" "$build/expected-rx.bin" "$build/app.bin" \
    "$build/app.hex" "$build/app.map" "$build/tools.txt" > "$build/inputs.sha256"
sha256sum --check --quiet experiments/uart0-flexe/reference.sha256
