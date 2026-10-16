# Console8 controlled receiver diagnostic

Console8 R0010 now passes the physical diagnostic: normal control plus forced
recovery-before-disable ordering,66 FIFO bytes stranded before rescue, all8192
payload bytes verified with zero receive errors. See [physical-results.json](physical-results.json).
This establishes the mechanism under the intentional timing trigger; a natural
stock-image failure and production receiver repair are not established. The
Author confirms the menu repair works. Diagnostic VDP is still installed;
stock restoration confirmation remains open. Raw return and verified archive
are build/uart0-race/hardware-return-002 and build/uart0-race-console8-r0010.tar.gz.

The first physical diagnostic R0009 hung because the fixture reused MOS SAVE
for a progress filename; that API refuses an existing file. The repaired
native fixture uses overwrite/write/close and performs no disk/screen I/O
from ARM until DONE, avoiding RTC timestamp bytes in the raw payload. See
[the findings](../../docs/uart0-checkpoint-failure.md). `fat-regression.py` checks
the real MOS FatFS/SPI path using disposable FAT images: old hang reproduced,
both-engine fixed native checks and full menu integration passed, payload/
handshake/storage failure controls rejected. VDP and MOS images are unchanged.
The corrected test and menu repair are staged together for a substantive
hardware retry; no separate menu-only bench trip is requested.

The unchanged-VDP hardware tests passed. This new test asks whether the ESP32
receiver can enter the particular stuck state captured in Flexe when we widen
the suspected timing window. It records the actual driver operations, captures
the state before rescue, then checks the recovered payload. A forced diagnostic
result does not establish a naturally occurring stock-firmware failure.

HW-002 in the sole TODO owns this work; [the plan](../../docs/uart0-recovery-diagnostic.md)
defines scope. This agent owns VDP firmware and MOS integration; Flexe owns the
emulator. Upstream trees and installed SDK archives remain untouched. Physical
flashing/execution is performed by the Author, using [readme.txt](readme.txt).

The private build exports VDP2.16.0 commit c7ac293d2aa81ddfa693390549bcd909069c8fc3,
vdp-gl ac2dd5986daf496c43ae8e7fe41836274aec54a0, CRC1.0.4 and ESP32Time2.0.6.
PlatformIO espressif32@6.6.0 uses Arduino-ESP32 2.0.14/IDF4.4.6. A source copy
of [Espressif's UART driver](https://github.com/espressif/esp-idf/blob/v4.4.6/components/driver/uart.c)
is pinned by SHA2560a90ac006b6a0cadaac4c47ab035a54c782fb6171fda82e9dd059a3d84c4b0be.
Its Apache-2.0 copyright/header and LICENSE are preserved; new hooks/helpers
are MIT. Full sources, VDP/library licenses and contributor notices accompany
the bundle. No upstream code is relicensed.

`prepare.rb` inserts hooks at actual full-flag publication, ISR RX mask write,
reader recovery after its RX re-enable, and ISR error observation. The copied
driver replaces the archive object through normal application linkage; it does
not patch the installed SDK. `audit.py` checks linked definitions and retains
both original and instrumented disassembly. The original object publishes the
flag at ISR offset0x33e, enters the lock via0x34b and writes RX mask at0x36a.
All original operations remain; hooks are disarmed at boot. A trigger holds
the first ISR publication window until normal reader recovery or at most
2400000 CCOUNT cycles (10ms at the pinned240MHz). It never waits under the
UART lock or globally disables interrupts. The diagnostic deliberately changes
scheduling; it is not a stock binary or production repair.

Private VDU23,0,E6 supplies version-specific HELLO(D6), ARM(mode0/1) and
serialized nibble reports. It avoids the existing E7 margin and D8/D9 owner
commands. Stock VDP lacks the handshake and produces SKIP. Each case waits
briefly for the real256-byte ring to fill, then reads through normal
`uart_read_bytes` on the VDP processing core. The triggered ISR waits for
normal recovery on the other core before its original mask store. When reads
stop, state is captured before a one-shot diagnostic re-enable. Source memory
is retained until drain; the payload is4096 nonzero bytes plus an end marker.

Each160-byte URD1 version1 receiver record contains count/CRC, latched RX
errors, phase flags, pre-escape FIFO/ENA/RAW/full/buffered/stash/remain state,
ISR/reader core IDs, flow settings and four24-byte event slots. Slots identify
publish, recovery, mask and escape, with observed flag/FIFO/mask/raw/buffered/
stash and core-local CCOUNT. CCOUNT values are not compared across cores.
The cross-core handshake and observed flags establish the controlled ordering.
Snapshots are stopped-progress observations, not atomic driver snapshots.

Host URDHOST1 version1 reports are332 bytes:12-byte header and two records.
Native name slots73/89/105/121 hold completed/baseline/failure/progress names.
The menu allocates U/L/V/O report names and R/runs.log journals; no RTC naming.
Progress is saved before case/arm/drain and report retrieval, with case text
on-screen. Native timeouts preserve reports and borrowed RAM when safe return
cannot be proven. The menu validates count/CRC/diagnostic epochs, core roles,
publish/recovery/mask state and pre-rescue FIFO wakeup failure independently.
Invalid ordering is PENDING, not PASS; damaged payload/reporting is FAIL.
Emulator runs always report physical_target0/PENDING even with valid evidence.

Build with `bash experiments/uart0-race/build.sh` on the Pi controller; ZDS II,
AgonDev menu and ESP32 compilation run on Oryx. On Oryx, its project venv runs
`profile.py` and `qualify.py jit` / `interp`; `profile.py menu-auto` followed by
`qualify.py <engine> --menu` checks integration. `profile.py manual` then
`interactive.py` exercises real SDL keys headlessly. Human review profiles
remain stopped; invoke only their profile-local `./fab-agon-emulator` wrapper.
Positive/negative attempts are archived separately. Corrupt payload, missing
end marker, missing HELLO and contradictory evidence controls are required.

Menu8/4 invokes only this explicit diagnostic test. Run-all excludes it and
does not flash. Menu9/2 offers the staged diagnostic image,9/4 stock restore;
emulator profiles block the updater. Console8 retains the old experimental
MOS API1.1/ROM CRC239097B7. No new batching firmware is tested here.

Packaging requires both-engine protocol/menu receipts, all negative controls,
linked-driver audit and real-key menu receipt. The guarded deployer recognizes
the existing /test/mos-uart0 manifest, checks unique UUID8658-1C23, archives prior
contents off-card and preserves root MOS/results. Hardware-readable firmware
identities and restoration instructions are beside test.bin. Physical results,
natural failure frequency, any firmware repair and release qualification remain
unestablished until their separate evidence gates are met.

Preparation is complete: native JIT/interpreter9.040s/9.335s, integrated menu
14.053s/14.303s and real-key menu16.335s pass. Corrupt payload9.041s, missing
end marker14.858s and absent handshake13.849s are rejected; the three
contradictory-evidence controls are rejected independently. See [results.json](results.json).
The bundle is hash-verified on Console8 UUID8658-1C23, preserving all22 earlier
report/journal files and root MOS. Diagnostic file CRC is3039EE5C. The fresh
Oryx manual profile is stopped. Hardware execution/restoration/return remain
pending; no physical firmware flashing or receiver repair occurred.

The Author requested notes then stop. Raw attempts/builds/ELF/map/disassembly
and bundle are retained in Oryx build/uart0-race; previous SD contents in Oryx
build/uart0-suite/before-race-20261014. The subsequent archive-only follow-up
completed build/uart0-race-evidence-20261014.tar.gz on both hosts, with SHA
verification and22 required entries checked. Missing Oryx notes were synchronized
before creation; the failed archive is preserved separately. No test, flash or
deployment work resumed. New work is uncommitted after checkpoint0e01958.
