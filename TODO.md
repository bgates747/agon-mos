# MOS TODO

Executive summary: the UART0 candidate is integrated and passes native ZDS II,
scripted and full-image headless Flexe qualification. The Author passed human
emulator review on 2026-10-13. Physical qualification remains. This is the sole unfinished-work checklist.

Subtask IDs are immutable: a short namespace followed by a hyphen and three
zero-padded digits, then a checkbox. Reordering never renumbers an item.
Record completed/disposed IDs and evidence in the development log, remove them
here, and never reuse an identifier.

## Acceptance and qualification

TX-006 [ ] Qualify CTS headroom, full-duplex traffic, timing and recovered
CPU work physically. Coordinate game integration separately; do not remove DI
here. Emulator results do not establish physical headroom or game performance.
The Author performs manual Console8 flashing/testing from the staged SD bundle;
agent-operated board/USB/firmware access still needs a fresh explicit bench grant.
The first physical run saved RX error bits 0x98 after its first blocking-case
verification; investigate this failure using the new progress fixture.
The corrected diagnostic benchmark now passes all eight cases physically,
with zero baseline/case RX errors and 24 blocking / 16 async raw ticks per pair.
Controlled CTS reserve, wider full-duplex and calibrated timing remain pending.

## Provenance

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
