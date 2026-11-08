# RX-005 — Console8 R0067 hardware pass

The first physical Console8 synthetic run passes. Returned `R0067.log` identifies
fixture build9c72616d7f4a4ef7 and ends with **RX005 SUITE PASS**. All staged immutable
files match the deployment and manual-start correction. The card was read only;
its current boot script, firmware files, counters and reports were not modified.

## What the run establishes

* All ten0/1/2/8/16/17/127/255/256/512-byte cases passed exact payload and guard
  checks. Register preservation and the explicitly exercised disabled-interrupt
  state checks reported no failure.
* Complete unarmed discard, NULL callback, BUSY refusal preserving the first arm,
 512B overflow into capacity511 without destination writes, invalid NULL/wrap/
 capacity, source-error retaining the arm followed by a valid reply, and16 repeated
 positive rearms passed.
* A real key press/release arrived while the bulk receive was armed; the512-byte
  response then completed. Recorded key counts are1/1, callbacks30, regfail0 and
  ifffail0. Foreground work counter3477 proves waiting foreground progress, not
  calibrated compute capacity or a timing comparison.
* The passing frozen fixture's control flow represents32 counted frames and2397
  returned payload bytes:1868 bytes are compared after valid copies, while529
  bytes are intentionally discarded (17unarmed and512overflow). These totals
  are source-derived; there is no hardware wire trace or per-frame hardware log.
* The installed MOS prefix CRC guard3933C3ED/101257B passed before opening the
  report. VDP capability and counted responses were exercised, and the staged
  VDP image matches7d09dfea; installed VDP was not cryptographically read back.

The report records LCTL03/IER01/issued1 for the unchanged same-value IER snapshot.
This is not a hardware overrun counter. Exact-byte/callback/guard PASS must not
be described as a measured zero-UART-error result. The fixture records SUITE PASS
before closing its report; its subsequent RETURN PASS print/CLI return is not
persisted in that log. Brandon reports the run looked like a pass.

## Custody and identities

Console8 volume AGONC8 UUID8658-1C23. Only new R0067.log and expected next.txt68
are found in the appliance; all other appliance files match the corrected
staging hashes. Current autoexec SHA1538b7a7 differs from the previously restored
file and was preserved untouched, without assuming how or why it changed.

Both project machines retain `build/rx005/hardware-r01/returned.tar.gz`,1223482B,
SHA256 `81375b25777bede32478b384f11bab5813d1024e2484b05394eef23c18ba0aa6`.
UART verified its hash and archived file contents independently on Pi.
[Raw report](returned/R0067.log), [capture receipt](returned/capture.json),
[checked interpretation](returned/analysis.json), [next counter](returned/next.txt).

This is one finite hardware integrity pass of the same MOS/VDP/app as the two
Flexe engines. It is not an EMOS/Olimex result, sustained-throughput/CPU/latency
benchmark, new protocol allocation or release. Dedicated test firmware need not
be restored solely to close this run. No new card deployment, firmware flash,
game change or consumer prototype distribution was performed during inspection.

## Next boundary

The hardware-integrity question for this first trial is answered positively.
Return to Brandon for review before distributing prototypes or assigning an
application pilot. The proposed first useful consumer comparison remains Rally's
retained post-race export, keeping bytes and its semantic completion oracle
matched; that is a proposal, not an assigned consumer task or demonstrated gain.
