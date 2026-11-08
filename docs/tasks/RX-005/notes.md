# RX-005 running notes

Append dated decisions, evidence, open questions and corrections here. Keep raw
conversation/Discord records unchanged. [README.md](README.md) defines the task;
[TODO.md](../../../TODO.md) remains the sole actionable checklist.

## 2026-11-07 — Receive-side discussion and stock baseline

Brandon shifted focus from sending to devices sending bytes to the eZ80, then
asked about stock UART0 reception and whether safety might have been preferred
over performance. The full exchange is in [conversation.md](conversation.md).

Stock MOS v3.0.2 reads/parses one byte per UART0 IRQ and retains packet state;
it does not wait in the IRQ for the rest. Some request/reply callers separately
spin on a completion flag. Receive IRQ cost and foreground waiting are distinct
targets. No design intent, optimality or measured improvement was established.

## 2026-11-07 — Expand the same task to general bidirectional transport

Brandon supplied the Discord export, confirmed its boundaries and directed:

> the thing to hone in on is a general, efficient bi-directional transport protocol that dosen't break existing apps and doesn't require rewiring massive tracts of mos or vdp.

He specified the goal as “implementing the simplest general bi-directional
transport protocol we can do,” then clarified “add to that then” and “yes and
the running notes.” Expand RX-005 rather than duplicate it. Keep the stock
receive investigation as its baseline step.

Full source: [discord-transcript.txt](discord-transcript.txt). Attributed relevant
comments, provenance and cautions: [discord-extract.md](discord-extract.md).

### Requirements now recorded

* General, efficient communication both ways, including a proper bulk return
  path replacing the keyboard-map workaround.
* Existing apps work unchanged; preserve startup, legacy commands/replies and
  their ownership. New application behavior is opt-in.
* Small local MOS/VDP changes, with assembled code/RAM costs recorded. Avoid
  another oversized framework or unnecessary protective machinery.
* Demonstrate a useful consumer and improvement over the workaround.
* Community consensus before advocating upstream merge; local work is separate.

### Starting proposal, not a finalized ABI or wire format

Tom proposes a bulk-return packet type/count and registered destination pointer,
capacity and callback. Prefer reusing the existing TX capability and adding the
missing return mechanism over replacing legacy traffic. One outstanding receive
buffer is a minimal candidate; queues/channels/pipelining are not requirements.
No opcode, syscall number, frame layout or callback context has been chosen.

Arm valid destination storage before the peer sends. Define capacity, result,
completion publication and reuse/retirement. Bulk bytes must not be mistaken
for keys or legacy replies. Unarmed reception and oversize offers need defined
behavior, without silent overwrite/truncation. Select only the pacing/readiness
needed for correct buffering; automatic retries, echo, checksums and elaborate
sessions are not default requirements. Simplicity does not mean uncontrolled
sender bursts while the receiver is processing its only available buffer.

Our existing async TX needs no VDP protocol change. A new bulk-return packet
requires matching MOS/VDP support; compatibility means opt-in extension with
legacy traffic preserved, not pretending stock firmware already supports it.
Exact donors and a capability/refusal policy remain open.

### Open design questions

* Can a new dispatch branch copy bulk data directly into admitted RAM, bypassing
  the legacy fixed reply scratch buffer without rebuilding its state machine?
* Is packet type plus one ordered receive transaction sufficient, or does the
  actual consumer need a separate request identifier?
* How does readiness/pacing protect FIFO reserve during DI and application
  processing/rearm? Direct RAM copying is not flow control by itself.
* Which completion context is smallest and practical: a tiny IRQ callback or
  deferred notification? Preserve existing callback contexts and conventions.
* Would multi-byte draining/another RX trigger help enough to justify altered
  latency and reserve? Preserve keyboards/short replies; no14-byte trigger or
 16-byte message/buffer size is selected by analogy with TX OTIRX.
* Which first demonstration is simplest and useful: disk-block return/readback,
  variable-time render completion, or another existing producer? Measure large
  message integrity and small notification latency separately.

### Evidence and scope

The6502 KEY-R03 snapshots conditionally match intact key bytes consumed as an
unfinished mode reply. Its original cause remains unresolved. Keep that issue,
RX hardware overrun, VDP's earlier receive-recovery race and performance redesign
separate. Do not assume a corrected/reliable parser or attribute the key failure
to async TX. Related source assessments are linked from README.

This update extracts requirements and sets the implementation goal; it does not
implement firmware, choose a wire ABI, start a test/deployment, resume paused
MechAgon work or publish upstream. Existing owner, resource and toolchain rules
remain. Later decisions/evidence should be appended here.

## 2026-11-07 — Additive namespace and implementation-file organization

Brandon agreed with the additive return-service direction: register destination
storage/capacity/completion, request an operation through a VDU extension, and
receive a typed counted reply into that storage. Ordinary VDU traffic must not
be wrapped in new packet identifiers or bookends. A reserved function bank
provides a local dispatch namespace; exact prefix/opcode allocation remains
subject to checking existing uses. No wire values have been assigned.

Brandon clarified that “one page” meant **one file, not a memory page**:

> i meant one *file* with all our code in it. then we only need update one or two files which register our reserved bank of functions.

Implementation requirement: keep enhancement code together in one dedicated
implementation file per firmware side (MOS and VDP), with only the small edits
needed in one or two existing registration/dispatch files. Avoid scattering
feature logic across the existing firmware. This is source organization and
reviewability, not a256-byte size limit or a memory-alignment requirement.
Retain the existing code/RAM cost measurement and minimal-feature goal. No
firmware changes or registration-number selection occurred in this update.

## 2026-11-07 — Consult VDPlet during design

Brandon directs consultation with the VDPlet owner as the design workup begins,
to make the transport work with that mode of operation. Obtain its source-based
input before settling the protocol/API and integration points, particularly
shared reply/output ownership, asynchronous module execution, completion and
buffer lifetimes, and minimal registration hooks. Preserve the one-file-per-side
organization and ordinary application compatibility requirements. Record the
feedback and resulting decisions here. This entry schedules the consultation;
no message, peer implementation assignment or test run was performed now.

## 2026-11-07 — Consumer consultation requirement and scope correction

Brandon added the applications using the keyboard-channel return-data workaround
to the design consultation: start with VDPlet, then FSIM, Wolf and MechAgon;
inspect their code to find other actual consumers. Ask what would make their
applications easier, rather than designing in isolation. Record concrete input
and its disposition before settling the protocol.

UART began contacting VDPlet immediately. Brandon clarified:

> i meant for you to add that to the task, not to start doing. but as youre goiing down the road already, continue with that, then stop for more task scoping and refinemment.

Finish this bounded source-review round and stop. No implementation, build,
test run, deployment, protocol allocation or resumption of a paused goal is
selected by this continuation. The task and TODO now carry that explicit gate.
The earlier entry's “no message” status describes that earlier documentation
update; the actual consultation requests are recorded in
[consultation.md](consultation.md).

Initial source inspection confirms a terminology distinction: VDPlet uses
tagged **keycode packets0x81** delivered through MOS's keyboard callback; these
are not held-key map transfers. Preserve the user's shorthand in historical
discussion, but identify the actual mechanism in designs and measurements.
VDPlet's private D8/D9 commands are existing experimental allocations, not a
freshly assigned general transport bank.

The6502 and MechAgon retained bulk-read helpers share an identical inspected
`mos_transport.c`: they request up to8 useful bytes per exchange (or READ16
fallback), wait for replies, and manage tokens/late-reply teardown. This confirms
a concrete extra consumer and a potential simplification; it does not establish
that these retained helpers are either application's current active renderer.
Owner consultation must distinguish those paths.

### Round completed: requirements to discuss, not a frozen design

VDPlet, FSIM, Wolf, MechAgon, 6502 and code-confirmed Rally returned substantive
source reviews. [The collation](consultation.md) links exact records; unchanged
mail and source/hash evidence are preserved alongside it. Wireframe's inspected
helper belongs to FSIM and is historical; Nurples/Jukebox generic API definitions
alone do not prove use of this workaround. Golem's loader and runtime benchmark
frontends remain possible later leads, not an expanded assignment now.

Common input: one outstanding receive is enough initially; admit stable caller
storage/capacity before requesting output and publish actual count/status after
copying. Remove synthetic-key dispatch/mailbox glue and serialized tiny reads.
Retain application correlation and define positive retirement before timeout/
rearm/storage reuse; no consumer asks for a new queue/channel/retry framework.
Keep ordinary traffic unchanged, bound IRQ work and establish real pacing.

Concrete useful sizes differ: FSIM 128-byte status; 6502 a 40-byte descriptor plus
512-byte block; Wolf 16+20 bytes per profiler frame; MechAgon bounded 256–1024-byte
replay readback; Rally 256-byte export chunks/406-byte state. Larger data sets do
not require giant buffers or IRQ callbacks. Source transaction/byte counts show
where overhead could be removed; they are not measured speedups or FPS gains.
Receive completion does not mean a render was presented or a disk write committed.
VDPlet's OPEN-session D8/D9 admission gate needs explicit integration if we add
a request selector. No allocation or approach has been chosen.

Correction from MechAgon/Rally, checked against stock MOS v3.0.2
`vdp_protocol_KEYSTATE` and the retained VDP `agon.h`: UART's initial requests
incorrectly called 0x88 a literal key-map reply. It is KEYSTATE carrying five
repeat-delay/rate/LED bytes. The confirmed private carrier is keycode 0x81;
ordinary held-key map access is another mechanism. Preserve sent mail verbatim
with this explicit correction. Do not propagate the erroneous0x88 label.

MechAgon also reports its goal was independently resumed by Brandon; UART's
request used stale paused-goal wording. This consultation grants no goal work,
and this project does not alter the other owner's independently selected scope.

**Stopped for Brandon's task scoping and refinement.** No ABI, wire values,
firmware/application implementation, build, test, deployment or upstream action
was selected or performed by this consultation round.

## 2026-11-07 — Check current documents for stale terminology

Brandon asked to ensure the correction was reflected in current canonical
documents. The maintained task README, this notebook and consultation summary
already use the correct packet meanings. A search of this project's maintained
Markdown found no remaining assertion that0x88 is a key-map packet; matching
mentions explain the correction. Historical mail/review directories now have
explicit README notices identifying their status and the known wording error.
Their original bytes and evidence hashes remain unchanged.

The external6502 owner's maintained `RX-005-CONSULTATION-R01.md` paragraph2
still used the misleading label. Sent concrete correction request
`2026-11-07_17-52-09_agon-mos_rx005-canonical-keystate-terminology-correction-two`
and an accepted immediate chat notice. The owner returned
`2026-11-07_17-52-57_agon-6502_rx005-6502-terminology-corrected-two`; UART
then verified the corrected Markdown paragraph, JSON annotation and current
HANDOFF. Its existing human commit gate remains with that owner. Other named
maintained owner reports inspected did not assert that0x88 is the held-key map.
This is documentation accuracy cleanup only;
the design/implementation scoping stop remains in effect.

## 2026-11-07 — Selected first implementation goal

Brandon supersedes that stop and explicitly starts the first trial goal. UART
coordinates the whole RX-005 effort, owns MOS code and original synthetic cases;
VDPlet owns all VDP/VDPlet changes. Neither edits game code. Passing synthetic
qualification ends at Brandon's review before any prototypes reach individual
application owners. The new scope does not distribute prototypes, install
firmware, change defaults or publish a release/PR.

Direct human source: turn01a1b844-3a1a-7a80-af4d-4763a4075894,
item01a1b844-3a88-7840-ae55-be0c44bd9aab in this UART thread; VDPlet independently
verified the source through its read-only app tool. The explicit goal is active.
See [trial-plan.md](trial-plan.md) and [wire-contract.md](wire-contract.md).

VDPlet task VDPL-036 initially pins donor46a93af/classicESP32 with async disabled,
proposes private90h/u16-count/payload(max512), existing D8op8 and INFO27=512.
UART accepts the binding and normal source-error/same-arm retirement semantics.
Its whole-frame serialization audit uses one temporary515-byte frame and one
existing HAL-locked UART write shared with ordinary writers; no private-only
mutex or new flow-control policy. Owner component checks/build remain pending
before a shared target freeze. It owns every edit on that side.

MOS donor is exact released Eirene RC3 97311c4 in an isolated worktree/branch;
no official ZDS source migration or neighboring feature-checkout modification.
Native baseline rebuild reproduces the released100879-byte image and map
exactly, with the48-slot startup invariant passing. The initial build tool tried
to use a flat map without local startup labels; its failed check is preserved.
A byte-matched ELF supplies the full symbols for the corrected baseline check.
Compiler481 was released and actual successor FSIM immediately steered.

Initial MOS source is one new `uart0_receive.asm` plus two small hook edits in
`interrupts.asm`/`mos_api.asm`. It adds344ROM bytes and21BSS bytes. Startup and
sender compiled objects remain donor-identical; all other compiled units except
those two hooks/new object also match. The first two freezes retain the short
branch range error and first mistaken branch edit; the corrected trial-r03
native build, ELF parity, startup and original C-fixture link pass. This is not
an executed parser, IRQ, emulator or hardware pass. Compiler489 is released;
actual successor6502 was immediately steered (scheduling only, no prototype).

Original fixture covers deterministic0..512-byte patterns, actual counts/guards,
BUSY/invalid/unarmed/oversize, NULL callback, source rejection retaining the same
arm, repeated positive rearm, useful foreground work, ordinary GP and genuine
key make/break. Current pending work: matched VDP component and source audit
disposition, runtime/input infrastructure pins from Flexe, then frozen finite
Oryx cells. No game source was read for modification or edited in this goal.

The private host runner now selects Flexe owner FX224 host-r03 (frontend
bad83f54/backendd77a7305) and its existing e223b8f5 SDL3 key injector. Profiles
are generated stopped with canonical identity/naming helpers copied privately;
shared templates and helpers stay unchanged. The finite case includes actual
SDL A down/up after the app's READY marker, a separate stopped wire oracle and
app byte/guard/count/callback assertions. No emulator or physical run yet.
Source review caught an evidence limitation before running: MOS_UART_STATS only
flushes on selected IER writes. Preserve it without calling an early snapshot
an end-of-case zero-overrun result. Positive integrity needs the application
oracle, complete producer/delivered trace comparison and backend failure stats.

Compiler500 ran the bounded host script/oracle controls: the exact32-frame/
2397-byte/30-callback manufactured transcript passes and seven corrupt framing,
payload, key and report variants are rejected. These are independent checker
controls, not firmware execution. Actual slot released with all own work stopped;
VDPlet501 was autogranted and immediately steered. Native producer checks and
matched firmware build remain owner work; joint emulator run is pending.

VDPlet503's disabled BIN did not reproduce the old image hash. Owner stopped
and retained the failed exact gate. Its independent ELF comparison finds all
allocated code/data/BSS declarations identical, with differences limited to
nonallocated debug info/line/string sections. The full ELF hash embedded in the
BIN changes image metadata/checksum/digest as a consequence. UART read the task
amendment3a6148a and section comparison, agreeing to retain original c7978a74/
24d76d14 as selected disabled control and separately identify the fresh companion
6c2dc561/7ad7e2db. Qualification still requires independently checked image validity,
embedded hashes and exact metadata-only BIN difference locations. No stripping,
normalization or relabeling; executable parity and all runtime gates remain.
The enabled component compile proceeds separately, joint emulator still unrun.

Shared Oryx367 first attempt reached the normal MOS prompt but never invoked
fixture: the newly generated wrapper omitted --sdcard-img and selected an empty
hostfs directory. Runner stopped on45s without UART progress, preserved raw output,
joined owned processes and released with fresh empty-host evidence/nextnull.
This is an invocation-harness failure, not receiver or firmware qualification.
The corrected builder explicitly embeds the prepared FAT image, asserts that
selection, and generates fresh qualification-r02 profiles. MOS/VDP/app bytes stay
unchanged; old profile/results retained. New attempt rejoins the normal FIFO.

Corrected Oryx368 run invokes the fixture. INFO27 returns512 and source upload/
ordered GP33 pass, but first op8/count0 produces old tagged ERROR status9
UNSUPPORTED before any90 header. This leaves the MOS receive arm pending and
callbacks0, exactly the agreed source-rejection lifetime rule; no new payload
case passed. The fixture reports FAIL without rearming/reusing storage. Runner
stopped at first failure, preserved the raw report/wire, joined owned children,
and released00:02:39UTC with fresh idle evidence. Actual next FSIM was immediately
steered. Owner VDPlet received exact request/reply/pins and diagnosis request in
rx005-r02-normal-context-refusal-six; UART does not edit the VDP producer.

VDPlet identified a sufficient refusal condition from actual368 debug echo:
the selected stock vdu.h echoes literal0x17 command bytes only in consoleMode.
The fixture had no explicit FE0 setup. Existing producer therefore correctly
refused the active console context. Fixture-only correction sends existing
VDU23,0,254,0 before initial ordered GP and receive admission; no MOS, VDP or
guard change. Owner source findings remain scoped: they do not prove every
other admission predicate will pass. Fresh fixture build and FIFO attempt next.

Oryx372 diagnostic isolates the failing interval: pre127 snapshot has rx_overruns0,
rx_irqs337; final snapshot has rx_overruns9,rx_irqs458,tx_drops0. Actual LCTL03/
IER01/issued1 confirms the unchanged-value diagnostic flushed the intended
register. Full127B producer/delivered frame is retained; prior six counted sizes
pass. Lifetime counters now have a matched pre-case cut; the model discarded
nine bytes at full RX FIFO during this interval. IIR RX counts are not claimed
as accepted-byte/RBR counters. No physical timing/root-cause claim follows.
The existing one-byte receive boundary cannot keep up with this counted trial.

Selected correction within the trial goal: add a finite maximum16-byte drain
inside the one new MOS file, and only while a counted frame is active. Stop
at complete/discarded frame or empty FIFO; ordinary legacy packets retain their
one-byte path and existing callback context. Keep producer, wire/API, startup,
TX and source/capacity/lifetime rules unchanged. No ring, queue, cancellation,
retry, HAL change or pacing workaround. Compare the same fixture/VDP/runtime
before and after; require all0..512B/key/guard cases and final counters to pass.
The diagnostic app also now emits a post-close failure marker; host grants at
most5s for failed-log closure while retaining live storage. Prior prompt-failure
capture cut off fclose and left a zero-length SD log; raw failure evidence was
retained and remains authoritative, not relabeled as a clean report close.

Final native r07 passes: MOS101257B/CRC3933C3ED/SHA40dc3d17, added378ROM/22BSS;
fixture16036B/build9c72616d7f4a4ef7/SHA6f79d47e. Startup48-slot and unchanged
other-unit checks pass. The bounded drain adds34ROM/1BSS over the initial parser.
Shared Oryx373 r05 passes BOTH JIT9.071s and interpreter9.449s, each32 counted
frames/2397 exact bytes/30callbacks/2 genuine SDL keys/guards/negative cases/
source-error same-arm completion and clean return. Full final same-IER snapshots
both tx_drops0/rx_overruns0; backend failure counters zero. Work3699/14027 is
nonblocking evidence only, not comparable CPU performance. Source/delivered
fixture prefix matches through ordered GP34; startup/later CLI scope explicit.

Actual source patch reapplication to donor files reproduces all three frozen
MOS files byte for byte; current fixture sources match the executed freeze.
Exact source hashes, native proof, model counters, key events, raw wire, reports,
archive hashes and control-disposition history are retained in trial-evidence,
REVIEW.md and build/rx005. Coupled code/results remain private and uncommitted.
All owned processes joined and Oryx373 released00:32:14UTC with fresh idle and
nextnull; all Pi compiler checkouts released. STOP FOR BRANDON'S REVIEW: no game
edits, consumer prototypes, physical tests/card writes/default/release/upstream
publication selected or performed. This closes the bounded trial goal, not the
later hardware/application/benchmark or broader protocol investigation.
