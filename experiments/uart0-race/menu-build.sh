#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
b=build/uart0-race
cp "$b/identity.h" build/uart0-suite/identity.h
make -C experiments/uart0-suite AGONDEV_TOOLCHAIN="$PWD/build/uart0-suite/toolchain/agondev"
cp experiments/uart0-suite/bin/menu.bin "$b/menu.bin"
.venv/bin/python -B - <<'PY'
from pathlib import Path
p=Path('build/uart0-race');b=(p/'menu.bin').read_bytes();assert 0<len(b)<0xf000
(p/'menu.inc').write_text(''.join('    DB '+','.join(map(str,b[n:n+24]))+'\n' for n in range(0,len(b),24)))
PY
cp experiments/uart0-suite/entry.asm experiments/uart0-suite/entry.linkcmd "$b/"
(cd "$b" && ~/.local/bin/agon-zds ez80asm -list -listmac -quiet -NOsdiopt -warn -debug -NOigcase -cpu:eZ80F92 entry.asm && ~/.local/bin/agon-zds eZ80link @entry.linkcmd && objcopy -I ihex -O binary --gap-fill 0 entry.hex test.bin)
