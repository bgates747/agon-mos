# RX006 completion confirmation — explicit SAVE radix

Existing Brandon-selected RX006 goal, same ten-size and36-cell fixture. Actual129
has a durable original SD log passing every size/cell and SUITE PASS, but the
host completion chain timed out. [Source diagnosis](actual129/README.md) finds
UART's batch used invalid decimal0447CF and decimal20 rather than32 for SAVE.
Exact incoming firmware/state were restored and129 released10:10:35UTC.

## Minimal correction

New kit `/Agon/mystuff/agon-mos/build/rx006/kit-r02/kit.json`, SHA256
`6d467b5111c3d5379ad573fea4c86054017bb6b250cdcaee9897be89e57dba4c`.
The reproducible [packager](../../../experiments/rx006/package.py) copies exact
app0208015a/18376B/2a0d9312 unchanged and emits explicit hex SAVE:

```text
CD /test/mos-rx006-r02
test
SAVE /test/mos-rx006-r02/WITNESS.BIN &447CF &20
CD /
EMOS sdserve --fast /
```

This is an explicitly executed test batch, not a boot script. New target
directory must be absent/empty; preserve populatedr01 and all129 evidence.
Fresh host output `build/rx006/physical-r04` must not exist. No old token, actor,
directory or uncertain operation is resumed. Original kitr01 is untouched.

No firmware/core/benchmark change or native rebuild: EMOS171c/mapccbda,
VDP7d09, source60001, callbacks and strict analyzer remain. All six host/SDK
inputs retain their original hashes. No optimization or extra case is selected.

## Finite scope and custody

Use a new normal FIFO task `RX006-matched-physical-r04`, behind current owners.
Extender alone prepares new request-local selection/source binding to kitr02,
reconciles fresh incoming state, installs and independently verifies the exact
same two images under owner540 from original grant. Whole1800, consumer420,
application180, cleanup600 and >=1020 remaining before launch are unchanged.
Keep normal/failure cleanup bound to this attempt's original verified stage
receipt. Preserve startup/listener/P4/bootloader/table/OTA/app1/tails.

Actual joined RX006-OWNER-HANDOFF1/current token/URL/argv/actor/tool registration
are mandatory before UART's one unchanged runner invocation. Four-file
independent readbacks, ONE EXEC, P4 metadata only during RUN, no commands into
uncertain HALT. Successful log alone is insufficient for the remaining gate:
require normal batch continuation, WITNESS32B state3, next2, strict10/36 analysis,
positive terminal-listener EXIT/offline and joined consumer return. No additional
performance demand. First failure stops and preserves actual state, no replay.

Extender alone performs exact incoming native85f9 FIRST/fullreadback, then
a25f fullROM/readback and fresh whole-file/state/rootCLI/input/resources, joins
all actors, releases and steers actual next. SD mounted. Do not preempt queued
FSIM/Mech. No grant/reservation is implied by this preparation document.

After that completion gate, share actual measured tuple/findings with the
selected Rally/6502 owners for their existing bounded helper trials. Keep game
edits in their lanes and stop when adoption confidence is demonstrated; no
further speed tuning. Earlier129 timings remain honestly original129 data.

## Prepared reservation

SOURCE4 bb3c8bae7022f8ff61ae6a151ded8a112cf6b6fe3a00bbe95fdc0c14283902e6
and all49 inputs independently match; [review](completion-r04/owner-review.json).
Actual new normal request `e4d3981a89ae`,10:18:56.016021UTC November8, is
recorded in [reservation](completion-r04/reservation.json). At reservation
FSIM130 owns the bench and Mech1282 precedes this request. No target access,
grant or consumer handoff is implied. Extender has the actual request for its
fresh runtime binding and subsequent normal admission.
