# Console8 stock VDP restoration, 2026-10-31

The Author requested checking the Console8 attached to the Pi5 and replacing
its VDP with stock Bistromathics if necessary. The active firmware was a custom
Pingo2 build. Official VDP 2.16.0 Bistromathics was installed successfully;
esptool verified the written application's hash and reset the ESP32.

The USB endpoint was CP2104 serial 027E3885, ESP32-PICO-D4 revision 1.1,
MAC 64:b7:08:b8:50:48. A complete 4 MiB flash backup was taken first:
`build/c8-vdp-stock-20261031/before-flash.bin`, SHA256
`8b759a1f0a180713af1f2aa5f8032c663682a5f09471a347962dc25ab9e10ae7`.

The installed partition table has app0 at 0x10000 and app1 at 0x150000,
each 0x140000 bytes. Both OTA selection records have valid sequence CRCs;
sequences 31 and 30 select app0. Neither application matched stock. The active
app0 contains `Pingo2 typed control` and `esp32dev-pingo2-hud` build paths.
This identifies a custom build, without claiming its exact version or provenance.

Wrote only app0 at 0x10000 using esptool 4.12.0, 460800 baud. Bootloader,
partition table, OTA selection records, NVS and app1 were preserved. MOS was
not flashed. The source was `build/uart0-suite/vdp-2.16.0.bin`, 1,077,840 bytes,
SHA256 `b807beef35823b13a0a056f11b7464cd1b1c6356dce0e4098b78ebe059ded35f`,
matching the pinned official release in `experiments/uart0-bench/fetch-vdp.sh`:
https://github.com/AgonPlatform/agon-vdp/releases/download/v2.16.0/firmware.bin

`build/c8-vdp-stock-20261031/write-flash.log` records successful write,
“Hash of data verified”, and RTS reset. This is verified installation evidence;
the monitor's visual boot banner was not observed by the agent.
