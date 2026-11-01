#!/usr/bin/env bash
set -euo pipefail
build=$1
repo=$PWD
fixture="$repo/$build/${2:-fixture}"
make -C "$fixture" AGONDEV_TOOLCHAIN="$repo/build/uart0-suite/toolchain/agondev" > "$fixture/menu-build.log" 2>&1
cp "$fixture/bin/menu.bin" "$fixture/menu.bin"
.venv/bin/python - "$fixture" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]);b=(p/'menu.bin').read_bytes()
assert 0<len(b)<0x10000
(p/'menu.inc').write_text(''.join('    DB '+','.join(map(str,b[i:i+24]))+'\n' for i in range(0,len(b),24)))
PY
for spec in entry stress/stress app/app; do
 unit=${spec##*/}
 dir=${spec%/*};[[ "$dir" != "$spec" ]] || dir=.
 (
  cd "$fixture/$dir"
  ~/.local/bin/agon-zds ez80asm -list -listmac -quiet -NOsdiopt -warn -debug -NOigcase -cpu:eZ80F92 "$unit.asm"
  ~/.local/bin/agon-zds eZ80link "@$unit.linkcmd"
  objcopy -I ihex -O binary --gap-fill 0 "$unit.hex" "$unit.bin"
 ) > "$fixture/$unit-zds.log" 2>&1
done
cp "$fixture/entry.bin" "$fixture/test.bin"
cp "$fixture/stress/stress.bin" "$fixture/stress.bin"
cp "$fixture/app/app.bin" "$fixture/app.bin"
