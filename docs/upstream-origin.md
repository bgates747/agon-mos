# Official MOS origin and native source traceability

The foundation derives from official Agon Platform MOS v3.0.2. Original history,
file placement, routine names, explanatory comments and license notices remain
available, while maintained assembly now uses GNU syntax and native macros.
Local portability changes are explicit in the deviation register rather than
hidden in a preparation step.

Upstream repository: `https://github.com/AgonPlatform/agon-mos.git`.
Tag: `v3.0.2`; commit: `8336409351ee5314e02801a7b72a4f1bb5282519`.
The fork retains that commit and its history as ancestry, not as a squashed
source import. The remote named `upstream` points to the official repository;
`origin` points to the private `bgates747/agon-mos-agondev` repository.

All original firmware paths remain the same: `main.c`, `src/`,
`src_startup/`, `src_fatfs/`, `src_umm_malloc/`. Each native `.asm`/`.inc`
header identifies its upstream path. The legacy `.asm` suffix is retained for
reviewability; contents are maintained GNU-as, not ZDS source. The inherited
ZDS project/target files are historical reference and are not build inputs.

To inspect original source or review a local change:

```bash
git show v3.0.2:src/serial.asm
git diff v3.0.2 -- src/serial.asm
```

`docs/migration/initial-map.json` preserves 20 assembly/include file mappings,
original/native initial hashes, per-line origins and local/macro symbol
correspondence. Human-readable native labels replace generator hashes. The
record describes the initial conversion, not later development line numbers.
`docs/migration/upstream-files.json` inventories all original tracked files
and their first-tranche counterparts; Git history remains the original source
authority. Source mappings are evidence, never a regeneration input.

The implementation was checked in two separate passes: mechanical dialect
conversion, then readable local labels/macros/includes. Both built directly
and reproduced the same 102,055-byte translated AgonDev control. The persistent
migration workspace retains both passes separately; source commits must keep
those concerns reviewable when promoted. ELF private/debug symbol spelling may
differ without altering firmware bytes or public symbol addresses.

No experimental UART, EMOS enhancement or post-release VDP bug fix is silently
part of this pin. Clean official-source ancestry does not mean the port has
corrected every inherited MOS defect. Future fixes require their own reviewed
deviation and qualification.

The original MIT license and FatFS license remain unchanged, as do attribution
and copyright notices in imported files. The upstream README and project setup
are recoverable through the retained tag/history; they are not current native
build/deployment instructions. Vendor tool binaries are external dependencies,
not tracked source or repository payloads.
