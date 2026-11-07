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

For RX-005, Brandon superseded the earlier diagnostic-VDP ownership on
2026-11-07: this agent coordinates the goal and owns MOS changes and original
synthetic test fixtures only. The VDPlet owner owns every VDP/VDPlet firmware
change. Neither owner edits game code for this goal. Obtain a passing finite
synthetic trial, then stop for Brandon's review before distributing prototypes
to consumer project agents. Existing historical diagnostic ownership below is
not authority to cross that new boundary.

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

## Oryx emulator scheduling

Follow the shared [reservation and checkout procedure](../agon-dev-env/cross-agent/vdplet-rollout/README.md)
on the Pi. It uses a self-service FIFO queue; Golem approval is no longer needed.
Only one Oryx emulator session may run, including headless tests and human
reviews. Reserve through `oryx_lease.py`, check out with fresh whole-host idle
evidence, and assert the lease immediately before each emulator process. Stop
only owned processes, preserve results, obtain fresh idle evidence, release and
immediately notify the next agent through its recorded chat using steering.
For human review, reserve when the Author is ready, stage the profile stopped
and retain checkout until review and shutdown are complete. Do not maintain a
local queue or edit shared scheduling state by hand.

## Console8 firmware workflow

The Author prefers the installed `flash` MOSlet: from the appliance directory,
use `flash mos <filename>` or `flash vdp <filename>`. The bundled `flash.bin` is
a fallback for a self-contained appliance, not a mandatory invocation path.
On 2026-11-01 the installed `/mos/flash.bin` matched the bundled official1.9
binary byte for byte. Use explicit firmware filenames and retain the normal
updater checks. Physical flashing remains an Author action.

The Author elected to leave the startup-preserving experimental MOS and matched
test VDP installed between tests while Console8 is dedicated to this project.
Record that state; do not require stock restoration merely to close each run.
Keep stock restoration files available and revisit firmware choice before using
Console8 for another project. This is not stock-firmware or release approval.
