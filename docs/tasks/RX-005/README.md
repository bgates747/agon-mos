# RX-005 — Minimal compatible bidirectional MOS/VDP transport

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

UART owns MOS source investigation and any separately selected diagnostic VDP
work. Flexe owns emulator admission/FIFO/IRQ-model evidence; Extender owns EMOS
adaptation and unattended-bench composition. MechAgon's paused GOAL remains
paused. Existing cooperation is context, not authority to resume other work.

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
