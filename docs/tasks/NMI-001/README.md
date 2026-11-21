# NMI-001 — Application NMI registration and watchdog handback

**Status: the first bounded proof passed in Flexe and on physical Console8.
Public API implementation remains open. M304 remains paused.**
[API and watchdog handback proposal](DESIGN.md) · [Proof plan](PROOF-R01.md) ·
[Proof result](RESULT-R01.md).
MOS owns this API proposal. M304 is the first consumer. Its current pinned
firmware is Eirene RC3, `3.1.0_uart0_rc_3`, at
`97311c437093e416342a6c836cf9914f2ced027d`.

Native Model III code can execute `DI` and temporarily use its short stack
pointer as a general register. The F92 watchdog can give the host a chance to
regain control even while maskable interrupts are disabled. With a non-ADL
guest, mixed-mode NMI entry uses the host long stack when MADL is set. RC3 routes
the physical NMI vector at `000066h` through MOS's RAM gateway to its default
`RETN.LIL` handler. It exposes no application registration hook. Scope a
supported MOS dispatch API so an application can use that entry without patching
live MOS or writing through the guest stack. Host watchdog delivery and guest
Model III floppy NMIs have separate ownership and semantics.
[M304 scope](../../../../trs-80-m304/projects/model3-native/docs/tasks/M304/mos-nmi-api-scope.md) ·
[M304 entry analysis](../../../../trs-80-m304/projects/model3-native/docs/tasks/M304/nmi-entry-notes.md) ·
[RC3 vector source](https://github.com/bgates747/eirene-mos/blob/97311c437093e416342a6c836cf9914f2ced027d/src/reset.asm#L40) ·
[RC3 default handler](https://github.com/bgates747/eirene-mos/blob/97311c437093e416342a6c836cf9914f2ced027d/src/handlers.asm#L62)

## Questions for the API proposal

1. **Registration and ownership.** Evaluate one owner per running app and
   define discovery, supported caller context, handler address and lifetime,
   duplicate registration, conflicts, and invalid or stale ownership. Define
   whether MOS owns watchdog setup as part of acquisition. Register safely
   before arming and define what happens if an NMI arrives midway. Masking
   ordinary IRQs with `DI` cannot protect publication against NMI.
2. **ADL handler and guest return.** Specify the supported entry modes, long
   stack frame and capacity, context visible to the callback, register and bank
   preservation, and which layer owns the final mixed-mode return. Cover guest
   PC, SP, MB, ADL/MADL and interrupt state, plus both register sets and index
   registers. Preserve a guest's original `DI` state on resume. Define bounded
   callback work, which MOS calls are valid there, and behavior if an NMI
   arrives while MOS, a normal IRQ, or the NMI handler is already running.
3. **Opportunity for normal MOS IRQ service.** Define how the host gets a
   bounded chance to service pending input, display and timer work while the
   guest is suspended. Compare a controlled host continuation with servicing
   inside the NMI path. Analyze interrupt state changes and re-entry before
   choosing either. A callback that immediately returns to the interrupted
   guest under `DI` alone cannot deliver that service opportunity.
4. **Unregister, failure and no-owner policy.** Define the safe state before
   acquisition, during ownership, during release and after exit. Cover normal
   return to MOS, abort, a timeout racing any transition, and a failed handback.
   Require a positive point at which neither a fresh NMI nor an in-flight
   handler can reach app code, data or stacks. The app can release its memory
   only after that point or across a defined reset. Evaluate retaining a return
   default where compatible and Calc84maniac's proposed soft reboot where
   appropriate. Cover watchdog versus other NMI sources, accidental masking,
   and repeated events that could otherwise stall recovery or loop at boot.

## Watchdog handback decision

An armed F92 watchdog requires a hardware reset to disable it. Reloading its
counter extends service time. A software jump into MOS startup does not by
itself provide the reset guarantee. The proposal must establish which reset
path resets the peripheral and how startup handles an already armed watchdog.
[Zilog eZ80F92/eZ80F93 specification, Watchdog Timer, pp. 72–75](https://www.mouser.com/catalog/specsheets/Zilog_ps0153-2.pdf#page=79)

Compare two options. MOS can take over feeding the watchdog from resident code
and keep the current session alive if it can meet the deadline throughout
prompt, I/O and interrupt handling. Alternatively, MOS can make a defined
reset part of exit when the watchdog is armed. Describe what a caller can
expect on success, refusal or uncertain handback in either case. Explicitly
account for a pending timeout, the interval during ownership transfer,
and a timeout immediately after the old handler becomes unreachable. If a
software reboot is considered, show how the watchdog remains serviced until
reset or becomes owned by startup before any old app memory can be reused.

## Evidence to propose for later qualification

- Baseline RC3 and no-owner checks. Show ordinary startup, app launch and
  interrupt service under a compatible default with no registered owner.
- Registration, refusal, repeated NMI under guest `DI`, and mixed-mode returns
  with known register, stack and bank sentinels. Verify unchanged guest short
  stack, bounded long stack use, preserved guest interrupt state, and actual
  progress of pending MOS IRQs while the guest is suspended.
- Forced timeout at registration, while the callback is active, at unregister,
  and immediately after app memory is reused. Exercise normal exit, abort, a
  handback failure and the chosen no-owner behavior. Every case needs a
  positive indication that the watchdog is either safely owned by MOS or
  cleared by reset, with no jump into released application memory.
- Record model and real F92 results independently. Hardware must establish
  actual timeout delivery, servicing margin and reset behavior. Select any
  execution and firmware separately after Brandon approves the design.

The review deliverable is a proposed public ABI, a lifecycle with explicit
failure handling, a recommended watchdog handback policy, and a finite
qualification plan. The task record authorizes review only. Prototyping,
building, testing and firmware changes require a separate instruction.
