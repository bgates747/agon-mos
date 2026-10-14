# AgonJukebox skins audit for UART0 A/B testing

Executive summary: Jukebox is an appropriate motivating workload, but its timer
currently performs blocking audio and UI work with interrupts disabled. Async
MOS output cannot recover foreground CPU time if used inside that existing
long handler. Shorten the application ISR and give foreground code ownership
of preparing/publishing whole packets, while MOS remains the sole transmitter.
Compare scheduling changes separately from the scalar-versus-OTIRX gain.

## Reference identity and inspection boundary

Inspected local `/Agon/mystuff/AgonJukebox`, branch skins at 157cfcd, and then
fetched the actual GitHub skins tip into a MOS-owned bare reference under
`build/jukebox-skins-reference.git`. Remote tip at inspection:
`f3cd5925a14778f8c5ed4666bac10b2e109731b3`.
The neighboring checkout and its uncommitted agent instructions/artwork were
left unchanged; no checkout, pull, build, emulator run or app modification.
Reference extraction is in `build/jukebox-skins-reference/src/asm`.

## Observed source behavior

| Finding | Pinned source |
|---|---|
| Timer 1 reload targets 60 interrupts/s, not 44,100 | [timer_jukebox.inc](https://github.com/bgates747/AgonJukebox/blob/f3cd5925a14778f8c5ed4666bac10b2e109731b3/src/asm/timer_jukebox.inc#L1) |
| ISR holds DI, saves both register banks/IX/IY, calls `ps_read_sample` then `ui_flush`, and enables only at exit | [handler](https://github.com/bgates747/AgonJukebox/blob/f3cd5925a14778f8c5ed4666bac10b2e109731b3/src/asm/timer_jukebox.inc#L53) |
| Unsigned 8-bit mono PCM, base rate/60 plus distributed remainder, read through FatFS inside `ps_read_sample` | [play.inc](https://github.com/bgates747/AgonJukebox/blob/f3cd5925a14778f8c5ed4666bac10b2e109731b3/src/asm/play.inc#L145) |
| Upload uses a mutable 8-byte buffer-write header followed by a separate blocking RST18 payload call | [vdu_load_buffer](https://github.com/bgates747/AgonJukebox/blob/f3cd5925a14778f8c5ed4666bac10b2e109731b3/src/asm/vdu.inc#L230) |
| Two VDP data buffers 0x3002/0x3003 accumulate one second; command buffers 0x3000/0x3001 consolidate/create/play and channels 0/1 alternate | [play commands](https://github.com/bgates747/AgonJukebox/blob/f3cd5925a14778f8c5ed4666bac10b2e109731b3/src/asm/play.inc#L448) |
| Foreground flushes UI then blocks in `mos_getkey`; commands dispatch under DI | [input.inc](https://github.com/bgates747/AgonJukebox/blob/f3cd5925a14778f8c5ed4666bac10b2e109731b3/src/asm/input.inc#L1) |
| `ui_send`/`ui_flush` preserve DI and drawing is reachable from the audio ISR | [layout.inc](https://github.com/bgates747/AgonJukebox/blob/f3cd5925a14778f8c5ed4666bac10b2e109731b3/src/asm/layout.inc#L60) |
| RAM staging uses a shared `ps_wav_data` address 09034Ch | [files.inc](https://github.com/bgates747/AgonJukebox/blob/f3cd5925a14778f8c5ed4666bac10b2e109731b3/src/asm/files.inc#L60) |

The WAV reference document describes a short event-posting ISR, foreground
rendering and keyboard polling, but the inspected current assembly above still
calls audio/UI in the ISR and waits in `mos_getkey`. Treat executable source as
the basis of this plan; do not assume the documented restructuring is present.
EOF/playlist paths also call close/transition routines from this ISR context.
These require review in any future application adaptation, not merely the
ordinary audio feed loop. This audit reports the mismatch without modifying
the other project's maintained records.

## Workload arithmetic, not measured performance

At 44,100 samples/s, unsigned 8-bit mono is 44,100 payload bytes/s. At 60 feed ticks/s,
that is 735 payload bytes per tick, with no quotient remainder at this rate.
The buffer-upload header is 8 bytes, so ordinary feed traffic is 743 ×60 =44,580
bytes/s, before play/clear/UI commands. At nominal 1.152 Mbaud, 8N1, the ideal
capacity is 115,200 bytes/s: audio feed alone uses about 38.7% of the wire budget.
Each 743-byte transaction takes at least 6.45 ms on that wire, before software gaps,
CTS delays, SD reads and UI work. The feed interval is about 16.67 ms. This is a
line-time calculation, not an observed ISR duration or a measured CPU budget.

VDP alternation gives one-second sample buffering, so a late individual 60 Hz
feed is not automatically an audible underrun. Track both feed backlog/lateness
and whether a complete next sample is ready for its playback handoff. Send/drain
completion does not independently prove the VDP audio engine played without a
gap. Specify observation/instrumentation for actual underrun claims.

Current audio uploads call MOS rather than writing UART THR directly; the
integration problem is the long interrupt-masked producer and its mutable
source lifetime, not evidence of an existing second hardware UART consumer.

## Revised architecture hypothesis

The timer ISR should acknowledge its timer, record bounded due work and return.
No SD reads, rendering, MOS async publication or UART writes in that handler.
The existing MOS async ABI is foreground-only; its UART-ISR guard does not
necessarily detect arbitrary application timer context. Do not infer permission
from an API call appearing to work inside the timer ISR.

An interruptible foreground loop should service due audio, prepare immutable
whole VDP packets, publish through MOS, reap released buffers, perform bounded
UI work and poll keyboard input. File/track transitions also belong there.
Use short atomic handoffs for counters/state, not DI around an entire SD read
or upload. Do not enable nested interrupts inside the old handler as a shortcut.
Establish bounded backlog/overrun behavior; a boolean due flag loses multiplicity,
and even a software counter cannot recover hardware ticks coalesced while
interrupts were masked. Measure long masked intervals independently where possible.

A stable packet should contain its 8-byte header plus 735-byte payload (743 bytes
at 44.1 kHz), rather than borrowing a mutable shared header or allowing graphics
between a header and its payload. Use preallocated RAM packet slots retained
until source RELEASED; after release the source may be reused, but play/clear
commands still require correct wire order. Reserve capacity before reading into
or advancing ownership of a slot. On BUSY retain/retry the packet; never silently
drop audio, overwrite borrowed data or advance the accepted stream as if sent.

The existing three-descriptor queue can carry multiple packets, but is not an
unbounded audio buffer or a priority scheduler. Bound graphics transaction size
and queue occupancy so a large UI transfer cannot block the next audio handoff.
All producers use one ordered MOS path. Ordinary blocking UI calls impose drain
barriers and may erase overlap, so adapted graphics must join the ordered packet
producer. Keep headers/payload/play/clear ordering intact. Queue BUSY policy,
SD read-ahead and playout headroom need explicit limits before actual integration.

## Revised comparison and scope

Retain the bulk RAM benchmark to isolate the driver. For paced testing use a
RAM-fed 735-byte/60 Hz workload first, then add SD reads separately to expose I/O
jitter. Include play/clear traffic and a fixed graphics workload. Non-divisible
sample rates can later exercise the existing quotient/remainder schedule.

Measure the current blocking/ISR pattern as the application reference, then
compare adapted foreground scalar async against adapted foreground OTIRX async
using the same scheduler, packet pool, graphics work and payload. Grouped scalar
is an additional driver control. Comparing old ISR blocking directly to a new
foreground OTIRX implementation alone would conflate two different gains.

Required counters include completed useful work/graphics operations, accepted
and transmitted bytes, queue high-water/BUSY, pending feed high-water and deadline
lateness, release lifetime violations, full-sample readiness and UART integrity.
Separate nominal sample rate from timer cadence in every report. Report audible
or receiver underruns only when directly observed; do not relabel backlog as an
underrun. Keep hot-path logging out of the timed wire workload, with breadcrumbs
between phases or included equally in every measured case.

This turn authorizes inspection and planning only. The next implementation is a
MOS-owned synthetic fixture plus the isolated OTIRX candidate. Actual Jukebox
integration needs a separately scoped application change coordinated with its
owner; no cross-project messages, app changes or private VDP feature are implied.
