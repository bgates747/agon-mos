# RX-006 — existing counted producer is sufficient

The exact already-tested512B producer supports the proposed short/long logical
size sweep. An8092B source can use one ordinary buffer upload and16 serialized
reads, with no VDP rebuild or larger wire reply. This is source feasibility;
UART/Extender still own the concrete receiving-ROM/bench admission and finite
trial. Stop at useful correctness evidence and selected-owner confidence,
without a performance optimization program.

## Authority and exact component

1. RX6-001: Independently read direct human items in UART turn
   01a1b959-0dff-7982-baa9-04147581e35b: message
   01a1b959-0e46-7053-85e3-63885b5df76c selects own short/long checks and normal
   Olimex scheduling;01a1b95b-772a-7563-bac1-5c3cc459bd71 selects bounded
   practicality/correctness and an early useful-feasibility stop. No full-game
   port, optimization, broad prototype release or startup edit follows.
2. RX6-002: Rehashed unchanged selected BIN1100320B
   7d09dfeac4e7a1654dca486a8e86cd7b5d283f0d53bac0ab128cb8dd33e10087,
   ELF25049816B2918727ad256389e3ac0d9074e736acdbbde3a9ce6f95a280fd7fa3673d6fd92
   and exact export4ce246a3. Paths/hashes in adjacent feasibility JSON. Features
   pixels/borrow_rows/read_bytes/text96, async_worker=false,counted_return=true,
   version0.1.1-alpha. Published sourcea83d912 is isolated; exact tested export
   is authoritative for these retained artifacts, not a new-build hash claim.

## Supported source and sequencing

3. RX6-003: Stock BUFFERED_WRITE consumes a u16 length, so8092 fits. Clear an
   exclusively owned buffer ID first, then ONE write command for the whole
   logical payload. bufferWrite appends one stream per command; repeating
   writes under an ID creates multiple blocks, while countedReturn requires
   exactly one nonnull block. Splitting transmission of the same declared
   payload among transport calls is different from issuing more write commands.
   BufferStream uses PSRAM; allocation/receive timeout/current available memory
   still need the selected finite case. No unconditional successful allocation.
4. RX6-004: D8 op8 body14/flags1 takes ID:u16,offset:u32,count:u16. Bounds are
   checked as offset<=size and count<=size-offset; reads do not consume a stream
   cursor. Counts<=512 and arbitrary valid repeated offsets are supported.
   The selected logical sizes use1/2/8/16 replies for<=256/1024/4096/8092;
  8092 is15x512+412, final offset7680. Keep INFO27=512. Source unchanged through
   the entire logical read: per-request copying does not make a changing source
   atomic across16 chunks. Do not clear/replace it before positive completion.
5. RX6-005: Arm the real receiver before each request, issue exactly one read,
   validate actual count/payload/callback and complete it before the next chunk.
   Success is raw90/u16/payload without a token. Existing tagged ERROR has the
   request token and retains the arm; do not blindly rearm or reuse storage.
   Timeout is unknown outcome, not cancellation or replay authorization.
   Preserve borrowed TX source until its actual send completion and RX storage
   through its real callback/completion contract. A successful VDP writer return
   is not UART TEMT, receiver completion or an entire logical transfer commit.
6. RX6-006: Each read request is19wire bytes and reply adds3header bytes. Thus
  8092B logical read uses16requests/16headers:8140reply bytes,8444total request+
   reply bytes, excluding upload/setup/ordinary health/key traffic. These are
   source arithmetic, not measured throughput. A single ordinary8092 upload
   has an8B command header. Keep setup/upload/verification outside pure-TX
   intervals and label whole operation timing separately.

## Context and bench tuple

7. RX6-007: The current producer requires normal stock23,0,254,0 command route,
   original UART input/output, active context, no echo/redirect/suppression/
   printer/teletext or registered callbackBuffers, and no busy runtime/live
   async session. A MOS keyboard callback is a separate receiving-side hook;
   do not confuse it with VDP callbackBuffers. An ordered ordinary query after
   upload can show parser progress; it does not verify payload equality or
   guarantee op8 context admission. Compare the returned deterministic bytes.
8. RX6-008: Usable owner producer component is exact7d09/2918 classicESP32
   mainboard VDP above. It is not P4 firmware, an async035 image or permission
   to replace a current bench tuple. The receiving MOS/EMOS must actually
   provide26h and90h handling. Retained a25f CP10 tagged-reply compatibility
   does not establish counted receive support. UART and Extender select the
   smallest supported receiver/fixture/recovery composition; preserve actual
   current owner, startup, route, rollback and normal FIFO. Source compatibility
   does not authorize Console8 MOS installation over live EMOS/P4 controls.
9. RX6-009: Existing both-engine373 and manual Console8 R0067 integrity evidence
   are retained. No VDP correctness obstacle to this serialized <=512B method
   was found in the inspected path;8092 logical upload/read has not been newly
   exercised here. No new producer/renderer feature, ABI, size limit, owner
   build/run, card operation or consumer migration is selected. UART owns any
   new own-suite execution; report concrete correctness errors to VDPlet.

[Source/artifact pins](RX006-PRODUCER-FEASIBILITY.json) identify exact exported
producer/dispatcher/buffer/serial code and installed HardwareSerial/HAL source.
No code from those donors is imported by this advice.
