# GOAL-001: foreground callback-to-HALT handoff

Source consultation requested in
`2026-11-07_09-38-47_mechagon_goal001-lost-wake-source-uart-fiftysix`.
The retained R05 `main.c` services render/NM/ready state, then can execute the
literal HALT/RET in `rfc.s` using an unchanged local `advanced` variable. A
callback between its relevant poll and HALT can publish work that remains
unobserved until another interrupt. This is a conditional source-level delay,
not proof of a measured R05 delay or the cause of83 overrun.

Keep frozen R06/367/80fe unchanged. Root owns this later app correction; UART
supplies the contract, Extender any SDK integration seam. No new build, test,
firmware edit or physical run was requested or performed by UART.

## Recommended small app contract

Use one application-owned volatile sticky byte, plus the existing VBlank-driven
MOS clock as a periodic eligibility token. No new vector, timer or resident
MOS syscall is needed. Cache the supported sysvar pointer before the loop; the
clock comparison is a fixed four-byte RAM comparison, not a MOS call or UART
register read under DI. Standard sysvar_time is offset0/size4 in agon/mos.h.

```
begin_service_pass():                  // foreground, ADL1/MB0/IFF enabled
    atomically:
        wake_pending = 0              // ONLY foreground clear point
        pass_clock = public_clock32
    service foreground with IRQs enabled

mark_event():                         // relevant producer, existing IRQ ABI
    publish payload/state first
    wake_pending = 1                  // never clear it in a callback

wait_after_service():                 // one bounded assembly leaf
    refuse disabled-IFF entry without enabling it or halting
    DI
    if wake_pending != 0 or public_clock32 != pass_clock:
        EI
        return                        // another foreground service pass
    EI
    HALT                              // IMMEDIATELY following EI
    return                            // wake is a hint; recheck all real state
```

Do not clear the latch immediately before sleeping: that erases work arriving
after the foreground polls. Do not sample pass_clock after the polls either.
Clear/snapshot together BEFORE all service predicates; arrivals before that
clear must be visible to the following ordinary service pass. Payload/ready
publication and notification need volatile/compiler ordering in the actual C
integration. The latch coalesces notifications; it is not a completion counter,
queue, ownership token or proof of source/drain/receiver completion.

The final test and EI/HALT belong in the SAME assembly leaf. `unlock()` using
EI/RET followed by HALT in its caller is insufficient: an IRQ may run after
that RET and before HALT. No function call, POP, NOP, tracing instruction or
compiler-generated code may intervene between EI and HALT. Preserve the
selected C ABI, primary/index/alternate registers as required, full ADL widths
and incoming IFF. Disabled-IFF callers return an explicit refusal and remain
disabled; never sleep with maskable interrupts disabled. Existing callbacks
retain their own ABI and must not introduce EI, waits, MOS calls or reentrancy.

Why the handoff works for normal maskable IRQs: a published event after the
pass clear remains latched through the final check. An IRQ pending during DI
is accepted after the instruction following EI, which is HALT. This uses the
eZ80 rule in [Zilog UM007715-0415, Interrupts p36](https://zilog.com/docs/UM0077.pdf).
The official indexed text supplies this rule; opening the full PDF currently
redirects to an inaccessible Littelfuse page. No emulator execution was used
to infer the instruction semantics.

## Producers: close coverage, not just the assembly window

* UART0 RFC source callback: add the app latch store after its existing done
  flag. Its current flag-only assembly callback can use the same A=1 value;
  respect the caller's saved-register/return convention.
* VDPL reply and NM reply/error callbacks: mark after retained payload/ready or
  fault publication in the root-owned callback chain. Bounded coalesced false
  positives are harmless; a subset of producers is not complete coverage.
* U1 source release, TAIL-to-IDLE and fault/owner-loss publication need an app
  notification seam as well. The present generic core has a source callback,
  but NO drain-completion callback. Do not invent one in its documented ABI.
  Extender should select the smallest OPTIONAL application SDK/service-wrapper
  seam: source callback marks the latch; the existing app service hook marks
  actual phase/fault transitions, after updating them. Core/emitter and resident
  firmware stay unchanged. Do not set the latch on every no-progress foreground
  progress call: that makes the loop spin instead of sleeping.
* VBlank advances the existing clock, covering poll eligibility/deadlines and
  tick-driven CTS/drain retry without replacing its vector. A tick between the
  last poll and final DI is detected by the clock token; one pending during DI
  wakes after HALT. Full32-bit comparison avoids the low byte's128-VBlank alias.
* TEMT changing on the wire has no dedicated completion callback here; raw CTS
  becoming ready also need not generate a wake. Until the owner next observes
  them, VBlank is the fallback. That remaining up-to-next-service latency is
  separate from the lost-software-notification window. With no U1 notification
  seam, label U1 progress explicitly tick-serviced rather than claiming immediate
  wake coverage. Read no extra acknowledging LSR in the wait leaf.

Existing source release, later TEMT, receiver reply and positive close gates
are unchanged. Silent idle owner loss still requires the existing owner probe
before submission/close; a wake flag is not a health check. Retain the selected
finite timeouts and deliberate empty-POLL backoff. Blocking setup loops in
render_link.c need the same begin/service/wait discipline if migrated; do not
change intentional quarantine HALT semantics as part of this correction.

## Owner implementation checks, before any later case

W83-001 [x] Return the minimal app contract and missing U1 notification seam.
W83-002 [ ] Root/Extender bind all actual producers and pass-clear ordering,
including source callback before submit return and fault paths. No generic
driver or frozen R06 change is selected by this source consultation.
W83-003 [ ] Root checks arrivals before clear, during service, after the last
poll, during DI, and at EI/HALT; ready work must trigger reservice or wake.
Check disabled-IFF refusal, register preservation, coalesced events and no
no-progress spin. Include VBlank eligibility and explicitly tick-only TEMT/CTS.
W83-004 [ ] Inspect final linked adjacent FB/76 (EI/HALT), bounded masked RAM
loads, callback ABI and exact code size. Source/interleaving models alone do
not establish executed eZ80 behavior or a physical latency improvement.

## Selected application SDK seam

Extender returned the concrete contract in
`2026-11-07_09-45-20_linux-extender_goal001-u1-optional-notify-source-agon-mos`
and sent the same selection directly to MechAgon. No additional reply is needed
without a material conflict. For a separately selected adapter revision,
`AGON_NETA_NOTIFY(client_pointer)` is optional/default no-op and runs after:

* `agon_neta_source_done` publishes `source_released=1`;
* `agon_neta_service` actually changes phase, fault or fault_error from its entry
  snapshot, after u1_start/u1_step/u1_report_fault state publication and before
  returning the existing demand. No-change calls do not notify.

Duplicate notifications coalesce in the one-byte app latch. Use the retained
active client, publish-before-notify compiler ordering, and the existing IRQ/C
ABI and positive-close storage lifetime. Notification must not allocate, wait,
log, call MOS/gateway, enable IRQs, reenter or authorize source reuse/detach.
Source notification may precede SUBMIT return; retain the pre-service clear.

At the initial consultation this was a future seam. Extender subsequently
delivered an isolated checked implementation in
`2026-11-07_10-15-21_linux-extender_goal001-app-notify-checked-source-r01-agon-mos`,
source `a6a8a4b3a124a4285a2f0c91b8130693b2d88a97`. Its root SDK and frozen
consumer packages remain unchanged; this does not mean the hook is already
integrated into MechAgon.

UART reviewed the actual header and retained notification tests against this
contract. Source release is stored before the barrier/notification; the
ordinary service wrapper compares phase/fault/error and notifies only after a
change. The source callback may run before submission returns, and duplicate
source/phase notifications coalesce. No material conflict with the wait helper
was found. W83-002 remains open for the actual consumer binding and all other
producers.

UART independently verified the private ZIP's SHA256, all 43 payload members
(44 entries including its manifest), matching source header, baseline/default
objects and full link-only binary equality, and unchanged enabled core/emitter
objects. See [review receipt](wait-leaf-r01/sdk-notify-review.json).
Extender's compiler386 checks report +145 text bytes/+1 application wake byte
for the enabled probe and a +12-byte service static frame; these are not whole
consumer or nested interrupt stack costs. UART did not rerun those checks or
execute the native probes, which are not runnable MOS appliances.

This closes the SDK source-seam preparation, not combined application or
hardware qualification. Silent-idle owner checks and tick-only TEMT/CTS
fallback remain necessary. No generic core/emitter/resident changes, frozen
R06/R07 edits, deployment or queue/custody changes were made by this review.
