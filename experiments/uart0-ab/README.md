# Controlled UART0 streaming A/B experiments

Executive summary: compare CPU cost for paced output and maximum unpaced data
rate using native ZDS II kernels. The first cycle-model campaign demonstrates
substantial CPU savings from bounded OTIRX and per-chunk accounting, but no bulk
throughput gain over the current async kernel. Actual VDP firmware qualification
is separate; no silicon cycle or physical throughput measurement is claimed.
Production MOS, its public API, shared emulator runtime and SD card are unchanged.

## Variants and workload

The generated isolated kernels derive from pinned production uart0_tx.inc:

| Variant | CTS checks | Copy/accounting |
|---|---|---|
| blocking | per byte | model uses minimal blocking leaf; native uses MOS RST18 |
| default | per byte | unchanged production scalar core |
| grouped | once at refill start | original scalar copying/per-byte descriptor updates |
| chunk | before each bounded descriptor chunk | scalar loop, progress updated per chunk |
| otirx | before each bounded descriptor chunk | native OTIRX, progress updated per chunk |

Each service still requires THRE and permits at most 16 writes. Block counts
are positive and clamped to source span and remaining refill allowance.
No public ABI 1.2 setter/getter is implemented; compiled candidate variants are
selected only inside the experiment. Do not mistake this for shipping batching.

The instruction-model bulk case publishes three 16384-byte transactions containing
valid buffer-clear/write commands and known data. Paced output sends 743-byte
buffer-write packets at 60 Hz (735-byte PCM-shaped payload), 120 feeds over 2 modeled
seconds. Cases run three times, reversing variant order on the middle pass.
CPU service cycles include API calls and complete modeled UART IRQ service,
including the explicitly assumed 8-cycle IRQ acknowledge tax. Useful work is an
actual native two-instruction INC/JR loop; host dispatch logic is not itself
compiled into eZ80 code. The model framework's memory/fetch timing is not a
silicon calibration. Do not substitute its raw cycles for measured hardware.

`prepare.rb` produces isolated source snapshots; it never patches src/.
`build.sh` builds with ZDS II 5.3.5 under Wine on Oryx, runs the pinned instruction
model, all-byte stream comparisons, inherited queue/lifetime/width/register/RX/
barrier/randomized cases and 35 CTS cut/resume cases per kernel. Missing progress
and deliberate byte corruption must fail. `analyze.rb` reports cycle/rate data
in build/uart0-ab/analysis.json. These are deterministic model results; three
identical repeats do not create statistical evidence of physical repeatability.

## Native real-VDP fixture

`prepare_native.rb` generates four separately named RAM kernels linked into one
MOS-loadable test.bin. It temporarily installs exactly one private UART owner
per test and restores the original vector/IER before ordinary output or SD I/O.
Its failure path retains app memory until reset. This is an isolated driver
experiment, not an application adoption of the production async API.

It runs 30 phases: five modes × bulk/paced × three passes, reversed mode order
on the middle pass. Bulk sends three 16384-byte transactions; paced sends 60
735-byte payloads, with buffer clear/write framing, on two-MOS-tick boundaries.
The native paced packet is 749 bytes (extra 6-byte clear) versus 743 in the cycle
model. This keeps VDP storage bounded, but is not Jukebox's complete playback
schedule. Each paced phase runs 120 raw MOS ticks: approximately 60 Hz feeding only
where the clock actually measures 120 ticks/s. Report raw ticks; no RTC is used.
Native useful work is a fixed RAM-counter loop. Polling, loop cost and native
scheduling differ from the cycle harness; do not merge their measurements.

Receiver byte-compare checks use four-command groups with GP barriers outside
timed phases, following the established receiver-test convention. A known
bad-byte probe must return 1 and a matching probe 0 before testing. Current native
checks verify 735 stored bytes after each phase, not every bulk payload byte or
every overwritten packet. Frontend transcript checks verify all 945 transmitted
packets exactly; the cycle model checks all transmitted bytes. Full physical
receiver integrity under changed CTS behavior remains a separate qualification.

Headless profiles reuse the frozen frontend/adapter and Golem 2.16.0 VDP snapshot
with stock buffer-command APIs; this is not the official release binary and
not a physical throughput reference. Host scheduling and virtual clocks can
vary. Native phase ticks must not be converted to physical bytes/s using an
assumed 120 Hz calibration. Both-engine protocol qualification is required before
hardware readiness; human review precedes commit of this experiment.

## Reproduction

Run cycle-model campaign with `bash experiments/uart0-ab/build.sh`.
Then run `ruby experiments/uart0-ab/prepare_native.rb`, stage its native/ sources
and this experiment directory on Oryx, and use:

```sh
bash experiments/uart0-ab/native_remote.sh
.venv/bin/python -B experiments/uart0-ab/profile.py --auto
.venv/bin/python -B experiments/uart0-ab/qualify.py jit
.venv/bin/python -B experiments/uart0-ab/profile.py --auto
.venv/bin/python -B experiments/uart0-ab/qualify.py interp
```

`profile.py` without --auto prepares a separate stopped human profile. It never
launches a graphical instance. This experiment is not yet deployed to SD or
integrated into the existing menu; preserve sequential reporting and the stable
hardware path when qualified packaging is added. No Jukebox changes are made.

## AB-006 forensic runs

Native readiness is revoked. See [the captured receiver failure](../../docs/uart0-ab-stall.md).
The new tools use only the dedicated auto profile; the human profile and SD
remain untouched. Run on Oryx with the project Python, after preparing --auto:

```sh
.venv/bin/python -B experiments/uart0-ab/debug_stall.py jit 4
xvfb-run -a env UART_AB_VIDEO=x11 .venv/bin/python -B experiments/uart0-ab/supervise.py interp 4 coarse
```

The supervisor preserves attempts under build/uart0-ab/host-stalls, capturing
through host GDB only after 15 seconds without TX progress. It checks child
process-group/executable identity and stops only its owned emulator. sudo is
used solely for attaching GDB to that child and stopping its own GDB watcher.
The capture decoder pins this exact frontend/adapter and firmware ELF layout.
A returned observational run is not a qualification receipt; shutdown status,
packet integrity and the unresolved human failure still matter.

UART_AB_CAPTURE_RETURN=1 validates the capture path on a returned control.
UART_AB_WATCH_RX=1 adds hardware watchpoints for the VDP driver's recovery flag
and UART2 INT_ENA, preserving a bounded write history; this changes execution
timing. UART_AB_RECOVER_RX=1 permits one diagnostic INT_ENA MMIO write only
after a captured receive-wakeup failure, then records whether TX resumes.
That intervention permanently disqualifies the run as a benchmark or passing
qualification. These options are not part of the normal fixture or launchers.
