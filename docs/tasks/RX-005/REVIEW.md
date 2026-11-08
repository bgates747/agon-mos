# RX-005 — Emulator-qualified counted return trial

Applications can now ask the VDP for a block of data and receive it directly
into their own RAM while doing other work. The first trial passes with actual
MOS and VDP firmware running in Flexe. Existing keyboard events still arrive;
bulk data does not have to masquerade as key events. No games were changed.

Brandon reviewed this result and selected manual Console8 qualification on
November7. The exact test package is now [staged on the card](hardware-r01.md).
No consumer prototype has been distributed, hardware run performed or release
created. The results below remain emulator evidence.

## What passed

Oryx373 ran the same finite fixture in both JIT and interpreter engines. Each
passed in about 9 seconds including startup and host teardown:

- 32 counted frames containing 2397 verified payload bytes, with sizes 0/1/2/8/
  16/17/127/255/256/512 and header-looking data values.
- 30 completion callbacks, one null-callback receive, guarded destination RAM,
  exact actual counts and preserved BC/DE plus the explicitly tested disabled
  interrupt state.
- BUSY/invalid admission, complete unarmed-frame discard, complete oversized
  reply discard without payload writes, repeated rearm and source rejection
  followed by a valid response to the same still-live receive arm.
- A genuine SDL/PS2 key down/up while a receive was armed; data generated no
  spurious test key events. Ordinary poll replies remain aligned.
- Source buffer/keyboard callback retirement, sequential R0001.log and clean
  return to MOS. Both final model snapshots show zero TX drops/RX overruns;
  backend failure/unhandled/unregistered/unmapped counters are zero.

The stopped host oracle independently checks framing/payloads through the
ordered GP34 cleanup fence. Startup key traffic and later CLI tail remain
archived with their separate scope. Eight damaged/inconsistent manufactured
transcripts are rejected. Foreground work counters 3699/14027 prove work occurred
while waiting; they are **not** calibrated CPU savings or comparable hardware
performance measurements.

## The issue found and corrected

The first MOS implementation used one byte per receive interrupt. It passed
through 17 bytes, then stalled on 127. A matched diagnostic cut recorded modeled
FIFO drops increasing from 0 before that case to 9 afterward, although the VDP
emitted the complete frame. The original failure and raw counters are retained.

MOS now consumes at most 16 currently available bytes per interrupt while a
counted frame is active. It returns at an empty FIFO, completed frame or budget
limit; it never waits for a future byte. Ordinary legacy packets retain their
one-byte path. With the same fixture source and unchanged VDP/runtime, both
engines pass all cases and final counters remain zero. No ring, queue, retry,
cancellation engine or VDP pacing workaround was added.

Earlier harness failures are separate: an omitted raw-SD-image launcher option
prevented invocation; then serial-console mode caused a correct VDP admission
refusal. The fixture now explicitly selects normal VDP operation. These failures
are not labeled receiver passes or firmware defects.

## Size and source layout

MOS adds **378 executable bytes and 22 BSS bytes** to exact released Eirene RC3.
The feature lives in one new assembly file, with small syscall/IRQ hooks in two
existing files. Startup and serial-TX compiled objects match the donor, and the
48-slot startup invariant passes. The bounded drain costs 34 bytes/one RAM byte
over the initial receiver. Eirene keeps its existing AgonDev toolchain.

The VDPlet-owned producer adds **608 image bytes and no static DRAM**. Its
temporary frame is at most 515 bytes. The reported native 48-byte producer and
144-byte dispatcher frames are static function frames, not whole-task stack
peaks. VDPlet owns all VDP edits; UART owns only MOS and this original fixture.

The selected disabled VDP control remains the original c7978a74/24d76d14 image/
ELF. A rebuilt disabled companion has identical allocated sections; nonloaded
debug changes explain its different embedded ELF hash/checksum. Both identities
and the original failed exact-image gate are retained, without normalization.

## Exact trial pins

- MOS donor: Eirene RC3 commit 97311c437093e416342a6c836cf9914f2ced027d.
- Trial MOS: 101257B, CRC32 **3933C3ED**, SHA256
  `40dc3d17a4f856c329e118b0376ff26f33085ef00410a26cda5739d4396589ea`.
- Fixture: 16036B, build 9c72616d7f4a4ef7, SHA256
  `6f79d47e615f2b4afca146a6c4ccf62677bf5c33b53b67c2f10b6ca3a729b949`.
- VDPlet counted producer: 1100320B, SHA256
  `7d09dfeac4e7a1654dca486a8e86cd7b5d283f0d53bac0ab128cb8dd33e10087`;
  ELF `2918727ad256389e3ac0d9074e736acdbbde3a9ce6f95a280fd7fa3673d6fd92`.
- Flexe FX224 host-r03: frontend bad83f54/backend d77a7305, exact full hashes in
  trial-evidence/oryx-runtime-inputs-r01.sha256. Existing SDL injectore223b8f5;
  actual mapped system SDL3.4.2 verified. No emulator code was changed.

The final source freeze/binaries are in build/rx005/trial-r07; the full MOS
source manifest is retained there. The exact MOS [patch](proposed-mos.patch),
[API/wire contract](wire-contract.md), [build proof](trial-evidence/mos-fixture-build-r07.json),
[passing receipts/raw traces/reports](trial-evidence/pass-r05/) and
[artifact hashes](trial-evidence/review-artifacts.json) make the trial reviewable.
The full raw archive is build/rx005/qualification-r05-results.tar.gz; the matched
loss diagnostic is qualification-r04-results.tar.gz. The MOS source is now committed/pushed on the isolated fork branch at
8db14b2; fixture and qualification evidence are committed/pushed in this project
at72528f7. This is an experimental branch, not an upstream allocation or release.

## Limits and stop

This is firmware-running **emulator** qualification, not Console8/Olimex proof
or a throughput/CPU benchmark. The producer is qualified only to 512 bytes per
reply. The private 26h syscall and 90h reply are not upstream allocations.

One receive owns its buffer/callback until positive completion. Source errors
do not retire it; a truncated or uncertain transfer still requires reset. No
cancellation or automatic resynchronization is claimed. Discovery/error control
still uses the old small management adapter, while counted bulk data is separate.
The first producer uses the ordinary VDP route with its async worker disabled.

All leases are released and no target process is held. Brandon has selected the
manual Console8 test; see hardware-r01.md. Protocol expansion and consumer
prototypes still require the next review after physical results.
