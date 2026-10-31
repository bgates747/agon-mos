# Console8 unprobed identity check — 2026-10-30

Removing the analyzer signal probes restored repeatable identification on
Olimex, but the equivalent Console8 check still fails. This run does not
establish whether Console8 receives the requests correctly or what electrical
mechanism remains. No analyzer waveform exists for this comparison.

## Setup and execution

The Author moved WROOM and Console8 to direct Oryx USB ports, without intervening
hubs, retaining their signal connection. Initial discovery found only WROOM;
the Author then confirmed Console8 had been unpowered and powered it on.
Subsequent USB discovery identified WROOM CP2102/serial0001 and Console8
CP2104/serial027E3885, both directly beneath the host root hub. Neither serial
port had an owner. The WROOM port alone was opened.

The last confirmed physical setup has both33 Ω series resistors and all four
sniffer signal probes disconnected. No later probe reconnection was reported.
The maintained identity helper records this inherited physical-state assumption
explicitly; no analyzer or hardware-side measurement verifies it in this run.

Used the installed quiet identity-only v3 programmer, checked by its exact boot
banner. No WROOM firmware installation occurred. One WROOM-only reset preceded
the test; no target reset was requested. The prepared host runner permits only
P/T/Q, records raw serial data and GPIO snapshots, and stops at the first bad
identity or local driven-bit check. Its parser was checked against the archived
passing v3 transcript and mutations of a local input and identity before use.

## Result and limits

First slow read: **F8 10 3E 46**, product10F8/revision3E: invalid. All13 local
driven-bit snapshots pass. Those snapshots check the WROOM input, output latch
and output enable; they do not prove signals at Console8 or all waveform edges.
The planned four sets of five reads stopped after this first failure.

Final P confirms both GPIO output enables cleared, GREEN HIGH and BLUE LOW.
These are WROOM-side digital observations, not a measured target voltage or
proof of a short/opposing driver. Both signals were released and the serial
port closed. No target halt, RAM access, programming, flash erase or target
reset command occurred. Console8 MOS remains unrecovered. The prepared stock
recovery programmer remains off-device, and P4 normal restoration is deferred.

Olimex's20/20 unprobed control remains a separate result. Probe attachment
demonstrably affects that setup, but removing probes and USB hubs has not
restored valid identification on this Console8 setup. Do not infer successful
Console8 RAM/flash communication or attempt blind programming from the Olimex
control. The next physical investigation remains TRY-003: shorten GREEN/BLUE
paths and improve their nearby ground return, retaining software and resistor
values. Establish an unprobed baseline first; adding probes changes the setup.
Wiring changes require the Author, with both boards powered off.

## Evidence

Raw serial, exact executed runner, USB discovery/topology, programmer USB
properties and result.json are retained on Pi and Oryx at
`build/zdi-unprobed-20261030/c8-direct-usb-001/`. The Pi copy was independently
checked against the Oryx receipt's raw serial and runner SHA256 values:

- console.bin:0b29c5806357ec8db5093b5d6df55665fe6ec84a61afde7d5e8ae176f99d8a61
- runner.py:92e59c4378d3ab29455e7dcad3f2932f354d2e39ed845381b667f8bedac74f52

The new helper is experiments/zdi-wroom-diagnostic/identify_unprobed.py. It
requires no analyzer, preserves every attempted reply, and never treats a
completed observation run as a successful identity qualification.

## Author-swapped GREEN/BLUE comparison

The Author switched BLUE and GREEN and requested another check. Run
`build/zdi-unprobed-20261030/c8-swapped-signals-001/` returns FF FF FF FF on
the first slow read, with all13 WROOM local driven-bit checks passing. Stopped
there; both outputs released, both local inputs HIGH, serial closed. No target
reset/halt/RAM/flash operation requested. The swap does not restore valid
identification; all-FF alone does not establish the exact wiring fault or
prove the CPU is disconnected. Raw evidence is retained on Oryx and Pi.
Console SHA256:597b80e7d62792836e09fad1fda4ded1f019e98cc9797085d75d749a211a4fb9.

## Direct wires, no series resistors

The Author bypassed both series resistors and requested another identity check.
No reversal of the preceding GREEN/BLUE swap was reported; actual connector
endpoints remain unverified. Run c8-direct-wires-001 returns C6 7F FF FF on
the first slow read, with all13 local drive snapshots passing. Stopped there,
released both outputs, both local inputs HIGH, serial closed. No target reset,
halt, RAM or flash command requested. Removing resistors has not restored a
valid identity in this setup. Raw evidence is on Pi/Oryx under the same
build/zdi-unprobed-20261030/ parent. Console SHA256:
048b57e755fb036c25ecebf0178a84a58de6dca3d11527f8890399aebab0a9b0.

## Direct-wire repeatability, no resets between reads

The Author requested five identical trials. One initial WROOM-only reset,
then repeated T commands with no intervening resets or wiring changes:

| Trial | Raw reply | Local drive checks |
| --- | --- | --- |
| 1 | C6 7F FF FF | pass |
| 2 | FF FF FF FF | pass |
| 3 | FF FF FF FF | pass |
| 4 | FF 88 1E 62 | fail |

The host permitted repeated invalid identities for this explicitly requested
comparison but retained its local drive-failure stop. It therefore stopped
after trial4 rather than sending trial5. Replies vary under unchanged settings;
four observations do not establish statistical randomness or its cause. This
run additionally records disagreement at WROOM's own input during a driven-bit
snapshot. No analyzer waveform or analog voltage measurement was taken.
Both outputs released, GREEN HIGH/BLUE LOW, serial closed. No target reset,
halt, RAM or flash operation requested. Evidence on Pi/Oryx:
build/zdi-unprobed-20261030/c8-direct-wires-repeat-five-001/.
Console SHA256:3bb18f3636c18def324cb4b5c9e5fe11bdd0b4ba1d5daed4f7aa0f7b9ee1fec2.

## Alternate WROOM pins18/19, series resistors restored

The Author confirmed the boards connected/powered after instructions to use
GREEN CLOCK WROOM GPIO18 -> C8 pin4 and BLUE DATA GPIO19 -> C8 pin6, and
explicitly authorized WROOM flashing/testing. The Author restored series
resistors;33 Ω is the last measured value, not a new measurement. No signal
probe reconnection was reported. Physical endpoints were not independently
measured. This changes pins and restores resistors relative to the immediately
preceding direct-wire run, so any changed repeatability cannot be attributed
to GPIO selection alone.

Prepared v9 from the maintained v8 source by changing every GPIO26 reference
to18,27 to19, and the distinguishing banner to v9. No protocol/edge-timing
change. Checked against Espressif ESP32 GPIO documentation:18/19 are general
bidirectional pins without the strapping/flash/input-only restrictions.
Original26/27 are also supported digital pins; no generic defect of those
pins is established by the preceding errors.

WROOM CP2102 identity and MAC40:22:d8:76:01:c8 checked before programming.
Backed up app0 affected span274432bytes; its267904byte prefix exactly matches
the installed original quiet v3. Installed only app0 at10000h, verified with
esptool plus full readback comparison of image and FF erase padding. Confirmed
quiet v9 GPIO18/19 boot before any identity command. New image271632bytes,
SHA256097b58aacc9fa8d197808cbee982eb38c1126082eb7494dd19168fab3e248d08.
Installer/evidence: build/zdi-alt-pins-20261030/wroom-v9-install-001/.

First run c8-alt18-19-resistors-001 stopped after one FF FF FF FF reply.
Follow-up c8-alt18-19-repeat-five-001 completed five identical slow reads in
one session, with no resets between reads: all five FF FF FF FF. All78 local
drive snapshots across the six reads pass. No valid product/revision in6reads.
This is repeatable all-HIGH sampled reply data, not successful communication
or proof that the target is disconnected or which endpoint is wrong.

Final outputs released, both local inputs HIGH, serial closed. Installed
WROOM is now v9 on18/19, not v3 on26/27. No Console8 reset, halt, RAM or flash
operation requested. The stock-MOS repair programmer remains off-device.
Pi copies independently verify the WROOM before/after images and both raw
serial/runner hashes against the Oryx receipts. All artifacts retained on
both machines under the stated build directories.

## Alternate pins, Author reversed GREEN/BLUE

The Author reversed GREEN/BLUE and requested another check. Firmware remained
v9, CLOCK on GPIO18/DATA on GPIO19; series resistors retained. Run
c8-alt18-19-swapped-five-001 completed five slow reads without intervening
resets: all FF FF FF FF, all65 local drive snapshots pass. No valid identity.
Both outputs released, both local inputs HIGH, serial closed. No Console8
reset, halt, RAM or flash command requested. Wiring remains Author-reversed;
receipt GPIO/color labels describe firmware logical assignments, not a fresh
physical verification. Raw evidence retained Pi/Oryx under
build/zdi-unprobed-20261030/c8-alt18-19-swapped-five-001/.
Console SHA256:cd7e9b320371466bf97e4293d8352eed023743c78c11fe4b8711f2db12c520fe.

## Leads replaced with the passing Olimex leads

The Author replaced all leads with those that passed on Olimex. WROOM remains
v9 CLOCK=GPIO18/DATA=GPIO19; physical endpoints were not independently checked.
Resistors were last reported present, but their retention with the replacement
leads was not explicitly reconfirmed; receipt value33ohms is inherited, not a
new measurement. Run c8-olimex-leads-five-001 completes five slow reads with
no intervening reset: all FF FF FF FF, all65 local drive snapshots pass.
Both outputs released, both local inputs HIGH, serial closed; no target
reset/halt/RAM/flash requested. Raw evidence retained Pi/Oryx under
build/zdi-unprobed-20261030/c8-olimex-leads-five-001/. The full serial transcript
is byte-identical to the preceding swapped-wire run, SHA256
cd7e9b320371466bf97e4293d8352eed023743c78c11fe4b8711f2db12c520fe.

## WROOM-side wiring attachment

The Author reports attachment on the WROOM side of the series resistors.
Agent incorrectly asked whether this meant probes; Author explicitly confirms
NO SNIFFERS ATTACHED. This is a wiring update, not an analyzer attachment.
The run receipt's pending/unknown probe state is superseded by a separate
operator-clarification.json; original evidence remains unchanged.
Run c8-wroom-side-attachment-five-001 completes5reads, allFF FF FF FF,
all65 local drive checks pass. No waveform acquired. Outputs released,
both local inputs HIGH, serial closed. No target reset/halt/RAM/flash.
Evidence on Pi/Oryx under build/zdi-unprobed-20261030/.
