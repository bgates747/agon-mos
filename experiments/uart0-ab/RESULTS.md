# Initial controlled UART0 A/B results

Console8 update: run0005 passed all30 phases, with zero late feeds and case RX
errors. At identical120-tick paced windows, OTIRX completes31.3% more useful
loop work than default async. Bulk medians: blocking96, default58, grouped56,
chunk56, OTIRX58 raw MOS ticks. This establishes recovered useful CPU work on
this workload, without a bulk throughput gain over default async. See
physical-results.json. Tick frequency and exact CPU cycles were not measured;
receiver checks cover735 bytes per phase rather than every bulk byte. The
emulator race and reported menu keyboard delay remain separate unresolved work.

Executive summary: the paced instruction-model experiment finds about 74% fewer
UART service cycles for the OTIRX/chunk-accounting candidate versus the existing
async kernel. Unpaced throughput does not improve: roughly 108.5k versus 110.7k
UART data bytes/s in that model. These are model estimates, not hardware rates.
The experiment separates CTS grouping, accounting and block-copy effects.

| Variant | Service model cycles over two paced seconds | Saving versus default async | Bulk model data bytes/s |
|---|---:|---:|---:|
| Default scalar async | 11,429,071 | baseline | 110,689 |
| Grouped CTS, scalar/per-byte accounting | 7,943,791 | 30.49% | 110,448 |
| Grouped CTS, scalar/chunk accounting | 3,958,711 | 65.36% | 108,536 |
| Grouped CTS, OTIRX/chunk accounting | 3,000,511 | 73.75% | 108,537 |

The paced workload delivers 735-byte payloads at 60 Hz for two modeled seconds.
The service-cycle fraction falls from about 31% to 8% of the assumed 18.432 MHz
CPU budget, before accounting for the real application's scheduler, SD, graphics,
wait states or other interrupts. The fixed useful-work loop completes about 33%
more iterations. This is not a claim that a whole application runs 74% faster.

The minimal blocking leaf reaches the modeled 115,200 bytes/s ceiling, but it
omits ordinary MOS RST overhead and ties up the CPU polling. It does not refute
the Author's observed real-world one-byte MOS limit. At 1.152 Mbaud, 8N1, 115,200
UART data bytes/s is the ideal ceiling; VDP command headers consume some of
those bytes before application PCM/graphics payload.

Current unpaced numbers suggest investigating refill admission/first-write
latency before claiming maximum throughput benefits. More efficient copying
can recover CPU without filling the line better; the new chunk planner has
its own setup cost. This is a hypothesis requiring profiling or a controlled
fast-path comparison, not a proved cause.

## Qualification and practical limits

The native ZDS kernels pass the inherited 1176 contract cases plus 35 bounded
CTS cut/resume cases per unique kernel. Tests cover both interrupt states,
source lengths/boundaries, ownership, RX, barriers, registers and randomized
queues. All modeled wire bytes match; corruption and stopped-transmitter
controls are rejected. Timing uses the pinned eZ80 model and ideal 160-cycle
UART byte period, with an assumed 8-cycle IRQ acknowledge tax. Host-side test
control is not modeled application execution.

A separate real-VDP Flexe fixture exercises five paths over 30 timed phases,
including native MOS blocking output. Its raw clock/work observations are
protocol evidence, not physical timing. It uses a frozen Golem VDP 2.16.0
snapshot with stock buffer APIs, not the official release image. Native and
cycle-model pacing/harness overhead differ; do not combine their raw counters.

Development runs exposed timing-sensitive stalls, including the blocking
baseline, as well as chunk/OTIRX cases. Bounded four-comparison GP barriers were
restored in untimed receiver verification; kernel dispatch pointer updates are
now atomic under DI. Keep failed development observations separate from final
candidate receipts. A successful instrumented probe is not proof of a fault's
root cause. Native qualification status is recorded in results.json; do not
infer readiness from one earlier passing run or stale receipt.

The native fixture checks every transmitted packet through frontend traces,
plus 735 receiver-stored bytes after each phase and known good/bad receiver
controls. It does not verify every overwritten bulk payload in the receiver.
No physical test, SD deployment or Jukebox modification has occurred. Full
receiver qualification, calibrated hardware throughput, public ABI integration
and real audio/graphics performance remain subsequent work.

The final candidate completes two full campaigns in each engine: 120 phases
in total, each campaign reversing order in its middle pass. Initial candidate
runs take 44.334s (JIT) and 69.287s (interpreter); repeat receipts and exact image
pins are in results.json. These passes bound the current protocol claim; they
do not prove the root cause of earlier timing-sensitive development stalls.
Human review is pending. No hardware campaign is announced as ready.

## Human review failure — 2026-10-14

The current image stalled at repeat 2, mode 1, phase 0 (scalar async bulk).
The Author confirmed the stall and closed the emulator. The four successful
headless campaigns remain historical observations; native readiness is revoked.
Closed-run counters report no TX drops, RX overruns or backend execution faults.
The cause remains unknown. Evidence: build/uart0-ab/human-stall-001.tar.gz.
No hardware deployment is authorized by these results.
