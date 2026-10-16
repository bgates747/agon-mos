# Next tranche: UART0 A/B streaming and application CPU headroom

Executive summary: we need to establish how much useful CPU time background
sending gives back, whether bulk transfers become faster, and whether every
byte still arrives correctly. Earlier Console8 results are promising for CPU
headroom, but show no bulk-speed gain from batching over our experimental
one-byte-at-a-time background sender.

First finish the controlled comparisons and reliability checks. Then test a
workload like Jukebox's regularly scheduled audio uploads, followed by Jukebox
itself, to see whether the saved CPU time improves graphics without disrupting
sound. The VDP receive fault now has a hardware-confirmed repair under controlled
timing. Requalify the original A/B workload against that repair before relying
on emulator passes for release approval. TODO.md is the sole actionable checklist.

## Status and qualification gate

Console8 replay on 2026-10-16 passes all 90 phases across R0026/R0027/R0028,
followed by candidate compatibility PASS R0029 and 49,152 final-buffer bytes
verified. OTIRX provides 31.87% more median paced useful work than experimental
per-byte async; their median bulk time remains equal. These tests used the
unbranded API1.1 MOS and repaired VDP candidate. The branding-only rebuild does
not invalidate sender results; it has separate native/emulator evidence and
has not been physically tested. No full rerun is requested for branding alone.
The Author installed another project's VDP afterward; leave that firmware alone.
Remaining AB-006 work is emulator regression/coordination and renewed human
qualification. Full A/B bulk integrity and supported ABI1.2 tests remain separate.

Stock MOS is the approved baseline. Experimental per-byte async, grouped
scalar, chunk-accounted scalar and OTIRX are development candidates, not
approved production behavior. Mode 0 measures stock-style blocking output
through the unchanged legacy path in the candidate fork; it is not a separate
measurement of a reflashed upstream stock ROM.

The Author authorized an exploratory Console8 comparison on 2026-10-14 despite
the emulator fault. Returned R0005 passes all 30 phases with no late feeds or
case RX errors. OTIRX yields 31.3% more median paced useful work than experimental
per-byte async, with equal bulk drain ticks. This does not verify every bulk
byte, measure exact CPU cycles or approve a production feature.

The human Flexe stall at `A/B repeat 2 mode 1 phase 0` led to a captured VDP
cross-core receive-buffer recovery race: the ISR disables RX after reader
recovery clears its full flag. See [failure evidence](uart0-ab-stall.md).
The MOS agent's private VDP correction now passes the matched Console8 pair:
R0012 captures/rescues the baseline fault, R0014 recovers every byte without
rescue, and R0017 passes candidate compatibility. Stock restoration is confirmed.
AB-006 retains regression of the original A/B workload, Flexe coordination and
renewed both-engine/human qualification. See uart0-receiver-sync-fix.md.
Historical failed attempts and runtime identities remain archived in the workspace.

## Remaining route to release

First complete the supported experimental driver/session API under BT-003,
including per-byte fallback, ownership, CTS wakeups, bounded IRQ work and safe
exit. Pair this with AB-003 and BT-005/BT-006 receiver checks covering every
bulk byte, sustained full duplex, queue/descriptor boundaries and repeated CTS
stop/resume. This is the next implementation tranche before app integration.

Then complete repeated stock-versus-experimental performance comparisons under
AB-001/AB-002 and BT-004, with independent timing, useful-work measurements,
variation and explicit baseline identities. AB-004 adds the source-derived
paced audio fixture; AB-007 separately scopes actual skins-branch Jukebox
integration and audio/graphics measurements with the application owner.

UI-001's keyboard fix is confirmed on hardware. AB-006 retains original-workload
regression and emulator acceptance after the physical receiver repair.
BT-007 assembles the repeatable tests, supported combinations, compatibility
limits and safety rationale into a release candidate for explicit Author
approval. Neither successful hardware tests nor permission to commit constitutes
approval to promote or release an experimental transport. TODO.md owns all
unfinished task checkboxes and immutable identifiers.

## Controlled comparisons and application workload

The comparison includes blocking MOS output, experimental per-byte async output,
grouped scalar output and bounded OTIRX refills. Use identical valid bulk VDP
commands, payload sizes, baud rate and receiver work. Alternate run order and
repeat. Measure from comparable start conditions through wire drain; enqueue
acceptance and VDP execution completion are distinct events. Report useful work
completed concurrently and service cost/latency alongside fixed-payload time.
If both methods saturate the UART, equal wire time can coexist with improved
CPU headroom. Keep the conservative baseline and isolate experimental options.

Verify count/CRC and receiver errors with diagnostic VDP separately from stock
VDP performance. Use a stock-supported bulk payload with known parser semantics;
arbitrary display bytes are not a controlled workload. Preserve all source
buffers until their documented release and confirm drain/receiver completion
as required. Emulator results precede physical tests but do not prove timing.

The source-derived workload is 735 unsigned 8-bit mono PCM bytes per 60 Hz tick
for a 44,100 Hz stream, uploaded in an 8-byte VDP buffer-write command header
plus payload. Alternate the two one-second VDP audio buffers and include their
play/clear commands. First feed from RAM to isolate UART cost, then introduce
SD reads as a separate jitter case. Queue bounded fixed graphics work through
the same producer. The synthetic fixture uses a short due-work timer ISR and
an interruptible foreground loop, not publication from the audio ISR.

Compare the inspected Jukebox blocking/long-ISR scheduling as a reference,
then adapted foreground scalar and OTIRX variants with an identical scheduler
and packet pool. This separates scheduling gains from refill gains. Record
queue/feed backlog, lateness, completed useful work, stable-source lifetimes
and full-sample readiness. A late 60 Hz feed is not by itself an audible gap
because VDP samples are buffered in one-second alternation; report underruns
only through specified direct observations. Avoid counting enqueue speed as
wire throughput, and avoid large graphics transactions monopolizing the FIFO
queue ahead of audio. Actual Jukebox changes are a separate coordinated scope.

Deliver one numbered, menu-driven suite for headless Flexe and manual Console8
qualification, with run-all, repeated A/B cases, progress breadcrumbs, sequential
reports and staged firmware/readme in the same stable SD directory. Retain
stock restoration and receiver safety. No Jukebox changes are authorized by
this inspection; app integration must be scoped after the source review.
