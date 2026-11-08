# RX-005 — First Console8 hardware qualification

Brandon reviewed the both-engine synthetic PASS and on November7 authorized
commit/push followed by deployment to the Console8 card mounted on Oryx.
This selects one manual hardware integrity run. No consumer prototype, game
change, performance claim, release or automatic hardware flashing is selected.

## Deployed appliance and protocol

Volume AGONC8, UUID8658-1C23, directory `/test/mos-uart0`. Firmware/fixture
readback is exact. The original `autoexec.txt` has been restored byte-for-byte
after an unauthorized replacement; the current test is manually invoked.
The installed standard `flash`
MOSlet remains the intended flashing interface. Flash **VDP first, then MOS**:

```
cd /test/mos-uart0
flash vdp vdp-rx.bin
```

Let the normal updater finish/reset. Return to the directory if needed:

```
cd /test/mos-uart0
flash mos mos-rx.bin
```

Keep updater checks. Once flashing has completed, reboot if the updater has not
already done so. Once BOTH firmwares are installed, manually invoke:

```
cd /test/mos-uart0
test
```

The original boot script is preserved and does not launch this fixture.
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
step. The original boot script, including its comments and Moon Patrol commands,
is restored on the card and also preserved in the off-card archive.

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
* [Initial readback receipt](hardware-r01/deployed.json) and [preparation/archive pins](hardware-r01/prepared.json) are historical deployment evidence.
  [Exact autoexec restoration](hardware-r01/autoexec-restored.json) and
  [manual-start correction](hardware-r01/manual-start-corrected.json) record the current corrected state.
* Both Pi and Oryx project workspaces retain
  `build/rx005/console8-deploy-r01/predeployment.tar.gz` (3464402B), SHA256
  `d47273597698d6341c4433d8c47b2c9a9e5bad1a73d37eaddbdb2c461415ba8c`.
  All119 archived files were independently checked before deletion of the old
  `/test/mos-uart0` appliance and its four `mos-uart0-*` history directories.
  Root autoexec is preserved too. Other card projects remain untouched.

The firmware and SD deployment remain experimental; physical results are pending.

## Published VDP provenance received after deployment

VDPlet published isolated counted implementation
`a83d912ab0bd6ce60bd09a919cf1d6b11b2d84f0` and qualification evidence
`e8014c3f459986e7a392a56e465a687da64a495e` on `origin/codex/initial-runtime`.
The selected7d09dfea BIN and2918727a ELF remain unchanged. The exact tested
export receipt is `agon-vdplet/build/vdpl036-producer-r05/enabled/firmware-source.json`,
SHA256 `4ce246a3da8d74fe54dca561c28573cb249ec43a11f50bc690977a16245f7af2`,
independently rehashed by UART.

The isolated source commit excludes unrelated async diagnostics from two files.
Those bodies were inactive under the tested `async_worker=false` configuration.
This is an implementation publication pin; the immutable export manifest remains
the exact tested-build provenance. No fresh build or byte-identical rebuild from
the isolated commit is claimed. [Owner identity comparison](hardware-r01/vdp-publication-source-identity.json).
The already-written card/deployment receipt is unchanged; this provenance note
adds no new firmware, card access, hardware claim or consumer distribution.

## Boot-script correction

The initial deployment replaced the Author's boot script without explicit
permission, incorrectly treating appliance deployment as boot-script authority.
That was an agent error. The file is restored exactly to its437-byte original,
SHA256 `a2e3fc48788ea771fc114ccb230985873f3e61e81d55c448c7408169e4d6d8cb`.
All original comments and commands are preserved. The corrected readme says
to invoke `test` manually only after both firmware updates. Firmware/test binaries,
reports and counters were not changed by the correction. Historical initial
receipts retain their actual contents and are superseded for boot behavior by
the restoration/correction receipts linked above.

AGENTS.md now explicitly prohibits boot-script changes without a direct human
request or prior permission. Deployment alone grants none. When authorized,
preserve comments and commands, commenting conflicting lines rather than erasing
them unless replacement was explicitly requested. The deployer now rejects
boot-script archive members, never writes autoexec, and checks it is unchanged.
