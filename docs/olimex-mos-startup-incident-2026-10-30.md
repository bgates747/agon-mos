# Olimex MOS startup failure reported after identity tests

The Author reported VDP branding without MOS while WROOM was attached. The
Olimex subsequently booted normally with WROOM disconnected, then booted with
last-working upper-middle-ground wiring and WROOM-first power order. The
requested repeat read-only test then returned1000/1000correct identities.
No recovery flash was needed. The exact attached-circuit startup mechanism
remains unresolved; this incident is not proof of persistent MOS corruption.
No remote Olimex reset, halt or flash was attempted. Post-test physical CLI
responsiveness has not been independently observed by the agent.

## Preserved sequence

Three1000-request WROOM runs used the same archived identity-onlyv3 binary,
SHA256 abaa0bc98876389f14a2f92a47115a5e95a5009dd1975f61a026d74978984fd9.
Initial33-ohm setup:325correct; direct upper-middle ground:1000correct;
ground alone moved upper-left:0correct,1000×FF FF FF FF. The earlier clean
run's raw ground5metadata was corrected by Author to actual upper-middle3;
original raw files remain with an explicit correction sidecar.

The Author subsequently reports VDP-only boot and explicitly confirms WROOM
still attached. No standalone/disconnected boot result is available yet.
Latest commanded WROOM state was output-enable release, both local inputsHIGH;
that snapshot is not proof of later physical target state.

## Read-only audit performed after the report

No device/serial/network-hardware commands were issued during this audit.
Only local source, build and log files were inspected. Raw transcript hashes
match each saved result; every test records ten quiet identity-onlyv3 banners.
The statistical runner admits only serial P,Q,S, resets only CP2102/WROOM and
does not open the CH341/Olimex serial endpoint. Its metadata fields saying zero
flash/halt/reset are declarations of intent, not an independent bus trace.

The single preparatory esptool write was to CP2102/WROOM application0x10000,
not the Olimex or its VDP. The270336-byte affected WROOM span was preserved,
and the replacement image verified. The verified identity binary contains
neither the known90-byte eZ80 flash-agent bytes nor the selected stockMOS image.
This does not prove that arbitrary target writes are impossible under corrupted
signalling. No wire capture or target flash dump exists for these1000-read runs.

The exact archivedv3 source snapshot has not yet been recovered in this audit;
current trackedv8/v7 source is not proof of byte-identicalv3 behavior. Preserve
that limitation rather than passing off later source as the executed program.

No cause assigned. In particular, do not claim MOS flash unchanged solely
because requests were intended as reads, and do not claim flash corruption
solely from a VDP-only boot with the programmer attached. No MOS flashing is
currently authorized by this incident report.

Evidence: build/olimex-wroom-breadboard-20261030, its three read-run records,
installation logs and preserved WROOM bytes. Earlier raw logs remain immutable.

## Subsequent Author boot observations

Author reports that the Olimex boots normally after disconnecting WROOM leads:
“ok thank god it comes up.” This rules out a persistent inability to boot MOS
in that standalone observation; it does not determine the exact attached-circuit
mechanism or prove every flash byte. No recovery flash was needed.

For the next test Author powered both off, restored last working direct wiring
with upper-middle ground, powered WROOM first then Olimex, and confirmed both
banners/idleMOS prompt with the boards attached. Explicitly authorized another
1000identity-only trial. The same ten-WROOM-restart/100reads-per-epoch protocol
is running as run004-ground3-ordered-power; no Olimex reset/halt/flash. The old
incident hardware hold is superseded only for that explicitly requested test.

## Authorized repeat completed

run004-ground3-ordered-power:1000/1000correct product0007/revisionAA,998status1C,
2status18(IEF1flag);13000local drive checks pass. Ten WROOM-only restarts,
firstafterreset10/10valid. Same firmware/S10us schedule. No target halt/reset,
RAM or flash. WROOM outputs released, linesHIGH, serial closed. Detailed report:
olimex-wroom-ground3-power-sequence-2026-10-30.md.
