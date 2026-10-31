# Olimex/WROOM direct wiring — ground subsequently confirmed at pin3

All1000requests returned the correct eZ80 identity, across ten WROOM restarts,
using unchanged firmware and timing. This setup was reliable in the observed
run, compared with325/1000correct previously. It does not establish which
physical change caused the improvement or prove flash/high-speed operation.
Olimex MOS was untouched.

Author confirms BLUE WROOMGPIO26 to ZDI4/TCK(lower middle), GREEN GPIO27 to
ZDI6/TDI(lower left), no inline resistors and the same higher-quality breadboard.
**Subsequent Author correction: ground had NOT moved during this run; it
remained on upper-middle pin3.** The initial pin5 report was mistaken. Original
raw metadata and filename are preserved; the campaign parent contains
operator-correction-run-002.json. The pin5-only change is tested separately in
run-003-ground5-only-change. Do not treat this earlier clean result as evidence
of operation through pin5.

Author believes signal functions unchanged and insulation colors simply changed
to match upstream. The prior325/1000run had33-ohm resistors; this clean run had
none. That earlier improvement does not isolate individual physical changes.

Firmware unchanged: archived identity-onlyv3, SHA256
abaa0bc98876389f14a2f92a47115a5e95a5009dd1975f61a026d74978984fd9.
S commands with10us edge delays and50ms firmware gaps. Same ten WROOM-only
restart epochs of100reads, no Olimex reset. Host runner metadata now accepts
physical wire colors, resistor value, ground pin and connection note; reader
firmware and serial command/read schedule were not modified.

| Measurement | Result |
|---|---:|
| Correct product0007/revisionAA |1000/1000 (100%)|
| Wrong product/revision |0/1000|
| Raw07 00 AA 1C |999|
| Raw07 00 AA 18 |1|
| First request after WROOM restart correct |10/10|
| Local driven-bit checks passing |13000/13000|
| Correct identities per100-read epoch |100 in every epoch|

Status1C versus18 differs only by bit2, the IEF1 interrupt-enable flag in the
upstream CPU getIEF1flag implementation. Device identity is unchanged; this
status difference is not counted as an identity failure. Total runner time
106.577seconds. Zero identity failures gives a one-sided95% binomial failure
upper bound0.299%, conditional on independent stationary requests. Reads on one
bench may correlate; this is not qualification across boards or conditions.

No CPU halt, Olimex reset, RAM access or MOS erase/program. Both WROOM output
drivers released afterwards; BLUE(clock) and GREEN(data) both sampledHIGH.
Serial closed, no polling; WROOM quietv3 remains. No P4 operations in this run.
No Console8 programming or target change authorized by this result.

Raw console, per-read records, JSON and runner snapshot retained at
build/olimex-wroom-breadboard-20261030/run-002-ground5-direct and its parent
onPi/Oryx. TranscriptSHA256
61ffa8958482d92b8d5a8c12cceceda678e53692fdaa22b93d9e775c33a481ed.
Upstream diagrams/provenance: ../agon-extender/docs/mos-recovery/.
