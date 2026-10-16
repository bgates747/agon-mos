# VDP receiver synchronization repair

The receiver could turn itself off just after the other CPU recovered it.
This repair moves the buffer-full flag update under the UART lock already
used to disable receive interrupts. The reader clears that flag under the same
lock, so those operations can no longer cross in the failing order. It adds no
new lock or per-byte work. Upstream VDP and installed SDK files remain unchanged.

The Author authorized implementation after Console8 R0010 captured the forced
ordering and recovered every byte after rescue. RX-001..RX-003 in the sole TODO
owned this tranche, now completed by the 2026-10-15 Console8 return. Matched
hardware tests confirm the repair under forced timing; release approval remains
pending. The software-only results.json is the frozen preparation snapshot;
[physical-results.json](physical-results.json) records the later hardware result.

R0012 captures the baseline fault with66 FIFO bytes pending and requires rescue.
R0014 verifies both4096-byte payloads, CRC87897582, with zero receive errors and
no rescue. R0017 passes all five candidate compatibility phases. R0018 records
the restoration request; the Author confirms the normal stock2.16.0 banner.
hardware_return.py independently validates the preserved reports, firmware and
fixture pins, journals, candidate phases and restoration confirmation. No claim
is made about natural stock-failure frequency or new performance measurements.

`patch_driver.py` applies the minimal change to the audited Espressif IDF4.4.6
driver SHA0a90ac006b6a0cadaac4c47ab035a54c782fb6171fda82e9dd059a3d84c4b0be.
The original Apache2.0 header/license is preserved. New hooks and tests are MIT.
`prepare.py` copies the pinned VDP2.16.0 private source, applies the patch only
in the repaired builds, and produces these images:

| Image | Purpose | Menu flash / test |
| --- | --- | --- |
| vdp-race-before.bin | Unpatched matched diagnostic; expected forced fault and rescue | 9/6 then 8/5 |
| vdp-race-fixed.bin | Repaired matched diagnostic; rescue function excluded by linker | 9/5 then 8/6 |
| vdp-rx-fixed.bin | Repair without timing, recording or rescue hooks; identity query only | 9/7 then 8/7 |
| vdp-2.16.0.bin | Unchanged official stock restoration image | 9/4 |

The before/after payload, traffic, ring size and64-byte flow threshold match.
Both record publication, mask and other-core recovery. The baseline wait stays
between publication and lock entry. The repaired wait runs after the protected
publication/mask and lock release. This is deliberate: the repaired operation
has no unlocked gap to widen, and a wait inside its lock would block recovery.
Both waits are bounded and disabled at boot. The candidate has no such hooks;
its only private command reports its identity so the suite can refuse the wrong
firmware. Existing stock commands keep their behavior.

The new native fixture has MOS signature URF1, expected variant at offset137,
HELLO D8/D9 and URFHOST1 reports. It refuses the original D6 diagnostic or an
opposite variant before sending payload. Records remain160bytes and use URF1,
version1; byte63 identifies the repair. Baseline forced outcome2 requires the
captured stuck state and rescue. Repaired forced outcome5 requires complete
payload/CRC, correct protected ordering and no rescue. Absolute cycle counters
from different cores are never compared for event ordering.

Checkpoint writes use overwrite/write/close and occur outside ARM-to-DONE;
FatFS timestamp queries must never enter raw payload traffic. `qualify.py`
uses the canonical generated profile launcher and actual MOS FatFS/SPI on
disposable FAT16 images. The frozen frontend/MOS match prior Console8 tests.
`audit.py` verifies source transforms, linked object replacement, compiler flag
store placement inside the lock, and contradictory-evidence rejection. It also
checks that the fixed diagnostic has no linked rescue function and that the
candidate has no diagnostic driver symbols.

Headless checks and manual physical execution remain separate. The operator
procedure is in [readme.txt](readme.txt); no agent flashes or resets the board.
All tests and firmware files belong at /test/mos-uart0/test.bin and beside it.
The original receiver diagnostic and earlier passed suite tests remain usable.
