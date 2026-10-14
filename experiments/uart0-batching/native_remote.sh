#!/usr/bin/env bash
set -euo pipefail
b=build/uart0-batching/native
(cd "$b" && ~/.local/bin/agon-zds ez80asm -list -listmac -quiet -NOsdiopt -warn -debug -NOigcase -cpu:eZ80F92 host.asm && ~/.local/bin/agon-zds eZ80link @host.linkcmd && objcopy -I ihex -O binary --gap-fill 0 host.hex test.bin)
for n in 1 2 4 8 16; do
 cp "$b/packets.inc" "$b/stress$n/"
 (cd "$b/stress$n" && ~/.local/bin/agon-zds ez80asm -list -listmac -quiet -NOsdiopt -warn -debug -NOigcase -cpu:eZ80F92 stress.asm && ~/.local/bin/agon-zds eZ80link @stress.linkcmd && objcopy -I ihex -O binary --gap-fill 0 stress.hex test.bin)
done
