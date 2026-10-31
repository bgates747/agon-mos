# Console8/WROOM1000-read identity test

Console8 returned the correct eZ80 identity on all1000requests. We now have a
clean identity-read result on the previously unrecovered board using the same
WROOM firmware/timing as the clean Olimex controls. This does not verify target
RAM writes, flash contents or MOS boot. No recovery flash was attempted.

Author confirms Console8 and WROOM moved toOryx, wired the same as the last
working Olimex setup: BLUE GPIO26/TCK to reported ZDIpin4, GREEN GPIO27/TDI to
pin6, ground upper-middle(reportedpin3), no inline resistors, same breadboard.
Device CP2102/WROOM identity confirmed; no programmer firmware modification.
Archived identity-onlyv3 banner verified after each programmer-only restart;
expected firmwareSHA256 abaa0bc98876389f14a2f92a47115a5e95a5009dd1975f61a026d74978984fd9.

Same S/10us edge-delay commands and50ms firmware gaps, ten WROOM-only restart
epochs of100reads each. Host runner adds an explicit target argument so this
run is labeledConsole8 rather than the prior hardcodedOlimex. No wire-protocol,
read order or firmware changes.

| Measurement | Result |
|---|---:|
| Correct product0007/revisionAA |1000/1000|
| Incorrect product/revision |0|
| Complete07 00 AA 1C |996|
| Complete07 00 AA 18 |4|
| FirstafterWROOMrestart correct |10/10|
| Local driven-bit checks passed |13000/13000|
| Each100-read epoch |100correct|

Status1C/18 differs only in IEF1interrupt-enable flag; identity is unchanged.
Runner100.470seconds onOryx. Zero identity failures gives one-sided95%binomial
failure upper bound0.299%, conditional on independent stationary trials;
repeated reads may correlate. No high-speed/flash or cross-condition claim.

No Console8 reset, CPU halt, RAM access or erase/program requested. Both WROOM
output drivers released; BLUE/GREEN both locallyHIGH, serial closed, no polling.
WROOM stays identity-onlyv3. Console8 MOS recovery remains pending; no new boot
observation was made. P4 unused; original P4 restoration remains deferred.

Raw transcript/results and exact runner/helper snapshot retained onPi/Oryx at
build/c8-wroom-identity-20261030. Source:
experiments/zdi-wroom-diagnostic/statistical_identity.py. TranscriptSHA256
1abfcc8282d4efced6a0f94f9cfd805b3bb4b10254296788f60b021a991c5dcc.
