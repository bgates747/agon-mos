#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
mkdir -p build/uart0-race
if [[ ! -f build/uart0-race/uart-idf-4.4.6.c ]]; then
  curl --fail --silent --show-error --location https://raw.githubusercontent.com/espressif/esp-idf/v4.4.6/components/driver/uart.c -o build/uart0-race/uart-idf-4.4.6.c
fi
if [[ ! -f build/uart0-race/ESP-IDF-LICENSE ]]; then
  curl --fail --silent --show-error --location https://raw.githubusercontent.com/espressif/esp-idf/v4.4.6/LICENSE -o build/uart0-race/ESP-IDF-LICENSE
fi
ruby experiments/uart0-race/prepare.rb
ruby experiments/uart0-race/packets.rb
tar --exclude='*/.pio' -czf build/uart0-race/inputs.tar.gz experiments/uart0-race experiments/uart0-suite/src experiments/uart0-suite/entry.asm experiments/uart0-suite/entry.linkcmd build/uart0-race/firmware build/uart0-race/source.json build/uart0-race/host.asm build/uart0-race/host.linkcmd build/uart0-race/cases.inc build/uart0-race/expected.json build/uart0-race/identity.h
ssh -o BatchMode=yes oryx-linuxlite 'mkdir -p ~/Agon/mystuff/agon-mos/build/uart0-race'
scp -q -o BatchMode=yes build/uart0-race/inputs.tar.gz oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-race/
ssh -o BatchMode=yes oryx-linuxlite 'cd ~/Agon/mystuff/agon-mos && tar -xzf build/uart0-race/inputs.tar.gz && ~/.platformio/penv/bin/pio run -d build/uart0-race/firmware -j 6' > build/uart0-race/build.log 2>&1
ssh -o BatchMode=yes oryx-linuxlite 'cd ~/Agon/mystuff/agon-mos/build/uart0-race && ~/.local/bin/agon-zds ez80asm -list -listmac -quiet -NOsdiopt -warn -debug -NOigcase -cpu:eZ80F92 host.asm && ~/.local/bin/agon-zds eZ80link @host.linkcmd && objcopy -I ihex -O binary --gap-fill 0 host.hex race.bin' > build/uart0-race/native-build.log 2>&1
scp -q -o BatchMode=yes oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-race/race.bin build/uart0-race/
ssh -o BatchMode=yes oryx-linuxlite 'cd ~/Agon/mystuff/agon-mos && bash experiments/uart0-race/menu-build.sh' > build/uart0-race/menu-build.log 2>&1
scp -q -o BatchMode=yes oryx-linuxlite:Agon/mystuff/agon-mos/build/uart0-race/test.bin build/uart0-race/
