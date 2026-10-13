# MOS UART0 project handoff

Executive summary: the isolated UART0 driver passes the scripted suite and
actual-firmware headless Flexe Agon Emulator testing on Oryx. Flexe exposed a second lost
wakeup, now reproduced and corrected. The Author passed human review and selected a separate
`flexe-agon-emulator` owner; production integration still needs the two
compatibility decisions.

Read `/Agon/mystuff/agon-dev-env/codex/AGENTS.md` first, then `OWNERSHIP.md`,
`TODO.md`, `docs/tasks/ASY-001.md` and `docs/uart0-async.md`. The latest dated
log is `docs/devlog-2026-10-13.md`. The experiment README defines the actual
experimental ABI; its RESULTS.md records qualification and benchmark limits.

The working branch is `codex/uart0-async`, based on qsort revision
`6de0eafcb2cd328a8e33c160f7a364bd04592558`. Pre-existing qsort modifications in
`src/mos_api.asm` and `src/mos_api.inc` were preserved, then included in a
separate checkpoint at the Author's request to commit and push all dirt.
The Author approved committing the isolated tranche on 2026-10-12. New
emulator work still requires its own review before committing. No physical
bench was changed.

Build and test with `experiments/uart0-async/build.sh` from this checkout.
Outputs are under ignored `build/uart0-async`. Rust/Bash/Ruby are used; no Python
or new venv is required. Dependency identity is verified against the pinned
model manifest. Native ZDS II under Wine on Oryx Linux Lite is the build route. The isolated
sources assemble/link there through the canonical launcher and pass all
qualification using that image. No mos-agondev translation path is maintained.
Production MOS linking and live integration remain unqualified.

The initial checkpoint was pushed as `564de93` (preserved qsort exposure) and
`7182bc7` (isolated UART qualification) on `codex/uart0-async`. The subsequent corrected driver and human-reviewed fixture are recorded in
the current development log. Read `docs/uart0-flexe-audit.md` and
`experiments/uart0-flexe/README.md` for the corrected project-local UART model,
real ESP32 firmware fixture, receipts and stopped Oryx human-review command.
TX-007/TX-008/TX-009 are complete. Reusable runtime source is now owned by
`../flexe-agon-emulator`; MOS consumes its pinned Oryx build. The primary
profile entry is `./flexe-agon-emulator`; the old Fab entry is a shim.

The Author selected Fab/Flexe for initial emulator testing and authorized
headless runs on Oryx Linux Lite. Use Oryx for compilation and emulator workloads
to avoid contention on the Pi 5. Both Pi ARM64 and Oryx x86_64 Fab/Flexe build
artifacts were inspected on 2026-10-12; their existence does not qualify this
driver. Before UART testing, audit the Fab eZ80-side interrupt/FIFO/CTS model
as well as Flexe's ESP32 side. Keep this project's fixtures isolated from the
Golem and agon-6502 owners' sources, builds and profiles. ZDS II under Wine
remains the MOS assembly/link route.

Both qualification scripts now compile and execute their Rust/native code on
Oryx. The Flexe tooling uses a project-local Oryx `.venv` for standard-library
profile generation and verification; local Bash/Ruby only stage and audit.

The authoritative unfinished-work list is TODO.md. Subtask IDs are immutable
short namespaces followed by three zero-padded digits and a checkbox, e.g.
`TX-005 [ ]`. Never renumber on reorder or reuse a disposed identifier.
