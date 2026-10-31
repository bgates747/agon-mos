# Olimex/WROOM replacement-breadboard identity test

The link remains unreliable:325 of1000 requests returned the correct eZ80
product and revision, with failures throughout every restart epoch. This test
does not establish the breadboard as the cause. Olimex MOS was untouched.

Author-confirmed setup: WROOM onPi5, GREEN clockGPIO26, BLUE dataGPIO27,
33-ohm series resistors and higher-quality breadboard. Installed archived
identity-onlyv3 (SHA256 abaa0bc98876389f14a2f92a47115a5e95a5009dd1975f61a026d74978984fd9)
after preserving its incoming270336-byte application span. Used S commands:
10us edge delays,50ms firmware gaps plus trace-output overhead. This differs
from both Jeroen's undelayed driver and the P4 reader; their rates are not
firmware-neutral comparisons. No analyzer added or capture taken.

| Measurement | Result |
|---|---:|
| Correct product0007/revisionAA |325/1000 (32.5%)|
| Wrong product or revision |675/1000 (67.5%)|
| Complete expected07 00 AA 1C |280/1000 (28.0%)|
| Local driven-bit checks passing |13000/13000|
| First request after WROOM restart correct |3/10|

Status is separate from immutable identity because it represents CPU state.
Ten WROOM-only restarts,100reads per epoch; Olimex not reset. Total runner
time106.686seconds, excluding preparation/installation.

| WROOM restart epoch | Correct /100 |
|---|---:|
|1|31|
|2|32|
|3|27|
|4|37|
|5|27|
|6|35|
|7|35|
|8|36|
|9|30|
|10|35|

The95% Wilson interval for identity success is29.67–35.47%, conditional on
independent stationary requests. Reads on one setup may be correlated; this
is not qualification across boards or operating conditions. Common wrong
replies:07 07 07 07(141),78 78 78 78(85),F0 F0 F0 F0(60),07 01 AA 72(40).
Local GPIO checks do not prove downstream sampling or identify a physical fault.

No Olimex halt/reset, RAM access or MOS erase/program. WROOM quietv3 remains,
GPIO output enables released; final localGREENHIGH/BLUELOW is an observation,
not an assigned cause. Serial closed, no polling. P4 was not involved.
Raw traces/results and preserved WROOM bytes: build/olimex-wroom-breadboard-20261030
onPi/Oryx. Runner: experiments/zdi-wroom-diagnostic/statistical_identity.py.
TranscriptSHA256 f64f08567ace75e0cd4cee550c1d06b770133174a4ab05153c68f9cb7f3c41ce.

## Later wiring clarification — 2026-10-30

After this run the Author supplied upstream diagrams and identified a wire-color
mismatch. Both diagrams specify BLUE GPIO26/TCK to targetpin4, GREEN GPIO27/TDI
to targetpin6. Author announces changing the wiring to match. This report/raw
record retains the earlier reported GREEN26/BLUE27 setup; target endpoints were
not independently verified. These observations do not validate the intended
corrected wiring or isolate an electrical cause. No post-change test yet.
Canonical diagrams/provenance: ../agon-extender/docs/mos-recovery/.
