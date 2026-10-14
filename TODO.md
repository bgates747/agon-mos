# MOS TODO

Executive summary: the UART0 candidate is integrated and passes native ZDS II,
scripted and full-image headless Flexe qualification. The Author passed human
review of the earlier fixtures on 2026-10-13. The reusable suite is qualified
headlessly and staged; its corrected human software campaign also passes.
The Console8 software campaign and approximate manual calibration also pass.
Console8 receiver instrumentation also passes, with 62 observed spare FIFO
slots at stock threshold. Prior suite/instrumentation work is accepted for commit;
worst-case/electrical timing is unmeasured. Opt-in CTS batching is planned.
This is the sole unfinished-work checklist.

Subtask IDs are immutable: a short namespace followed by a hyphen and three
zero-padded digits, then a checkbox. Reordering never renumbers an item.
Record completed/disposed IDs and evidence in the development log, remove them
here, and never reuse an identifier.

## Acceptance and qualification

The Author lifted the SD write hold and authorized staging the suite. Multiple
cards may be attached to Oryx: rediscover the unique UUID 8658-1C23 and match
the prior UART manifest/fixture immediately before deployment. Keep the active
/test/mos-uart0 path; preserve history only in project workspace.

TX-006 [ ] Close out CTS qualification scope and record the measured Console8
reserve separately from unmeasured worst-case/electrical timing; confirm stock
VDP boot version after the R0004 restore request. Retain any further timing
investigation as deferred unless needed for batching qualification.
Original measurement routes: validated receiver diagnostics
and threshold sweeps, or a controlled passive capture with receiver reserve.
The Author chose diagnostic firmware as the next route. Safe Console8 probe
access remains unestablished; software results do not prove electrical margin.
Possible alternative: Olimex Agon Light 2 Rev B has CTS at eZ80 U1 lead 71,
ESP32 GPIO13 and two PCB vias; TX/RX have series-resistor pad candidates.
Actual board revision, exposed copper and practical solderless probe access
remain unverified. An Olimex capture would qualify that configuration, not
automatically Console8. Recorded as a possibility only; Olimex probing remains
deferred at the Author's request, including its already damaged keyboard port.
The Console8 suite now passes diagnostics, API/ADL=0, all eight benchmark and
four acknowledged-round stress cases, with 98,304 compared receiver bytes,
128 ordered replies and zero trial RX errors. Manual calibration measures
about 120.270 ticks/s (7,304 ticks / 60.730 seconds). Blocking takes 24 ticks;
async takes 14–16 for this fixed workload. Entry RX 0x98 predates test output;
its origin remains unknown and is separated from fresh zero diagnostic epochs.
See experiments/uart0-suite/physical-results.json and the development log.
Coordinate game integration separately; do not remove DI here or infer game
performance. Agent-operated physical board/USB/firmware access still needs a
fresh explicit bench grant. No repeat software-only SD test is currently needed.

## Provenance

TX-016/TX-017 fixture and capture-preparation work completed on 2026-10-13.
The Author passed human emulator review; physical stress/headroom remains TX-006.

TX-014/TX-015 were accepted for commit on 2026-10-13 after the passing physical
benchmark and explicit commit/push instruction; emulator-review history remains
recorded accurately in the development log.


C-001/C-002, TX-001 and TX-005 were resolved/delivered on 2026-10-13; see
[the development log](docs/devlog-2026-10-13.md). Human acceptance TX-010 passed on 2026-10-13.
Earlier TX-002/TX-003/TX-004 and TX-007/TX-008/TX-009 remain completed evidence.
Console8 preparation TX-011 and human fixture acceptance TX-012 passed on 2026-10-13.
Manual Console8 SD deployment TX-013 completed on 2026-10-13.
Original ASY-001 identifiers remain valid provenance references in
[the MOS-owned task](docs/tasks/ASY-001.md).

## Opt-in CTS batching (design goal; implementation not started)

See [the design goal and acceptance plan](docs/uart0-cts-batching.md).
Complete existing qualification/release bookkeeping before this implementation.

BT-001 [ ] Specify session-scoped batch selection, capability/API compatibility,
quiescent configuration, unsupported requests and default/reset behavior.

BT-002 [ ] Audit UART FIFO/in-flight bytes and ISR paths; derive a conservative
batch budget and permissible initial experiment sizes from hardware behavior.

BT-003 [ ] Implement an isolated opt-in candidate with per-byte default,
bounded service, transmitter-ready checks and existing lifetime/ordering fences.

BT-004 [ ] Measure paired throughput and recovered CPU/useful work, including
service cost and latency; establish whether batching offers a worthwhile gain.

BT-005 [ ] Extend menu/reporting and both-engine qualification for batching,
receiver integrity, negative controls, default regression and session cleanup.

BT-006 [ ] Qualify manually on Console8 with stock threshold and diagnostic
controls; repeat near any failure boundary without Olimex probing or wiring.

BT-007 [ ] Select conservative supported options from evidence, document
compatibility/limits, and complete human review; defer shipping if gains do not
justify the tradeoff.
