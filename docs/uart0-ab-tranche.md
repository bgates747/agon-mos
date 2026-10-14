# Next tranche: UART0 A/B streaming and application CPU headroom

Executive summary: close Tom Morton's original OTIRX proposal with paired
sustained-stream measurements and a paced AgonJukebox-shaped workload. Compare
correct bytes delivered and useful CPU work recovered, not just enqueue speed.
The [skins audit](uart0-jukebox-skins-audit.md) establishes 735-byte uploads at
60 Hz for 44.1 kHz PCM and a long blocking timer handler; the paced fixture must
model a short scheduler ISR with foreground packet production instead.
This document describes the tranche; TODO.md is the sole actionable checklist.

## Current gate: intermittent native fixture stall

Human review failed at `A/B repeat 2 mode 1 phase 0`: the current scalar async
kernel's bulk case. The Author confirmed the stall and closed Flexe. Four prior
successful headless campaigns and a subsequent successful debugger run do not
resolve this intermittent failure. Native readiness is revoked; do not stage
the A/B fixture for a Console8 run yet. Earlier accepted Console8 results and
the instruction-model cycle observations retain their original scope.

AB-006 owns the immediate investigation. Reproduce in a separate MOS-owned
emulator profile and capture a stalled CPU's PC, IFF state, UART interrupt
enable/status, queue head and descriptor progress, along with the last phase
and TX transcript. Distinguish a fixture, driver or emulator failure using the
captured state; do not infer a cause from another passing run. Preserve failed
attempts and runtime/source identities. The closed human-run evidence is
archived on Pi and Oryx at `build/uart0-ab/human-stall-001.tar.gz`; its counters
record no TX drops, RX overruns or backend execution fault, without explaining
the stall.

Completion requires an evidence-backed cause, a targeted correction and a
regression check that exercises the identified failure mechanism. Then repeat
the full native campaign in both frozen Flexe engines and obtain human review
before hardware staging under AB-005. Keep production firmware and the SD
unchanged during investigation. No new hardware run is currently requested.

The comparison includes blocking MOS output, current per-byte async output,
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

Compare current Jukebox-like blocking/long-ISR scheduling as a reference,
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
