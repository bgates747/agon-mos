# Console8 ZDI diagnosis with four confirmed probes — 2026-10-29

The replaced connector leads did not restore communication. Simultaneous,
correctly identified probes show the requested DATA levels at WROOM but different
levels at the Console8 connector during some transmitted bits. Neither tested
clock mode produces a valid identity. MOS recovery remains incomplete.

This is a new record. Earlier documents, probe attributions and raw captures
remain unchanged; see [the discrepancy audit](audits/sniffer-color-audit-2026-10-29.md).

## Physical arrangement and interpretation limits

| Probe | Location | Signal |
| --- | --- | --- |
| GREEN / D0 | Console8 connector, after series resistor | GREEN CLOCK |
| BLUE / D2 | Console8 connector, after series resistor | BLUE DATA |
| RED / D5 | WROOM side, before series resistor | GREEN CLOCK |
| BROWN / D7 | WROOM side, before series resistor | BLUE DATA |

The Author confirmed this final arrangement and replaced the connector leads.
Both signal paths retain their reported 33 Ω series resistors near WROOM;
common ground remains connected. No physical changes or manual resets were
requested during the following unattended tests.

The analyzer measures threshold crossings at its probe attachments, not actual
analog voltage/current or the eZ80 package's input thresholds. “Arriving wrong”
below means conflicting digital observations at the Console8 connector. It does
not establish a defective resistor, cable, driver, eZ80 or ground connection.

## Completed tests

DG-001 [x] New-lead baseline: five slow identity reads with all four probes.

Evidence: `build/c8-zdi/c8-four-probe-baseline-01/` on Pi and Oryx.
Raw `FP-001.bin`: 96,000,000 uint8 samples at 24 MHz, bit0=D0 through bit7=D7.
SHA256 `346c3eaee0045b289bd2b20da8908a927f372248f413b5fc0faa958e5a471e23`.

- IDs: 0/5 valid. Replies: `E0 07 0E 1C`, then four `07 0E 1C 38`.
- Each clock end records five 45-clock transactions: 225 rises, 225 falls.
  Corresponding sampled crossings differ by at most one 41.7 ns sample.
- All 65 local DATA input/latch snapshots match the requested bit, with both
  outputs enabled during those snapshots.
- BROWN/WROOM DATA matches 65/65 requested levels at −5, −1, +1 and +5 µs
  from its clock rise. Thirteen exact-rise discrepancies are one-sample
  disturbances, not held wrong levels.
- BLUE/Console8 DATA disagrees on 25/65 transmitted bits throughout each inspected
  ±5 µs window: 15 intended LOWs read HIGH; 10 intended HIGHs read LOW.
- Reply bytes sampled at both ends match the CPU's returned bytes at all five
  tested offsets. Independent frame association uses the 13 transmitted-bit
  positions within each 45-clock transaction; it does not confuse read clocks
  with the GPIO transmit snapshot index.

Reproducible independent review:
`independent_four_probe_review.py` / `independent-four-probe-review.json` in that
run. The 10 µs window is an observation interval, not a quoted timing tolerance.
The wrong level spans the clock rise where the outgoing bit should be accepted.

DG-002 [x] Paired clock-mode comparison: push-pull / open-drain / push-pull /
open-drain, five slow reads per phase; DATA driver remains unchanged.

Evidence: `build/c8-zdi/c8-four-probe-clock-compare-01/` on both hosts.

| Phase | GREEN clock mode | Valid IDs | Console8 TX correct at +5 µs | Wrong throughout ±5 µs | Extra sampled clock rises |
| --- | --- | --- | --- | --- | --- |
| FP-001 | Push-pull | 0/5 | 39/65 | 26 | 0 |
| FP-002 | Open-drain | 0/5 | 58/65 | 7 | 5 |
| FP-003 | Push-pull | 0/5 | 49/65 | 16 | 0 |
| FP-004 | Open-drain | 0/5 | 50/65 | 14 | 3 |

Open-drain has fewer bad settled outgoing bits in this sequence but adds
one-sample CLOCK HIGH pulses near intended rises. Some replies change by/after
the clock rise. All 260 local GPIO input/latch snapshots match the requested
bits. Both ends' replies at −5/−1 µs agree with the CPU in all 20 trials.
The open-drain analysis retains raw edge counts and explicitly groups nearby
rise chatter only for nominal transaction comparison; it does not hide it.
No mode establishes reliable communication or a proven repair.

Reproducible reports: `independent_clock_mode_review.py`,
`independent-clock-mode-review.json`, `independent-clock-mode-summary.json`.

DG-003 [x] Bounded line control with four probes: abort before DATA pulses.

Evidence: `build/c8-zdi/c8-four-probe-linecontrol-01/` on both hosts.
The existing v7 `C` command holds GREEN LOW and checks that released BLUE is HIGH
before permitting up to five short open-drain LOW pulses. BLUE was already LOW,
so it emitted zero pulses. This is a guarded abort, not a successful path test.
Its entry/exit clock edges may advance an existing target transaction; no
intentional START, target reset, MOS erase or programming was requested.
Raw `FP-001.bin` SHA256:
`be1d2e07a29294230109208b6529c5fb31476001bd6bcbc44c2525d70bf7b49c`.

## Consequences for recovery

DG-004 [x] Record the Author's suggestion to try flashing despite bad IDs.

The Author proposed attempting a flash because the outgoing bits were reported
correct. Clarification: they are correct at WROOM, but the connector-side
transmit mismatch remains. A successful RAM upload and complete readback of the
flash-programming agent is a necessary gate before allowing it to erase MOS.
No Console8 flash attempt was made during this diagnosis. The prepared stock
MOS recovery programmer remains off-device; its normal identity gates are not
silently removed.

A healthy 33 Ω resistor feeding only a high-impedance input does not by itself
explain sustained opposite logic observations. Possible explanations include an
opposing active driver, an unexpected connection/load, or a measurement/probe
reference/threshold problem. A hypothetical measured 1 V drop across 33 Ω would
require about 30 mA; **no such analog voltage or current was measured here**.
Do not promote that example or the driver-contention hypothesis into a finding.

## Next controlled physical comparison

DG-005 [ ] If the Author changes resistors, compare GREEN CLOCK 33 Ω → 68 Ω →
100 Ω, with BLUE DATA kept at 33 Ω, all leads/probes/grounds fixed. Power off
both boards for the physical changes. Run the same five-read paired-end capture
for each actual value, record it explicitly, and require correct full identities
before progressing to verified RAM upload and stock MOS programming.

This value sweep is an engineering experiment, not a Zilog recommendation for
these exact values or an established fix. Increasing source resistance can damp
fast edges; decreasing resistance can reduce voltage drop but increase opposing
output current. Increased resistance may also worsen rise time/loaded voltage
drop. Neither direction is assumed beneficial without evidence.

[Zilog TN0035](https://www.zilog.com/docs/ez80acclaim/appnotes/tn0035.pdf), page 2,
shows 33 Ω source termination at the debug tool and mentions optional target-side
DATA termination because that line is bidirectional. Page 3 warns that ringing
through intermediate voltage levels can be interpreted as extra edges and
recommends checking the signals at the microcontroller with an oscilloscope.
The current sniffer cannot make that analog measurement.

## Final state

WROOM still runs quiet identity-only v7, installed application SHA256
`d0c7080fd9d729eafdbc4b58668cfc1d727df8a2c127258955708f7a9f3ff4dd`.
The last runner restores GREEN push-pull mode, releases both GPIO outputs,
checks their output-enable bits, and closes serial. Last local levels after
the guarded line-control run: GREEN HIGH, BLUE LOW. No polling remains.

No Console8 reset or firmware-programming command was requested. MOS remains
unrecovered. P4 normal-firmware restoration remains deferred under the Author's
earlier instruction. No further identity retries are justified solely by
repeating this same configuration.
