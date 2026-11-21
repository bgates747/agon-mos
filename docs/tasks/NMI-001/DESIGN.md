# Application NMI registration and F92 watchdog handback

**Proposal for Brandon’s review. The exit policy is approved.** M304 needs to
yield from native Model III code even while the guest has executed `DI`. Provide one MOS-owned watchdog
session for one running application. MOS takes the physical NMI on a protected
long stack and suspends the guest. It then calls the registered ADL handler
from the restored host foreground. On an exit after the watchdog has ever
been armed, MOS takes a verified reset path that clears the F92 peripheral.
The current M304 and firmware pins apply until Brandon selects further work.

## Proposed interface

Use a versioned MOS API entry with suboperations. Allocate the syscall number
only after checking the Eirene API and outstanding RFC allocations. Version 1
supports the F92 watchdog and a managed, mixed-mode Z80 guest. Use full ADL
`RST.LIL 08h` from an active MOS application with host `MB=0`, a valid host long
stack and normal foreground interrupt state. `A` selects the eventual syscall,
`B` selects the operation, and `HL` points to a versioned request in resident
application RAM. `A` returns a status when the operation returns. Other primary
and index registers are preserved across the syscall, with flags unspecified.
The request begins with a byte size and ABI version. Multi-byte fields are
little-endian. The ABI uses fixed-width fields with no compiler padding.

| Operation | Inputs | Result |
| --- | --- | --- |
| `QUERY` | Request header and output room | Version, supported watchdog profiles, mixed-mode capability and armed-exit policy. Old MOS reports unsupported through its normal invalid-syscall path. |
| `ACQUIRE` | Header, 24-bit ADL handler address, 24-bit opaque app context, requested watchdog profile | Exclusive session, with a 24-bit opaque token tied to this app invocation. MOS copies the descriptor and leaves the watchdog unarmed. |
| `RUN` | Header, token, `START` or `RESUME`. `START` supplies a 24-bit address of an initial guest-state record and declares its bank and memory bounds | Enters or resumes a guest slice. The first successful entry arms the watchdog. On a managed yield, returns to the same ADL caller after the registered handler, with a reason in the request. `RESUME` uses the MOS-owned saved frame. |
| `RELEASE` | Header and token | An unarmed owner gets success and can unload immediately. For an armed owner, success is a reset into normal startup. The call has no successful return in that case. |

The guest-state input has version, size, guest bank, PC16, SPS16, requested
initial interrupt state, and the guest register sets. The proposal uses a
read-only event view during the host callback. An opaque resume frame stays in
MOS, so the app cannot accidentally change the mode marker or resume a stale
frame. Final binary layout, return codes and profile IDs belong in the reviewed
ABI after the source and hardware constraints below are settled. Distinguish
`unsupported`, `invalid`, `wrong context`, `busy`, `stale owner` and
`no resumable guest`. A refusal before ownership publication or arming has no
watchdog or registration side effects. Refuse to arm if a watchdog is already
enabled, required memory or stack windows are unsuitable, or the board lacks
a verified reset contract. Validate callback address and token against the
current app invocation. This is a lifetime check for cooperating native code.

The registered handler is a long ADL call using `CALL` and ordinary ADL `RET`.
`A` gives the event reason, `DE` the opaque context, and `HL` the read-only MOS
event view, valid for the call only. MOS invokes it with the normal host stack,
mapping and IRQ policy. It may do bounded app work or set a flag for the caller
and use foreground-safe services. `RUN` returns after the handler, so the app
can do further work before choosing `RESUME` or `RELEASE`. Refuse recursive
session operations from inside the handler. The handler cannot return directly
to the guest or retain a pointer to the event record. If a cooperative guest
exit is required, review it as a second entry into the same host continuation,
with explicit guest-stack rules. Watchdog preemption does not depend on any
guest cooperative exit or on the guest changing `DI`.

## Entry, service and resume

1. Before executing guest code, MOS saves the host continuation and declares
   `GUEST_ACTIVE` only at its controlled entry boundary. It establishes
   `MADL=1`, keeps MOS and its vectors mapped, and uses protected, bounded host
   `SPL` storage. In a Z80 guest the mixed-mode NMI saves a 16-bit PC and mode
   marker `02h` on `SPL` and enters ADL at physical `000066h`. `SPS` is left as
   the guest supplied it. RC3 already routes through a resident NMI gateway
   and returns using `RETN.LIL`. The proposal replaces the gateway behavior
   in a supported MOS build. [Zilog CPU manual, Table 21](https://zilog.com/docs/UM0077.pdf) ·
   [Pinned RC3 gateway and default](README.md)
2. The NMI entry is a resident, bounded path. Capture the hardware frame,
   guest MB, SPS, register pairs including upper bytes, both register sets,
   index registers, and relevant control state before changing them. After
   saving guest flags, capture the enable state that NMI copied from IEF1 to
   IEF2. `LD A,I` exposes IEF2 in P/V. Save the observation before any `DI`,
   `EI` or further NMI can affect it. Keep the return PC and long-stack frame
   in protected MOS storage. Capture any pending guest HALT, I/R and delayed
   enable semantics that the supported native execution contract requires.
   Establish visibility and ownership of those features during ABI review. A
   raw CPU refresh count or an unobservable internal latch cannot be promised
   as bit-for-bit guest state without evidence. [Zilog CPU manual, interrupt and LD A,I descriptions](https://zilog.com/docs/UM0077.pdf)
3. Park the guest frame and finish the NMI with a mixed-mode return to a
   MOS-owned ADL continuation. The proposed mechanism uses a separate ADL
   return frame for that continuation and keeps the original guest frame for
   later resume. Ensure maskable interrupts are disabled on landing. The
   continuation restores the host `SPL`, mapping, `MB`, vectors and
   foreground context before enabling ordinary IRQs. IRQs use their normal MOS
   paths here. The continuation gives pending IRQs an instruction boundary and
   an enabled service window before the handler and `RUN` return. It uses no
   fake IRQ invocation or unrestricted nested ISR. The host foreground can then
   handle keyboard, display and timers. Bound the work of that window and the
   callback without promising a hard IRQ latency under existing MOS handlers.
4. `RESUME` accepts only the same owner's suspended frame and consumes it
   exactly once. With the host IRQ window closed, recover all guest context and
   return through the verified mixed-mode sequence using the untouched guest
   `SPS`. The re-entry sequence must restore the saved enable state at the
   guest boundary. For a `DI` guest, ordinary interrupts remain masked. For an
   enabled guest, the approved ISA sequence must admit an IRQ only when the
   active mapping, mode and stack satisfy MOS or the guest's interrupt policy.
   Verify the exact instruction ordering, mixed return frame, and EI delay on
   the F92 before offering that case. This version cannot claim arbitrary
   guest `EI`, vector changes, direct I/O or hardware `HALT` until their
   routing and semantics are defined. A software-visible guest floppy NMI is
   handled by M304's guest model, independently of this host interrupt.

The safe host window is a foreground boundary reached **after** NMI return.
Enabling IRQs in the raw NMI handler would need a different design for nested
IRQ/NMI, IEF preservation and stack use. A direct return to a guest that ran
`DI` would restore its masked state before normal MOS service could run.

## Ownership, faults and watchdog handback

| MOS state | Timeout and ownership rule |
| --- | --- |
| `IDLE` / `CLAIMING` | Unarmed. Publish one selector only after the descriptor, stack and recovery target are valid. Any NMI during publication follows the resident default or recovery path. A foreground `DI` cannot make a multi-byte update atomic to NMI. |
| `CLAIMED` / `ENTERING` | Set up the host continuation and a resident recovery route before the first arm. If the watchdog fires after arm but before committed guest entry, use resident recovery. Guest dispatch is valid only for a committed state and a matching interrupted-mode frame. |
| `GUEST_ACTIVE` | Capture the expected guest frame once. A nested event, inconsistent frame, or untrusted source must take resident recovery. There is no reentrant app callback. Keep the acquisition and resume instruction boundaries within the watchdog policy. |
| `SUSPENDED` | Guest and owner records remain resident. MOS reloads the watchdog before the bounded host interval and at defined progress boundaries. A timeout during host foreground, IRQ service or callback is a host fault and goes to resident recovery. It cannot dispatch an app handler using a guest frame. |
| `RELEASING` / `RECOVERY` | Invalidate app dispatch before abandoning frames or stacks. Move to resident storage and run only the reset path. Pending or repeated events also go there. Cleanup remains safe if app code, data or stack are already unreliable. |
| Startup after reset | Verify the watchdog is clear, discard the volatile lease and restore ordinary defaults. No-owner startup and unrelated NMIs retain the verified baseline behavior. |

Specify priority and latch rules for a pending NMI and for an NMI during NMI
entry. The watchdog's reset-cause flag can remain set after a timeout, so it
cannot by itself prove that a later NMI belongs to the active watchdog slice.
Use the admitted source configuration, published state and frame checks.
If a supported board has another indistinguishable source, refuse this mode
unless the platform can isolate it. Reserve an emergency resident fallback
with no dependency on guest stack, app code, app data or a functioning app
callback. An unexpected app return or recoverable abort goes through this same
release path at the MOS app boundary. A timeout outside the guest path takes
that fallback. Native code that changes protected vectors, required mappings
or the watchdog behind MOS's back lies outside the managed execution contract.
[Zilog F92 watchdog register and reset semantics](https://www.mouser.com/catalog/specsheets/Zilog_ps0153-2.pdf#page=79)

The watchdog profile must leave enough time for NMI capture, host IRQs, the
callback, and foreground work until the next `RUN` or `RELEASE`. Define that
budget before arming. A watchdog timeout used as a guest scheduling interval
is also an armed deadline while the host is running. A separate, longer
host interval is an option only if live period changes are verified. Reject
workloads that exceed the selected host budget. Feeding from an unrelated
periodic IRQ would risk masking a stuck application.

**Approved first-version policy — reset after armed exit.** Brandon selected
this policy for simplicity. Release before arming returns normally. Release
after arming uses a verified reset that clears the watchdog and starts a fresh
MOS session. The particular reset mechanism still needs to be established.

An F92 watchdog can be disabled only by reset. Reloading it and jumping to a MOS entry point leaves
it armed. Prefer a documented on-target reset path that runs from resident
code and clears the peripheral. Investigate switching the armed watchdog to
reset-on-timeout, then allowing a finite expiry, as a possible path. The F92
must establish that changing the timeout action after enable takes effect and
that a pending NMI during the transition still stays in resident recovery. If
that path cannot be established, use a verified board reset mechanism or
decline to offer watchdog arming on that profile. An unverified reset is not
an exit route. The reset choice must account for normal MOS/VDP restart and
any persistence or queued I/O the app must finish before release.

Unarmed release lets the app reclaim memory after MOS returns success and no
handler/frame is outstanding. Armed release, or a fault after arming, allows
reclamation only by fresh startup after reset. A failure to confirm release
must keep dispatch cut off and storage reserved until reset, with a resident
recovery path. Returning to the CLI and reusing the app region with an active
watchdog is outside the first version. If the first version works, Brandon
wants a separate investigation into returning to the same live MOS session
without reset. Keeping the session alive would need a design for resident
watchdog feeding across unrelated apps, long masked intervals, SD work and
error recovery, with deadline evidence for all of those paths.

## Review decisions and later qualification

- Approve a managed watchdog lease with a foreground ADL callback as the
  first API. A raw application NMI vector and arbitrary NMI sources would
  require a broader contract.
- Agree which M304 guest modes are required initially, especially guest `EI`,
  native `HALT`, and guest-visible interrupts. The first requirement is
  repeated watchdog yields during guest `DI` with no guest-stack writes.

Approval applies to the exit policy only. M304 remains paused. Implementation,
prototypes, builds, tests and firmware changes remain deferred.

After design approval, qualify the exact CPU transitions in a model and on
real F92 hardware. Require repeated `DI` yields while `SPS` points at sentinel
RAM, register and bank preservation, return through the correct PC and IEF
state, measured host input/timer progress, bounded host-stack use, and exact
behavior around `EI` if supported. Exercise wrong tokens and modes, NMI at
every ownership transition, repeated/nested NMI, a timeout during host work,
normal and abnormal application exit, and release failure. Prove the reset
route clears the watchdog and restores startup before reusing app memory.
Include the unarmed baseline and the no-owner path, and keep model results
distinct from physical F92 timing and reset evidence.
