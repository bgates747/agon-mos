# NMI-001 first proof result

**The bounded proof passed in Flexe JIT and on Console8.** The isolated
RC3-based MOS candidate took eight watchdog NMIs from a synthetic native Z80
loop with `DI` in effect, serviced normal MOS interrupts, resumed seven times,
and rebooted after the eighth yield. Fresh startup accepted an explicit
`nmicheck` and reported `NMI001 POSTBOOT WDT 20 STATE 0` followed by
`NMI001 POSTBOOT PASS`. M304 remains paused for review.

## What was observed

- Each `NMI001 YIELD` marker followed checks of the mixed-mode `02h` frame,
  saved PC and the matching relation between guest HL and guest memory. Each
  sample showed progress and `IEF2=0`, which reflects the guest's interrupt
  enable state at NMI entry. The proof checks guest bank, accumulator/carry and
  primary, alternate and index register sentinels. It checks all 16 guard bytes
  around the separate short stack and the guest's recorded SPS value.
- The dispatcher parked the hardware return frame and used `RETN.L` with an
  ADL frame to enter the host continuation. Each marker required progress of
  the ordinary MOS clock after enabling IRQs and waiting for VBlank on the
  foreground long stack. The CLI keyboard commands before and after reboot
  traveled through the real VDP firmware in Flexe's modeled session.
- After the eighth host window the candidate wrote an eight-yield witness,
  disabled app dispatch, selected watchdog chip reset and reloaded the
  watchdog. A second normal boot banner and CLI prompt appeared without a
  host-requested reset. `nmicheck` checked WDT enable clear, watchdog reset
  cause set, idle proof state and the retained witness before reusing the
  first two bytes of guest code RAM. The boot entry also gates initialization
  if it sees an enabled watchdog.

The proof used a private fixed guest and CLI controls. It establishes the
mechanism for that case and leaves the public API, generic app ownership,
non-DI guest support and arbitrary register-state coverage for later work.

## Flexe run and build evidence

- Eirene base `97311c437093e416342a6c836cf9914f2ced027d`. Isolated AgonDev
  build produced a 102,035-byte MOS with CRC32 `3EB916B1` and SHA-256
  `b451861d775a0c930dd51848b5ab4c535010a4797fd80b787232822fe42406cf`.
  The flat MOS matches the linked ELF converted back to binary. Pi compiler
  generation 1116 was released. [Proof source](../../../experiments/nmi001-proof/)
- Oryx checkout 547 reached the initial CLI. The runner waited for a baud
  banner absent from the non-debug build and issued zero commands. It timed
  out at 90 seconds and released cleanly. Checkout 548 used the corrected
  passive prompt detection and the same ROM, runtime and VDP. The first actual
  guest run passed in 11.3 host seconds including startup and typed commands.
  The backend reported no failure, unhandled, unregistered or unmapped events.
  Both leases released with fresh whole-host idle evidence.
- [First attempt log and wire](../../../build/nmi001/proof-r01/oryx-evidence/),
  [passing result](../../../build/nmi001/proof-r02/oryx-evidence/result.json),
  [passing raw wire](../../../build/nmi001/proof-r02/oryx-evidence/last-run/),
  [release](../../../build/nmi001/proof-r02/oryx-release.json),
  [ROM, ELF and map](../../../build/nmi001/proof-r01/source/bin/),
  [linked listing](../../../build/nmi001/proof-r01/listing.txt).

## Console8 hardware evidence

Brandon manually ran the proof on November 20, 2026. The photo shows
`nmiproof`, `START`, `YIELD 1` through `YIELD 8`, a second MOS boot banner,
and then `nmicheck`, `NMI001 POSTBOOT WDT 20 STATE 0` and
`NMI001 POSTBOOT PASS` at the returned CLI. This is physical evidence for
repeated watchdog rearm, the guest and VBlank checks behind each yield marker,
and the armed exit path on this Console8. `20h` records watchdog reset cause
with the enable bit clear, and the proof checks that before reusing guest
code RAM. The result covers this one synthetic workload and board.
[Original Console8 photo](evidence/console8-proof.png)

- The photo is a byte-for-byte copy of Brandon's attachment, SHA-256
  `431c81218a6ca4456020a1cb6865567cc3060d9295d6ea12fcf2ab83da2ed585`.
  Human report and attachment were in TRS-80 chat
  `01a0c63b-cd79-70e1-a522-0cea96165f6a`, message
  `01a1fbdb-f568-7901-adbe-f2fba70ed087`.
- The staging record verified the candidate `mos-nmi001.bin` on the AGONC8
  card in `/test/nmi001`, SHA-256
  `b451861d775a0c930dd51848b5ab4c535010a4797fd80b787232822fe42406cf`.
  That matches the model-tested image in the
  [Console8 package](../../../build/nmi001/proof-r01/console8/). The hash is
  a card-file verification. There was no independent installed-ROM readback.
- The visible banner strings are Agon Platform VDP `2.16.0` and VDPlet
  `0.1.3-alpha`. Exact VDP image identity is unknown. Brandon reported
  restoring stock MOS after the photo. The restored build has no recorded
  readback here.

## Startup identity for the next custom candidate

Brandon asked for custom MOS builds to identify themselves at startup. The
tested proof inherits the `3.1.0 RC 3 RFC25 + startup fix` banner, which does
not identify NMI-001. Keep the base version visible and append a clear
experiment or build suffix such as `NMI-001 proof R02` on the next custom
candidate. Check the visible startup string during that candidate's planned
qualification. The archived result applies to the original proof image.
