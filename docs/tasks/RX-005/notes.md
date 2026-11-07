# RX-005 running notes

Append dated decisions, evidence, open questions and corrections here. Keep raw
conversation/Discord records unchanged. [README.md](README.md) defines the task;
[TODO.md](../../../TODO.md) remains the sole actionable checklist.

## 2026-11-07 — Receive-side discussion and stock baseline

Brandon shifted focus from sending to devices sending bytes to the eZ80, then
asked about stock UART0 reception and whether safety might have been preferred
over performance. The full exchange is in [conversation.md](conversation.md).

Stock MOSv3.0.2 reads/parses one byte per UART0 IRQ and retains packet state;
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
