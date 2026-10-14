# MOS TODO

Executive summary: the UART0 candidate is integrated and passes native ZDS II,
scripted and full-image headless Flexe qualification. The Author passed human
review of the earlier fixtures on 2026-10-13. The reusable suite is qualified
headlessly and staged; its corrected human software campaign also passes.
The Console8 software campaign and approximate manual calibration also pass.
Console8 receiver instrumentation also passes, with 62 observed spare FIFO
slots at stock threshold. Prior suite/instrumentation work is committed and pushed;
worst-case/electrical timing is unmeasured and deferred. Batching contract and
hardware audit are delivered; isolated implementation is next.
This is the sole unfinished-work checklist.

Subtask IDs are immutable: a short namespace followed by a hyphen and three
zero-padded digits, then a checkbox. Reordering never renumbers an item.
Record completed/disposed IDs and evidence in the development log, remove them
here, and never reuse an identifier.

## Deployment policy

The Author lifted the SD write hold and authorized staging the suite. Multiple
cards may be attached to Oryx: rediscover the unique UUID 8658-1C23 and match
the prior UART manifest/fixture immediately before deployment. Keep the active
/test/mos-uart0 path; preserve history only in project workspace.

## Provenance

TX-016/TX-017 fixture and capture-preparation work completed on 2026-10-13.
The Author passed human emulator review; subsequent Console8 physical software
and empirical reserve campaigns pass. TX-006 qualification closeout is complete.

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

## Opt-in CTS batching (contract and audit delivered; implementation next)

See [the design goal and acceptance plan](docs/uart0-cts-batching.md).
Contract: [proposed ABI](docs/uart0-cts-batching-api.md).
Budget and source review: [hardware audit](docs/uart0-cts-batching-audit.md).
BT-001/BT-002 are complete. TX-006 closeout records empirical reserve and
defers electrical/worst-case qualification; stock restoration is confirmed.

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
