# UART0 stock-VDP pause and full-duplex fixture

Executive summary: this fixture uses the accepted API 1.1 MOS unchanged and
stock VDP commands to pause receiver parsing, send 8,192 bytes and collect
32 ordered GP replies per case. It verifies every stored byte using the
benchmark's qualified comparison protocol. Physical CTS headroom still needs
an independently grounded capture. The Author passed human emulator review
on 2026-10-13, including all cases, return to MOS and keyboard DIR operation.
The subsequent Console8 run passed all four cases; the returned report verifies
all 128 replies and 32,768 receiver bytes with zero case RX errors. Pre-trial
sticky RX flags were 0x98 and were retained separately in baseline.dat.
See `physical-results.json`; electrical CTS margin remains unmeasured.

`bash experiments/uart0-stress/build.sh` generates commands locally in Ruby,
assembles/links with native ZDS II under Wine on Oryx and runs both pinned
headless Flexe engines. It also runs corrupted-sequence and corrupted-payload
controls in a separate disposable profile. No other project's emulator or
profile is changed. The exact accepted MOS hash and MOS-owned runtime pins
are checked before building; no AgonDev route is used.

The four transactions prefix 0, 1, 4 or 8 `VDU 23,0,&C3` commands. In the
selected single-buffered mode 0, stock VDP waits for VSYNC. Each transaction
then appends 32 blocks of 256 bytes to scratch buffer 0x6af0 and emits distinct
GP tokens 16..47 between blocks. The app polls the normal MOS GP sysvar,
requires every token in order and requires a reply followed by BUSY from
`tx_poll_drain`. It never takes over UART registers, interrupts, callbacks or
the timer. The GP sysvar is a last-value latch, so missed tokens fail rather
than being silently counted. This is a bounded, moderate reply workload;
it is not a maximum RX-rate or keyboard/mouse saturation qualification.

All bytes remain borrowed until RELEASED and queue/TEMT drain. The source
length is checked, the descriptor reaped, then the session closed. A missing
reply after safe drain has a 2,400-raw-tick diagnostic wait limit; raw ticks
are uncalibrated and that limit is not a transmit-abandonment timeout. A
permanent CTS blockage retains source memory and needs explicit reset.
Software errors print FAIL, save a stage-marked report and stop for reset.

Untimed verification reuses `../uart0-bench/packets.rb`: mismatch/good-byte
preflight controls, buffer-to-buffer comparison of all 8,192 receiver bytes,
four comparisons per GP execution barrier. Scratch IDs 0x6af0..0x6af4 match
the prior benchmark. Diagnostics are sampled/cleared only with the session
closed; baseline flags are saved separately and each case requires zero fresh
RX flags both after its transaction and after verification. No FIFO is reset.
The app changes display mode to 0 and does not restore the previous mode.

The headless VDP is the already pinned Golem-built snapshot reporting 2.16.0;
it is not the exact official release binary packaged for the Console8.
Only stock commands are used. Headless timing is not hardware timing.

On Oryx, the prepared human-review profile is stopped. Run locally:

```bash
cd ~/Agon/mystuff/agon-mos/.emulator/uart0-stress
./fab-agon-emulator --precise-interrupts
```

Expect the initial clear/title and two-minute expectation, setup PASS,
four cases with their pause counts, ordered replies and verification quarters,
then `UART0 STRESS FIXTURE PASS`, `UART0 STRESS RETURN PASS`, and a usable MOS
prompt. Type `DIR` to check keyboard response. Close the emulator afterwards.
The canonical human review gate is satisfied for this fixture.
No graphical emulator is launched by the agent.

`readme.txt` is the hardware runbook. `capture.txt` records the manufacturer
schematic findings and deliberately leaves practical CTS probe access unresolved.
`analyze.rb stress.dat expected.json` validates a successful report offline.
The existing benchmark `analyze.rb trace capture.csv` remains the capture
analyzer; packages name that copy `capture-analyze.rb`.

Report format: 12-byte header `UART0ST1`, version 1, stage, count 4, RX error;
then four 16-byte records: pause count, expected replies, observed replies,
replies before drain, accepted u24, raw ticks u24, RX errors, modem deltas,
sequence error (1 wrong/missing sequence, 2 reply wait expired), last token,
two reserved zeros. Stage 1 is send/reply, 2 receiver verification, 0 success.
On success receiver checks cover 32,768 bytes. Baseline is [RX, modem, zero].
Modem deltas alone neither prove nor timestamp a CTS blocked interval.

The accepted package was staged on the Author's removable SD at
`/test/mos-uart0`; see `deployment.json` for its exact identity and
manifest hash. `deploy.py` reuses the benchmark's mount/removable-device,
checksum, collision and archive guards with this fixed destination and
requires a human-reviewed package. Existing benchmark deployment defaults
are unchanged. No firmware flashing is performed by deployment tooling.
