# Native MOS candidate review

Historical shared-foundation qualification only. It does not qualify this
UART feature, and the old Fab commands below are not its review profile.
See uart0-native-source.md and ../../../agon-mos/docs/uart0-native-tranche.md
for this product's actual-image checks and dedicated Flexe review.

The committed native candidate reproduces the selected AgonDev stock image and
passes bounded headless boot, shell and two-cold-boot API checks. The Author's
graphical boot, help, directory and fixture-read checks passed. The initial
manual API review failed: its fixture was staged at the wrong guest path, and
the instructions incorrectly requested two probe runs in one boot. Corrected
file and persistence checks now pass unattended against both firmware images.
The Author need not repeat that probe manually; this is not an accepted release.

## Selected candidate

1. Native source: `92662538a5766ae1e3d5b47e7dd78829a4dfe1c5`, following
   mechanical conversion `a5fa859367998b05a8e4d17364d18d6b12b9607c`.
2. Shared helpers: `6cbaf08b7dc4155a1428a83ad9dcb99ae8cbf847`. The later
   `7b584ae` infrastructure commit corrects documentation/export paths only.
3. ROM: 102,055 bytes, SHA-256
   `f891721bbb2a0bc2845dbb13edbeb449365a315f11be48500d8e65e2ab1aebb4`.
   All 512 public symbols and all 16 C objects match the translated control.
4. Review runtime: clean official Fab `1.2.5`, commit
   `c22876d1f7ad903537c308cf65afd6553b37cdb8`, built locally on Oryx with
   its recorded submodules and stock Platform VDP. No Flexe runtime is involved.

The source/helpers are local committed candidate pins; they have not been
pushed as part of this tranche. No qualified release tag or downstream adoption
is implied. The inherited stock oversized-VDP-packet defect is deliberately
retained; it reproduced as a negative control, not a passing corrected case.

## Human review on Oryx

Open a terminal on **Oryx Linux Lite**, starting at this native repository root:

```bash
cd .emulator
./fab-agon-emulator
```

This is the real generated wrapper, not the raw runtime link. It pins MOS,
map, executable, VDP, SDL library, startup identity text and wrapper bytes;
input overrides are rejected. The stock firmware banner is followed by an
explicit native-candidate identity containing the selected source/helper pins.
That profile text is not a new firmware API or API-001 implementation.

1. Confirm the MOS 3.0.2/Arthur banner, native-candidate identity and usable
   command prompt. Check that typed keys and screen output behave normally.
2. Run `help`, `dir`, then `type native-fixture.txt`. The file should print
   `Native MOS review fixture`, with no SD/mount or unexpected parser errors.
3. Close the emulator window normally and report pass/failure and observations.
   No special quit hotkey is required for this gate. Do not flash or deploy
   anything to physical hardware.

The Author's screenshots already establish these graphical shell checks for
the selected candidate. File/API tests are automated agent work, not an
additional manual reboot exercise.

## Automated file and persistence checks

The corrected root-based SD fixture passes reads, writes, copy, rename, delete,
directory enumeration/creation/removal, 32-bit seek/tell and persisted-payload
verification. The harness performs CREATE and VERIFY in separate emulator
processes, automatically, for both the native candidate and official v3.0.2.
All four invocations report `CONTRACT-PASS`; matched transcripts agree and each
pair restores the exact initial fixture. The latest unattended run took 10.22 s
including SSH/command setup. Runtime/input hashes also verify.

The shell profile is under ignored `.emulator/`; its raw executable is
`fab-agon-emulator.bin`, with a project-local official runtime under
`.emulator/runtime/fab-1.2.5`. It maps only its own SD overlay and individual
standard tools, not the containing project/workspace back into that overlay.
`.native-foundation-review.json` and `.native-api-fixture.json` inside the profile
record the original staged inputs; they are historical staging receipts, not
human pass records. The original failed fixture remains intact. The corrected
diagnostic profile is `.emulator/contract-review-20261016/`, uses the same pinned MOS,
probe and official runtime, and has its own real generated wrapper and isolated
root fixture. `.native-contract-review.json` records its staging identity.
The intentional sparse file is confined to that guest SD tree.
`.emulator/unattended-file-checks-20261016/` contains the latest machine result
and four probe transcripts. This diagnostic profile has not been manually
reviewed graphically; its file checks do not require another Author launch.

Running the unmodified probe twice in one boot reproduces
`api-extractnumber-u24-output` failure on both the native candidate and official
v3.0.2 MOS. It remains an unresolved state-dependent finding, not a passed case
or a proven compiler defect. The selected mos-agondev dependency records the
reproducer and scope as `MOS-EXTRACTNUMBER-001` in `docs/upstream-findings.md`.
Do not repeat the earlier `/native-api` or same-boot instructions.

## Evidence and limits

BUILD-005 in the selected mos-agondev dependency owns coordination and the
dated validation report. Full scripts, receipts and failed diagnostic attempts
are retained in its persistent `worktrees/mos-build-005-validation` workspace;
the directory layout is not a build requirement for other developers.

The broad infrastructure suite ran 154 tests with one known Binutils
backward-JR display failure and one optional UART-model class skipped. Source
tests passed on Pi and Oryx; three generated-launcher guard tests passed. CLI
parity and API checks use Fab's fake VDP, not physical UART timing or the
graphical native VDP. Human review covers that distinct presentation/input path;
it does not establish electrical CTS reserve, hardware baud safety, broad C
compiler equivalence or correction of inherited MOS defects.

The Author approved committing and pushing these records on 2026-10-16 after
the unattended file tests. No manual API rerun is requested. This approval does
not constitute physical qualification or acceptance of a production release.
EMOS, UART and
API-001 implementation remain outside this tranche.
