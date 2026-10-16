#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
mkdir -p build/uart0-ui/packets/src
b="$PWD/build/uart0-ui/packets"
printf '#include "%s/experiments/uart0-suite/tests/menu_packets.c"\n' "$PWD" > "$b/src/main.c"
cp experiments/uart0-suite/src/uart.src "$b/src/uart.src"
cp experiments/uart0-suite/tests/menu_packets.src "$b/src/packets.src"
cat > "$b/Makefile" <<'MAKE'
NAME = menu
RAM_START = 0x90000
RAM_SIZE = 0x18000
LDHAS_ARG_PROCESSING = 0
LDHAS_EXIT_HANDLER = 0
include $(AGONDEV_TOOLCHAIN)/config/makefile.inc
CFLAGS += -std=c11 -Wall -Wextra -Werror -I$(MENU_IDENTITY)
MAKE
make -C "$b" AGONDEV_TOOLCHAIN="$PWD/build/uart0-suite/toolchain/agondev" MENU_IDENTITY="$PWD/build/uart0-ui"
.venv/bin/python -B - <<'PY'
from pathlib import Path
p=Path('build/uart0-ui/packets');b=(p/'bin/menu.bin').read_bytes();assert 0<len(b)<0xf000
(p/'menu.inc').write_text(''.join('    DB '+','.join(map(str,b[n:n+24]))+'\n' for n in range(0,len(b),24)))
PY
cp experiments/uart0-suite/entry.asm experiments/uart0-suite/entry.linkcmd "$b/"
(cd "$b" && ~/.local/bin/agon-zds ez80asm -list -listmac -quiet -NOsdiopt -warn -debug -NOigcase -cpu:eZ80F92 entry.asm && ~/.local/bin/agon-zds eZ80link @entry.linkcmd && objcopy -I ihex -O binary --gap-fill 0 entry.hex test.bin)
