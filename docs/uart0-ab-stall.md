# AB-006: native A/B receiver stall

Executive summary: a hardware-watchpoint trace catches the VDP receive ISR
disabling RX interrupts after the other core has recovered its buffered data
and cleared the recovery flag. This strands incoming bytes and holds CTS
blocked. A one-shot diagnostic RX re-enable restarts transmission. The captured
failure mechanism is established; no production repair or renewed hardware
readiness is claimed. The original human stall has no RAM snapshot, so
attribution of that run to the same mechanism remains an inference.

## Captured evidence

The unchanged native image is SHA-256
`8c7bab73b14a0a9f5903fb781fe252ff6fca1412354993a6f079b911ae184d4e`.
Oryx runs use the original frozen frontend/adapter/Golem VDP and a separate
auto profile. Off-screen X11 uses Xvfb, without opening a desktop window.
Runtime/source identities and every attempt are retained under
`build/uart0-ab/host-stalls`; debugger-assisted attempts are separate under
`build/uart0-ab/debug-stalls`.

Attempt012 stalls at repeat3/mode3/phase1. Its RAM shows 400 of749 packet bytes
accepted, with349 outstanding; eZ80 UART holding/shift registers are empty,
CTS is blocked, and modem wakeups remain enabled. That initial capture lacks
VDP peripheral/driver snapshots, so it only narrows the boundary.

Attempt017 stalls at repeat3/mode3/phase0. Two read-only host captures, after
15 seconds without TX progress, retain the following state. The snapshots
temporarily stop only the owned emulator and resume it between captures.

| Witness | First snapshot | Second snapshot |
|---|---:|---:|
| Descriptor accepted / outstanding | 448 / 15936 | 448 / 15936 |
| eZ80 foreground useful work | 11644886 | 12274624 |
| eZ80 IFF1 / IFF2 | 1 / 1 | 1 / 1 |
| MOS clock | 4236 | 4248 |
| UART IRQ count in this phase | 31 | 31 |
| eZ80 UART IER / CTS / modem delta | 0x0D / 0 / 0 | 0x0D / 0 / 0 |
| eZ80 holding FIFO / shift / RX errors | 0 / empty / 0 | 0 / empty / 0 |
| Adapter ingress queue / UART pending | 0 / 128 | 0 / 128 |
| ESP32 UART2 unread FIFO | 128 | 128 |
| ESP32 UART2 raw / enabled interrupts | 0x4103 / 0x94 | 0x4103 / 0x94 |
| Firmware ring size / queued items | 256 / 0 | 256 / 0 |
| Driver buffered / current-read bytes | 0 / 0 | 0 / 0 |
| Driver full-recovery flag | false | false |
| Driver requested RX interrupt mask | 0x101 | 0x101 |
| FreeRTOS ticks | 37459 | 37560 |

The requested RX-full/timeout causes (mask0x101) are pending in raw status but
disabled in INT_ENA. Neither the UART ISR nor application reads of an empty
software ring can transfer the unread bytes. The adapter consequently holds
CTS blocked. The MOS descriptor and borrowed source remain intact, and CPU
work continues. This is receiver backpressure with a missing receive wakeup,
not evidence that OTIRX alone hangs or that the foreground disabled interrupts.

Full evidence is archived on Pi/Oryx as `build/uart0-ab/capture-017.tar.gz`;
decoded summaries are in `experiments/uart0-ab/stall-results.json`. The capture
tools pin frontend/adapter layouts and firmware ELF before interpreting them.
Returned control attempt015 has an empty UART FIFO, enabled RX causes (0x195),
empty ring and cleared recovery flag; the failure-state oracle rejects it.

## Traced ordering and ownership

The emulator project's independent [FX-006 findings](../../flexe-agon-emulator/docs/tasks/FX-006/findings.md)
describe the same terminal pattern in a different consumer and firmware ELF.
This project independently inspected its own pinned ELF rather than reusing
that firmware's instruction addresses. Its actual driver contains:

| Instruction | Operation |
|---|---|
| 0x401287DE | ISR sets full-recovery flag before taking the UART lock |
| 0x40128DC6 | Reader recovery clears the flag under the lock |
| 0x40128D62 | Reader recovery re-enables requested RX causes |
| 0x4012880A | ISR masks RX causes after taking the lock |

Attempt026 catches that ordering in the unchanged default scalar kernel's
paced phase (repeat2/mode1/phase1). A bounded hardware-watchpoint history records
39 value transitions, after normal recovery sequences earlier in the run:

| Event | Change | Core0 PC / Core1 PC immediately after the write |
|---|---|---|
| 37 | ISR full flag0→1; RX still enabled0x195 | 0x40093E51 / 0x401287E1 |
| 38 | Reader full flag1→0; RX still enabled0x195 | 0x40128DC9 / 0x40093D73 |
| 39 | ISR INT_ENA0x195→0x94, with flag already0 and ring empty | 0x40176776 / 0x4012880C |

Hardware watchpoints record value changes, so a recovery write that leaves
INT_ENA at0x195 generates no separate event. The clear-before-late-disable
ordering is directly observed. Actual ELF disassembly independently places
the ISR store after lock acquisition and the earlier full-flag store before
it. This establishes the receive-buffer recovery race in the captured emulator
execution; it does not establish that Flexe executes an invalid instruction
or that this ordering has occurred on the Console8.

After the trace detached, two read-only snapshots show432 accepted and317
outstanding bytes, the same128-byte unread FIFO and0x94 interrupt mask, empty
ring/false flag, with both eZ80 interrupt flags enabled and clocks advancing.
Only then, in this isolated diagnostic process, GDB issued one UART2 INT_ENA
MMIO write0x94→0x195 through the existing memory/peripheral path. TX ingress
advanced from1051365 to1098332 bytes after one second. This demonstrates that
restoring receive wakeups releases the backpressure. It does not demonstrate
correct final parser state or byte integrity after the stalled interval, and
the intervened run is permanently disqualified as a benchmark/qualification.
Evidence: `build/uart0-ab/capture-026.tar.gz` on Pi/Oryx and the traced_failure
section of `experiments/uart0-ab/stall-results.json`.

The next dependency is this agent's controlled VDP hardware diagnostic under
HW-002, followed by a receiver correction if supported by physical evidence.
The Author clarified VDP firmware ownership belongs here; Flexe owns emulator
behavior and its regression. The firmware remedy
should make publishing the full condition and disabling RX atomic with reader
recovery under the same UART lock, then verify associated ring/ISR behavior.
Any model/scheduling remedy must justify hardware fidelity rather than merely
hiding this legal cross-core interleaving. No other project's sources, runtime
or profiles were edited. Do not force RX interrupts on in the installed
runtime, suppress CTS in MOS, add retries to the measured path, or extend the
test timeout as a qualification fix. The one-shot re-enable is diagnostic only.

AB-006 remains open in the sole TODO. Its correction/regression gate still
applies to production qualification. On2026-10-14 the Author explicitly selected
an exploratory Console8 comparison before receiver correction; menu8 and
numbered reports are staged under that authorization. This exception does not
represent a repaired emulator or production clearance. Earlier Console8 results retain their scope;
these emulator snapshots establish neither a physical failure rate nor safe
physical CTS timing.
