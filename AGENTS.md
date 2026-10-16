# Agent instructions

## UART0 project ownership

This agent owns MOS-side UART0 work and the diagnostic VDP firmware needed for
its physical Console8 tests, including receiver instrumentation, controlled
race triggers, test integration and interpretation. The Flexe agent owns the
emulator and its model/regression work; do not delegate VDP firmware ownership
to it. The Author clarified this boundary on 2026-10-14. Keep upstream VDP and
SDK checkouts read-only and build diagnostic copies in this project's workspace.
Physical firmware flashing and board execution remain manual Author actions.

## Network access authority

For access between development machines, read the [canonical network instructions](https://github.com/bgates747/agon-dev-env/blob/feature/standardized-deployment/codex/environment.md#ssh-between-development-machines) in `~/Agon/mystuff/agon-dev-env/codex/environment.md` and its machine-local `.local/ssh-001/CONNECTIONS.md` guide. They own current hostnames, discovery, SSH identities, sudo, and LAN shares. Do not duplicate access recipes or revive old aliases, addresses, or share mappings in this project. Project-specific device/protocol and bench-safety instructions remain local.

## Emulator product names

Select the name from the runtime and VDP backend: Fab uses a native host VDP;
Flexe executes actual ESP32 VDP firmware. From the profile directory, launch
Fab with `./fab-agon-emulator` and raw link `fab-agon-emulator.bin`, or Flexe
with `./flexe-agon-emulator` and raw link `flexe-agon-emulator.bin`.
Each entry must be a real generated wrapper with its existing host-library,
MOS/runtime identity and backend guards. Flexe must have no Fab-named launcher,
symlink or compatibility shim. Existing Fab launch instructions apply only to
Fab profiles. For Flexe, call the canonical setup tool's `name_flexe_profile`
after customization and before recording deployment checksums.
