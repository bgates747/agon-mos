# Actual132 — complete synthetic hardware pass

Corrected kit6d467b51, unchanged app0208015a/18376B, exact receiving EMOS171c
and VDP7d09 passed the full finite Olimex test. Fresh grant10:56:08.319718UTC
November8; original Extender installer77380 exited0/all phases0/all groups joined.
Both complete affected image readbacks, bootstrap, actual CLI/state/files/input
and stopped handoff passed. No firmware/benchmark change was required.

One original foreground consumer72988/PID1923754 staged and independently
verified all four files, then sent one corrected EXEC in freshr02. It completed
in58.0096s, exited0 and all owned processes joined. [Summary](summary.json),
[stopped receipt](physical-r04-stopped.json), [raw log](R0001.log).

- All ten exact sizes4,8,16,32,64,128,256,1024,4096,8092 passed both upload
  methods and both receive methods, including byte/count/callback/guard checks.
- All36 ordered matched benchmark cells passed the strict analyzer.
- The batch continued normally: WITNESS32B/state3, next2, terminal listener
  online, then positive EXIT/offline and consumer return. No reset/retry.

This confirms the batch-only radix correction resolves129's host completion
failure. Original129's results and absent witness remain separately recorded;
neither attempt is relabeled as the other. No raw UART error-counter, wire
trace, sound/optical, CPU-percentage or full-game acceptance is claimed.

Equal-payload no-work aggregate completion ratios are5.65x/6.49x/6.98x faster
for128/256/1024B logical pulls. These coarse public MOS counts include request,
adapter/IRQ and byte validation costs; upload/setup/logging are outside. Legacy
uses8 payload bytes per tagged0x81 reply; counted uses up to512. The1024B case
uses two512B frames, not one1024B wire frame. Work-enabled counters are retained
without a CPU-recovery claim. [All cells and comparisons](analysis.json).

Actual joined custody returned to Extender by durable mail/immediate accepted
steering11:05:45UTC. UART target-stopped. Necessary exact incoming native85f9
FIRST/readback then incominga25f/readback and full fresh state/resource
restoration/release remain pending in this snapshot. The synthetic pass does
not itself certify restoration or grant consumer bench access. Selected small
Rally/6502 helper trials follow normal handback and their own preparation/FIFO.

[Manifest](manifest.json) records copied evidence. No further synthetic sweep,
fault matrix, extra feature or performance optimization is required.
