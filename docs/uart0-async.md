# DRAFT — MOS asynchronous UART0 API and implementation plan

Executive summary: this project aims to let MOS send data to the VDP in the
background so applications can spend more CPU time on sound processing,
graphics and other work. Apps must explicitly request the experimental service;
legacy apps retain stock behavior. MOS keeps queued data in order and protects
an application's memory until it has finished reading that data.

The small-batch approach has shown useful CPU headroom in an earlier Console8
comparison, and the new app-controlled version passes software checks. It is
not yet approved for use: a VDP receive fault still blocks reliable emulator
qualification, and the new firmware needs further tests on Console8. This
specification describes an experimental MOS fork, not a stock MOS feature.

## Status and terminology clarification — 2026-10-14

Stock MOS is the approved baseline. The per-byte async implementation in this
fork and the grouped-scalar/chunk/OTIRX prototypes are experimental, not stock
or approved production features. Earlier fixture acceptance and commit authority
do not imply release approval. The [remaining roadmap](uart0-ab-tranche.md)
and sole [task checklist](../TODO.md) distinguish physical comparison evidence,
receiver integrity, the traced emulator receiver race, application integration
and explicit release approval. Use these qualified names rather than calling
an experimental transport “current.”

## Original motivation — Tom Morton

Tom Morton's original proposal is the design anchor for this project, including
the efficient block refill, rather than background transmission alone.
[Discord provenance](https://discord.com/channels/1158535358624039014/1158537054959964220/1559209863954038915).
The Author supplied this verbatim text and provenance on 2026-10-13; the quote
is preserved as supplied, without claiming independent access to Discord:

> why not ask codex to use interrupt-based UART0 transmission?
> then you can enqueue 16 bytes using a single `otirx` instruction, and walk away to calculate other stuff
> maybe there is a good reason nobody has done it. 🤷‍♂️

The intended mechanism is an interrupt-driven, bounded FIFO refill using
`OTIRX`, followed by returning the eZ80 to useful application computation while
the UART shifts the bytes. `OTIRX` performs CPU-driven block I/O; it is not DMA.
A full contiguous 16-byte refill is the motivating case. Short source spans,
descriptor boundaries and remaining service budget require smaller bounded
copies; never read beyond the published source merely to fill the FIFO.

The final sentence is an open caution. The Author read it as either snark or
a genuine warning; Tom's intent is not established. Investigate the possible
reasons through CTS reserve, interrupt/wakeup correctness, receiver integrity
and measured CPU benefit. Neither dismiss the concern nor turn it into an
unsupported claim that the mechanism is unsafe.

The implemented per-byte CTS/copying path is the conservative baseline, not
completion of the block-refill goal. The next experiment must compare that
baseline, grouped CTS checks with scalar copying, and CTS-guarded bounded
`OTIRX` copying. Update descriptor progress once per copied chunk where correct,
retaining ordering, source lifetime, service caps and TEMT drain semantics.
The 16-write refill cap remains; CTS may change during a block copy, so the
opt-in mode needs receiver-headroom qualification. Use stock VDP for normal
operation; diagnostic VDP exists only to measure the experiment.

Measure useful eZ80 work recovered and ISR cost as well as throughput. A mode
that merely removes some CTS reads while retaining all scalar copy/accounting
costs does not by itself evaluate Tom's proposal. Any decision to omit `OTIRX`
from the delivered option must explicitly record its measured or technical
reason against this design goal.

## Production integration status

`src/uart0_tx.inc` is the single core used by production MOS and the isolated
wrapper. `src/uart0_async.asm` supplies MOS state, receive-parser routing,
legacy synchronization, polling and discovery. Startup clears BSS and seeds
the ticket counter before enabling interrupts. `_uart0_handler` dispatches
real UART causes through that core without a private receive owner.

Build the complete image with `tools/zds/build.sh`. Reproduce all automated
qualification with `experiments/uart0-mos/build.sh`. Both use native ZDS II
under Wine on Oryx; no assembly translation or AgonDev build is used.
Legacy applications retain blocking output. CPU/work overlap requires explicit
use of the discovered async operations.

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
from its configuration. `src/interrupts.asm::_uart0_handler` now routes to the bounded UART cause dispatcher. `src/serial.asm` retains CTS/THRE polling when closed and routes output
through the ordered compatibility path when an async session is open. `src_startup/vectors16.asm` routes RST10 and each
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
if necessary. Bounded OTIRX refills are a required experimental comparison
from the original proposal above; adoption still requires demonstrated
headroom, correctness and a useful measured benefit.

## Candidate API

Discover the candidate API through existing `mos_getfunction` (50h), with
B=13h and C=0. A=0 and HL!=0 identify the discovery entry; call it in ADL
with MBASE=0 to obtain HL pointing at the ROM table below. Older MOS can
reject the function number, so callers must check the result and retain their
synchronous fallback. No existing function index or RST call changed.

| Table offset | Size | Meaning |
|---|---|---|
| 0 | 4 | ASCII `UTX1` |
| 4, 5 | 1 each | Experimental ABI major 1, minor 2 |
| 6 | 1 | Table length 54 bytes |
| 7 | 1 | Flags: bit 0 callback exclusion, bit 1 drain-before-return, bit 2 diagnostic epochs, bit 3 session CTS batching |
| 8, 9 | 1 each | 3 descriptors, 16-byte burst cap |
| 10 | 3 | Maximum transaction length 00FFFFh |
| 13..39 | 9 × 3 | Operation pointers in the order listed below |
| 40 | 3 | Pointer to sticky RX error byte, followed by modem-delta byte |
| 43 | 3 | `tx_diag_take` pointer (minor 1 extension) |
| 46, 49 | 3 each | `tx_set_cts_batch`, `tx_get_cts_batch` pointers (minor 2) |
| 52 | 2 | Supported-size bitmap 808Bh: experimental sizes 1/2/4/8/16 |

Operations use the ADL **register ABI**, rather than the C stack ABI.
A returns OK=0, BUSY=1, INVALID=2, CLOSED=3 or CONTEXT=4. Reserve returns
HL=ticket; publish consumes DE=ticket, HL=source and BC=length. Status consumes
DE=ticket and returns B=state and HL=accepted count. Cancel and reap consume
DE=ticket. The batch setter consumes B=size; setter/getter return B=effective size on
success. Other operations take no arguments. AF/BC/DE/HL are scratch;
IX/IY, shadow banks, MBASE, ADL and incoming foreground IFF are preserved.
The session is singleton; no session-handle parameter is passed. Descriptor
states are RESERVED=1, QUEUED=2, ACTIVE=3, RELEASED=4 and CANCELLED=5.

All pointers and counters below are unsigned 24-bit values stored in three
bytes. Do not store them in `dw` fields. Maximum transaction length is 65,535;
reject zero lengths and address wrap. Borrowed data must be stable readable
application RAM in [040000h, 0BC000h) until release. MOS RAM is excluded.
The foreground producer is single-owner. UART receive callbacks return CONTEXT;
NMI and other application-owned ISR calls are unsupported.

| Operation | Inputs | Result and behavior |
|---|---|---|
| `tx_open` | none | Exclusive singleton session; BUSY if already open. Preserve baud, FIFO configuration and RX. |
| `tx_reserve` | none | Nonblocking descriptor reservation or BUSY; reserves one of three slots before rendering. |
| `tx_publish` | DE=ticket, HL=source, BC=length | Atomic publication of the reserved ticket; no payload copy. Failure leaves reservation/source caller-owned. |
| `tx_status` | ticket | RESERVED, QUEUED, ACTIVE, RELEASED or CANCELLED, with accepted-byte count and diagnostics available through the table pointer. |
| `tx_cancel` | ticket | Cancel reserved or wholly unstarted transaction only; ACTIVE returns BUSY without changing progress. |
| `tx_reap` | released/cancelled ticket | Free descriptor; stale tickets rejected. |
| `tx_poll_drain` | none | Nonblocking DONE only when no published work remains and TEMT=1; otherwise PENDING. |
| `tx_close` | none | Nonblocking close only after drain and all reservations/tickets resolved; otherwise BUSY. |
| `tx_diag_take` | none; session must be closed | Atomically sample pending LSR/MSR, return HL=00:modem-deltas:RX-errors, then clear those software latches. BUSY while a session is open; no FIFO/parser reset, byte read or transmit wakeup acknowledgement on rejection. |
| `tx_kick` | none | Bounded service opportunity for masked-interrupt callers; preserves their IFF state. |

Each operation returns an explicit status: OK, BUSY, INVALID, CLOSED or
CONTEXT. No failure silently drops a command. Tickets must never alias a live
or accepted stale handle; the shared implementation uses monotonic u24 IDs
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

The installed handler uses explicit IIR dispatch for line status,
RX data/timeout, TX holding-empty and modem status; no-pending returns without
reading a fictitious byte. Preserve parser and keyboard/reply processing.
The budgets bound driver work; arbitrary legacy callback runtime remains
application-owned, with async closed.
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

The isolated tests explore CTS changes at every read/mask boundary,
including ready-to-blocked-to-ready transitions, initial empty FIFO and
publication racing the last-byte transition. An idle or blocked FIFO must
not cause a TX interrupt storm.

## Compatibility policies accepted on 2026-10-13

Foreground RST10, whole RST18, stdout and errors acquire a synchronous-output
barrier, finish earlier published transactions, then send through the same
consumer. New publication returns BUSY while the barrier is held. Reservations
alone do not delay it. Keep each RST18 call serialized across its entire block
or delimiter stream. Preserve legacy register/flag, MBASE and short-mode
contracts. Legacy return currently means accepted into UART, not necessarily
TEMT; do not advertise wire completion for that API. Masked foreground output
must pump rather than wait for an interrupt that cannot run.

**C-001 — callback/session exclusion.** Async open returns BUSY while a user
keyboard callback is installed or a synchronous-output scope is active.
`mos_setkbvector` first drains and closes any async session, then installs or
clears the callback. Existing callbacks retain their ISR timing and synchronous
output behavior. Async applications must use MOS keyboard state/map or polling;
installing a callback invalidates their session and tickets after drain.
The new API returns CONTEXT from the UART ISR/receive callback, or with nonzero
MBASE. NMI and other application-owned ISR entry remain outside its contract.
Applications that replace UART vectors, modify UART registers or write private
MOS state directly do not satisfy this ownership contract.

**C-002 — retain and wait.** Both execution wrappers fence normal return before
MOS may reuse application RAM or report a result. OSCLI fences before a nested
command can load a child into that RAM; execution entry fences too. The fence
excludes publication, pumps TX and RX, waits for queue empty and TEMT, then
clears unused reservations/completions and closes. Tickets remain monotonic.
There is no timeout that frees a borrowed buffer: permanent CTS blockage waits
indefinitely, as the Author explicitly selected. Recovery then requires an
explicit system reset; this API does not silently flush the FIFO or reset the
VDP parser. A reset during a partial VDP command may also require explicit VDP
recovery; eZ80-only reset is not a promised protocol resynchronization.

RST38 panic output first drains/closes an intact foreground consumer. If panic
entry interrupts UART service itself, MOS retains RAM in a stopped loop rather
than recursively servicing half-updated state; recovery requires reset. The
panic path cannot promise progress during a permanent CTS stall. General
memory corruption and applications bypassing the execution wrappers remain
outside normal-return guarantees.

Whole RST18 calls hold a nested synchronous scope. Individual PUTCH/stdout/error
bytes use that scope and preserve their legacy register contract. Foreground
DI output pumps bounded RX/TX service rather than waiting for its own ISR;
internal compatibility operations also work with a short caller's nonzero
MBASE. The public async API remains ADL/MBASE-zero only. Ordinary output may
wait longer to maintain ordering, and still returns on UART acceptance rather
than advertising VDP execution completion.

The driver preserves both register banks, index registers, ADL, MBASE and
stack contracts as applicable to its entry points. Existing agon-6502 DI
chunks of roughly 0.5 ms exceed the roughly 139 us FIFO wire interval at
1.152 Mbaud. Its separate integration must shorten protected sections or
prove safe preemption; this project does not remove DI or modify games.

## Implementation and validation sequence

Physical qualification targets Heber Agon Console8 without Extender hardware.
The Author manually installs firmware and runs fixtures. The SD bundle keeps
the candidate MOS, official stock VDP 2.16.0, flash utility and fixture files
together with a plain `readme.txt` in `/test/mos-uart0`. Automated emulator
evidence used a Golem-built snapshot reporting VDP 2.16.0; it does not establish
qualification of the byte-distinct official stock image. No custom VDP command
or module-loader extension is required by this UART0 fixture.

This sequence describes the experiments; actionable status lives only in
[TODO.md](../TODO.md).

Pending implementation steps remain in [TODO.md](../TODO.md). Completed
TX-002/TX-003/TX-004 and their evidence are recorded in the dated development
log. Identifiers remain fixed and are never reused.

Minor 1 diagnostic epochs preserve the offsets and behavior of the original
nine operations and diagnostic pointer. Error latches normally accumulate since
boot (or the preceding explicit snapshot); opening/closing a session does not
reset them. A benchmark must separate setup/history from the interval it
claims to measure. `tx_diag_take` establishes that boundary under DI, captures
pending status and clears only captured software flags. It requires a closed
session to avoid consuming a modem wakeup from queued transmission. It never
flushes RX/TX or resets VDP parsing. Repeated occurrences of the same error bits
are detectable in successive epochs; subtracting a baseline bitmask is invalid.

## Experimental CTS batching extension

The Console8 installed candidate remains ABI 1.1 with per-byte CTS checks.
The off-device source now implements experimental ABI 1.2, including session
setter/getter and bounded OTIRX for selections above 1. Its
[contract](uart0-cts-batching-api.md) and [hardware/source audit](uart0-cts-batching-audit.md)
keep the 16-write refill cap independent of the selected CTS interval. Size 1
uses the conservative scalar per-byte path; legacy output remains unchanged.
This source change does not install firmware or approve any async transport
for production. See [implementation evidence and limits](../experiments/uart0-batching/README.md).
