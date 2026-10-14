#!/usr/bin/env bash
set -euo pipefail
cd build/uart0-ab/native
sha256sum *.asm *.inc app.linkcmd > native-source.sha256
for unit in app default grouped chunk otirx fixture; do
 ~/.local/bin/agon-zds ez80asm -list -listmac -quiet -NOsdiopt -warn -debug -NOigcase -cpu:eZ80F92 "$unit.asm"
done
~/.local/bin/agon-zds eZ80link @app.linkcmd
objcopy -I ihex -O binary --gap-fill 0 app.hex test.bin
sha256sum --check --quiet native-source.sha256
