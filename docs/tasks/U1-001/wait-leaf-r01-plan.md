# U1-WAIT-R01: reusable foreground atomic wait leaf

Selected implementation delegation:
`2026-11-07_09-48-46_mechagon_goal001-wait-leaf-delegation-fiftyeight`,
under verified direct human GOAL-001 scope in goal001-owner-support.md.
Root owns app glue, Extender optional SDK notify, UART this reusable leaf/header
and source/native-listing controls. Frozen R06/367/80fe remains unchanged.

WLF-001 [x] Implement isolated original AgonDev app source under
`experiments/foreground-wait`. Explicit app state holds volatile sticky byte,
valid-pass byte, clock token4 and stable public MOS clock pointer. No resident
code, vector, PRT, UART read or peer edit. begin clears/snapshots before service;
wait consumes its pass then atomically checks event/clock and uses adjacent
EI/HALT. Refusal0, pass1, work2, HALT-executed3; refuse IFF0/MBnonzero/NULL
without enabling or halting. ADL1 and valid nonwrapping app/public RAM spans
remain caller preconditions. State/code/clock lifetime persists through callbacks.

WLF-002 [x] Add finite abstract notification/interleaving model controls and
source/linked negative controls. No ISA, IRQ or emulator execution. Cover
before-clear/during-service/post-poll/DI/EI-HALT arrivals, no-progress sleep,
coalescing, callback-before-return and tick fallback. Audit all save/restore
paths, no global IFF scratch, disabled-entry refusal, C argument offsets,
return in A, full BC/DE/HL/IX/IY/shadows/SP/MB preservation and FB76 adjacency.
No cycle or hardware latency claim from these checks.

WLF-003 [x] Reserve normal Pi compiler FIFO for one native assembly/C probe/
link/archive/disassembly and bounded model/check tranche. Expected under30s,
120s child/300s whole, serial compiler,512MiB minimum,80C maximum with sensor
availability mandatory. Run only after actual checkout/assert. Join/stop only
owned child groups, retain logs and release immediately; steer actual successor.
No Oryx, target, hardware, service, SD or firmware operations.

WLF-004 [ ] Return pinned header/assembly/object/archive/listing/control results
and exact code/state/stack costs in a private source/artifact bundle. Explain
missing executed-ISA/IRQ/hardware proof and incomplete app producer binding.
No integration or physical acceptance follows from the reusable library build.
