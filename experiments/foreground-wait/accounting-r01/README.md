# Optional WAIT accounting — source only

This isolated derivative proposes three calls into Extender's existing app-RAM
MGCPU001 recorder. It does not replace the checked WAIT leaf or deliver a
library. No compiler, test, model, emulator or hardware execution was performed
for this proposal. The original header and C entry points are unchanged.

`proposed.diff` shows all changes against `../src/aw_wait.s`. The adjacent
`aw_wait.s` is a convenience source copy for later explicitly selected native
qualification. Do not link both versions. `source-pins.json` identifies the
exact baseline/header and owner API read for this proposal. The owner manifest
must be revalidated at later composition, rather than silently choosing updates.

The GNU assembler symbol `AW_CPU_ACCOUNTING` defaults to0; enabled qualification
would assemble this copy with `--defsym AW_CPU_ACCOUNTING=1`. Do not use a C
prototype call to pass these events: the native API takes event in A.

| Branch | Placement | Native call |
| --- | --- | --- |
| AW_WORK | Under the existing DI, after the work predicate, before setting ordinary A=2 | A=7, `_agon_cpu_entry` |
| Taken HALT | Under the existing DI, after the final predicate, before restoring caller registers | A=6, `_agon_cpu_entry` |
| Actual HALT return | Immediately after HALT, with original AF saved | A=86h, `_agon_cpu_foreground` |

Nothing is inserted between EI and HALT. No marker is called on begin/PASS or
either refusal path. Refusal still never enables IRQs or halts. The ordinary
results remain A=0/1/2/3; return AF is saved around the86h event. BC/DE/HL/IX/IY,
alternate registers, SP and MB retain the old contract through the owner's
all-register-preserving native API. The foreground wrapper preserves actual
incoming IFF; the entry marker requires the leaf's already-established DI.
The marker is not allowed to reenter through nested EI. No new shared scratch
or state is added in the leaf, and event/clock predicate ownership is unchanged.

Expected ON leaf delta is24 executable bytes: two `LD A,n`+ADL CALL pairs
(6B each), plus PUSH AF/LD A,86h/CALL/POP AF (8B), and two required JR-to-JP
widenings (2B each). The original MB refusal and first NULL refusal forward
branches would exceed the signed8-bit JR range with the hooks inserted;
only ON uses the wider branches. The final clock-pointer JR remains within
range (expected124B displacement). This is source opcode
accounting, **not an assembled size result**. Baseline static state stays9B
per caller. The recorder/provider and their native stack costs are additional,
owner-defined costs; no aggregate IRQ/foreground stack bound is claimed.
OFF is intended to emit identical original bytes and no recorder references;
that equality requires later real assembly/link comparison, not this document.

The leaf adds no direct LSR/RBR/CTS/MOS/GPIO/clock/timer access. Enabled recorder
calls necessarily use the owner's admitted PRT sampler: this does not promise
zero additional timer reads in the full call graph. Their cost also extends
the DI interval before EI/HALT; no receive reserve or safe latency bound is
established by source inspection. Prefix/suffix saves and post-sample tails
remain unknown/partial, never measured zero. Event7 is a raw AW_WORK boundary,
not useful compute or CPU percentage. First IRQ entry ends logical HALT;86h
must not charge that same wait a second time. The owner's class state machine
rejects an unobserved/missing IRQ sequence instead of manufacturing coverage.

Full composition requires the exact supported firmware markers, recorder and
sole timer provider, true initial UART quiescence, one admitted short window,
valid foreground context and positive stop/retirement/CLOSE. A disabled marker
or poisoned record does not waive those contracts. The current owner firmware
is oversize by251B, so no deployable composition is implied. Root owns raw
return glue/capture; UART has changed no game, firmware, SDK or generic driver.

`future-controls.json` is a prepared qualification checklist, not test results.
Do not run it or existing build/check tools without a separate actual selection
and the ordinary compiler/resource lifecycle.
