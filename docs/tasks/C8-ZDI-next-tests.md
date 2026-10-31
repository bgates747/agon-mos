# Console8 recovery: next diagnostic tests

Latest2026-10-30: Author handed back Console8/WROOM on direct Oryx USB. With no
reported signal-probe reconnection, the first identity is invalid F8 10 3E 46;
test stopped, outputs released, no target programming. See
[the C8 run](../c8-zdi-unprobed-2026-10-30.md). TRY-003 remains the next physical
comparison; preserve an unprobed baseline before attaching measurement leads.

Update2026-10-30: the Author authorized the Pi5 Olimex campaign. TRY-001,
TRY-002 and TRY-005 are complete with scoped outcomes in
[the campaign record](../olimex-zdi-control-2026-10-30.md). With all signal
probes disconnected, the control gives20/20 exact identities. Two-probe
operation remains intermittent. Remaining physical work and the Console8
handback await the Author. The specifications below remain the recorded plan.

Recorded 2026-10-30 at the Author's request. **Await the Author's readiness;
do not execute these tests or change hardware merely because they are listed.**
The unfinished checkboxes are in [TODO.md](../../TODO.md); identifiers below
are immutable and retain the priority order discussed in chat.

The objective is reliable Console8 ZDI communication, followed by restoration
of verified stock MOS 3.0.2. The experimental native MOS remains withdrawn.
The latest [four-probe diagnosis](../c8-zdi-four-probe-diagnosis-2026-10-29.md)
and [color discrepancy audit](../audits/sniffer-color-audit-2026-10-29.md)
are the evidence baseline. Preserve earlier documents and raw captures.

## TRY-001 — Audit the measurements again

Software/evidence review first; physical confirmation only when the Author is
ready. Recheck raw eight-channel packing, physical probe identities, attachment
locations, clock-to-frame association and the 13 transmitted-bit positions.
Compare source GPIO snapshots with both ends' settled levels. Distinguish
brief disturbances at an edge from a level wrong throughout the inspected
window. Review passive/released levels and whether analyzer channel thresholds,
loading or ground reference could explain disagreement.

The fixed Author-confirmed arrangement is:

| Analyzer probe | Signal and location |
| --- | --- |
| GREEN / D0 | GREEN CLOCK at Console8, after the resistor |
| BLUE / D2 | BLUE DATA at Console8, after the resistor |
| RED / D5 | GREEN CLOCK at WROOM, before the resistor |
| BROWN / D7 | BLUE DATA at WROOM, before the resistor |

D3 is ORANGE, never BROWN. Historical removal observations do not override the
confirmed color map. Record any new observation separately, without repairing
old evidence to match it. Completion means a reproducible statement of what
is actually measured and which assumptions still require a bench check.

## TRY-002 — Weaken only GREEN CLOCK drive

Prepare a private WROOM diagnostic that changes only GREEN CLOCK drive strength,
with BLUE DATA drive, protocol, edge delays, wiring and resistor values fixed.
Earlier weak-drive comparisons changed both pins, so they do not isolate this
variable. Clock open-drain was separately tested and did not restore valid IDs;
it is not the same experiment as reduced push-pull drive strength.

Use matched baseline/changed/baseline/changed phases with five slow identity
reads per phase and all four probes. Preserve raw extra edges, settled outgoing
bit checks, reply/software agreement and actual settings. Confirm the quiet
startup/release behavior before installation. Restore the baseline and release
both outputs afterward. A smaller glitch count alone is not a communication pass.

## TRY-003 — Shorter signal paths and better ground return

When the Author is ready for physical changes, use short GREEN and BLUE leads
and arrange a nearby ground return for each. Do not invent a ground-wire color.
Keep resistor values and software fixed, record the actual wiring change, and
repeat the same paired-end capture. Do not make several unrecorded wiring,
power-source and probe changes and attribute the result to one of them.

## TRY-004 — Analog waveform inspection, if equipment is available

An oscilloscope is optional; its availability has not been established. Inspect
actual GREEN CLOCK and BLUE DATA voltages, edge shape and ground reference at
both resistor ends and, where safely accessible, the target pins. Look for
ringing through input thresholds, slow edges, sustained voltage drop and
possible opposing drivers. Correlate with the digital capture. Do not infer
voltage, current or contention solely from HIGH/LOW analyzer readings.

## TRY-005 — Repeat the known-working Olimex control

Only when the Author makes that board and the same WROOM/harness available,
repeat the earlier slow identity test with the reported 33 Ω resistors and
record probe locations. The earlier control returned five exact
`07 00 AA 1C` identities. Establish whether this remains reproducible; do not
assume it from history. Do not erase/program Olimex MOS for this control, or
interrupt an Extender bench owner. Preserve its current firmware.

## TRY-006 — Investigate onboard Console8 ESP32 recovery

This is a feasibility task, not an approved wiring recipe. The standard recovery
utility requires an external ESP32 for Console8. Compare a private minimal
recovery build with temporary reuse of GPIO26/GPIO27, normally mouse CLOCK/DATA.
Check access, output-only expansion buffers, PS/2 bidirectional level shifters,
pull-ups, voltages and connected loads before proposing connections. An exposed
mouse connector is not automatically a safe direct 3.3 V ZDI connection.

Console8 Rev 2 exposes five spare input-only ESP32 pins, GPIO35–39; Olimex Rev B
also exposes these plus the two spare bidirectional pins GPIO26/GPIO27. The C8's
five inputs cannot directly drive ZDI. Pins already assigned to board functions
must not be counted as free. No jumper is documented to route onboard ESP32 to
ZDI. No board modification or onboard ESP32 installation is authorized merely
by this investigation item.

## Comparison and recovery gates

The resistor-value comparison remains separately recorded as DG-005 in the
four-probe diagnosis: GREEN CLOCK 33 → 68 → 100 Ω, BLUE DATA held at 33 Ω.
Those values are experimental, not a proven fix. Power off both boards before
physical resistor/wiring changes. None of the listed physical changes has been
performed by this planning turn.

For all new runs, record actual settings and probe endpoints, preserve raw
captures/serial output, and use fresh sequential run directories. Require
repeatable correct identity and verified RAM upload/readback before executing
the flash agent. No flash gate is removed by these tasks. After actual stock
recovery, full flash verification and the Author's successful boot confirmation
remain necessary. P4 normal-firmware restoration remains deferred until repair.

## Sources

- [Console8 Rev 2 schematic, printed pages 14–16](https://heber.co.uk/wp-content/uploads/2024/01/Heber_Agon_Console8_user_manual-2.pdf#page=16).
- [Olimex Agon Light 2 Rev B schematic](https://github.com/OLIMEX/AgonLight2/blob/main/HARDWARE/AgonLight2_Rev_B/AgonLight2_Rev_B.pdf).
- [ESP32 GPIO restrictions](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/gpio.html).
- [Agon recovery utility: ESP32 target requirements](https://github.com/AgonPlatform/agon-recovery#utility-esp32-target).
- [Zilog TN0035: ZDI electrical design guidance](https://www.zilog.com/docs/ez80acclaim/appnotes/tn0035.pdf).
