# Native regular MOS UART implementation

2026-10-16 hardware hold: the first native candidate failed to boot Console8.
The [completed audit](../experiments/uart0-native/BOOT-FAILURE.md) identifies and
corrects a 24-bit overflow in startup baud calculation. The replacement passes
software checks but remains off-device. Earlier qualification/deployment text
is historical; N-006 governs fresh replacement qualification and acceptance.

The next implementation brings the measured CPU-saving UART sender into a
maintained native AgonDev MOS variant, with explicit application opt-in and
unchanged legacy blocking behavior. It is a separately qualified experimental
regular MOS product; EMOS remains deferred and installed firmware is untouched.

The Author authorized implementation on2026-10-16 after a commit/push checkpoint.
Existing MOS work is pushed as d4569e8; the isolated EMOS budget assessment is
pushed as e147549 on its own branch. This authorizes the implementation tranche,
not a new production release or automatic hardware installation.

The only actionable task index is TODO.md; N-001..N-005 identify this tranche
in the development log, alongside existing BT/AB gates.
Our own agon-mos repository holds isolated source worktrees under
`../worktrees/uart-native-001/{stock,uart}`. The feature branch is
`codex/uart0-otirx-native`; no UART branch/source is added to either owner's
foundation or infrastructure repository. The original working fork is retained.

Selected foundation and canonical interface:
`ab95feee301d2cd40470cf2bda85a0fe1c3c008e` from private agon-mos-agondev.
Selected build helpers: `49dc33fee817cb184572351ee71dae7da9a139c4` from mos-agondev.
Use immutable local dependency exports and verified Oryx transport, not mutable
owner files. Build/behavior evidence names dirty source hashes until accepted.
The clean stock control must reproduce102055 bytes/SHA256
f891721bbb2a0bc2845dbb13edbeb449365a315f11be48500d8e65e2ab1aebb4.

The feature reference is frozen ABI1.2 source.tar SHA256
38321531d35faff356b065daab1b4ac64dea9a4acb4e3d1e0b72177937dacc9f.
Port its UART-only delta into maintained GNU source. Generated translation is
an encoding oracle and one-time aid, never the normal build's source of truth.
Keep macros, private scopes, comments and original provenance recognizable.

Consume canonical shared assembly/C bindings. UART discovery remains
mos_getfunction13, returning a discovery function before the UTX1 table.
Slot12 stays null/retired; qsort's experimental public API is excluded.
No new global number or range is allocated. Preserve ABI1.2 length54, capability
discovery, default1, short-mode/context checks, masked-IFF restoration, the sole
MOS receive parser, callback exclusion and return/OSCLI/crash lifetime fences.
CTS is checked before each positive bounded OTIRX block, within the16-write
service cap. The supported-size bitmap is not physical safety certification.

The root native firmware-check must invoke product linked-image checks and
retain shared runtime, flash/RAM/stack/provenance guards. Keep the stock control,
feature port and explicit branding measurements distinct. Validate actual
candidate machine code and complete payloads; do not substitute old ZDS test
results or mask arbitrary relocation-looking bytes. Known inherited defects
and failed attempts stay visible. Human emulator review and hardware acceptance
remain separate gates. Leave the other-project Console8 VDP untouched.

Implementation and software checks are delivered. The isolated native source,
exact image measurements, both-engine raw reports, retained failures and
stopped human review are described in experiments/uart0-native/README.md and
results.json. This does not complete the old menu/batching integration,
supported-combination selection, native physical acceptance or release gates.
