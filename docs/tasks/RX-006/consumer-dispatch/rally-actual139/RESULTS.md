# RX6-HLP actual139 — one real consumer pass

**The retained Rally exporter works with counted replies on hardware and is
useful to adopt.** Both methods produced the exact584-byte original file. The
original READ16 path used292 requests and30 public MOS counts; the counted copy
used3 requests and6 counts, a5.0 ratio for this one ordered complete-export pair.
This meets Rally's bounded practical consumer check; no further tuning, sweep,
game migration or additional helper run is needed.

| Actual helper path | Payload | Requests | Raw MOS counts |
| --- | ---: | ---: | ---: |
| Unchanged extracted timingDumpBuffer / READ16 | 584B | 292 | 30 |
| Separate counted inner-transport copy | 584B | 3 | 6 |

Intervals include fopen, request construction/transfer/waits, foreground fwrite
and fclose; counted byte/count/guard checks are included. Setup, upload, progress
logging, independent file reopen verification, cleanup and result retrieval are
outside. Public counts are coarse; one fixed-order pair is not a stable speed
estimate, calibrated wire rate, CPU recovery measurement or frame-rate result.
This exporter runs after a race; the trial ran no race, physics, renderer or
native module. No additional game FPS follows from it.

Actual139 used source-reviewed app595f73c2/16392B/build17f8fefe, corrected host
kitf2de4f3e and explicit new request19e9824cf0fe. Extender supplied the actual
installed171c receiving ROM and7d09 producer with independent readback/bootstrap/
fresh-state evidence. Actual READY preceded the genuine installed observation.
The one original foreground process/session4514 was actually launched once;
its real native PID1947147/start40252709/PPID1750/PGID1947147 was registered
immediately after the returned toolhandle. No new wrapper, duplicate or stale
135 token was used. The original process returned0 and its native PID/group
were independently absent; all synchronous child calls joined before custody
return. Consumer host duration22.1722s includes staging, typing and retrieval.

The actual runner verified the fresh empty namespace and both staged files via
whole GETs, dispatched one explicit EXEC, observed the terminal listener within
120s, retrieved all four result files, ran the exact analyzer, then normal EXIT/
offline. Seventeen recorded steps complete with no pending step. Positive file/
witness evidence includes receive state2, three callbacks, actual/announced
256/256/72, all guards/payload/header/EOF/reopen checks, source50307 cleared,
callback retired and entry mode0 unchanged. WITNESS state3/phase5 agrees with
both request counters and raw intervals. See physical-actual139/analysis.json,
RX6HLP.TXT, WITNESS.BIN and summary.json.

CONTROL.BIN and COUNTED.BIN both have SHA256
648abfc3547bb878767f199710ef7a817f8cfc679f70edf716f30dc427e13732,
matching the pinned retained input exactly. The RTM2 stats header has no game
generation field;4503 remains originating state.bin provenance, not a live
generation or newly generated race result. No file identity is invented from
transport admission alone.

Practical judgment: the exporter no longer reconstructs every two-byte word
and waits on292 tagged control replies. It arms and consumes three checked
payload chunks directly for the existing file writes. A small public26h adapter
and persistent guarded destination replace the per-word bulk reconstruction;
management/error keyboard delivery remains separate and necessary. Exact source/
destination lifetimes, one outstanding arm, positive completion and fail-stop
residence after uncertainty still apply. The real finite pass plus materially
fewer requests and this observed modest export benefit are sufficient; there
is no selected full-game adoption or further performance program.

Actual135 remains entirely UNRUN from expired delivery; it is never relabeled
as this pass. Its exact incoming restoration and release were separately
completed. Actual139 stopped consumer custody has been returned promptly to
Extender with native actor/terminal/result hashes in
delivery-correction/ACTUAL139-CONSUMER-STOPPED.json and the owner's matching
consumer-stopped.json. Extender alone now owns exact incoming native-prefix
FIRST/EMOS restoration, fresh CLI/input/resource handback and normal release;
that final owner outcome is pending here. No Rally target actor or collector
remains and no new consumer action is selected.
