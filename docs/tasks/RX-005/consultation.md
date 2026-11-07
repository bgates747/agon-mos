# RX-005 — Bounded return-path consultation

Brandon authorized finishing this source-review round, then stopping for task
scoping and refinement. This record collates requirements; it does not select an
ABI, wire format, implementation or test. The consultation requirement is now
part of [the task](README.md), with decisions in [the running notes](notes.md).

VDPlet was contacted first. FSIM, Wolf and MechAgon were named by Brandon;
source inspection confirmed 6502 as an additional consumer. VDPlet identified
Rally and Wireframe as further concrete leads. Rally's retained native fixture
was inspected and its owner contacted. The inspected Wireframe helper is in
FSIM's repository and that owner distinguishes it from its current client.
Golem loader integration and VDPlet's benchmark/timer frontends remain leads
for later scoping; this round is not an unbounded project census. Narrow searches
of Nurples/Jukebox source found generic keyboard API definitions, not evidence
of private return-data use; no consultation was inferred from those definitions.

## Requests and returns

All requests were durable mail on `rx005-bidirectional-transport`, followed by
immediate native chat notification. Active chats received steering; the idle 6502 and Rally
chats received normal turn starts. Send acceptance alone is not evidence of
reading. Replies below establish the source reviews actually returned. Exact
message IDs, copied mail hashes and source observations are retained in
[consultation-evidence.json](consultation-evidence.json). Immutable owner report
and pin copies are in `consultation-reviews/`; the original request/return mail
is in `consultation-mail/`. Copies preserve historical wording, with corrections
called out below.

* VDPlet request `2026-11-07_17-33-04_agon-mos_rx005-vdplet-existing-return-integration-one`;
  returned `2026-11-07_17-38-06_vdplet_rx005-vdplet-current-return-requirements-one`.
* FSIM request `2026-11-07_17-36-46_agon-mos_rx005-fsim-pingo-return-requirements-one`;
  returned `2026-11-07_17-38-18_fsim-pingo_rx005-fsim-current-return-findings-one`.
* Wolf request `2026-11-07_17-36-46_agon-mos_rx005-wolf3dorig-return-requirements-one`;
  returned `2026-11-07_17-38-24_wolf3dorig_rx005-wolf-source-return-one`.
* 6502 request `2026-11-07_17-36-47_agon-mos_rx005-agon-6502-return-requirements-one`;
  returned `2026-11-07_17-39-57_agon-6502_rx005-6502-return-source-findings-one`.
* MechAgon request `2026-11-07_17-36-47_agon-mos_rx005-mechagon-return-requirements-one`;
  returned `2026-11-07_17-43-09_mechagon_rx005-mechagon-source-return-requirements`.
* Rally request `2026-11-07_17-39-43_agon-mos_rx005-rally-return-requirements-one`;
  returned `2026-11-07_17-43-41_rally_rx005-rally-return-requirements-return-one`.

All six returned. This round is complete and UART is stopped for Brandon's
further scoping; there is no implied request for another review or execution.

## Findings returned

### VDPlet: reuse the producer, replace the small return carrier

Current replies use **keycode packet 0x81**, with a length and a tagged `VDPL`
body. It is not a held-key map transfer. UART's request incorrectly called 0x88
a literal key-map reply; MechAgon and Rally corrected this. Stock MOS v3.0.2's
`vdp_protocol_KEYSTATE` copies five bytes of repeat-delay/rate/LED state, matching
the retained VDP `PACKET_KEYSTATE=8`. Thus 0x88 is that keyboard-status packet,
not the held-key map. The archived original questions retain the mistake; this
is the explicit correction. D8 requests and D9 discovery are
private experimental allocations, not upstream general-transport assignments.
Legacy replies have 10-byte bodies and two useful value bytes. Optional
READ_BYTES supplies 1..8 useful bytes in a fixed 16-byte body. MOS's keyboard
callback supplies a borrowed payload pointer without a length argument; clients
copy known shapes, neutralize private replies and preserve real keys.

The runtime already has checked buffer/span access, foreground dispatch,
capability discovery and controlled reply production. Modules have no raw serial
service. A counted return could reuse that ownership, avoiding a new module-side
transport framework. Useful first sizes are16-byte results, 128-byte status and
512-byte exports. Larger queued output must either own a copy or retain its
source through positive retirement; a local/stack packet cannot simply become
an asynchronous borrowed send.

Experimental VDPL-035 admits only D8/D9 while OPEN. A new inbound selector needs
explicit integration with that gate; pure MOS receive registration may avoid a
new request selector, but reply routing and source ownership still need design.
The experimental worker is not physically qualified by this source review.
Runtime/module completion, receive completion, Canvas drain and presentation
remain separate.

Owner report/pins:
[VDPlet consultation](/Agon/mystuff/agon-vdplet/docs/tasks/VDPL-035/RX005-RETURN-PATH-CONSULTATION.md),
[exact source pins](/Agon/mystuff/agon-vdplet/docs/tasks/VDPL-035/RX005-RETURN-PATH-PINS.json),
published at 602fe37. These are source requirements, not adoption or run evidence.

### FSIM: return a coherent 128-byte status without16 small reads

The owner identifies the current source-qualified client at ae46ec9:
`utilities/pingo-vdplet-flight/async/{client_backend.inc,client_prepare.py,wire.h,controller_adapter.h}`,
with generated `build/p071-client-r5/source/{main.cpp,callback.s}`. The inspected
Wireframe `packets.src` is historical. Its current source is not yet executed.

The client uses 0x81, copies 10/16-byte native replies and maintains a separate
real-key ring. It has one outstanding operation, token/kind validation and
separate runtime ownership. Final status 128B takes 16 READ_BYTES exchanges;
normal health reads need 8B. Proposed simplifications are removing synthetic-key
multiplexing/neutralization, the tiny reply mailbox and status chunking. Keep
input/physics able to proceed while an operation is pending. A useful later
comparison is identical 128-byte status with genuine keys, not a changed scene.
Nominal pose/health cadence is source intent, not measured performance.

### Wolf: bulk profiler export, beyond a tiny completion notice

The maintained client is `/Agon/mystuff/Wolf3dOrig/src/asm/wolf3d/src/`, not the
older reduced PERF donors. Owner pins correction 44c5f40/7e83958 and exact file
hashes in its returned mail. `w3d_render_packet_callback` handles VDPL/W3DR/W3DV
before real keys, copies 10-byte records, and neutralizes private keyboard fields.
The ordinary data return is READ16: 2 useful bytes per 17-byte request and 12-byte
reply. One outstanding receive fits its composition.

WPN1 profiler exports have a 16-byte header plus 20 bytes per completed frame,
usually 120 frames: 2416 useful bytes, currently many READ16 round trips in logging
gaps. A counted destination could remove the tiny-read loop and callback glue.
Keep application kind/token/handle checks and distinct render/fence completion.
Foreground processing after ready is sufficient; no substantial IRQ callback is
needed. A future matched comparison can retrieve identical WPN1 bytes with keys.
No performance measurement or new Wolf execution was selected by this review.

### MechAgon: bounded replay verification, without a whole-clip buffer

The current renderer uses `native/renderer/src/render_link.c`, `receiver.c` and
`packets.s`, sharing the portable readback decoder. Its adapter uses RFC25 and
foreground wake handling; the older synchronous getter is not its steady-state
path. Normal RUN returns a two-byte status in a 10-byte VDPL body, not the
module's entire 16-byte result buffer. Its optional UART1 NM route is separate.

Stopped profiling currently uses 15 RUNs plus 120 READ16s for 15 selected 16-byte
pages. A larger destination alone would not aggregate those producer pages.
The prepared replay verifier compares 113326 bytes through 56663 READ16 requests
before START. Bounded256–1024-byte returns are useful; 1024 bytes fits existing
file scratch and would reduce that comparison to 111 data requests if a matching
producer operation is selected. This is source arithmetic, not a speed result.

One outstanding mainboard return suffices. Keep publication/lifetime/late-reply
rules and application identity; no additional generic token framework is needed
if ordered retirement establishes association. A future matched comparison can
verify the same immutable saved clip in chunks. Owner source/pins and actual
versus prepared evidence are in
[MechAgon's report](/Agon/mystuff/MechAgon/docs/tasks/GOAL-001/rx005-return-source-consultation.md).
It also corrects our stale paused-goal wording: Brandon independently resumed
its goal. This consultation assigns no goal work or change to its current scope.

### 6502: whole disk block and durable acknowledgement are separate

The maintained saving frontend is an ESP32-hosted guest with eZ80 filesystem
persistence. The separately prepared IO003 eZ80-CPU comparator is read-only;
its capabilities must not be conflated. Owner source HEAD 46b5a8a and 19 exact
current/generated file pins are in
[its review](/Agon/mystuff/agon-6502/docs/tasks/IO-003/RX-005-CONSULTATION-R01.md)
and adjacent JSON.

Current transport uses 0x81 fixed10/16-byte bodies, borrowed callback scratch,
mailbox copies, serialized pulls and clean token-epoch renewal. A 40-byte export
descriptor plus 512-byte payload uses 69 eight-byte requests, or 276 READ16 requests.
A whole 512-byte block is the useful first bulk case; a 552-byte combined stable
export is another option. Other existing spans are 8/40/48/128/960 bytes. 64KiB
RAM capture is optional diagnostic work, not a minimum requirement.

The exporter is bursty, not a required continuous 60/120Hz return stream. Receive
into eZ80 RAM, validate the export, write/sync/reopen/read back in foreground,
then acknowledge that exact disk generation. Receive completion alone never
permits durable disk ACK or clears dirty data. One outstanding transfer suffices.
The proposed future comparison starts with an existing 512-byte known-pattern
utility; a genuine DOS SAVE/LOAD path is useful application validation later.

### Rally: retained readback client, not every game build

Normal `rally-game` uses ordinary VDU output and key-map input. The optional
R27T timing callback and retained TIM-002 D8 client are distinct opt-ins; neither
is every current game's receive architecture. The inspected TIM-002
`native.hpp`/`callback.asm` use ten-byte 0x81 VDPL mailboxes and synchronous READ16.

Useful returns include four-byte scalars, 16–48-byte completion snapshots and
406 bytes of final state. Its largest retained post-race export is 65448 bytes
in two buffers, requiring 32724 READ16 exchanges. The caller already saves in
256-byte chunks: a counted path need not allocate or copy 65KiB in one IRQ.
One outstanding receive fits; keep kind/token/generation checks and real-key
handling. Existing data buffers can outlive module UNLOAD independently, but
must remain stable through the return.

A future matched export comparison can use the same frozen generation and
byte-exact saved oracle; a 256-byte chunk or 406-byte state is a smaller first
case. Export occurs outside the timed race, so faster export must not be called
an FPS improvement. Exact current/retained distinctions, paths and hashes:
[Rally report](/Agon/mystuff/AgonArcade/docs/consultations/rx005-return-requirements-20261107/REVIEW.md)
and adjacent `SOURCE-PINS.json`. No run or benchmark is selected.

## Common requirements to carry into scoping

* A distinct typed data return can remove synthetic keyboard handling and tiny
  serialized pulls while preserving ordinary key/mode/point replies and VDU bytes.
* Arm stable writable destination/capacity before the request; expose actual
  count, status and completion after committed data. Handle a larger total than
  one old reply body without making FIFO 16 an application limit.
* One outstanding receive is enough for the reported initial uses. No queue,
  channels, retry/echo/checksum framework is requested. Existing application
  identifiers can remain above the transport; no extra generic wire ID is chosen.
* One outstanding operation does not solve late replies after timeout/rearm.
  Define the smallest positive retirement/ordering or correlation rule needed
  to avoid assigning old data to new storage. A timeout or cleared flag alone
  cannot establish retirement. Scope that concrete rule before adding machinery.
* Capacity is not flow control. Bound production against actual FIFO/service/DI
  behavior, serialize complete reply packets between producers, and preserve
  short-event/keyboard latency. Do not infer speed or safe uninterrupted bursts
  from wire-byte arithmetic or destination size.
* Keep IRQ work bounded; a ready/count/status publication or tiny callback can
  suffice. Foreground does file writes, decoding and application logic. Decide
  callback context explicitly rather than importing a deferred execution engine.
* Keep source release, wire drain, operation completion, received-data ownership
  and presentation/durable commit separate where the application needs them.
  A coherent producer snapshot is an application responsibility, not automatic
  just because bytes arrive intact.
* Keep the one-file-per-firmware requirement and small registration hooks.
  Agree with VDPlet on its live-session selector/output ownership before edits.

## Questions left for Brandon's scoping review

Choose a first useful slice rather than requiring every consumer to migrate:
small status/completion, 512-byte pattern/disk export, or Wolf profiler readback.
Decide the exact donor/toolchain, registration/completion contract, source
snapshot/retirement and necessary pacing. Collision-check the reserved bank.
The reports above are input to those decisions, not a frozen design or authority
to implement. Stop here after the finite returns are recorded.
