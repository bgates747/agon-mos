# RX-006 — Practical feasibility established

The selected consumer owners are comfortable that the existing counted-return
method would work if adopted and simplify their code. The prior Console8
synthetic pass supplies physical correctness evidence for the underlying
receive path. This meets Brandon's explicit stopping rule; further application
ports, firmware integration and timing sweeps are not completion requirements.

No new firmware, game code, card contents or boot scripts were changed for
RX-006. No compiler, emulator or physical bench was reserved or used. No new
performance measurement is claimed.

## Concrete benefit, assessed against each owner's source

* **Rally:** its retained post-race export can replace 32,724 READ16 exchanges
  with 129 serialized reads of at most 512 bytes. Two stable source buffers hold
  64,864 and 584 bytes; rounding each separately gives 127 + 2 reads. Request
  and reply traffic falls from 948,996 to 68,286 bytes, excluding discovery and
  unrelated commands. The owner explicitly accepts this as useful without a
  game port or another benchmark. This is an export improvement, not race FPS.
* **6502:** the retained ESP32-hosted machine's disk exporter can replace 69
  eight-byte pulls with two receives: a 40-byte descriptor and a block of at
  most 512 bytes. For a full block, request/reply traffic falls from 2,553 to
  596 bytes. Existing durable write, sync, reopen, readback and exact ACK remain.
  The owner explicitly accepts feasibility. Its current eZ80-local persistence
  already has the bytes locally and needs no UART return service.
* **VDPlet:** the exact existing producer supports these operations without a
  new feature or build. A larger logical read can use successive 512-byte
  responses while its source stays immutable. One ordinary buffered upload
  must create the entire source as a single block; repeated upload commands
  append blocks, which this read operation refuses.

These are independently checked source-derived counts, not measured speed,
CPU, latency or FPS improvements. Exact owner reviews and source pins are
preserved in [evidence](evidence/snapshot-manifest.json):
[Rally](evidence/rally-review.md), [6502](evidence/6502-review.md),
[VDPlet](evidence/vdplet-review.md). All 37 supplied source/artifact pins
matched when independently rehashed before this report was written.

## What is actually tested

[RX-005 Console8 R0067](../RX-005/hardware-r01/RESULT.md) passed the existing
synthetic cases up to 512 bytes, exact copied data and guards, callbacks,
unarmed/oversize discard, admission, error-retains-arm, repeated rearming and
real keyboard input during a receive. Its foreground counter shows that work
can continue; it is not calibrated CPU capacity. Both Flexe engines had passed
the same frozen fixture earlier. Those results retain their original identities;
they are not relabeled as RX-006 runs or consumer executions.

The receiving MOS source is Eirene commit
`8db14b221137a6d2a3bc6f0cdeac5c8ee9361db0`; the exact producer BIN SHA256 is
`7d09dfeac4e7a1654dca486a8e86cd7b5d283f0d53bac0ab128cb8dd33e10087`.
The tested VDP source export is pinned by manifest SHA256
`4ce246a3da8d74fe54dca561c28573cb249ec43a11f50bc690977a16245f7af2`;
the separately published implementation commit is not a fresh-build claim.

## Common adoption contract and resolved planning caveats

1. Keep one producer and one admitted receive at a time. Arm before requesting
   data; check terminal state and exact stored/announced counts before using it.
   Success frames have no transaction token. Preserve semantic generation and
   disk/export identity checks above the transport.
2. Keep both destination and callback code live until actual completion. A
   tagged source ERROR does **not** cancel the arm. Timeout, unrelated INFO or
   local bookkeeping cannot free it. Preserve the documented residence/reset
   boundary after uncertainty; do not automatically retry or return to MOS.
3. Keep the source immutable across the whole logical export, not merely each
   chunk. Receive completion means bytes in RAM, separately from outgoing
   source release, wire drain, rendering or durable disk acknowledgement.
4. Retain legacy management/error handling. Bulk data no longer needs the
   keycode carrier, but this first producer still uses it for control/error
   replies. An optional receive callback only publishes a flag; foreground code
   performs file I/O and other work, with UART interrupts serviced.
5. The 6502 client's existing `br_begin` accepts operations 1..6, so adoption
   needs a small local counted-transport branch. Remote ERROR must not fall
   through its ordinary safe filesystem-retry path while the receive is live.
   This is an identified future adapter requirement, not an implemented app
   change or a newly discovered defect in the MOS receiver.

All three reviews agree that these requirements fit the narrow retained export
seams. None requests a larger frame, cancellation framework or extra benchmark
as a condition of its affirmative feasibility judgment.

## Stopping point and unrun work

The proposed 4, 8, 16, 32, 64, 128, 256, 1024, 4096 and 8092-byte sweep was
**not compiled or run**. Its initial source draft is preserved privately with
[hashes and explicit unqualified status](deferred-draft.json), not distributed
as a working fixture. [Size expectations](size-expectations.json) are arithmetic
only: 1024/4096/8092-byte logical reads require 2/8/16 replies; the last 8092-byte
chunk is 412 bytes. The 8092-byte operation is not one large wire reply. Actual
long-source allocation, integrity and timing remain unmeasured by this sweep.

Extender was consulted before any Olimex reservation and told to stop new work
solely for this goal once both consumers accepted feasibility. A compatible
EMOS receiver/VDP/input/recovery composition is a separate integration task;
existing EMOS does not gain syscall 26h or the 90h parser by assumption. No
Console8 image was installed over the shared Olimex setup. Existing owners and
queued runs were not interrupted.

Brandon's later instruction says to stop as soon as selected owners are
comfortable this would work and make their code easier. The existing physical
integrity result plus both concrete affirmative consumer reviews meet that
criterion. Additional sweeps or ports are deferred, not recorded as passed.
No performance optimization, prototype rollout or adoption is selected here.

## Extender's closing source assessment

The [final owner return](evidence/mail/2026-11-07_23-30-18_linux-extender_rx006-existing-emos-composition-limits-one.md)
confirms no new correctness obstacle in the feasibility argument. Retained EMOS
`a25f` and temporary `1e4e` implement neither syscall 26h nor raw 90h dispatch;
the existing tagged keyboard route is not a substitute. Future integration needs
the bounded receiver and registrations while preserving P4 input and route
ownership. TX and RX admission must stay separate: arming RX must still permit
the outgoing producer request. The temporary image has only 120 ROM bytes free;
the standalone receiver's 378-byte code/22-byte BSS delta is not an EMOS fit
result. No splice, build, reservation or physical run began for RX-006. The goal
remains closed; current bench custody and independent work are unchanged.
