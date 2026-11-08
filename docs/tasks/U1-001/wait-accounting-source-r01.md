# U1-WAIT-CPU-R01 — Optional WAIT accounting splice

Selected source-only request:
`2026-11-08_01-54-11_mechagon_goal001-cpu-wait-splice-source-selected-one`,
within the existing MechAgon GOAL-001 owner-support delegation. UART owns this
app-only reusable leaf. MechAgon owns app glue and composition; Extender owns
the recorder, timer-provider lifecycle and firmware fit correction. RX006's
frozen fixture, reservation and blocked hardware dependency are unchanged.

- [x] Read the actual owner header/native assembly/README and pinned manifest.
- [x] Prepare a separate default-OFF derivative and explicit proposed diff.
- [x] Record native A-event placement, register/IFF contract, expected delta,
      unknown timing and prepared future qualification controls.
- [ ] Native OFF byte equality and ON linked/listing qualification: NOT selected
      by this source-only request. No checks, compilation or target run executed.

Source and patch: `experiments/foreground-wait/accounting-r01/`. Original checked
`src/aw_wait.s`, header, old object/archive/evidence and frozen Mech588/617 are
untouched. The source-only ON derivative is not a qualified/runnable package.
The owner's enabled firmware exceeds ROM by251B; this task does not fix it or
select a physical case. No compiler, timer, device or other resource is acquired.

No new API argument/state/callback, generic driver, recorder or direct peripheral
access is introduced. Enabling the assembly-time option requires the exact
owner recorder plus unchanged sole timer provider and actual app admission.
See the source README for placement and the future controls JSON; no binary
delta or hardware timing has been measured for this candidate.
