# P4 checked stock MOS recovery

The Author explicitly requested Jeroen's normal checks after blind recovery
failed. This P4 adaptation restores product-ID7 admission, MOS RAM upload CRC32,
and post-flash MOS CRC32 over the108490-byte stockMOS3.0.2 image. The90-byte
flash agent and peripheral initialization derive from upstream agon-recovery
95d68464afd049945e1dfd780c1c07621d565450. No extra pre-erase dump or PC-value
admission check is imposed. CPU PC reads in memory CRC preserve/restore PC as
upstream does; they are not a diagnostic gate.

GREEN clock is GPIO46/EXT2pin7; BLUE data GPIO47/EXT2pin6. Harness GPIOs are
inputs without pulls. Same private ESP-IDF5.5.5/Arduino3.3.11 build environment
as experiments/zdi-p4-flash-only; stock payload header retained. Only exact
FLASH starts recovery, never boot. A failed identity returns before CPU halt,
RAM initialization or MOS upload; failed MOS RAM CRC prevents flash-agent
upload/execution. Final CRC checks MOS bytes at0; this is not full128KiB
verification. Target stays in break following post-flash CRC until reset.
Every terminal outcome releases both ZDI outputs and waits without retry.

install_and_flash.py installs/verifies the selected P4 application and runs
one explicitly armed recovery. Device paths are arguments. It preserves the
previous verified P4 programmer through the existing archived binary/full
backup. Original P4 restoration remains deferred until Console8 is repaired.

First run: identityFFFF, revisionFF, statusFF; expected product0007. No MOS
upload/erase/program. Evidence build/c8-zdi/p4-checked-20261030/run-001 on both
Pi and Oryx. Console8 remains unrecovered.
