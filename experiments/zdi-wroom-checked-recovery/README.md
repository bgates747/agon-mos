# WROOM checked stock MOS recovery

This restores stockMOS3.0.2 through the now-clean Console8/WROOM link. It keeps
the proven10us signal timing and Jeroen Venema's normal checks: eZ80product7,
MOS RAM upload CRC32, then post-flash MOS CRC32. A completion result without a
passing target flash CRC is not success. Physical boot remains a separate check.

Author-confirmed wiring: BLUE WROOMGPIO26 clock to targetZDI4, GREEN GPIO27 data
toZDI6, upper-middle ground, no series resistors, improved breadboard. External
WROOM USB endpoint is selected explicitly by the host. P4 is not used.

Algorithm authority is AgonPlatform/agon-recovery95d68464afd049945e1dfd780c1c07621d565450.
Initialization ports, instruction injection, RAM addresses, size parameter,
original90-byte flash agent and MOS CRC algorithm follow that source. Full
upstream MIT copyright/permission notice is LICENSE.agon-recovery.txt. The P4
checked adaptation supplied the existing portable class/scalarCRC shell; WROOM
GPIO input-enable/direction/read timing matches the successful identity baseline.

Only26/27 are configured. Startup selectsINPUT_PULLUP, releases both outputs
and waits for exact FLASH. No BOOTbutton shortcut, VDP update, SPIFFS or automatic
flash/retry. Product/revision/status are read, product must be7. CPU initialized,
MOS uploaded at0x050000 in256-byte chunks with yields for the watchdog. MOS RAM
CRC must equal15BD0583 before length0x070000 and original90-byte agent0x040000
are uploaded. Agent runs, waits10seconds with no ZDI, CPU break is requested,
then CRC over108490flash bytes must again equal15BD0583. PC preservation during
memory reads follows upstream; there are no added PC-value admission gates,
pre-erase dump requirement, custom RAM parameter checks or new target diagnostics.

Every terminal result releases outputs and waits without automatic retry.
After post-flash CRC the CPU is in break; Author must reset/powercycleConsole8
to boot. Do not reset before the post-flash verification result arrives.

StockMOS108490bytes SHA256
 d564243283972690933a4554296ad6202ca4ef54572279533a942960846bebae.
Originalagent90bytes SHA256
 ca44786969dc2dd1b0fa51e6b80f530b7241317dc27bf8efac3ca7d56bddee06.
Generated headersrc/generated/mos_recovery_payload.hpp uses the same fields/
namespace as the maintained Extender payload generator and is ignored byGit.
Build with pinned PlatformIOplatformespressif32@6.7.0/Arduino2.0.16 onOryx:
platformio run -e esp32dev. Source/ELF/binary/build logs remain in the isolated
build/c8-wroom-checked-20261031/project; upstream checkouts stay unmodified.

install_and_flash.py preserves the affected WROOM app span, confirms the prior
quietv3bytes, installs/verifies the selected recovery app, captures its banner
and sends FLASH once. These programmer checks do not replace target CRC checks.
Device paths are arguments. Host timeout300seconds is a failure stop, not an
automatic replay. CRC success verifies the programmed MOS length, not padding
through the whole128KiB or physical boot.
