# DRAFT — MOS asynchronous UART0 API and implementation plan

Executive summary: use three borrowed-buffer descriptors, one ordered MOS
consumer, interrupt-driven FIFO service and modem-status CTS wakeups. Keep
per-byte CTS checks initially. Ordinary foreground output drains earlier
transactions and excludes new publication while it sends. No VDP change is
needed for transport. Interrupt-context output and abnormal exits remain
integration decisions; this draft is not a supported firmware API.

## Isolated implementation status

The Author authorized the isolated tranche on 2026-10-12. The driver and
benchmark now exist under `experiments/uart0-async`; its README defines the
actual experimental ADL ABI and RESULTS.md records the evidence. That ABI
uses a singleton session and exported sticky diagnostics rather than final MOS
call numbers/session handles. Live MOS is unchanged. C-001/C-002 remain open
before integration. No Python or venv was needed: the harness uses Rust,
Bash and Ruby. Native ZDS II under Wine on Oryx Linux Lite assembles and links
the isolated sources through the canonical environment launcher. The resulting
image passes the documented tests; the integrated MOS image is still pending.

TX-007 also executes that driver as a stock-MOS-loaded test application against
real ESP32 firmware through Fab/Flexe on Oryx. The audit and results are in
`docs/uart0-flexe-audit.md` and `experiments/uart0-flexe`. IIR acknowledgement
exposed a second lost wakeup: after spending its TX budget, the ISR now returns
before another IIR read could consume an unserviceable TX-empty request.
The independent UART model acknowledges that request too. Both engines and
the revised scripted suite pass; TX-008 human review passed. TX-009 moved the
reusable runtime to `../flexe-agon-emulator`. The application
temporarily uses a capture sink, not the production MOS receive parser.

## Verified source facts


The selected MOS source revision is recorded in [ASY-001](tasks/ASY-001.md).
`src/uart.c` enables/clears UART0 FIFOs with FCTL=07h and takes the IER mask
from its configuration. `src/interrupts.asm::_uart0_handler` unconditionally
calls RX and then the VDP parser. `src/serial.asm` waits for CTS and THRE for
each ordinary output byte. `src_startup/vectors16.asm` routes RST10 and each
RST18 byte through PUTCH. Simply enabling TIE is unsafe.

Local Zilog PS015317-0120, `/Agon/docs/PS0153-eZ80F92-eZ80F93-Product-Specification.pdf`,
printed pp.105, 113–114, 119–122, confirms 16-byte TX FIFO, THRE meaning FIFO
empty, TEMT also requiring the shift register empty, and inverted CTS in MSR
bit4. Reading MSR clears delta bits; reading LSR acknowledges receive errors.
IIR bit0=1 means no pending cause; use the explicit table rather than the
inconsistent adjacent validity prose. No automatic CTS transmitter gate or
memory-to-UART DMA was established. OTIRX executes on the CPU.

The prototype's per-byte CTS sampling is the baseline. An unconditional
OTIRX burst cannot observe CTS during the copy. Even per-byte sampling cannot
recall bytes already in the FIFO/shift register. A 16-byte cap therefore needs
receiver headroom qualification on hardware; use a smaller configurable cap
if necessary. OTIRX is a later measured alternative only with a demonstrated
headroom contract.

## Candidate API

Initially expose ADL assembly entry points in the isolated driver. Assign MOS
call numbers only during integration after auditing the current dispatch table.
All pointers and counters below are unsigned 24-bit values stored in three
bytes. Do not store them in `dw` fields. Maximum transaction length is 65,535;
reject zero lengths and address wrap. Borrowed data must be stable readable
RAM until release. The foreground producer is single-owner; calls from NMI,
ISR or keyboard callbacks are rejected for the new API.

| Operation | Inputs | Result and behavior |
|---|---|---|
| `tx_open` | none | Exclusive session handle; BUSY if already open. Preserve baud, FIFO configuration and RX. |
| `tx_reserve` | session | Nonblocking descriptor reservation or BUSY; reserves one of three slots before rendering. |
| `tx_publish` | reservation, source, length | Atomic publication and ticket; no payload copy. Failure leaves reservation/source caller-owned. |
| `tx_status` | ticket | RESERVED, QUEUED, ACTIVE, RELEASED or CANCELLED, with accepted-byte count and sticky error snapshot. |
| `tx_reap` | released/cancelled ticket | Free descriptor; stale tickets rejected. |
| `tx_cancel` | ticket | Cancel reserved or wholly unstarted transaction only; ACTIVE returns BUSY without changing progress. |
| `tx_poll_drain` | session | Nonblocking DONE only when no published work remains and TEMT=1; otherwise PENDING. |
| `tx_close` | session | Nonblocking close only after drain and all reservations/tickets resolved; otherwise BUSY. |
| `tx_kick` | session | Bounded service opportunity for masked-interrupt callers; preserves their IFF state. |

Each operation returns an explicit status: OK, BUSY, INVALID, CLOSED or
CONTEXT. No failure silently drops a command. Tickets must never alias a live
or accepted stale handle; the isolated implementation uses monotonic u24 IDs
(refuse further allocations at exhaustion until full driver reinitialization). Status and
descriptor mutation use short interrupt-masked critical sections that restore
the incoming interrupt state. Long waits and payload encoding occur outside.

Reserved slots do not order unpublished commands or block ordinary output.
Publication defines stream order. Released slots remain available for status
until reaped, so a producer that never reaps eventually gets BUSY. Payload
capacity is caller-owned, bounded by three descriptors of at most 65,535 bytes;
MOS allocates no payload heap. A copy convenience wrapper, if later provided,
must use owned bounded storage with a separately specified lifetime.

Acceptance transfers immutable-source ownership. RELEASED means the last
source byte has been copied into hardware; reuse is safe even if bytes remain
on the wire. Drain means published queue empty and TEMT. Neither establishes
VDP execution completion. An ordered query/reply is separate and only needed
when the application depends on receiver execution. No per-frame CRC,
acknowledgement or vblank wait is introduced.

Cancellation never removes transmitted payload. Applications cancelling an
unstarted delta must also cancel/rebase dependent deltas. A caller's timeout
does not free borrowed storage, reset the FIFO or abort a partial command.
LSR errors are sticky RX diagnostics, not evidence that a TX byte was lost;
status must not falsely report successful receiver execution.

## Interrupt and wakeup design

Replace the receive-only handler with explicit IIR dispatch for line status,
RX data/timeout, TX holding-empty and modem status; no-pending returns without
reading a fictitious byte. Preserve parser and keyboard/reply processing.
Bound each entry's RX work, cause dispatch count and total TX writes; pending
RX must preempt lower-priority refill work. Verify the retrigger behavior when
the budget is exhausted rather than assuming it.

One consumer owns THR writes, IER updates, and all LSR/MSR reads and sticky
latches. Every TX service call admits a burst only after observing THRE,
performs at most the configured cap (initially 16) writes and samples CTS
before each byte. Never treat THRE as a single-free-slot indicator. State
updates record partial progress exactly once.

With queued data, arm modem interrupts before sampling CTS. If blocked,
disable TIE, retain modem wakeup, and recheck current CTS after the mask
transition. If ready, kick/refill and arm TIE for remaining bytes. An edge
consumed by an MSR read cannot be the sole wakeup mechanism: use the current
level to choose/reconcile state under the same critical section. After a
short CTS burst, wait for FIFO empty before admitting another burst.
At idle disable both TIE and session modem interrupts, retaining the normal
RX/line-status policy. Do not enable transmission-complete interrupts for
the initial API; drain samples TEMT and latches LSR errors.

The isolated tests must explore CTS changes at every read/mask boundary,
including ready-to-blocked-to-ready transitions, initial empty FIFO and
publication racing the last-byte transition. An idle or blocked FIFO must
not cause a TX interrupt storm.

## Compatibility and decisions for review

Foreground RST10, whole RST18, stdout and errors acquire a synchronous-output
barrier, finish earlier published transactions, then send through the same
consumer. New publication returns BUSY while the barrier is held. Reservations
alone do not delay it. Keep each RST18 call serialized across its entire block
or delimiter stream. Preserve legacy register/flag, MBASE and short-mode
contracts. Legacy return currently means accepted into UART, not necessarily
TEMT; do not advertise wire completion for that API. Masked foreground output
must pump rather than wait for an interrupt that cannot run.

Two unresolved integration decisions require review:

**Compatibility decision C-001** — `vdp_protocol_KEY` invokes the user keyboard callback inside the UART ISR.
   A callback that performs synchronous output cannot wait for this ISR to
   refill, and draining a long packet there can overflow RX. Rejecting or
   dropping legacy callback output changes compatibility; bounded deferred
   storage cannot accept arbitrary unlimited callback output. Audit the
   documented callback contract and select an explicit policy before claiming
   full ordinary-output compatibility. Do not silently allow interleaving.
**Compatibility decision C-002** — Normal application return must close/drain before reclaiming source RAM.
   An indefinite CTS stall makes safe return potentially indefinite. Add a
   MOS return fence and retain memory on a timeout; crashes/reset require a
   separately defined recovery policy because a half-sent VDP command cannot
   be safely discarded. No implicit FIFO/parser reset is authorized here.

The driver preserves both register banks, index registers, ADL, MBASE and
stack contracts as applicable to its entry points. Existing agon-6502 DI
chunks of roughly 0.5 ms exceed the roughly 139 us FIFO wire interval at
1.152 Mbaud. Its separate integration must shorten protected sections or
prove safe preemption; this project does not remove DI or modify games.

## Implementation and validation sequence

This sequence describes the experiments; actionable status lives only in
[TODO.md](../TODO.md).

Pending implementation steps remain in [TODO.md](../TODO.md). Completed
TX-002/TX-003/TX-004 and their evidence are recorded in the dated development
log. Identifiers remain fixed and are never reused.
