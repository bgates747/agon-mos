# Bounded UART0 CTS derivative: owner integration handoff

The sender now has an assembled/linked alternative to waiting indefinitely in an
interrupt when CTS blocks. It defers the same borrowed source and resumes via
bounded VBlank rearm. This removes that source-level exclusion hazard; it does
not establish the cause or cure of the failed EMOS UART1 receive-overrun trial.
The current working ROM and published RC3 are unchanged.

## Exact code and artifacts

Project `/Agon/mystuff/agon-mos`, branch `codex/rfc25-bounded-cts`, implementation
commit05b8b10. Generic core/emitter U1 remains823bb91. UART0 donor Eirene
97311c437093e416342a6c836cf9914f2ced027d; its own AgonDev toolchain is preserved.
No ZDS II migration. Patch:
`/Agon/mystuff/agon-mos/experiments/uart0-rfc-retry/bounded-cts.patch`.
Reconstruction/build/verification scripts and contract README are beside it.

Package `/Agon/mystuff/agon-mos/build/goal001-uart0-retry/bounded-cts-r01.zip`,
1792287 bytes, SHA256
`5877625525ea0c66d82d4da8218b4d36bd652ecffd83af9186efbf39a9059f1d`.
Contains full private original/candidate source snapshots, native ROM/map,
patch/scripts/license and retained build/disassembly/structural evidence.
No SDK library is bundled; its exact hash/tool hashes are in build-info.json.
This is an offline owner handoff, not a flash appliance or release candidate.

Candidate raw ROM100946 bytes, SHA256
`6f6aad86f547cc3848d94b11cae8e972648c33d6918cf51fded26ec684ab48b7`, CRC4CC4D184.
Original paired source rebuild100894 bytes, SHA256
`b188b700727b8d88249042b4a680472938a41c7093f9517d79b772a053dcd994`, CRC5658179C.
They use installed libagon5de78783, which differs from published RC3's frozen
04e34018 dependency; original is not relabelled as the released d7a51147 ROM.
Paired delta is52 ROM bytes and1 BSS byte. Serial text390→438, IRQ text378→382.
Only serial.asm and interrupts.asm source change; boot/init ordering is intact.

## Mandatory EMOS binding

Exports `uart0_async_retry` and one BSS byte `uart0_tx_retry_pending`. One GPIO
CTS sample precedes all count/pointer mutation. Blocked ISR masks only TX-empty,
sets pending and restores its existing AF/EI/RETI frame. The VBlank helper only
rearms; no independent FIFO copier, LSR read, timer, queue or syscall is added.
Inactive helper does no peripheral I/O. Existing callback/mixed-mode ABI and
positive source semantics remain the donor's; zero count/invalid/double-submit
remain outside that donor's valid-caller contract, not newly supported inputs.

Extender owns derivative splice, full-register/IFF/Legacy/admission/RX integration
and exact size/qualification within its931-byte budget. It MUST test pending in
`_emos_uart0_async_owned` BEFORE IER/TEMT and retain BUSY while a source is
deferred. TX-empty OFF and TEMT ON can coexist with a live borrowed source.
Foreground callers must observe pending, IER and TEMT and retire ownership in
one bounded atomic section that preserves the caller's incoming IFF. Ordering
the reads alone is insufficient: TX IRQ may defer between the pending read and
the IER/TEMT reads. This clarification follows the owner's pre-install correction
`u1-goal001-foreground-ownership-atomic-correction-nine`; combined EMOS ROM
`d43150`/source244030d is withdrawn from deployment selection. Its historical
linked checks remain valid only within their recorded structural scope. This
live handoff addendum does not change the immutable standalone r01 ZIP.
Owner abort/reset/route teardown must atomically invalidate pending so no later
VBlank rearms abandoned storage. Keep existing callback+TEMT/reciprocal NM gate,
first-error retention, checked source storage and positive close. This is not a
drop-in EMOS ROM. No owner source tree was edited.

VBlank retry can cost a full refresh interval after CTS becomes ready. No timing,
headroom, reserve or throughput gain has been measured. Conditional UART0 risk
remains distinct from unknown trial76 overrun causality. Owner source/physical
isolation comes before any integrated-rate or bot-capacity claims.

## Validation scope and custody

Compiler318: original/candidate full native builds pass3.875s; owned child groups
joined/released09:31:35UTC. Actual successor Extender319 notified through immediate
steering. No Oryx work (now down), guest/CPU emulator, device/SD or firmware action.
Brief subsequent source/binary inspection is not another compilation.

Eight UART negative controls reject the original spinning donor and seven unsafe
mutations: pre-admission count write, RX-bit loss, missing rearm, retry copy,
pending callback, inactive I/O and bad saved frame. Checks compare exact source
paths and final linked defer/rearm/branch/hook bytes;256 IER combinations are
bit algebra, not executed interrupts. Both startup verifiers pass and each rejects
six startup mutations. These are structural/source/linked proofs, not actual ISR
execution or a physical regression pass. Existing source/linked evidence remains
explicitly scoped. Source/runtime/clock timing testing remains owner work.

The portable patch retains upstream tabs/blank context; git's whitespace checker
flags those embedded diff-context characters as new text in the patch artifact.
Code/docs outside that exact patch pass the whitespace check. Do not strip patch
context merely to change that style-check result. Native/source checks do not
depend on ignoring executable changes.

MechAgon's profiling helper already has `../goal001-timing-contract.md`: current
PRT /256 resolution13.889us, bounded single-pass epoch~0.910s, irq_complete0 until
atomic shared count/epoch/all-active-IRQ totals are supplied. Partial UART
brackets cannot claim exclusive CPU. Bounded spare-work against a quiet baseline
is a supported workload-equivalent alternative without a new UART timing API.

Direct GOAL/maxrate human sources were verified and retained before work; existing
queues/custody and owner integration fences remain. This handoff selects no
standalone flash, replay of failed kit76, or separate physical fixture.
