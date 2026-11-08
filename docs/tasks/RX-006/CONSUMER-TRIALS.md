# RX006 — Small consumer trials after the own hardware pass

Brandon's clarified scope requires actual selected-owner code trials, not just
the already affirmative source reviews. UART first completes its own Olimex
integrity and matched legacy/counting benchmark. Only after that pass and review
of its attributable measurements does UART send the exact tested tuple and
findings to the selected owners for finite trials. This document is preparation,
not a prototype handoff or permission to begin a target run now.

The source reviews remain under their original limits. Owners keep all their
current work, paused tasks and bench requests. UART edits no application code;
VDPlet edits no application code. Extender owns any actual EMOS/native firmware
installation, current keyboard/routing admission and exact restoration.

## Rally: retained post-race exporter

Use the retained TIM-002 `timingDumpBuffer` seam identified in Rally's
`docs/consultations/mos-rx006/REVIEW.md`. Prefer an isolated invocation of its
actual export helper over running a race or changing the current game. Its
ordinary single-block source buffer stays frozen across the complete export;
the existing file bytes, generation checks and legacy management/error callback
remain the oracles. One bounded retained export or representative slice suffices.
Do not require the complete65448B export if a smaller exact helper trial proves
the seam. The owner selects and reports the precise trial scope.

Keep the old path as a matched control where practical, with the same source
bytes and file oracle. Compare complete-operation duration/request count only;
this is a post-race export, so no rendered FPS or physics claim follows.

## 6502: retained ESP32-hosted disk export seam

Use the retained `drain_disk`/BRClient source described in
`docs/tasks/IO-003/RX-006-ADOPTION-R01.md`. Do not migrate the current eZ80-local
persistence, which already owns its bytes and needs no UART return. The owner
chooses a small isolated trial of its actual adapter: a40B descriptor and512B
payload are sufficient to exercise the concrete receive seam. Preserve descriptor
identity/length validation and, if persistence is exercised, its unchanged
write/sync/reopen/readback-before-ACK rule. Do not require a game boot or a new
VDP machine implementation to prove the receive helper.

The existing BRClient accepts only operations1..6. A local counted branch must
use the actual26h completion result rather than expect a legacy success packet.
Keep legacy management/error delivery separate. A tagged source ERROR leaves
the receive arm live; do not translate it into an ordinary safe storage retry.

## Shared evidence and stop rule

Each owner records exact tested source/app/firmware identities, the real invoked
helper and input, announced/stored counts, exact bytes/guards or existing file
oracle, positive lifetime retirement and normal cleanup. One outstanding receive,
live destination/code and IRQ service apply. Source release, receive completion
and durable persistence are separate events. No timeout reuses a live arm.

Use the own-suite results to select a modest meaningful transfer size. Aggregate
tiny transfers only when needed for clock resolution; do not create a new large
matrix or chase millisecond gains. A finite actual pass plus the owner's concrete
judgment of simpler code or a useful modest gain completes that consumer's role.
Retain failures, correct attributable integration errors, and avoid blind replay.
Normal fresh FIFO admission is required for any target action.

If the proposed retained seam is no longer practical, obtain the owner's concrete
small alternative before building. Do not quietly substitute another source-only
approval for execution. After own hardware and the selected finite trials pass,
collate the evidence and stop the goal; broad adoption/release remains separate.

## Planning dispatch

The corrected sequence and this bounded outline were sent before execution,
with no build/run/prototype request, in durable mails
`2026-11-08_00-28-21_agon-mos_rx006-conditional-rally-code-trial-eight` and
`2026-11-08_00-28-22_agon-mos_rx006-conditional-6502-code-trial-eight`.
Immediate Pi-native alerts were accepted (`turn/start` for Rally and
`turn/steer` for6502); acceptance does not prove either owner read or agreed.
Concrete seam/blocker feedback is pending. Own hardware pass remains prerequisite.
