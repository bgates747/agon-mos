# C2 remaining135B — bounded source consultation

Request `2026-11-08_02-25-01_mechagon_goal001-cpu135-source-size-consult-four`.
Read the exact fcb08f4 C2 source, owner RESULT/manifest/FIRST-WINDOW-CONTRACT.
No owner files edited, compiler/tests/resource/device/timer or firmware action.
Extender keeps implementation and actual size/fit qualification. RX006 admission
takes precedence. The earlier WAIT622 result uses unchanged native A-event ABI;
it does not qualify this C2 firmware fit.

## Concrete small assembly seam: expected4B

In fit-r02/source/src/emos_uart0_rfc25_io.asm, the enabled-only full and final
TX paths each use `jp uart0_cpu_tail`. The target is forward in the same object:
the first skips only the final-fill body plus CTS-defer body; the second skips
only the CTS-defer body. In this selected C2 configuration the diagnostic macros
are absent, and the straight-line instruction spans are comfortably within127B.
Use `jr uart0_cpu_tail` in those two C2-only branches, subject to the actual
assembler displacement check. ADL JP is4B versus JR2B: expected4B total saving.
The tail still calls `_emos_neta_uart0_exit`, emits81h, restores AF, EI/RETI;
the RX path, protection ordering and every logical exit marker remain intact.
Do not shorten the unrelated `_uart0_handler` jump into TX without measuring
its cross-object distance, or alter the default-OFF paths. This is source opcode
accounting, not a newly linked result or a solution to the whole135B deficit.

## Candidate C factoring: size unmeasured

In fit-r02/source/src/emos_net.c, CPU OPEN5 shape is repeatedly decoded in the
large generic length predicate, the separate C2 tag predicate, and the later
`emos_neta_open(...,n==5)` call. Before the generic operation/length predicate,
decode the enabled-only exact `(op==0 && async && n==5)` case once. Validate
input[4]==C2, set a local accounting flag and normalize only local `n` to4.
Then reuse the original ordinary OPEN4 predicate and pass the saved flag into
the existing `emos_neta_open` span/admission routine. Caller memory is immutable;
do not rewrite it. A similar local normalization already exists for the witness
OPEN7 path in this source, so the structure is familiar to its owner.

This can remove the extra exception embedded in the deeply nested generic
predicate and the second repeated op/async/n decode. A live flag can also add
stack/register work, so no byte recovery is promised without native measurement.
Keep all rejection results and zeroed outputLength identical; malformed tag,
ordinary synchronous5, old C1 OPEN8 and old OPEN7 must still reject before any
association or callback mutation. Genuine OPEN4 remains unobserved and uses
the one-byte service span; C2 still validates the complete8B JP table. No
validation, receive protection, IFF or lifetime check is removed or moved across
ownership admission. Normalization belongs after existing full input-range
validation, before the length predicate, and does not apply to other operations.

There is no reviewed single change here proven to recover135B. Do not delete
unsupported-path poison, ordinary OPEN4, register preservation, RX-first exits
or existing features to manufacture that result. Shared tails and factored
validation are owner candidates for its already-selected finite fit tranche,
not a new execution gate or a request for another optimization program.
