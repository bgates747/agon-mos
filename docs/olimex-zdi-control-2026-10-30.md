# Olimex ZDI control and sniffer interference — 2026-10-30

The Author connected WROOM, the sniffer and Olimex Agon Light 2 to the Pi5 and
authorized tests. The initial four-probe setup failed. With all sniffer signal
probes disconnected, the unchanged 33 Ω harness and exact older WROOM diagnostic
returned **20/20 exact `07 00 AA 1C` identities** across four runs, each with a
fresh WROOM-only reset. No Olimex flash, target reset or RAM-upload command was
requested. Console8 was not connected/tested during this campaign.

## What the comparisons establish

The Author confirmed 33 Ω in both actual signal paths and initially four probes:
GREEN/D0 at Agon CLOCK, BLUE/D2 at Agon DATA, RED/D5 at WROOM CLOCK and BROWN/D7
at WROOM DATA. Canonical probe colors remain unchanged.

The v7 baseline has all65 settled source bits correct and15 target-end bits
wrong throughout ±5 µs. CPU replies match the captured target/source DATA.
This reproduces the digital disagreement on Olimex as well as Console8; it is
not evidence of a Console8-specific fault. Both board-end identity replies and
full request bits become correct during passing two-probe runs. Functional
success rules out a simple GREEN/BLUE swap on the presently working Olimex
connection; it does not verify the disconnected Console8's wiring.

The clock-only drive test alternated default2/weak0/default2/weak0 while DATA
remained at drive2, verified by GPIO API readback. All20 IDs fail. Raw clock-rise
counts are225/226/228/225 at both ends. The decoder records malformed frame counts
rather than forcing the extra edges into45-clock decoding. This comparison did
not restore communication under the four-probe condition; no analog slew-rate
measurement or universal conclusion about drive strength is established.

Next, the exact original v3 binary from the earlier5/5 Olimex pass was restored
in WROOM. With four probes it still fails0/5. The Author then changed only probe
attachments, leaving actual GREEN/BLUE wires, resistor values, grounds and USB
fixed:

- Remove RED and BROWN: first run3/5, then5/5 and5/5;13 consecutive correct replies.
- Reattach only RED on WROOM-side GREEN CLOCK, BROWN still off:0/5.
- Remove RED again:4/5, then3/5. The latter includes one valid product/revision
  with status19 rather than1C; its last two IDs fail. The two-probe setup remains
  intermittent. Removing RED is not a complete repair.
- Remove the remaining GREEN and BLUE **sniffer probes only**: four consecutive
  sets pass5/5, all four returned bytes exactly07 00 AA 1C,20/20 in total.

This is strong evidence that measurement connections perturb a marginal link.
RED attachment is a demonstrated trigger in this sequence, but its electrical
mechanism remains unresolved: loading, a lead/channel fault, geometry/contact
changes or another interaction have not been separated. No claim is made that
all historical Console8 failures are explained, that the analyzer itself is
defective, or that a particular analog voltage/current was measured.

## Complete run accounting

“Valid ID” means product0007/revisionAA; the status byte is reported separately.
No intermediate failure is omitted or relabelled as a warm-up pass.

| Run under build/zdi-qualification-20261030 | Reads | Valid ID/revision | Exact07 00 AA 1C |
| --- | --- | --- | --- |
| olimex-baseline-001 | 5 | 0 | 0 |
| olimex-clock-strength-001 | 20 | 0 | 0 |
| olimex-original-v3-001 | 5 | 0 | 0 |
| olimex-v3-no-signal-probes-001 | 5 | 5 | 5 |
| olimex-v3-no-signal-probes-002 | 5 | 5 | 5 |
| olimex-v3-no-signal-probes-003 | 5 | 5 | 5 |
| olimex-v3-no-signal-probes-004 | 5 | 5 | 5 |
| olimex-v3-red-only-001 | 5 | 0 | 0 |
| olimex-v3-red-removed-001 | 5 | 4 | 4 |
| olimex-v3-red-removed-002 | 5 | 3 | 2 |
| olimex-v3-target-probes-001 | 5 | 3 | 3 |
| olimex-v3-target-probes-002 | 5 | 5 | 5 |
| olimex-v3-target-probes-003 | 5 | 5 | 5 |

Raw acquisitions, serial logs, installed-image backups, analysis and hashes are
under `build/zdi-qualification-20261030/` (ignored build evidence). Campaign
summary and raw-file verification are `campaign-summary.json` and
`capture-verification.json`. No-probe analyzer files explicitly contain no ZDI
waveform and must not be used as wire verification. Passing no-probe results
are software identity/local-GPIO observations.

## Programmer versions and installation checks

Only WROOM firmware changed. The clock-only v8 diagnostic built privately on
Oryx, SHA256 `80dc4b853972fc69ec55680038606d9cda73d50af0450fec643b303fae676ce5`.
Its affected application flash range was backed up and read back exactly.
It has no target programming API, MOS payload or BOOT-button action.

For the original-binary control, the host verifier initially stopped because
it wrongly expected old application pages beyond the smaller v3 erase range to
become FF. Retained before/after reads prove exact v3 bytes, FF in the actual
erased-page padding, and unchanged pages outside that erase range. The failed
receipt is preserved with a separate reconciled verification; no extra write
was needed to correct that host expectation. Subsequent captures verify quiet
v3 boot and its actual execution.

Current WROOM image: identity-only **v3**,267904bytes, SHA256
`abaa0bc98876389f14a2f92a47115a5e95a5009dd1975f61a026d74978984fd9`.
The maintained diagnostic source now contains v8's optional clock-drive command;
do not infer installed firmware from source HEAD. The capture helper requires
an explicit firmware version and checks its banner. Source snapshots and
immutable installed bytes are retained with the campaign.

## Task dispositions and next step

TRY-001 [x] Re-audited channel identities, waveform interpretation and physical
probe influence; limitations remain explicit. Probe attachment demonstrably
changes the outcome, and the uninstrumented control now passes20/20.

TRY-002 [x] Executed the isolated CLOCK-only weak-drive comparison; no reliable
identity under its four-probe conditions. No further blind repetition queued.

TRY-005 [x] Reproduced Olimex's valid control with the known original binary,
33 Ω resistors and all signal probes disconnected. Two complete two-probe
passes also occurred, but that setup later failed again.

TRY-003/TRY-004/TRY-006 remain available investigations. Before changing more
hardware, repeat Console8 identification using this known WROOM image with
**no sniffer signal probes attached**. That requires the Author's board
handback. Only after repeatable correct identity should the stock recovery
programmer proceed through verified RAM upload/readback and MOS programming.
The successful Olimex ID control is not qualification of RAM writes or flash.

## Final physical/software state

Olimex and WROOM remain attached to Pi5. Actual GREEN/BLUE wires, both33 Ω
resistors, grounds and USB remain connected. **All four sniffer signal probes
are disconnected.** Sniffer USB/ground remain connected. WROOM v3 is quiet,
both GPIO outputs released, GREEN/BLUE local levels HIGH, serial/capture closed.
No target programming/reset was requested. Mainboard startup, SD contents and
firmware were not modified by this campaign. Console8 MOS remains unrecovered;
P4 normal-firmware restoration remains deferred.


## Verified archive

`build/zdi-qualification-20261030-evidence-r01.tar.gz` is retained and independently
read/verified on Pi and Oryx:142regular files,29raw captures,1,550,845,994uncompressed
regular bytes. Compressed archive7,677,262bytes, SHA256
`0d4a4d9a9aa5d7ccbf4c1d7ac9e170f75ed7e9cda4c3ae30bf14938be13851df`.
The archive contains the campaign notes as written before this verification
addendum; original run receipts and failed host-verification evidence remain
intact. Portable summary: experiments/zdi-wroom-diagnostic/results-20261030.json.
