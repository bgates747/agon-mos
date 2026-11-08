# RX-005 — Minimal compatible bidirectional MOS/VDP transport

Current status2026-11-07: Brandon reviewed the passing synthetic trial and
selected the next manual Console8 check. The exact tested MOS/VDP/fixture is
deployed to AGONC8 at `/test/mos-uart0`. Original `autoexec.txt` is restored
exactly; invoke `test` manually after both firmwares are installed.
Read [hardware-r01.md](hardware-r01.md) for the flash order, key step and report
pins. Emulator qualification remains in [REVIEW.md](REVIEW.md). Physical results
are pending; consumer prototype distribution remains gated on Brandon's review.

Current authorization2026-11-07: Brandon selected a first synthetic trial and
explicit goal. UART coordinates and owns MOS/test-fixture changes; VDPlet owns
all VDP/VDPlet changes. No game-code changes or consumer prototype distribution.
The prior consultation stop below is superseded by this instruction. Follow
[trial-plan.md](trial-plan.md); stop again once the trial passes for Brandon's
review before individual application experiments. The selected private API/wire
is in [wire-contract.md](wire-contract.md), with finite execution/cleanup in
[trial-run-plan.md](trial-run-plan.md). The initial investigation and earlier
documentation-only limitations below are historical context; they do not
override this explicit trial authorization.

Brandon opened this investigation on2026-11-07, then expanded its goal to
implementing the simplest efficient general bidirectional MOS/VDP transport.
Add a proper return-data path without breaking existing applications or
rewriting large sections of MOS/VDP. Reuse existing TX where practical; do not
build a new framework merely for symmetry. Stock receive/reply-wait mapping
remains the first baseline step.

Brandon's source-layout requirement: one dedicated implementation file per
firmware side, with only small edits in one or two existing files to register
the reserved function bank. Keep feature logic out of those registration hooks.
“One page” in the discussion meant one file, not a memory page or256-byte limit.
Ordinary VDU traffic must not acquire new packet bookends; the namespace is an
additive extension, with exact allocation still to be checked.

The original question asks whether the design prioritizes safety at a possible
performance cost. That is a hypothesis to investigate, not an established reason
for the code. Preserve correctness, ordinary application behavior and startup.

The discussion from the first receive-side question through this task request
is preserved in [conversation.md](conversation.md), including both questions,
the full explanatory responses and the stock-source clarification. Technical
claims in that transcript retain their original context; later corrections
should be appended explicitly rather than rewriting the historical exchange.

Maintain decisions and open questions in [notes.md](notes.md). The full Discord
export is [discord-transcript.txt](discord-transcript.txt), with pertinent
comments/provenance in [discord-extract.md](discord-extract.md). Tom Morton's
minimal bulk-return registration/type proposal and Jeroen Venema's buffer-sync
cautions are design input, not a finalized protocol or community acceptance.

The sole actionable checklist is [TODO.md](../../../TODO.md). This silo records
scope, questions and acceptance criteria. The goal includes design and
implementation, but this documentation tranche does not choose an exact ABI,
firmware edit, run or deployment. Brandon's community-consensus condition before
advocating an upstream merge remains recorded.

## Initial stock-source findings

The reference inspected for the conversation is the stock tag `v3.0.2`, commit
`8336409351ee5314e02801a7b72a4f1bb5282519`, in this repository. This is an exact
baseline, not a claim that it is the latest upstream revision. Read files from
the tag: the working branch contains experimental modifications.

* `src/interrupts.asm::_uart0_handler` saves registers, reads one byte through
  `UART0_serial_RX`, calls the packet parser and returns with IRQs enabled.
* `src/serial.asm::UART0_serial_RX` checks data-ready and returns immediately
  when empty. This is the reader used by the IRQ handler; distinguish it from
  the separately named blocking `UART0_serial_GETCH` routine.
* `src/vdp_protocol.asm::vdp_protocol` retains packet state between byte arrivals.
  It does not wait in the IRQ for the rest of a packet. On completion it updates
  system variables/flags or invokes a keyboard callback. Parsing and completion
  handling execute within the interrupt's masked interval.
* `src/mos.c::wait_VDP` repeatedly checks a volatile completion-flag mask, with
  a 250000-iteration timeout. Its approximate-one-second comment is not a
  measured/calibrated timing guarantee. The function does no useful foreground
  computation while waiting; receive IRQs can supply the completion flag.
* `src/mos_editor.c::getModeInformation` clears the mode flag, sends a query and
  waits. `readPalette` has a caller-selected wait argument. Keyboard reception
  does not require a foreground request/reply wait.

Thus interrupt-driven byte collection, packet assembly, caller notification
and a synchronous waiting API are separate stages. Performance work must say
which stage it measures or changes.

## Investigation questions and work order

1. Map the exact stock setup, FIFO configuration/trigger, IRQ dispatch, byte
   read, packet storage, completion flags, callback ABI and caller waits. Check
   RX error handling, no-data entries, input ownership and real receive-side
   flow control. Do not assume setting RTS once supplies automatic backpressure.
   Identify all relevant blocking entry points without treating every incoming
   event as a synchronous request/reply transaction.
2. Separate throughput/CPU cost from worst-case service latency. Account for
   register saves, one-byte IRQ entries, parsing/completion work and competing
   masked sections. At 1.152Mbaud/8N1,16 empty FIFO slots represent about139us
   of incoming wire time; this is not a safe blackout budget. Existing occupancy,
   in-flight bytes and peer stop latency matter. Incoming bytes continue to
   arrive during DI. Separate hardware overrun from software framing/queue loss.
3. Define a controlled measurement plan for stock receiving and foreground
   waiting. Measure complete verified replies, byte/packet integrity, errors,
   CPU/foreground work, service latency and application-visible completion.
   Separate VDP processing/wire time from eZ80 collection/parsing and polling.
   Use real supported VDP reply shapes; do not assume an existing arbitrary
   bulk-input API or treat an emulator's pre-FIFO delivery log as consumption.
4. Assess options only after that baseline: bounded multi-byte FIFO draining,
   staging bytes in a RAM ring for later parsing, and optional split-phase or
   callback-based request/reply interfaces. Compare code/RAM/stack size, added
   delay, IRQ duration and application complexity. No one option is selected.
   Keep stock blocking behavior available for unaware callers; do not silently
   change timing, callback contexts, protocol ownership or existing safeguards.
5. Specify the smallest general extension: packet type/framing, destination
   pointer/capacity, completion/error/lifetime and necessary pacing. Keep legacy
   packets and unaware apps unchanged. Consider one outstanding receive buffer
   before queues/channels; select request IDs only if a real use needs them.
   FIFO size and16-byte TX refills do not impose a16-byte app-message limit.
   During the design workup, consult the VDPlet owner about compatibility with
   its operating model before settling the protocol/API and integration points.
   Cover reply/output ownership, asynchronous module execution, completion versus
   data-transfer lifetime, and the small registration hooks. Record its feedback
   and disposition; consultation does not assign VDPlet implementation or runs.
   Consult FSIM, Wolf and MechAgon about their actual keyboard-channel return
   integrations and concrete caller simplifications. Inspect those sources to
   discover other consumers and broaden consultation where there is a confirmed
   use, starting with VDPlet's existing integration. The6502 bulk-read client is
   one confirmed additional consumer. Distinguish tagged keycode replies from
   held-key map access and keyboard repeat/LED status; do not assume every
   project uses the same path. In the inspected baseline 0x88 is KEYSTATE
   repeat/LED status, not a key-map packet.
   Record source identities, current versus historical paths, useful data sizes,
   pacing/lifetimes and requested simplifications in
   [consultation.md](consultation.md), with decisions in the running notes.
6. Implement the small extension with local changes and worked caller/receiver
   examples once the concrete design is established. Preserve toolchains and
   startup; record assembled code/RAM/stack costs. New bulk-return packets need
   matching MOS/VDP support and opt-in admission. Do not import BDPP wholesale
   or add retries/echo/checksums/session machinery without demonstrated need.
7. Compare a useful consumer against the keyboard-map workaround with matched
   payload integrity, legacy keyboard/reply coexistence, buffer-boundary/rearm
   and CPU/latency controls. State uncertainty plainly. Do not move an unmeasured
   bottleneck or trade lost replies for apparent foreground headroom.

## Existing related evidence

* [IO003 first-key review](../U1-001/consumer-coordination/io003-first-key-review.md):
  the stock-derived RX handler ignores the reader's carry-clear/no-data return,
  a conditional synthetic-zero parser hazard. Its occurrence in the reported
  failure has not been established. Keep this correctness issue separate from
  a speculative performance redesign.
* [IO003 parser continuation](../U1-001/consumer-coordination/io003-keyseq-parser-review.md):
  starting from an unfinished mode reply, intact Return bytes produce exactly
  the saved final parser state without a key dispatch. This conditional source
  calculation does not establish how the earlier reply became incomplete.
* [Actual92 receive-boundary assessment](../U1-001/actual92-first-oe-assessment.md):
  EMOS/UART1 hardware overrun and marker/STOP/IRQ interpretation. This is a
  separately pinned owner composition, not a stock-UART0 baseline result.
* [Foreground wait contract](../U1-001/foreground-wait-contract.md): existing
  opt-in application work on safe event-to-HALT handoff. It does not replace
  stock reply waits or establish a receive-side optimization.

Published fork RC3's CTS spin under DI can delay incoming traffic, but RC3 is
not stock MOS. Likewise, the earlier VDP receive-recovery race concerns the
opposite receiver on the ESP32; it must not be conflated with eZ80 reception.
No safety-first design intent, baseline optimality, speedup or general cure is
claimed by opening this task.

## Ownership, tools and completion criteria

UART coordinates RX-005 and owns MOS source and original synthetic fixtures.
VDPlet owns all VDP/VDPlet changes for this goal. Neither edits game code.
Flexe owns emulator admission/FIFO/IRQ-model evidence; Extender owns EMOS
adaptation and unattended-bench composition. Consultation does not resume or
change any other project's goal. Existing cooperation is context, not authority
to expand other work; owner-reported independent activity stays separate.

Any future official MOS modifications retain ZDS II; original test applications
may use AgonDev. Eirene comparisons retain that upstream project's toolchain
and are labelled separately. Builds/emulator/bench work follow actual resource
checkout and existing custody; manual Console8 flashing remains Brandon's job.
This documentation step performs none of those actions.

Deliver an exact-source receive/wait map, a minimal documented protocol/API,
matching MOS/VDP changes and worked example, and attributable matched validation
demonstrating a useful return path with preserved legacy behavior. Include CPU
gains, latency/correctness limits and code/RAM costs; report if it fails to improve
the workaround. Source reasoning, compile checks, emulation and hardware remain
distinct evidence classes. Public submission is separate from local validation.

## Status at creation

Discussion preserved and task registered. Initial stock-source findings are
recorded above; the systematic investigation and new measurements are pending.

## Scope update — 2026-11-07

Brandon selected the minimal general bidirectional implementation goal and asked
to add the Discord extraction and running notes to this existing task. Both are
now recorded. No firmware implementation, format selection or new run occurred
in this documentation tranche.

## Previous consultation stop — superseded by the selected trial

Brandon intended the consumer-consultation direction as a task addition. UART
started contacting VDPlet before that clarification; Brandon then authorized
finishing this bounded source-review round and stopping for more task scoping
and refinement. Complete and record that round only. Do not proceed from the
consultations into protocol selection, firmware/application implementation,
builds, runs or deployment before that review. MechAgon reports a separate
human-authorized resumption of its goal; this review grants no goal work.
Unreturned requests must stay explicitly pending, not become implied
agreement or a reason to run an indefinite polling loop.

The finite round has now returned all six source reviews: VDPlet, FSIM, Wolf,
MechAgon, 6502 and Rally. Findings and current-versus-retained source distinctions
are in [consultation.md](consultation.md). UART is stopped for Brandon's scoping
review; no protocol/API selection, implementation or execution followed in that
round. Brandon's subsequent selected trial now authorizes the bounded work in
trial-plan.md, ending at a new review gate after passing synthetic tests.
