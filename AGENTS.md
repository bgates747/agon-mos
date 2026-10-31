# Agent instructions

## Preserve upstream toolchains

The Author clarified the policy on 2026-10-31: modifications or extensions to
official upstream firmware/software written for ZDS II must retain ZDS II.
Keep changes familiar and directly buildable for upstream developers and users
reviewing, testing or approving them. For this MOS fork, use ZDS II under Wine
on Oryx; do not migrate the firmware to AgonDev merely to add UART features.
Earlier native AgonDev MOS work remains historical/reference evidence, not the
selected delivery path. A toolchain migration needs explicit Author direction.

For original software, prefer free/open-source tools, including AgonDev. This
includes our standalone menu/test applications. Apply the upstream project's
own existing toolchain to VDP modifications; this policy does not mean building
ESP32 firmware with ZDS II. Permission to use AgonDev for original applications
does not authorize changing an upstream firmware project's compiler.

## UART0 project ownership

This agent owns MOS-side UART0 work and the diagnostic VDP firmware needed for
its physical Console8 tests, including receiver instrumentation, controlled
race triggers, test integration and interpretation. The Flexe agent owns the
emulator and its model/regression work; do not delegate VDP firmware ownership
to it. The Author clarified this boundary on 2026-10-14. Keep upstream VDP and
SDK checkouts read-only and build diagnostic copies in this project's workspace.
Physical Console8 firmware flashing and board execution remain manual Author
actions. On2026-10-15 the Author separately authorized unattended UART hardware
testing through Agon Extender, adapting the suites and integrating the sender
into EMOS at least in Legacy mode. Follow Extender's test-appliance lifecycle,
bench ownership, installation and recovery protocols for that target; this does
not authorize interrupting another owner's test or changing wiring.

## Hardware instructions to the Author

Use wire colors in physical instructions. On 2026-10-30 the Author directed
matching Jeroen Venema's original diagrams: **BLUE is ZDI clock/TCK, WROOM
GPIO26 to target ZDI pin4 (lower middle); GREEN is bidirectional data/TDI,
WROOM GPIO27 to target pin6 (lower left)**, in the pictured notch-at-top view.
This supersedes the earlier 2026-10-29 GREEN-clock/BLUE-data convention;
preserve historical logs unchanged. Current diagrams and provenance are at
`../agon-extender/docs/mos-recovery/`, linked from its maintained
`../agon-extender/docs/mos-recovery.md` procedure. P4 uses GPIO46 for clock
and GPIO47 for data; do not transplant WROOM GPIO numbers onto P4.
GPIO/pin numbers supplement colors in bench instructions. Never infer that an
announced wire change is completed; use the latest Author-confirmed setup.
Do not invent a ground-wire color. Distinguish meter leads and analyzer probes
from signal wires; added RED/BROWN probes are separate physical leads.

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
