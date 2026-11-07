# Atomic foreground wait leaf: off-device handoff

The application can avoid going to sleep just after a callback published work.
This reusable helper gives it an atomic final notification/clock check and
EI/HALT handoff. It adds no MOS, UART, vector or timer code. Actual application
producer glue and the selected optional SDK notification are still required.

Source: `experiments/foreground-wait/{include/aw_wait.h,src/aw_wait.s}`.
Private artifacts: `build/u1-wait-r01/native-r02`. Header is the exact ABI.

* Native leaf163text/0data/0BSS; app state9bytes each;12bytes of register saves
  above function-entry SP, excluding caller arguments/return and interrupt
  nesting/stack. One foreground caller per object; callback notification only.
* Result BYTE A: REFUSED0; PASS1 from begin; WORK2 or HALTED3 from wait.
  BC/DE/HL/IX/IY/shadows/MB/SP preserved by source/linked inspection; flags
  unspecified. Requires actual ADL1. Observed IFF0/MBnonzero/NULL refuses
  without EI/HALT; enabled-entry wait also refuses missing begin token.
* Initialize once, bind stable public MOS clock32 outside DI; valid distinct
  state9/clock4 RAM spans are ordinary caller preconditions. Begin clears the
  sticky byte and snapshots clock BEFORE all foreground service. Wait consumes
  the token, never clears pending, and compares event plus all four clock bytes.
* Final linked EI/HALT is adjacent FB76 at4008d..4008e in the retained leaf-only
  link. Register restoration precedes the pair. Relocations select new addresses
  in the actual consumer; do not hard-code these donor addresses.
* 34 instructions on the longest linked DI-through-EI path; no cycles, RAM wait
  or physical latency bound inferred. Full ABI probe compiled and linked through
  the archive. Eight source and three linked negative controls reject the
  deliberately broken variants; twelve abstract arrival cases plus refusal,
  coalescing, full-clock, consumed-token/no-progress controls pass.

Compiler380 PASS2.564s, all children joined/released14:58:47UTC, no successor.
Unused377 was released before editing; first379 native outputs passed but its
checker raised an uncaught ValueError while rejecting a missing-IFF mutant.
That retained failure and checker corrections are in provenance.json. The leaf
binary stayed byte-identical through the successful check. Installed objdump
truncates displayed JR targets to16bits; the checker resolves actual linked
relative displacement bytes instead of interpreting that display as a branch
to low RAM. Native ABI/stack/branch reasoning remains inspection, not CPU execution.

Standalone object928B SHA
`b5668a440099d6676b7fa8c304fdf7f0a6204ffae275b83604c64afa09207fd7`;
archive1088B SHA
`e0dcbed3f01ce3ef76888487da439d867273ffdf0c22c72905e27b7ad8b510dc`;
leaf raw163B SHA
`6a9ed1bf628a261dba3f43327681aed40a5edd9b74852b324eb3b01b1bff6c33`.
checks.json retains ELF/probe and all artifact hashes.

Missing acceptance: no executed ISA, IFF/register/HALT/IRQ, emulator, PRT,
hardware or physical latency test was performed. No app integration/deployment
or firmware acceptance follows. Root owns producer glue and later matched case;
Extender owns the optional app SDK AGON_NETA_NOTIFY seam. That future hook is
not silently assumed present. Frozen R06/367/80fe is unchanged. Wire-only
TEMT/CTS and silent idle-owner loss retain the established fallback/probes and
source/drain/receiver/positive-close boundaries. Quarantine stays separate.
