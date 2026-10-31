# P4 flash-only stock MOS recovery

This programmer sends known-good stock MOS to the bricked Console8 without
reading the eZ80. The Author explicitly requested this variant after WROOM
recovery failed to restore boot. Its completion message means the write
sequence finished; only the Author's monitor observation establishes boot.

GREEN clock uses P4 GPIO46 / EXT2 pin7. BLUE data uses GPIO47 / EXT2 pin6.
Both are outside the Extender harness. The Author confirmed this wiring,
33-ohm series resistors and Oryx power/USB on 2026-10-30. No analyzer is
attached. Ground remains common; no positive power rails are joined.

`main.cpp` adapts the maintained Extender P4 GPIO/USB implementation and the
initialization/upload/flash-agent algorithm from AgonPlatform/agon-recovery
commit `95d68464afd049945e1dfd780c1c07621d565450`. It has no eZ80 read API,
identity sampling, PC read, CRC verification or dump operation. The 256-byte
upload bursts yield between transactions for the P4 watchdog. Each bit has
explicit low/setup/high delays of one microsecond in the existing P4 adaptation.

Boot releases the harness and ZDI signals as inputs without pulls. Only an
exact `FLASH` console command starts the one-shot sequence. It initializes the
eZ80, uploads MOS at 0x050000, writes its three-byte length at 0x070000,
uploads the original 90-byte agent at 0x040000 and resumes there. It waits
ten seconds without further ZDI access, releases GREEN/BLUE and stops.
No erase occurs on boot and no automatic retry or target reset occurs.

The payload is stock MOS 3.0.2, 108490 bytes, SHA-256
`d564243283972690933a4554296ad6202ca4ef54572279533a942960846bebae`.
The original 90-byte flash agent has SHA-256
`ca44786969dc2dd1b0fa51e6b80f530b7241317dc27bf8efac3ca7d56bddee06`.
Generated payload bytes remain ignored build artifacts.

Build on Oryx using the retained private ESP-IDF 5.5.5 / Arduino 3.3.11
environment in `build/c8-zdi/repair-20261028`. Preserve its previous source,
copy this source into `project/main/mos_recovery.cpp`, retain the stock-payload
generated header and run its `build-paced.sh`. This reuses the existing
360-MHz, internal USB Serial/JTAG, 16-KiB stack configuration. Upstream and
Extender source checkouts remain unchanged.

`install_and_flash.py --help` describes the explicit host invocation. It
preserves the selected P4's full flash, installs/verifies only its application
partition, captures the USB console and sends exactly one `FLASH` command.
These P4 preservation/install checks do not read or verify target MOS.
Device paths are supplied as arguments. Keep original P4 restoration deferred
until the Author confirms the Console8 is repaired.
