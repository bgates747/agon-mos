# RX-006 — Goal complete

All selected hardware tests and practical consumer checks pass. Each run has
completed exact firmware restoration, fresh handback and normal release. Final
Rally release was November 8 at 13:20:32 UTC. The goal is complete; no further
runs, builds, game ports or optimization are selected.

- **Own synthetic suite, actual132:** all ten logical sizes4,8,16,32,64,128,256,
  1024,4096,8092B and36 matched benchmark cells pass.32B state3 witness and
  normal listener return/EXIT; exact originals restored and released.
  [Evidence](actual132/README.md).
- **6502 real adapter, actual136:** exact40B descriptor+512B payload through
  actual BRClient/persist_decode ordering;69 tagged requests become2 counted
  requests. Counts, two callbacks, guards, normal return and raw state pass.
  Owner judges this suitable and simpler. Exact restoration and release complete.
  Coarse8 versus0 ticks do not resolve a speed ratio. No game/persistence/ACK
  or new exporter was exercised. [Evidence](consumer-dispatch/6502-actual136/README.md).
- **Rally retained exporter, actual139:** both584B files exactly match retained
  input;292 READ16 requests become3 counted pulls256/256/72. Counts, three
  callbacks, guards, file reopen/EOF, witness and normal return/EXIT pass.
  Owner judges this useful and easier; exact restoration and release complete.
  [Restoration closure](consumer-dispatch/rally-actual139/CLOSURE.md). [Evidence](consumer-dispatch/rally-actual139/RESULTS.md).

Own actual132 no-work batch observations give5.65x/6.49x/6.98x completion ratios
at128/256/1024B versus8-byte tagged replies. Rally's single fixed-order complete
file export gives30 versus6 public MOS counts, a5.0 ratio for that pair including
fopen/transfer/checks/fwrite/fclose. These coarse observations are not CPU
recovery, pure wire rate, stable throughput or game FPS measurements. No further
performance campaign is required.

The exact temporary receiving EMOS171c and VDPlet producer7d09 are pinned in
[the handoff](CONSUMER-HANDOFF.md). Current stock/released firmware does not
acquire syscall26h/raw90h support by assumption. One outstanding arm, immutable
source, live destination/callback until positive terminal completion, and
separate legacy management/error handling remain required. Tagged ERROR or
timeout does not cancel a pending receive or permit reuse/unload.

Prior actual123/128 were installation-only failures,129 passed data but its
batch SAVE radix prevented completion, and Rally135 was entirely unrun after
delayed handoff. All remain separately preserved, never relabeled as later
passes. The [initial source-only report](HISTORICAL-SOURCE-ONLY-RESULT.md) is
historical and superseded by this hardware record; it does not describe current
status. Normal FIFO/owner lanes were retained, and no boot scripts or games
were edited for this goal.
