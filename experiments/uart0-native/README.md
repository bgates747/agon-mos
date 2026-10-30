# Native regular MOS UART qualification

Hardware hold,2026-10-16: the deployed native MOS did not boot on Console8
after flashing, manual reset and two power cycles. Only the VDP banner appears.
The candidate is withdrawn from hardware readiness. The Author and Extender
agent handle recovery. [The completed audit](BOOT-FAILURE.md) proves an
overflowing startup baud calculation: divisor 11 instead of 1. The corrected
off-device image passes actual-instruction boot/divisor checks and both full
Flexe campaigns. No replacement is deployed or physically accepted. Do not
reflash the old image on the strength of the historical results below.

The full background sender now builds as maintained native AgonDev MOS and
passes the software checks against its actual machine code. Both Flexe engines
complete byte-integrity and full-duplex campaigns using compiled ESP32 firmware.
Applications still opt in; legacy output stays blocking. Human emulator review
and physical acceptance of this new image remain before approval or deployment.

Update2026-10-16: the Author passed the native child review and authorized
Console8 SD staging. The verified bundle is now at /test/mos-uart0/test.bin on
AGONC8, with new native MOS, repaired VDP candidate, source companions and short
readme. Menu3 runs native batch16 with fresh numbered reports; repeat once.
Install the staged MOS via9/1 and VDP via9/7, rebooting and confirming identities.
Installed MOS must show CRC5B36B5B1/API1.2; root /MOS.bin remains stock/unchanged.
The Author performs physical flashing/execution. N-006 tracks returned reports.
The software-stage statements below precede this deployment; they do not claim
that the card remained untouched afterward.

## Selected product

The source is our own agon-mos worktree at
`/Agon/mystuff/worktrees/uart-native-001/uart`, branch
`codex/uart0-otirx-native`, with uncommitted implementation changes based on
foundation/interface ab95feee301d2cd40470cf2bda85a0fe1c3c008e.
Helpers are49dc33fee817cb184572351ee71dae7da9a139c4. dependencies.json locks
canonical assembly/C/C++ bindings. Global getfunction13 returns a discovery
function, then the UTX1 table; retired12 stays null. No private global ID or
qsort public experiment is included. EMOS remains deferred.

The complete native stock control reproduced102055 bytes exactly, SHA256
f891721bbb2a0bc2845dbb13edbeb449365a315f11be48500d8e65e2ab1aebb4.
UART-only unbranded firmware is104624 bytes; branding adds34, yielding104658
bytes with SHA256
5543d6acaa64bebd3006cb034a8dda9b61cfe92c82cbbffe2c391a9392f0f4c9.
UART BSS grows86 bytes. The actual2497-byte module and300 explicit relocations
match the frozen encoding reference, with no relocation-shaped masking.
Final build uart-010-final has the same ROM bytes as the tested uart-009-final;
the final changes are comments, documentation, source newline preservation and
test tooling. Root provenance retains the exact source/input identities.

## Evidence and limits

Root firmware-check passes shared memory/runtime/stack/provenance guards and
the product's linked-ELF contracts. Corrupt controls reject a non-null retired
slot, damaged table length and missing OTIRX. Canonical C/C++ overlay consumers
compile successfully. Nine source/interface checks pass.

behavior.py reuses the retained independent instruction/UART oracle against
the native ROM. Five batch-policy runs each cover27 production integration,
538 policy,425 descriptor-boundary and150 source-boundary cases. Controlled
missing CTS guards, a17-write refill and early buffer release are rejected for
the intended reason. Model timings remain idealized, not silicon measurements.

flexe.py uses a disposable FAT16 image and canonical generated Flexe wrapper.
Both final campaigns complete10 CRC cases and20 acknowledged stress cases.
Per engine:40960 payload bytes pass receiver CRC,163840 final-buffer bytes are
compared,640 ordered replies arrive, every complete stress packet matches the
captured wire, and all final comparison commands are present. TX drops/RX
overruns are zero. Intermediate stress buffer contents are not individually
receiver-compared. The private compiled VDP uses the hardware-qualified receiver
lock correction plus the existing CRC diagnostic protocol; it is not stock VDP.

Frozen frontend SHA256412089a89a5adccb3c1c0fc4b121472da28f2d3d48c435c88a660028d7cd84d9;
backend77b3cbf76564d54628c2bb876aa96ef3834c6b363d53df4892b8a3ab4248e5cd;
compiled VDP201ad8ab4af807c261cb92634286b2fbaedcf3879f140e820b60ab54cf707e2a.
Private SDK/upstream references stay read-only. No physical firmware or card
was changed. The inherited native foundation oversized-VDP-packet defect is
documented and deliberately excluded from this UART port.

## Retained failures and corrections

The initial frozen stress client attempted a batch-policy change immediately
after printing; TEMT was false. A native no-quiescence control reproduced the
actual setter BUSY status1, distinct from an open failure. The maintained client
now waits for public drain before changing policy. MOS's rule is unchanged.

Initial full-suite deadlines stopped normal progress at300 seconds. Final
JIT/interpreter executions took379.206/410.782 seconds; the harness now allows
900 seconds for the complete multi-client suite and rejects120 seconds with no
wire progress. These wall times are emulator execution durations, not hardware
performance results. Individual stress clients retain progress breadcrumbs.

The first report validator wrongly treated two reserved FF padding bytes as
zero-valued error flags. Both campaigns had already completed successfully.
validate.py corrects that interpretation and validates retained raw evidence
without rerunning firmware. Original failed-validator receipts remain intact;
validated-receipt.json records the corrected decision and original receipt hash.
Deliberately corrupt CRC, reply-count and wire-byte evidence is rejected.
An extra instruction test initially asked its IRQ helper to run under DI; the
corrected masked-IFF test pumps the public kick API. Both attempts remain.

## Reproduction and human review

Run commands on Oryx from its primary agon-mos directory. Each campaign requires
a fresh alphanumeric attempt ID; an existing output is refused. Full campaigns
take about seven minutes and do not need keyboard input:

```bash
.venv/bin/python experiments/uart0-native/flexe.py jit --attempt nextjit \
  --clients clients-003 --mos-build uart-010-final
.venv/bin/python experiments/uart0-native/flexe.py interp --attempt nextinterp \
  --clients clients-003 --mos-build uart-010-final
```

Retained final outputs are build/uart0-native/flexe-{jit,interp}-fixed2. Their
validated-receipt.json files are authoritative interpretations of the raw data.
The explicit no-quiescence diagnostic uses --no-quiescence-control; its expected
fixture failure is a passing negative control, not a passing transport campaign.

The stopped Oryx profile is prepared with its own fresh card and pinned runtime:

```bash
cd ~/Agon/mystuff/worktrees/uart-native-001/uart/.emulator/uart0-review1
./flexe-agon-emulator --precise-interrupts
```

Expect the experimental MOS banner, four progressing pause/full-duplex cases in
batch16, UART0 STRESS FIXTURE PASS and NATIVE UART REVIEW COMPLETE, then a usable
MOS prompt. Allow about two minutes. Check ordinary typed help/dir, close the
window and report the outcome. This reviews the new UART product, not the
already-reviewed generic foundation or its obsolete Fab probe. No graphical
instance was launched by the agent. All new affected changes remain uncommitted
under the canonical human-review gate. The sole task index is ../../TODO.md.

The complete144095070-byte build/raw-evidence archive is verified on Pi and
Oryx: build/uart0-native-evidence-20261016.tar.gz, SHA256
0b4142e7e8e620471ef29ab024d7df774062f01c19f83043c407814f43edfbd4.
The827842-byte encoding-reference supplement preserves the exact frozen source,
both objects and final byte/relocation comparison: SHA256
030baad1d8d5f35e6c53c97a24b46b480f7eb1d2fe575df679c28b51f687c573.
See archive.json and verification.json; closeout notes follow the archive's
snapshot. No physical/native acceptance or release follows from archiving.
