# Counted returns would simplify our retained ESP32 disk exporter

Yes: the pinned26h/90h interface is sufficient to replace dozens of small data
pulls with two exact receives, keeping our existing disk descriptor and durable
ACK unchanged. I am comfortable that this would work and simplify that consumer
if adopted with matching firmware and the lifetime rules below. No full-game
port, extra bench cell or millisecond optimization is needed for this bounded
source-feasibility judgment. This selects no implementation or adoption.

1. **Which version benefits.** This is the preserved ESP32-hosted machine's
   exporter, not current eZ80-local persistence. The latter already owns its
   track bytes and writes them through MOS with no UART return at all. Existing
   DSK work, queued normal-app qualification and accepted packages are unchanged.
   Exact consulted source hashes are in RX-006-ADOPTION-R01.json. MOS source is
   Eirene8db14b221137a6d2a3bc6f0cdeac5c8ee9361db0, not agon-mos's separate
   documentation checkout; VDP source is the qualified VDPL036 export.
2. **Exact seam.** build/cpu003/playable-r03/app/mos_app.c::drain_disk invokes
   EXPORT with guest quiescent, reads RESULT1792/40B into descriptor, validates
   its mounted drive/image/epoch/generation/token/length, then reads RESULT2048/
   block.length into existing payload[512]. It calls unchanged persist_apply,
   updates ACK1856 with the exact40B descriptor, and invokes ACKNOWLEDGE only
   after successful write/sync/close/reopen/exact readback. Swap/reset/exit may
   not bypass dirty draining. Two counted reads fit existing destination arrays;
   neither a552B combined frame nor an extra full-image buffer is required.
3. **Concrete reduction.** One full descriptor/block currently takes69 eight-
   byte pulls (5+64), or276 READ16 exchanges (20+256). The counted path takes2
   requests,40B then512B. Source-derived request/reply totals are1311/1242B for
   eight-byte pulls,4692/3312B for READ16 and38/558B for counted replies. Totals
   are2553/8004/596 wire bytes. EXPORT/RUN/ACK, discovery/fences, genuine keys,
   TX lifetime and filesystem IO are excluded. These are not measured latency,
   CPU saving or game speed. Exact odd payload lengths no longer need READ16's
   spare second backing byte.
4. **Receive discipline.** Establish the clean ordinary output/parser route and
   paired capability before issuing work. Arm static owned descriptor or payload
   through syscall26h before requesting D8 operation8. Foreground ADL1/MBASE0,
   valid nonwrapping span, IRQ service and one outstanding producer/arm apply.
   AdmissionA0/1BUSY/2invalid must be checked; BUSY does not authorize replacing
   the prior destination. Optional callback may be NULL; if used it only sets
   a flag, with no MOS/file/wait/rearm work. Read the volatile terminal state
   before consuming published counts/data; require announced and actual count
   exactly40 or the validated block length. No short/oversize result permits ACK.
5. **It needs a local transport branch.** The current BRClient br_begin admits
   only operations1..6 and expects a legacy success packet. Simply requesting8
   through it would be rejected or leave the wrong pending state. A future
   counted branch must retire its local bookkeeping on actual counted completion
   and preserve serialized token rollover/management semantics. It can remove
   per-eight-byte mailbox copies, waits and tail handling from bulk data. It
   cannot remove every private keyboard callback: this first producer still
   uses tagged legacy ERROR and existing management/control replies. Ordinary
   keys continue to the existing handler;0x81 is keycode/private carrier,0x88
   is repeat/rate/LED status. Bulk90h bytes are not synthetic keyboard events.
6. **Error and late-reply boundary.** A tagged source ERROR occurs before90h
   and DOES NOT retire the MOS arm. A future adapter must mark that situation
   transport-pending/uncertain, not map its small error number to the current
   ordinary storage-failure/F7 retry path. Keep callback/destination/code live;
   no rearm, automatic retry, reused stack destination or successful MOS return.
   Truncation/timeout similarly requires the existing honest quarantine/reset
   boundary unless positive retirement is established. Intact oversize is fully
   discarded and terminal; no partial data is stored. An unarmed intact frame
   is discarded without changing a previous result. Existing INFO0 teardown
   bookkeeping does not cancel this separate MOS receiver. No new cancellation
   feature is required for the bounded feasibility conclusion.
7. **Snapshot and identity.** Counted frames have no generic request ID, so one
   ordered producer and one completed arm at a time are essential. Do not resume
   the guest, mutate/rebuild RESULT or request another EXPORT between descriptor
   and payload reads. The producer validates one consolidated buffer, snapshots
   it and writes header+body in one shared HAL-locked operation, including the
   lock used by ordinary writers. Disk semantic token/generation and exact ACK
   remain above transport. Receive completion means bytes in RAM; it is neither
   receiver retirement after uncertainty nor durable disk persistence.
8. **Confidence and limits.** I independently read the pinned arm/parser and
   producer source. UART's R0067 Console8 report supplies attributable synthetic
   integrity evidence, not our application execution or a hardware wire trace.
   Existing IRQ-masked guest chunks and IO003's unresolved partial MODE/parser
   observation remain separate integration limits. Pausing/quiescing this
   export path and servicing IRQs is suitable; a continuous burst into a running
   mixed-mode core is not qualified by the512B allocation. Current Olimex EMOS
   and our Apple F6 image do not acquire these capabilities by assumption.

No source consumer was modified, no compile/emulator/hardware run or reservation
was made, and no firmware/profile/card was deployed. Keep the current eZ80-local
writeback and queued physical work first. Incremental and fixed388ef52 cumulative
performance comparisons are unavailable. This source-grounded positive judgment
is enough for RX006's stated practicality review; it requests no further sweep.
