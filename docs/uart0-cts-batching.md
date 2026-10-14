# Design goal: opt-in UART0 CTS batching

Aware applications should be able to request fewer CTS checks per transmitted
byte, recovering eZ80 execution time while retaining reliable, ordered UART0
output on a qualified hardware/VDP combination. The production default remains
a CTS check before every byte. This is a proposed extension, not an implemented
or qualified operating mode.

## Intended behavior

An application explicitly selects a supported maximum batch size for its async
session. MOS checks CTS before starting each batch and may then send up to that
many bytes before checking again. A batch is a maximum allowance, not a promise
to write into unavailable UART FIFO space: existing transmitter-ready checks,
ISR work limits and receive servicing remain necessary. The UART line rate is
unchanged; benefits must be demonstrated as recovered CPU time or reduced
software-induced gaps, rather than assumed from fewer checks.

Legacy calls and unmodified async applications retain per-byte checking.
Selection belongs to the active session, with a safe default on every open
and reset on close/application exit. Unsupported requests fail explicitly;
there is no silent escalation. The exact API is to be designed with versioned
capability discovery and compatibility with the existing 1.1 table. Initially,
configuration should be permitted only when transmission is quiescent, avoiding
an ambiguous change in the middle of a published descriptor. Exact quiescence
and error semantics are part of the contract review.

The setting must not turn into unrestricted CTS bypass. Source-memory lifetime,
completion/TEMT fences, descriptor ordering, callback exclusion, cancellation,
masked-interrupt progress and bounded ISR work retain their existing contracts.
A session must not leave relaxed CTS handling active for subsequent applications
or the MOS prompt. The setting cannot assert that firmware or hardware has
been identified merely from an operator label or an application request.

## Evidence and limits

Console8 diagnostic run R0003 verified 42 × 4096 bytes with matching CRCs,
zero reported UART errors and restored receiver settings. At stock threshold64,
all six 5/20ms pause trials settled at66/128 bytes: 62 observed spare slots.
This supports investigating batching; it does not establish a safe batch size.
Threshold124/126/127 cases reached128 without data loss, so no failure boundary
was established. The analyzer's full-FIFO counts cannot reveal further tail
occupancy. Electrical CTS timing and worst-case reserve remain unmeasured.

The current implementation's UART FIFO behavior, bytes already in flight,
CTS sampling race and VDP receive-service behavior must be included in the
batch budget. In particular, do not equate the observed62 spare slots with
permission to send62 unchecked bytes on every platform. Longer CPU delay is
not necessarily more dangerous than additional queued bytes; vary the actual
mechanism being proposed. Keep the default receiver threshold for the primary
qualification and use threshold sweeps only as additional diagnostic controls.

## Work sequence and acceptance

The sole actionable checklist is TODO.md, using immutable BT-nnn identifiers.
Finish the existing qualification/release bookkeeping before implementation.

BT-001 defines the session API/capability contract, supported values and reset
semantics. BT-002 audits hardware and assembly paths and establishes a
conservative in-flight-byte budget before selecting initial batch candidates.
BT-003 implements an isolated candidate, initially comparing sizes1/2/4/8/16
only where the audit permits. Include explicit per-byte fallback and bounded
interrupt service. These are experiment candidates, not promised supported
production settings.

BT-004 adds paired measurements for blocking/default async/batched async,
using identical payloads and useful application work. Measure throughput,
completed useful work or cycles, interrupt/service cost and latency. Keep
calibrated coarse MOS ticks separate from precise CPU accounting. A relaxed
mode must show a repeatable, useful gain to justify its compatibility cost.

BT-005 extends the existing menu/reporting to record requested/effective batch,
receiver firmware identity evidence, payload integrity, FIFO/error/restoration
measurements and the first observed failure, if any. Exercise both Flexe engines
for protocol/API regression and negative controls; emulator FIFO values cannot
qualify hardware reserve. Check default behavior, unsupported requests,
close/reopen, application exit, callback interaction, masked-IFF progress and
ADL=0/legacy regression. Do not duplicate the entire established suite when
focused controls and its baseline campaign cover the change.

BT-006 runs the qualified fixture manually on Console8. Progress from small
batches, stop or narrow the sweep on unexpected loss, and repeat near any
boundary. Keep corruption inside the diagnostic receiver. No Olimex probing,
new wiring or automatic firmware flashing. If every tested size passes, report
a tested lower bound on tolerance rather than inventing a breaking point.
Separate the experiment range from conservative production options.

BT-007 reviews benefit against receiver reserve and failure evidence, documents
which combinations were tested, and either ships a conservative opt-in mode
or records that the gain does not justify shipping it. Production acceptance
requires clean default/legacy regression, session cleanup, useful measured gain,
verified receiver integrity and a documented safety rationale. A successful
fault-injection experiment alone is insufficient. Human review precedes commit
and physical installation remains manual.

## Existing work that comes first

TX-018/TX-019 reusable suite and firmware menu already pass human and physical
software campaigns. TX-020 receiver instrumentation also passes its human and
physical campaign. Their pending work is evidence/documentation consistency,
review and explicit commit/push authorization; no new baseline run is needed
without a change or unresolved concern.

TX-006 must distinguish the now-observed Console8 reserve from unmeasured
worst-case/electrical timing. Confirm the installed stock VDP boot version after
R0004's restore request: the updater's zero return is not proof of installation.
Retain the unknown entry RX0x98 as a pre-existing observation, not a trial error
or a silently closed investigation. Application/game integration remains a
separate coordinated task; this plan does not authorize interrupt-policy changes
in another project.
