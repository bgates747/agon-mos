# P4 identity-only Olimex control

Author requested identity reads through the Pi5-attached P4/Olimex without MOS
flashing. This image has no MOS/flash-agent payload, CPU halt/write API, RAM
path or FLASH command. Only IDENTIFY exists. It reads product/revision/status
three times,100ms apart, then releases both pins. GREEN clockGPIO46/EXT2pin7;
BLUE dataGPIO47/EXT2pin6. Existing Extender harness pins remain inputs without
pulls. Read transactions match the preceding checked P4 build's timing.

Build with the retained private P4 toolchain described in
../zdi-p4-flash-only/README.md, replacing only its main source. run.py installs
and verifies this P4 application and sends IDENTIFY once; device paths are
arguments. It never opens or resets the mainboard USB port. Only P4 firmware
changes; neither MOS nor VDP firmware is flashed.

Two batches on2026-10-30: first [FFFF/FF/FF,0007/AA/1C,0007/AA/1C]; second
[6262/07/1C,0007/AA/1C,0007/AA/1C]. No explicit P4 reset between batches.
Four of six valid; first of each batch invalid. This demonstrates possible
communication on Olimex, not reliable initial identification or a cause.
No additional timing/wiring changes tested. Raw evidence:
build/olimex-p4-identity-20261030/{run-001,run-002}.
