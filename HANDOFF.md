# MOS UART0 project handoff

Executive summary: the isolated asynchronous UART0 driver and general producer
benchmark are in `experiments/uart0-async`. They run against a scripted UART and
pinned eZ80 instruction model; the live MOS transmit/receive path is unchanged.
Production integration waits for the two documented compatibility decisions.

Read `/Agon/mystuff/agon-dev-env/codex/AGENTS.md` first, then `OWNERSHIP.md`,
`TODO.md`, `docs/tasks/ASY-001.md` and `docs/uart0-async.md`. The latest dated
log is `docs/devlog-2026-10-12.md`. The experiment README defines the actual
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

The Author selected Fab/Flexe for initial emulator testing and authorized
headless runs on Oryx Linux Lite. Use Oryx for compilation and emulator workloads
to avoid contention on the Pi 5. Both Pi ARM64 and Oryx x86_64 Fab/Flexe build
artifacts were inspected on 2026-10-12; their existence does not qualify this
driver. Before UART testing, audit the Fab eZ80-side interrupt/FIFO/CTS model
as well as Flexe's ESP32 side. Keep this project's fixtures isolated from the
Golem and agon-6502 owners' sources, builds and profiles. ZDS II under Wine
remains the MOS assembly/link route.

The authoritative unfinished-work list is TODO.md. Subtask IDs are immutable
short namespaces followed by three zero-padded digits and a checkbox, e.g.
`TX-005 [ ]`. Never renumber on reorder or reuse a disposed identifier.
