# Application atomic wait candidate

This tiny helper closes the foreground callback-to-HALT handoff when its app
integration supplies all relevant notifications. It changes no MOS, U1 driver,
vector or timer. Original software uses the existing native AgonDev toolchain.
Native assembly/link and abstract model checks are not executed CPU/IRQ proof.

Link `src/aw_wait.s` (or the supplied `libaw_wait.a`) and include `aw_wait.h`.
Create one static `aw_state state=AW_INITIALIZER`. Before callbacks attach, bind
`state.clock` to public `mos_sysvars()+sysvar_time` (offset0, four bytes). This
helper never looks up that pointer or knows a private firmware address.

```
for (;;) {
    if (aw_begin(&state)!=AW_PASS) { /* explicit failure; do not spin */ break; }
    service_all_work_with_irqs_enabled();
    if (more_work_to_do) continue;
    uint8_t r=aw_wait(&state);
    if (r==AW_REFUSED) { /* explicit failure */ break; }
    /* WORK and HALTED are both hints to repeat the full service pass. */
}
```

Each relevant existing callback publishes its real state, then `aw_notify`.
Begin alone clears the sticky byte, BEFORE service. Never clear it after the
polls. An event during the final DI is serviced after adjacent EI/HALT; an
already published event or clock change avoids HALT. Final saves are restored
before that pair; an EI/RET helper followed by a caller HALT is not equivalent.

Callers must actually be ADL1/MB0/IFF-enabled foreground code. Both functions
reject observed MB!=0, IFF0 and NULL pointers; wait additionally needs a begin
token. Refusal does not enable IRQs or halt. Non-NULL pointers must identify
valid distinct nonwrapping RAM spans, with stable lifetime and clock binding.
No global IFF scratch is used. BYTE result A: REFUSED0, PASS1 (begin), WORK2,
HALTED3. Other primary/index/alternate registers, SP and MB are preserved;
flags are unspecified. HALTED means the instruction executed, not how long.
One foreground caller per object; it is not a lock, scheduler or nested guard.

Use notifications from RFC source release, VDPL/NM reply/error and the selected
optional app SDK U1 transition hook. That future `AGON_NETA_NOTIFY` seam must
exist before claiming full U1 coverage; no generic drain callback is invented.
Do not notify on every no-progress poll. Current public clock progression
supplies normal VBlank/deadline/backoff fallback; a wire-only TEMT/CTS change
still waits for owner observation. No state/borrow/drain/receiver/close contract
is weakened, and intentional quarantine loops are not migrated automatically.

See `docs/tasks/U1-001/foreground-wait-contract.md` for the complete integration
and primary eZ80 EI semantics. Frozen MechAgon R06 remains unchanged.
