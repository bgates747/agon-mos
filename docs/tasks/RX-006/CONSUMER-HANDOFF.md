# RX006 tested receive path — bounded owner trials

This is the tested-tuple reference for Brandon's selected small Rally/6502
consumer-code trials. Source preparation may start after the own pass; target
execution follows actual132 clean handback and fresh admission. This does not
grant a bench slot, authorize a full-game port, release a paused unrelated goal,
or ask anyone to optimize performance. Each consumer owns only its own helper
adapter/harness; UART owns MOS, VDPlet owns VDP, Extender owns installation,
keyboard/routing admission and restoration.

## Passing evidence

[Actual132](actual132/README.md) completes all10 sizes4..8092,36 cells, exact
WITNESS32B/state3/next2, normal listener continuation/EXIT and joined return.
The consumer took58s. Original129 had the same complete durable data pass but
our following batch SAVE radix was wrong; preserve that distinction.

Own matched no-work batches give5.65x/6.49x/6.98x lower complete-pull duration
at128/256/1024B, comparing tagged8B replies with counted<=512B replies. Request
construction, adapter/IRQ handling and byte validation are timed, upload/setup/
logging are not. Public clock is coarse; this is not CPU recovery, pure wire
throughput, rendered FPS or a prediction for another adapter. Rally's retained
READ16 control returns2B and is a distinct baseline. One useful owner-specific
check and its practicality judgment suffice; no new timing matrix is required.

## Exact tuple and examples

- Receiving full131072B ROM:
  `/Agon/mystuff/agon-extender/agents/rx006-receiver-r01/build595/on/ROM.bin`,
  SHA256 `171c7880c4c4e064293d67e41d4225d2112a13c690e49d803cf77899919f6914`;
  map `ccbda4bc18bb16ef247d291338037ebdee4c3185c28b9ea25f9c32c44fe3b71f`.
- Native VDP producer1100320B:
  `/Agon/mystuff/agon-vdplet/build/vdpl036-producer-r05/enabled/firmware-src/.pio/build/esp32dev/firmware.bin`,
  SHA256 `7d09dfeac4e7a1654dca486a8e86cd7b5d283f0d53bac0ab128cb8dd33e10087`.
- Worked C/assembly code:
  `/Agon/mystuff/agon-mos/experiments/rx006/fixture/src/main.c` and `bridge.src`;
  exact built snapshot/ELF/listing is `build/rx006/app-r04-emos-final` in UART.
  Do not edit/rebuild the owner firmware or use raw UART/private result addresses.
- [Wire/API contract](../RX-005/wire-contract.md) and
  [bounded consumer seams](CONSUMER-TRIALS.md) give the selected cases.

Released RC3 and ordinary installed EMOS do **not** acquire26h/90h by assumption.
This is the specifically tested temporary receiving composition, Legacy mode,
mainboard VDP. Extender handles any future native-first/EMOS installation and
exact rollback at an actual fresh grant. Do not flash from the consumer helper.
Current tuple/layout/startup/P4 must be reconciled at that turn; retained image
hashes alone do not establish current installation or service availability.

## Minimal caller contract

Foreground ADL1/MBASE0 with IRQ service. Before invoking the producer, arm an
owned persistent destination through syscall26h: HL=destination, BC=capacity,
DE=bounded assembly callback or NULL. A0 means admitted,1BUSY,2invalid; HL is
the public read-only result pointer. Do not guess its private address. Record
state1 means pending;2 complete;3 oversize. Offsets2/5 are actual/announced u24
counts, published before terminal state. Require both equal the requested size
and surrounding guards unchanged before reading/reusing the destination.

Callback, if used, only publishes a flag/count and returns normally; A0 success
or3 oversize, BC actual stored. No MOS/VDU/file/wait/allocation/rearm from IRQ.
The existing fixture's small assembly wrapper is a recipe, not a C callback
scheduler. Keep destination/callback/code live until positive terminal state.
TX source release, RX completion and storage durability are separate endpoints.

Issue ordinary D8 protocol1 operation8 with flags1/reserved0, sourceID:u16,
offset:u32,count:u16, little endian (14B payload/19B complete VDU request).
INFO27 reports512; INFO26 reports8 for the old8B method. Request TX remains
admitted while this independent RX arm is pending. Reuse the normal output
path; there is no transport-mode switch for ordinary unaware applications.

One arm/one producer at a time, no generic success token. Keep a single-block
source immutable for the complete logical read, and use ordinary foreground
VDU context23,0,254,0 with an ordered GP fence as in the worked example. Repeated
buffer-write commands append blocks; upload a single block once. No async
VDPlet worker, echo, suppression or redirection in this slice. Source60001 is
our fixture's ID, not a mandatory consumer allocation; use each checked own ID.

Successful bulk90h payload bypasses the keyboard callback. Preserve the
consumer's existing tagged0x81 management/error callback and genuine keyboard
handling. Operation5 READ16 remains present in the exact producer next to6/8.
A tagged source ERROR before90h leaves the receive arm live. Timeout/error is
not cancellation: no rearm/retry/free/reuse/normal unload while uncertain.
Stop resident and return custody to Extender for supported preservation/reset.
An intact oversize frame is wholly discarded and terminal, with zero stored.

## Small selected cases and completion

Rally: retained584B TIM002 stats into ordinary single-block50307, actual
timingDumpBuffer helper/control and isolated counted copy, file chunks256/256/72.
Verify the retained header/exact file hash and originating state provenance;
the stats have no generation field (4503 belongs to their source state). No race/module
or render/FPS test. Keep original helper untouched and preserve retained input.

6502: an isolated actual BRClient/drain_disk adapter slice,40B descriptor then
512B payload from the retained ESP32-hosted export seam. Keep semantic identity,
length and existing persistence-before-ACK if persistence is exercised. Current
eZ80-local persistence needs no receive and must stay unchanged. Add only the
small counted branch: existing br_begin accepts1..6 and expects legacy success.
No game boot or552B frame/new VDP producer is required. If retained runtime
oracles no longer fit, return the smallest concrete helper alternative first.

Each owner writes its small task, source/app/input pins, positive lifetime and
byte/file oracle, normal return/cleanup and concrete usefulness judgment. Use
ordinary compiler/bench FIFO and Extender ownership. One finite comparison
suffices, no millisecond tuning or broad adoption. Return evidence to UART;
we collate and stop this goal once the selected trials support practicality.
