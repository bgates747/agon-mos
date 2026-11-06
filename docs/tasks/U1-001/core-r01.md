# U1-001 first development tranche

The independent application TX core, copy leaf and simulated-port worked
example are implemented. They are not an installed EMOS adapter. Public
ownership/IRQ/GPIO-retry integration remains I-001; D-002's callable register
entry and actual install/restore also remain incomplete.

Under actual compiler slot 247, the real C core passed ASan/UBSan and its finite
byte/event oracle: 168,516 assertions, including deterministic 256-transfer
CTS/THRE interruption schedules, 1/15/16/17/146/65535/65536 byte lengths, exact
output, single/early source callback, delayed drain, busy/invalid/stop refusal,
owner and line faults, immutable first fault and uncertain partial-write retention.
The assertion count is bookkeeping, not independent scenarios or target proof.
IFF/register/RX coexistence and wake scheduling remain adapter qualification.

Native AgonDev C compilation and assembly/linking passed with warnings treated
as errors. App text for the core is 537 bytes and the OTIRX leaf is 30 bytes;
neither occupies firmware ROM. These exclude future owner/IRQ/install adapters.
Disassembly confirms the C leaf loads the source and count from three-byte stack
slots, zeroes full BC before loading its bounded low-byte count, uses UART1 THR
0xD0 with OTIRX, restores IX and returns A=1 without changing IFF. IY is untouched.
This is static ABI inspection, not executed port/ISR validation.

Compiled simulated-port example: 2,396 bytes, SHA256
`26c1b3a2a1c94dbd661e9c04343715cf7e2225acdc3987953a17fa9f3c3172c2`.
It was not executed. Its source does not call the hardware leaf. Native library:
`build/u1-001/core-r01/libu1.a`, SHA256
`c4c10fe10c2cce4c2519569ad49a395ef83e2fbf81e73cfda229d1a50237b17e`.
Exact input hashes, map, disassembly, logs and binaries are retained in
`build/u1-001/core-r01/`; selected immutable receipts are in receipts/.

The build/check group took 1.66 seconds. All owned children stopped and actual
compiler 247 was released at 17:46:40 UTC with no queued successor. The wrapper
is retained as `experiments/uart1-async/build.py`, parameterized for a fresh actual
checkout and a new output path; it was syntax-checked after parameterization.
Target C/assembly code did not change after the passing build.

No emulator, bench, UART port, vector, card, firmware or MechAgon source was
touched. Extender and MechAgon received source/contract consultation; MechAgon's
exact 146-byte framing and lifetime reply is incorporated in source-review.md.
The next implementation depends on the owner's supported attachment, exclusion,
LSR/error and GPIO-CTS retry contract. No numeric hook ABI or byte cost is assumed.
