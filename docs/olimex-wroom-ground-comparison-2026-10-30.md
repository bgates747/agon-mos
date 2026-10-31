# Olimex/WROOM ground-position comparison

Moving the ground lead from upper-middle to upper-left changed the observed
identity result from1000/1000correct to0/1000. Every new reply wasFF FF FF FF.
The new ground connection, its contact, or identification of that connector
position is the immediate issue to investigate. This does not establish damage
to the eZ80 or measure the voltage at either connector position. MOS was untouched.

## Corrected setup history

Author corrected the earlier handback: run002-ground5-direct had NOT moved the
ground; it was still upper-middle (called pin3 in the connector diagram).
Its filename and original metadata incorrectly say pin5. Raw evidence remains
unchanged; operator-correction-run-002.json records the correction, and the
human-readable preceding report is corrected explicitly. Only before run003
was ground actually moved to upper-left (called pin5 in the diagram).
Physical connector-to-number mapping was not independently measured.

Both matched runs: direct wiring, no series resistors; BLUE GPIO26/TCK to
reported pin4, GREEN GPIO27/TDI to reported pin6; same higher-quality breadboard,
identity-onlyv3 firmware and S/10us timing. Ten WROOM-only restart epochs,
100reads each. No Olimex reset. Author says ground alone changed between them.

| Ground lead position | Correct identities | Reply details |
|---|---:|---|
| Upper-middle, preceding run002 |1000/1000|999×07 00 AA 1C;1×07 00 AA 18|
| Upper-left, current run003 |0/1000|1000×FF FF FF FF|

All13000local driven-bit checks pass in each run. Current run firstafterreset
0/10valid; each epoch0/100. Programmer local checks establish only its local
GPIO observations; they do not establish the target-side levels or ground
continuity. AllFF means the programmer sampled dataHIGH throughout, not proof
that an eZ80 acknowledged anything. No electrical/transient capture taken.
Runner time106.722seconds; no need to infer a physical failure probability from
these entirely correlated-looking outcomes.

No target halt/reset, RAM access or MOS erase/program. WROOM outputs released;
BLUE and GREEN sampledHIGH at final local snapshot, host serial closed, no
polling. Current ground remains upper-left; agent has not changed wiring.
Identity-onlyv3 stays installed. Do not use this setup for blind MOS recovery.

Raw evidence Pi/Oryx: build/olimex-wroom-breadboard-20261030/
run-003-ground5-only-change. Source unchanged since previous metadata update:
experiments/zdi-wroom-diagnostic/statistical_identity.py. Firmware unchanged,
SHA256 abaa0bc98876389f14a2f92a47115a5e95a5009dd1975f61a026d74978984fd9.
ConsoleSHA2565906b143d84d566c243a85b8dc00a53743efbf5bc16da5556822621e6fc1387f.
