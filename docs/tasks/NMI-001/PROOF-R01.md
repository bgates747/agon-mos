# NMI-001 first proof

Brandon selected this bounded proof in the TRS-80 chat, human message
`01a1fbbd-8ab1-7470-a5ee-d7fe7fc671a0`. M304 remains paused for review. Use the
released RC3 source at `97311c437093e416342a6c836cf9914f2ced027d` and its native
AgonDev toolchain. Work in an isolated source export. The proof uses private
MOS test commands and a synthetic guest. Public syscall numbering, a general
caller ABI, guest `EI`/`HALT`, and return to a live MOS session remain separate.

## Pass criteria

- Eight real modeled or hardware watchdog NMIs arrive from a Z80 instruction
  loop running under `DI`. The mixed-mode frame stays on MOS's long stack.
- Each yield reaches a normal ADL host continuation. Stock MOS VBlank service
  advances the MOS clock inside every enabled host window.
- The guest PC and cycle-local register/memory relationship match the exact
  interrupted instruction boundary. Each resume retains `DI`, the expected
  register and flag sentinels, the guest bank and untouched short-stack guards.
- Armed exit disables application dispatch and invokes the resident reset
  policy. Fresh startup sees the watchdog disabled and the hardware watchdog
  reset cause before the postboot witness permits app memory reuse.

## Execution limits

One serial Pi compiler job per candidate revision, with a five-minute outer
bound and the compiler FIFO admission. Save source, binaries, maps, and
inspection results. Use one finite Oryx Flexe cell with an exact watchdog-capable
runtime and actual VDP firmware, a manual or injected CLI invocation, a 90-second
host watchdog and owned teardown. Stop and retain evidence on unexpected failure.
Real F92 testing requires a compatible physical target and the applicable
Console8 or Olimex operating procedure. Record model and physical results
independently. Current production, game code and startup scripts stay in place.

Watchdog reset-mode switching while already armed is a hardware question. The
retained FX-291 model deliberately makes live control changes effective and
services repeat NMIs by an explicit reload. A model pass on these operations
cannot establish the same behavior on silicon. The test has a finite host
bound and a resident recovery route. A real run needs a working board-reset
recovery path as well.
