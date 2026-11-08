# RX-005 — First Console8 hardware qualification

Brandon reviewed the both-engine synthetic PASS and on November7 authorized
commit/push followed by deployment to the Console8 card mounted on Oryx.
This selects one manual hardware integrity run. No consumer prototype, game
change, performance claim, release or automatic hardware flashing is selected.

## Deployed appliance and protocol

Volume AGONC8, UUID8658-1C23, directory `/test/mos-uart0`. All written files and
root `autoexec.txt` were read back byte-for-byte. The installed standard `flash`
MOSlet remains the intended flashing interface. Flash **VDP first, then MOS**:

```
cd /test/mos-uart0
flash vdp vdp-rx.bin
```

Let the normal updater finish/reset. The old MOS can refuse the automatically
invoked fixture at this intermediate stage. Return to the directory if needed:

```
cd /test/mos-uart0
flash mos mos-rx.bin
```

Keep updater checks. Once flashing has completed, reboot if the updater has not
already done so. Root autoexec contains exactly `CD /test/mos-uart0` then `test`.
The test clears the screen, verifies the exact MOS, selects normal VDP operation,
checks the matching producer and runs the same synthetic cases as the emulator.
Do not type during numbered cases. At `RX005 KEY READY`, promptly press and
release **A once**, within about20 seconds. Do not hold it. Allow less than two
minutes including this interaction. Expected end is `RX005 SUITE PASS`, then
`RX005 RETURN PASS` and the MOS prompt. One complete pass is sufficient for
this round; return the SD to Oryx afterward. A stall/FAIL is failure: retain the
last progress line and logs, and do not rerun an uncertain live transfer.

The next report is `R0067.log`; repeats allocate higher sequential numbers using
`next.txt`. No unreliable wall-clock dates are used. The same tested binary is
used unchanged; its IER snapshot is a same-value write and no hardware/model
counter is inferred from its on-hardware report. Callback/work/key/register
results establish integrity and progress, not calibrated CPU savings.

Stock MOS and stock VDP restoration images are beside the fixture. Dedicated
Console8 test firmware may remain installed; restoration is not a missing test
step. The previous boot script was a Moon Patrol launch and is archived off-card
for later restoration, rather than retained as card clutter.

## Exact pins and retained history

* MOS source: Eirene fork `codex/rx005-counted-return`, commit8db14b2, based on
  releasedRC3/97311c43. Tested image101257B, CRC32 **3933C3ED**, SHA256
  `40dc3d17a4f856c329e118b0376ff26f33085ef00410a26cda5739d4396589ea`.
  Its startup objects/serial TX match the donor and all48 startup entries pass.
  Startup branding remains EireneRC3; the fixture's full-prefix check identifies
  this specific receiver trial.
* Unchanged tested fixture16036B/build9c72616d7f4a4ef7, SHA256
  `6f79d47e615f2b4afca146a6c4ccf62677bf5c33b53b67c2f10b6ca3a729b949`.
  Source and original qualification committed/pushed in agon-mos72528f7.
* VDPlet-owned producer1100320B, SHA256
  `7d09dfeac4e7a1654dca486a8e86cd7b5d283f0d53bac0ab128cb8dd33e10087`,
  matching ELF2918727a. Component export/provenance remains owned by VDPL-036;
  no VDP source was edited for deployment. Its owner was notified of the human
  hardware selection and asked for the corresponding source commit/export pin.
* [Readback receipt](hardware-r01/deployed.json) and [preparation/archive pins](hardware-r01/prepared.json).
* Both Pi and Oryx project workspaces retain
  `build/rx005/console8-deploy-r01/predeployment.tar.gz` (3464402B), SHA256
  `d47273597698d6341c4433d8c47b2c9a9e5bad1a73d37eaddbdb2c461415ba8c`.
  All119 archived files were independently checked before deletion of the old
  `/test/mos-uart0` appliance and its four `mos-uart0-*` history directories.
  Root autoexec is preserved too. Other card projects remain untouched.

The firmware and SD deployment remain experimental; physical results are pending.
