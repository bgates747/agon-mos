# Native MOS foundation agent instructions

This repository maintains readable native C/GNU assembly derived from official
MOS. When available, read `../agon-dev-env/codex/AGENTS.md` first. Read
`OWNERSHIP.md`, `docs/upstream-origin.md` and `docs/deviations.md` before source
changes. `TODO.md` is the sole local source-task index; migration coordination
remains in mos-agondev's BUILD-005 rather than a duplicated checklist here.

Shared project policy is consolidated in
`../mos-agondev/docs/POLICIES.md` in the larger workspace (or `docs/POLICIES.md`
in the selected mos-agondev dependency). Read it before API or build-identity
work. Canonical interface files own allocations; consumer projects do not
manufacture private variants. The accepted reservation/identity policy is not
yet an implemented interface-distribution or metadata feature.

1. Preserve upstream history, names, comments, licenses and source structure.
   Explain meaningful deviations beside code and in the stable deviation
   register. Do not expand native macros or globalize private labels for ease
   of editing. GNU `.L` names are file-local, not ZDS procedure scopes.
2. Source under `src/` and `src_startup/` is now maintained GNU assembly;
   edit it directly. Do not run the migration script over this worktree or
   replace it from disposable translation output.
3. Build only through root `firmware-check`/`baseline-check`, selecting an
   explicit mos-agondev helper and qualified toolchain as in STARTHERE.
   The helper must execute every product-owned linked-image checker in
   `build.json`; low-level object linking is not a qualified product build.
4. Stock official v3.0.2 is the first control. No experimental UART or EMOS
   policy belongs in this generic foundation. Generic fixes are owner-reviewed;
   future upstream imports preserve the selected tag/commit and native mapping.
5. New implementation is an unqualified candidate until the required human
   emulator/hardware gates and release acceptance. Do not flash, reset, stage
   SD files, start graphical emulators, move qualified pins or publish publicly
   without explicit authorization. The GitHub repository must remain private.
6. Read official MOS/VDP documentation before API/ABI/format/hardware changes.
   Preserve eZ80 ADL widths, IFF and calling conventions; source appearance or
   emulator success alone does not establish physical timing or width safety.

Shared owner contract, when in the larger workspace:
`../agon-dev-env/cross-agent/mos_agondev_foundation/CONTRACT.md`.
This agent owns the generic foundation; linux-extender owns downstream EMOS
adoption within separately authorized scope. No EMOS adoption is released by
the initial native-foundation tranche.
