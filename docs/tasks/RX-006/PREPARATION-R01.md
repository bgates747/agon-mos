# Matched hardware fixture preparation

The goal is active after Brandon's correction. Both consumers' source reviews
remain useful, but actual own and subsequent consumer trials are still required.

The first original C application and bounded assembly callbacks compile and
link under actual Pi compiler594 with the retained native AgonDev SDK. The ELF
reproduces the pre-name-patched app binary; emitted callback and syscall bridges
were inspected. All owned compile/link/check children exited, compiler594 was
released normally and its release reported no next request.

* Reference build `0f7f56670d20e533`, app16831B, SHA256
  `2a41a41957dfdd31538dbe85b7504ef6924005a3c348209bb050fd42fd41354e`.
* `/Agon/mystuff/agon-mos/build/rx006/app-r01-eirene-reference/` retains exact
  source, generated identity, logs, ELF/map/listing/symbols and result.json.
* This is pinned to the already verified RX005 Eirene reference ROM, **not an
  EMOS-qualified or installed artifact**. Final EMOS identity/admission style
  and map must be bound and rebuilt before bench READY.
* The independent returned-log checker accepts its manufactured complete matrix
  and rejects seven incomplete/corrupt controls. Controls under
  `build/rx006/checker-controls-r01/` are not target results.

The app checks all ten sizes with two upload and two receive methods, then
benchmarks36 matched cells at128/256/1024 bytes. Both receive methods assemble
the same immutable source into the same guarded RAM and perform the same exact
byte check. Timing is across complete repeated pulls; no source setup, logging
or SD work inside the interval. No four-byte interval timing, PRT takeover,
private UART status read or CPU-percentage claim.

Extender's source binding is based on isolated a25f donor2c79c600. The defaultOFF
control reproduced exact a25f; the enabled image compiled but correctly stopped
at the existing CP10-only keyboard checker. The owner is making that check
explicitly flag-aware for the required16-byte baseline, retaining the failure
and all mandatory controls. No enabled firmware acceptance/fit or installation
is implied by the compile. Shared bench119 custody remains independent.

No physical RX006 reservation or hardware execution exists yet. Required next:
owner-qualified enabled ROM/map and callback/input/rollback binding, final
matching app build, one actual FIFO reservation and fresh grant, then finite
run/capture/restoration. After passing own results, coordinate actual small
consumer-code trials. Do not close on source review or manufacture a queue grant.
