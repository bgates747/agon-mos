# Native experimental UART source

This regular MOS variant implements application-controlled background UART0
sending with bounded OTIRX refills. Legacy output remains blocking. Applications
discover the feature, opt in and retain borrowed buffers until released.
This is an experimental implementation; hardware/release acceptance is separate.

Hardware hold, 2026-10-16: the first native image did not boot on Console8.
The adopted C baud calculation multiplied at 24-bit width and programmed
divisor 11 instead of 1 at 1152000 baud. UART0 and UART1 now widen an operand
before multiplying. This is UART-DEV-003, a required native C arithmetic
correction; replace it only with an equivalent, actual-register-tested divisor
calculation. The root linked-image guard rejects the withdrawn instruction
sequence. MOS-owned boot_audit.rs executes linked routines and reset/startup,
including a baud-aware minimal boot peer. Historical images and software
receipts are retained in ../../../agon-mos/build/uart0-native. The physical
incident, replacement evidence and limits are recorded in
../../../agon-mos/experiments/uart0-native/BOOT-FAILURE.md. Do not reflash the
withdrawn image. The replacement still requires physical acceptance.

Foundation: ab95feee301d2cd40470cf2bda85a0fe1c3c008e. Shared tools:
49dc33fee817cb184572351ee71dae7da9a139c4. The shared API is the byte-exact,
unmodified foundation export under src/shared-api; getfunction13 is this project's reservation,
and12 is null/retired. The qsort public experiment and unrelated post-release
VDP oversized-packet fix are not imported. Existing internal sorting remains.

UART delta comes from frozen source.tar SHA256
38321531d35faff356b065daab1b4ac64dea9a4acb4e3d1e0b72177937dacc9f.
docs/uart0-native-mapping.json records its units and one-time readable syntax
conversion. Normal builds assemble this maintained GNU source directly.

UART-DEV-001 is the intentional behavior change: async sessions, descriptor
queue, CTS admission, OTIRX/chunk accounting, sole receive ownership, legacy
serialization and return/OSCLI/callback/crash lifetime fences. Preserve the
existing ABI1.2 and default1; remove only through an explicitly reviewed feature
withdrawal or equivalent replacement. UART-DEV-002 is the dialect port: native
macros/sections and unique local names preserve emitted instruction semantics.
The original frozen source and relocation comparisons are the encoding oracle.

The root firmware-check invokes tools/check_uart0_native.py after shared
runtime/layout/provenance guards. It inspects the actual ELF, not only source:
two-stage discovery, table pointers, BSS layout, native OTIRX and owner hooks.
Behavioral oracles separately check CTS, IRQ, source lifetime and copied bytes.
No bitmap or linker success certifies every receiver's physical CTS reserve.

The sole unfinished task index is ../../../agon-mos/TODO.md. Owner boundaries
are in OWNERSHIP.md and the selected shared policy. No EMOS implementation or
installed firmware change follows from this regular MOS candidate.
