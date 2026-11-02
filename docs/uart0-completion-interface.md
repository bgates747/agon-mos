# Completion notifications and simpler async writes

The useful outcome is an application author replacing a blocking VDP write
with a small async-write wrapper, doing other work, and receiving a clear
notification when the source buffer can be reused. Test whether Tom Morton's
completion-callback proposal makes this easier without sacrificing the stable
transport's CPU benefit or consuming unnecessary firmware space, especially
in EMOS. The Author authorized implementation on2026-11-02; the experiment
now exists in [the implementation and evidence](../experiments/uart0-completion/README.md).
It is an unpublished experimental ABI, not a deployed firmware change.
The sole task checklist is [TODO.md](../TODO.md), task UX-001.

## Motivation and established implementation

On 2026-11-02 the Author supplied Tom's Discord proposal for an interrupt-based
RST18-like async write that calls a user callback when done, and his observation
that UART0 RX/TX share an interrupt handler. Tom also described his pirate MOS
having a syscall to feed bytes synthetically into MOS's receive state machine.
Verified by source inspection on2026-11-02 in
[tomm/rainbow-mos, commit f19be830](https://github.com/tomm/rainbow-mos/blob/f19be830c59176bb319305fe112d33d76ba9e849/src/mos_api.S#L1104):
syscall0x60, `mos_api_inject_uart0_rx_byte`, takes C=byte, loads
HL=`_vdp_protocol_data` and calls `vdp_protocol`. The matching repository is
cloned on Pi at /home/smith/Agon/others/tomm/rainbow-mos, clean main branch.
This confirms the described entry exists; it is not runtime qualification,
an allocation in this MOS fork or a decision to adopt a userspace UART owner.

Our candidate already performs interrupt-driven TX. Applications publish borrowed
buffers; MOS handles TX-empty/CTS wakeups and RX through a combined UART handler.
The RX path feeds the existing MOS parser. Completion currently uses descriptor
status/reap, not callbacks. Foreground status checks are not required for each
16-byte refill. Ordinary RST18 retains synchronous semantics. Preserve the
working startup-safe firmware and its exact image identities as the baseline.

TurboVega's inspected MOS bidir_protocol369ca3f uses interrupt-driven framed
packet TX/RX and done flags; its internal call_vdp_protocol wrapper injects
received bytes into the legacy parser. Neither that transport nor a userspace
UART owner is required to add a convenient interface to our existing sender.
Research snapshots and source references: build/otf-source-review/
assessment-2026-11-02.txt. Do not infer performance from static source inspection.

## Explicit RST18 mode — Author decision, 2026-11-02

Unaware applications retain stock synchronous RST18 behavior. Evaluate an
explicit application/session opt-in mode that permits the familiar RST18 call
to enqueue copied data and return before transmission finishes. Merely discovering
the API, registering a callback, or opening today's borrowed-buffer async session
must not silently change RST18 semantics. The previously hardware-qualified ABI1.2 candidate does not implement this
new mode; it is confined to the separately built UX-001 experiment.

Compare this copying mode with the efficient borrowed-buffer wrapper. Before a
queued RST18 call returns, all source bytes must have been copied into owned
storage or already consumed; the caller can immediately reuse its source.
Specify fixed bounded storage, ordered successive writes, backpressure (wait for
space rather than drop bytes), and incremental handling of writes larger than
the queue. Define all existing RST18 forms and register/IFF/short-mode behavior,
including calls made with interrupts masked; refuse unsupported mode activation
rather than introduce an undocumented deadlock or silent partial transfer.

Notifications are optional. Evaluate one registered callback with a per-logical-
write transfer ID and optional context. One RST18 call gets one completion event,
not one per internal chunk or FIFO refill. Specify how an aware caller obtains
or associates IDs without breaking the existing register contract; this is an
interface design question, not an allocated ABI. Define queue-admission versus
wire-drained completion precisely: copied-buffer reuse is already safe on return,
and an empty software queue alone does not prove UART TEMT or VDP execution.

Mode enable/disable must be explicit, quiescent and scoped to the application
session. Drain outstanding output and retire callback references before close,
OSCLI/child handoff/application return; reset restores stock behavior. Do not
let the next application or MOS prompt inherit the mode. Preserve the stock
startup path and legacy timing when not opted in. Test the mode using an aware
fixture; do not globally accelerate unaware applications. Measure copy overhead,
queue RAM, flash growth and useful CPU work before recommending inclusion.

## Interface experiment

Start with Jukebox's actual integration, once its owner supplies accepted code
and results. Its active app trial remains separately owned; this task does not
authorize editing it, changing its firmware or interrupting its run. Extract a
reusable assembly wrapper, with C-callable shims where useful, instead of
introducing another Jukebox-specific protocol.

Compare these implementations using the SAME batch16 OTIRX MOS sender,
workload, packet storage, source lifetime and foreground scheduling:

- Existing reserve/publish/status/reap interface as the baseline.
- A library async_write(pointer, length, callback, context) that hides discovery,
  session setup, descriptor ownership and reaping. A bounded foreground service
  call detects completion and invokes callbacks. Be explicit that this still
  polls completion internally; it does not provide an interrupt notification.
- A minimal MOS completion-notification extension, if justified by the first
  comparison: record a completion event in the existing ISR and dispatch a
  callback at an explicit foreground service point. Compare with a direct
  ISR callback prototype only to evaluate Tom's literal proposal, with a tightly
  documented ISR-safe callback contract. Never imply foreground callbacks run
  automatically if the application must call a dispatcher.

The test must state who runs each callback, when, with what interrupt state,
and whether application participation is required. Foreground dispatch is a
hypothesis to compare, not a decision to rename polling as interrupt completion.
An ISR callback may only post bounded notification work in the controlled trial;
no rendering, SD I/O, blocking MOS calls, recursive sends or arbitrary API use.
Do not enable callbacks from arbitrary application ISRs or weaken UART ownership.

## Contract that the trial must settle

For the common write callback, define completion as SOURCE RELEASED: MOS has
finished reading all source bytes; the tail may still be in UART hardware.
Wire-drained completion (queue empty and TEMT) is a separate fence. VDP command
execution requires a separate protocol reply when needed. If testing a wire-
drained callback too, give it a distinct name/event and measure its extra cost.

Specify accepted versus BUSY/error, when source ownership transfers, callback
arguments and preserved registers, exactly-once delivery after successful
submission, and cancellation/error outcomes. A notification must not get lost
if completion happens before the submit function returns. Define whether a
callback can run before that return, and prevent foreground recursive dispatch.
A reaped/reused descriptor must not receive a stale callback. Callback and
context storage must remain valid until delivered or explicitly retired.

Keep bounded queue/backpressure behavior, fallback when API/batching support is
absent, and an explicit opt-in. Document whether fallback may block and when its
callback fires. Open/close/OSCLI/app return must not call freed application code;
settle whether pending notifications are delivered or suppressed on teardown.
Preserve data delivery and drain/source-lifetime guarantees in either case.
Distinguish transfer-completion callbacks from MOS keyboard callbacks: the
existing keyboard-callback/session exclusion is not implicitly removed.

Preserve synchronous RST18 semantics for legacy applications. The explicit
queued-RST18 mode above is a separately evaluated opt-in extension. A familiar
async_uart0_write function is a library/new opt-in entry, not silent replacement
of a syscall whose return currently permits immediate buffer reuse. Keep the
borrowed-buffer form as the efficient baseline. A copying convenience wrapper
may be evaluated separately with fixed bounded storage and explicit copy cost;
do not make a MOS payload heap or mandatory copy part of this task.

## Shared receive-handler suggestion

Assess Tom's public RX-injection entry as an optional separate design result:
identify possible users, parser context/reentrancy, register and IFF rules,
receive-byte ordering, and who owns reading IIR/RBR. Our combined MOS UART driver
already preserves RX, so no new injection syscall is needed for this wrapper.
Do not add one unless a concrete consumer needs it and a safe contract is shown.
Do not replace the existing parser or introduce packet framing. Record a clear
include/defer decision and reason, not an automatic implementation commitment.

## Evidence and decision

Use a focused standalone application to test complete buffers smaller than,
equal to and larger than16bytes, queued descriptors, immediate completion,
BUSY retry, CTS stop/resume, simultaneous RX, cancellation, ordered ordinary
MOS output and close/application return. Compare every accepted payload byte
and callback/event identities/counts. Include one full wire drain separately
from source release. Exercise repeated open/close and stock fallback. Reuse
existing integrity fixtures where possible; no new crash-recovery campaign.

Measure matched paced useful work, bulk drain time, submission/completion
handling overhead, notification latency, maximum added ISR duration, and code/
RAM size. Record MOS flash growth and standalone library size separately; review
EMOS capacity before recommending a firmware extension. No hardware timing or
CPU-saving claim based solely on emulator runtime. Emulator work, if needed,
uses the canonical Oryx FIFO; physical Console8 operation remains manual.

Recommend the smallest stable interface that actually simplifies application
code and retains performance. A library-only result, or deferring callbacks if
status handling is cheaper/clearer, is an acceptable outcome. Any MOS change
must retain ZDS II/Wine, stock startup, session opt-in and the existing ABI;
append a versioned extension only if the evidence warrants it. Report the
choice and exact candidate before proposing another hardware deployment.
