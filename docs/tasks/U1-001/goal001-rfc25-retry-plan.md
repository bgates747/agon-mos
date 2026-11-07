# GOAL-001: bounded UART0 CTS deferral derivative

The experimental RFC25 sender can wait indefinitely inside its interrupt when
the VDP blocks CTS, preventing other interrupts from running. Prepare a small
private derivative that returns immediately and retries later. This corrects
that source-level exclusion hazard; the trial76 RX overrun remains unexplained.
Published RC3 and the installed working system are not changed by this work.

This is G1-003 under the directly verified delegated GOAL-001 scope recorded in
goal001-owner-support.md. Branch `codex/rfc25-bounded-cts`. Actual source donor:
Eirene RC3 commit97311c437093e416342a6c836cf9914f2ced027d, whose own toolchain is
AgonDev. Use its installed native toolchain, not a migration of ZDS II MOS.
Keep upstream and Extender checkouts read-only; assemble private copies here.

## Derivative contract

At TX-empty ISR entry read GPIO CTS once, before count/pointer updates. If STOP,
disable only UART0 TX-empty interrupt, set one retry flag and restore the existing
AF/EI/RETI frame. Keep the entire source/count/callback untouched. Normal admitted
service remains a positive burst of at most16 bytes through native OTIRX.

Add a bounded VBlank helper: inactive flag returns without peripheral I/O;
pending and still blocked returns after one CTS sample; pending and ready clears
the flag then re-enables only TX-empty, preserving RX/other IER. The normal UART0
ISR does the subsequent copy. No extra timer, syscall, queue, timeout, memory
revocation, nested IRQ or UART LSR acknowledgement. Initialize/reset retry state
only through ordinary BSS plus accepted submission/final retirement. Startup
ordering/ROM reset code stays unchanged. Final callback semantics and register/
mixed-mode ABI remain the donor's, not an expanded callback interface.

Bounded CTS retry can add up to a VBlank interval after the peer becomes ready.
Its throughput/latency effect needs later matched owner qualification; no speedup
or physical FIFO reserve claim is made. The existing consumer reciprocal gate
stays. Extender owns its derivative splice and any EMOS-specific ownership/reset/
abort integration. It must clear pending retry on its own abort/reset/route
retirement before source storage is reused; do not infer a generic owner state.

## Finite offline qualification

Prepare exact original/candidate source patch and paired object/ROM evidence.
Reserve normal Pi serial compiler FIFO. One owned finite build/check tranche,
expected under2min, hard child180s/whole600s, thermal stop80C, at least512MiB
available RAM; stop/join owned children before release and notify actual successor.
No Flexe/Fab/CPU guest run, device, SD deployment, firmware install or bench use.

Checks must show original blocked CTS has a reachable backedge while candidate
blocked/retry paths are finite and emit no bytes, mutate no source/count/callback
and preserve unrelated IER bits. Reject negative controls that move admission
after count mutation, lose retry wake, or turn the deferred source into completion.
Retain exact linked bytes/size, startup invariant, registers/return frame and
donor-only full16/final1..16 paths. Source/linked structural checks are not a
runtime or physical regression pass; label them explicitly. No claim of an
unexecuted ISR, receiver recovery, real CTS tail or integrated MechAgon result.

Return the standalone patch, hooks/state and exact cost to Extender/MechAgon,
with fit/integration caveats under EMOS's931-byte spare ROM. Hardware qualification
remains their dependency-ordered selected work after the protected entry queue.
