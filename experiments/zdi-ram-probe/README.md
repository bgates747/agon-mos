# Console8 halt / RAM diagnostic

RETIRED FROM ACTIVE RECOVERY at the Author's explicit request2026-10-30:
stop custom diagnostics/extra PC gates and use Jeroen's recovery protocol.
Current WROOM is the upstream-based recovery utility, not this probe. Final
normal upload attempts fail its original RAM CRC before flash. See
docs/c8-stock-recovery-2026-10-30.md. Preserve this source/history; do not
reinstall or resume these diagnostic admission tests without a new request.

This diagnostic tests whether ZDI commands work even when identity reads fail.
It cannot erase/program flash: no MOS image, flash agent, controller-write
sequence or resume command is included.

The Author's explicit wiring for this build is GREEN CLOCK GPIO27, BLUE DATA
GPIO26. Startup releases both outputs and waits for exactly
`PROBE CONSOLE8 RAM-ONLY` followed by LF. Nothing automatically runs at boot.
The fixed host runner verifies the matching v11 banner before sending it.

PROBE-001 [x] Send one HALT request despite invalid identity, then require three
status replies with ZDI_ACTIVE set and reserved bits6/1/0 clear. All-FF is
explicitly invalid. The physical2026-10-30 run returns FF/FF/FF and stops here.

Later Author-requested repeat probe-repeat-003 returns exact identity0700AA1C
and three valid halted-state replies9C/9C/9C. It stops at original-PC
verification before RAM. PC samples are not logged, so firstFFFFFF versus
inconsistent subsequent values remain unresolved. CPU last verified halted,
outputs released, serial closed. No new physical change reported; this one
valid identity/halt run does not establish sustained communication reliability.

PROBE-002 [ ] Once HALT is verified, require stable original PC, set ADL/DI,
and map on-chip RAM to upper byteB7. Verify64bytes atB7F000 with four patterns
and two readbacks per pattern, then restore original bytes and PC. CPU remains
halted; physical reset required. This stage was NOT reached in the run above.

The RAM window follows PS0153: F92 RAM spans upper:E000..FFFF. It is not
assumed to begin at upper:0000. Reads and writes are limited to the fixed
register/memory paths in the source. Every driven bit checks WROOM input during
both CLOCK phases and immediately releases pins/stops on disagreement.

Raw evidence, old/new WROOM app images, build and readback receipts:
`build/zdi-ram-probe-20261030/` on Pi and Oryx. The installation receipt's
erase_span_bytes field describes its274432byte backup/readback span; the
Pi verification addendum correctly records270336bytes actually erased for the
269760byte image, with remaining4096bytes unchanged.

The crossed-function v12 variant is built under
`build/zdi-ram-crossed-20261030/`: clock26/data27, without physically moving the
Author's GREEN27/BLUE26 wires. Initially held for the Author's ground check;
the Author instead replaced ground leads and requested a repeat. The unchanged
v11 probe still returnsFF/FF/FF. Temporary v12 returns invalid identity07011141
and invalid HALT statuses87/70/07, stops before RAM, and releases outputs.
Original quiet v11 then restored and readback verified byte-for-byte. No
sniffers attached. Full record: docs/c8-zdi-ground-control-2026-10-30.md.
