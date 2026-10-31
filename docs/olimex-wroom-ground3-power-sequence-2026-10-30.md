# Olimex/WROOM repeat after confirmed MOS boot

The upper-middle-ground setup again returned1000/1000correct eZ80 identities.
The Author confirmed MOS booted before testing after powering WROOM first and
Olimex second. No recovery flash was needed for the earlier startup incident.
This is a clean identity-read result, not qualification of flash writes or
higher communication speeds. Post-test keyboard/pixel behavior is not observed
by the agent.

Author-confirmed direct wiring: BLUE GPIO26 to ZDI4/TCK, GREEN GPIO27 to
ZDI6/TDI, ground upper-middle(reportedpin3), no inline resistors. Same improved
breadboard and archived identity-onlyv3 firmware, SHA256
abaa0bc98876389f14a2f92a47115a5e95a5009dd1975f61a026d74978984fd9.
Both powered off/reconnected, WROOM powered first, then Olimex; both banners
and idleMOS prompt reported. Test retains the previous ten WROOM-only restart
epochs of100reads each. No Olimex reset. S commands use10us edge delays and50ms
firmware gaps; no firmware rewrite or timing change occurred.

| Measurement | Result |
|---|---:|
| Correct product0007/revisionAA |1000/1000|
| Wrong identities |0|
| Complete07 00 AA 1C |998|
| Complete07 00 AA 18 |2|
| FirstafterWROOMrestart correct |10/10|
| Local driven-bit checks passed |13000/13000|
| Each100-read epoch |100correct|

Status1C/18 differs only in IEF1interrupt-enable flag, not product/revision.
Runner108.032seconds. Conditional independent-trial one-sided95%identity-failure
upper bound0.299%; repeated reads on one setup may correlate. Ground-position
history remains upper-middle1000pass, upper-left0pass, upper-middle1000pass.
No analog measurement or connector-pin continuity determination assigns cause.

No Olimex halt/reset, RAM access or MOS erase/program requested. WROOM outputs
released afterwards, BLUE/GREEN both locallyHIGH; host serial closed, no polling.
WROOMv3 remains installed. P4 unused; no Console8 action in this run.
Raw results/logs onPi/Oryx: build/olimex-wroom-breadboard-20261030/
run-004-ground3-ordered-power. TranscriptSHA256
44b19bf4cf294a7b38b37b6a59e544f5b67b87799b5905058c0b40f5d13695f5.
