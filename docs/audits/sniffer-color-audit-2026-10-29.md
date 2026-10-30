# Sniffer color audit — 2026-10-29

The Author supplied the physical probe colors below. Current Extender references
agree. Two kinds of conflicting records were found: a superseded historical
color table, and this UART project's unsupported conclusion that a BROWN probe
was D3. All pre-existing documents, scripts and evidence are preserved unchanged
by this audit. This new report records the differences; it does not repair them.

## Author-confirmed physical probe identity

| Analyzer channel | Probe color | Ribbon |
| --- | --- | --- |
| D0 | GREEN | Even |
| D1 | YELLOW | Odd |
| D2 | BLUE | Even |
| D3 | ORANGE | Odd |
| D4 | PURPLE | Even |
| D5 | RED | Odd |
| D6 | GRAY | Even |
| D7 | BROWN | Odd |

Physical probe identity is independent of the signal attached to it, bus-bit
names, and display colors chosen by software. BLACK is a ground probe, not D0;
use only the already qualified physical ground position. No color is assigned
here to the actual inter-board ground conductor.

## Recorded discrepancies

LA-001 [x] Historical hardware color table differs on seven channels.

`/Agon/mystuff/agon-hardware/first_steps/docs/logic-analyzer.md:14–21` says:

| Channel | Historical table | Author-confirmed map |
| --- | --- | --- |
| D0 | BLACK | GREEN |
| D1 | BROWN | YELLOW |
| D2 | RED | BLUE |
| D3 | ORANGE | ORANGE |
| D4 | YELLOW | PURPLE |
| D5 | GREEN | RED |
| D6 | BLUE | GRAY |
| D7 | PURPLE | BROWN |

This table is explicitly superseded. The current authority
`agon-hardware/extender/docs/logic-analyzer.md:10–13` directs readers away from
it; its table at lines 30–37 agrees with the Author. The historical status is
also stated in `agon-hardware/README.md:7–10`,
`agon-hardware/extender/README.md:70–74`, and
`agon-extender-legacy/docs/logic-analyzer.md:164–167`. A stale discovery link
remains in `agon-hardware/first_steps/HANDOFF.md:253–254` under “Canonical
documents.” Preserve it as part of that historical workspace.

LA-002 [x] UART notes incorrectly promote a removal observation to BROWN=D3.

These records conflict with the Author's BROWN=D7 and ORANGE=D3:

| Existing file | Location / claim |
| --- | --- |
| `agon-mos/HANDOFF.md` | line 5: “physical brown maps to D3, not the assumed D7” |
| `agon-mos/docs/devlog-2026-10-29.md` | lines 371–372: “red=D5 and brown=D3”; earlier BROWN=D7 metadata called incorrect |
| `agon-mos/build/c8-zdi/c8-both-added-disconnected-01/probe-removal-review.json` | line 6: `"brown": "D3"`; lines 10–11 describe removal evidence |
| `agon-mos/build/c8-zdi/c8-connector-five.py` | line 25: added BROWN “physical lead maps to D3” |
| `agon-mos/build/c8-zdi/c8-connector-five-01/result.json` | line 10: same inherited claim |

The raw observation remains useful: D3 activity disappeared when a lead then
reported as BROWN was removed. That does **not** override the Author's verified
probe map. The historical lead description/identification conflicts with that
map. Do not relabel the raw capture, silently reinterpret D3 as D7, or use that
observation as proof of measurements at both resistor ends.

LA-003 [x] Historical endpoint reports differ from the new fixed arrangement.

`agon-mos/build/c8-zdi/c8-direct-two-side-five.py:25`, its run's
`result.json:9`, and `c8-red-disconnected.py:25` / its run's `result.json:9`
record BROWN/D7 as CLOCK and RED/D5 as DATA. This was an earlier operator-reported
attachment arrangement. `c8-direct-two-side-five-01/two-end-review.json:11–20`
explicitly flags waveform-derived alternatives as unverified.

Today's final arrangement is RED/D5 on the WROOM GREEN CLOCK wire and BROWN/D7
on the WROOM BLUE DATA wire. Different historical signal assignments are not,
by themselves, physical channel/color reversals. Preserve their original scope.

LA-004 [x] A decoder hard-codes probe endpoints that were later moved.

`agon-mos/build/c8-zdi/wroom-20261029-sniffer/analyze_polling.py:43` describes
D0 and D2 as WROOM GPIO endpoints. Consequently
`c8-connector-five-01/identity.analysis.json:7–8` says WROOM although that
run's `result.json:7–8` records probes at the Console8 connector. This is an
endpoint metadata error, not a GREEN/D0 or BLUE/D2 identity error. Any new
analysis must supply its actual probe locations explicitly.

LA-005 [x] Legacy live diagram contains historical probe-to-signal overlays.

`agon-extender-legacy/design/wiring-diagram.svg:833–836,858–861` retains:
GRAY→GPIO14/CLOCK, PURPLE→GPIO13/VALID_N, BLUE→GPIO12/D1,
GREEN→GPIO11/D3, YELLOW→GPIO20/READY_N, ORANGE→GPIO21,
RED→GPIO22/D0, BROWN→GPIO23/D2.

These agree with the temporary PRX-06 wiring recorded in
`agon-extender-legacy/tests/runs/2026-08-16_005754_prx-06-speed/probe-map.txt:1–8`.
They do not reverse physical analyzer channel identities. Their presence in a
live diagram conflicts with `agon-extender-legacy/docs/logic-analyzer.md:35–39`,
which says not to make temporary probe-to-net assignments permanent in canonical
diagrams. Record only; leave the diagram intact.

## References that agree, and false positives

LA-006 [x] Checked current authorities agree with all eight colors.

- `agon-extender-legacy/AGENTS.md:121–123`.
- `agon-extender-legacy/docs/logic-analyzer.md:12–31`.
- `agon-hardware/extender/docs/logic-analyzer.md:30–37`.
- `agon-extender/hardware/fixtures/la03-p4-probe-fixture-r01/profile.yaml:38–49`.
- The same fixture's `legacy-evidence/logic-analyzer-harness.md:13–26`.
- `agon-extender/HARDWARE.local.md:3798–3809`.

“GREEN/D3” in PRX-06 reports means GREEN analyzer D0 attached to **bus D3**;
see `agon-extender-legacy/docs/prx-06-results.md:23`, `COMPLETED.md:217`, and
its run's `analyzer-summary.json:12`. It is not a contradictory channel map.
Likewise `agon-hardware/first_steps/byte/pi5-agon-surrogate.md:16–25`, its SVG,
and `byte/agon-wroom-mapping.txt:16–25` describe BYTE bus conductors.
`byte/tests/runs/2026-08-10_byte-gpio-walk-headless_run08/capture-map.json:52–100`
records canonical physical channel/color pairs despite different signal names.

## Fixed wiring for resumed diagnosis

LA-007 [x] Record the Author's final unattended arrangement.

| Probe | Exact location | Signal |
| --- | --- | --- |
| GREEN / D0 | Console8 end, beyond the series resistor | GREEN CLOCK |
| BLUE / D2 | Console8 end, beyond the series resistor | BLUE DATA |
| RED / D5 | WROOM end, before the series resistor | GREEN CLOCK |
| BROWN / D7 | WROOM end, before the series resistor | BLUE DATA |

The Author replaced the ZDI connector leads to rule out worn/intermittent
contacts. Both 33 Ω series paths and common ground remain as reported. Both
original GREEN and BLUE probes are connected; earlier “BLUE probe removed”
state no longer applies. No rewiring or manual reset is requested while the
Author is unattended. Historical BROWN=D3 statements above are not authority
for this run.

The next experiment acquires all four channels simultaneously, beginning with
a passive capture and then five bounded identity reads. It compares settled
request bits and replies at both resistor ends. Only after interpreting that
baseline should clock drive modes be compared. No Console8 flash or reset is
part of these identity tests.

## Coverage and preservation

The audit used `rg` first, including hidden/ignored project evidence, and
separate read-only reviews of MOS, Extender, Extender Legacy, Agon Hardware and
Oryx copies. Large nested source/build snapshots prevent an honest claim that
every file under every project was inspected. Search inventory and additional
scope/results are retained alongside this report. The conclusions above apply
to the inspected material; an unfinished broad search is not a clean bill for
unread files.

Excluded: Git objects/history, private agent-state/chats, SDK/toolchain/cache
and dependency trees, external symlink targets, raw binary waveform decoding
for the documentary audit, and raster-only image contents. Legacy archive
review additionally searched extracted text from 13 PDFs, one ODT and seven
KiCad backup ZIPs. Other compressed archives were not exhaustively opened.
All pre-existing documents and historical evidence remain unchanged.

The additional local-project review read 1,659 candidate files (409 distinct
contents): Agon Bench, Agon Fsim, worktrees, development-environment notes,
nine Extender variants, and the frozen WROOM hardware reference. It skipped
58 dependency/vendor/SDK or oversized files. No further physical probe
channel/color contradiction was found in that bounded pass.

Two examples deliberately remain unmodified:

- `agon-extender-nurples-final-r01/docs/tasks/PORT-008/DIRECTION-ISOLATION-R01.md:523,532`
  says BROWN D6 / GREEN D7 for **inter-board data wires with 220 Ω resistors**.
  The superseded, unexecuted text occurs in 16 copied reports/snapshots. It is
  not an analyzer color-map claim.
- `agon-hardware-wroom-reference/first_steps/byte/agon-wroom-mapping.txt:17–25`
  describes bus wire colors; its separate analyzer table at lines 107–114
  agrees with the Author. Its autorouted SVG at line 97 labels PURPLE analyzer
  D4 observing bus D3, also consistent.

The broad discovery lists are explicitly partial, not a completed all-files
search. See `sniffer-color-audit-2026-10-29/coverage.json` and the SHA256 receipt
for the preserved discrepant source files. The audit creates new files only.

The Oryx read-only review scanned 122,295 eligible text files under
`/home/smith/Agon/mystuff`, pruning SDK/vendor/dependency/cache trees and private
agent-state. Its direct channel/color matches were confined to 49 MOS lines;
other broad color matches were unrelated RGB/audio/emulator definitions. It
also found `agon-mos/build/c8-zdi/c8-connector-five.py:25` carrying the same
BROWN=D3 conclusion as LA-002. No device or source changes were made by that
review. This Oryx scan and the local bounded reviews complete this audit pass;
excluded/unread material is not asserted to be conflict-free.

Oryx SHA256 comparison confirmed two preserved LA-002 files are byte-for-byte
identical to their Pi counterparts:

- `build/c8-zdi/c8-connector-five.py`:
  `818dd8555021e9b5b7f886af5f6c590794d7b430d04e6694c567f6a25c7ddcf4`.
- `build/c8-zdi/c8-both-added-disconnected-01/probe-removal-review.json`:
  `e60253c54404bd730a97f00291b07b7cf307081eb58395d7d9892c9e058ecbb9`.

No Oryx-only contradiction was confirmed. The remote scan reported zero read
errors among eligible files; its refined C8 evidence inventory had 9,012 text
files. These counts describe the scan, not complete manual inspection.
