#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
build=build/uart0-suite
(cd build/uart0-mos/runtime && sha256sum --check --quiet ../../../experiments/uart0-mos/runtime.sha256)
make -C experiments/uart0-suite AGONDEV_TOOLCHAIN="$PWD/$build/toolchain/agondev"
cp experiments/uart0-suite/bin/menu.bin "$build/menu.bin"
.venv/bin/python -B - <<'PY'
from pathlib import Path
b=Path('build/uart0-suite/menu.bin').read_bytes()
assert 0<len(b)<0xf000
Path('build/uart0-suite/menu.inc').write_text(''.join('    DB '+','.join(map(str,b[n:n+24]))+'\n' for n in range(0,len(b),24)))
PY
cp experiments/uart0-suite/{entry.asm,entry.linkcmd} "$build/"
for fixture in entry bench/bench stress/stress api/app api/short; do
    kind="${fixture##*/}"
    dir="$build"
    if [[ "$fixture" == */* ]]; then dir="$build/${fixture%/*}"; fi
    (
        cd "$dir"
        ~/.local/bin/agon-zds ez80asm -list -listmac -quiet -NOsdiopt -warn -debug -NOigcase -cpu:eZ80F92 "$kind.asm"
        ~/.local/bin/agon-zds eZ80link "@$kind.linkcmd"
        objcopy -I ihex -O binary --gap-fill 0 "$kind.hex" "$kind.bin"
    )
done
cp "$build/entry.bin" "$build/test.bin"
