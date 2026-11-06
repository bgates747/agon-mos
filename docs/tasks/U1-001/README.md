# U1-001: application-owned asynchronous UART1 transmission

Give applications a UART1 sender they can start and leave running while doing
other work. Keep its code, transfer state, buffers and interrupt work in application
RAM. The default target is vanilla MOS, with its application-owned UART1 vector.
The first hardware test is the Console8's configured ESP8266, connected without
CTS/RTS. Extender owns a separate EMOS adaptation and any needed firmware hooks;
EMOS integration is not a prerequisite for this driver. No resident engine.

Brandon clarified this directly in this chat on 2026-11-06 after the core tranche:
write the default for vanilla MOS; let Extender modify it for EMOS; use the C8
ESP8266 for testing. This supersedes the original EMOS-first integration gate
below. Existing MechAgon feedback remains useful downstream input.

Brandon delegated this through Extender on 2026-11-06. The original human request
was inspected in Extender thread `01a13443-f921-72d1-9d3e-d05652c7a750`, turn
`01a1b1e9-bed0-7ea2-950d-93ba11f2036b`, message
`01a1b1e9-bf2e-7f31-b016-125a1825fa43`. It explicitly assigns development to UART
in this project and requests an ABI close to UART0 async. Detailed requirements:
`/Agon/mystuff/agon-extender/docs/tasks/NET-004/UART1-APPLICATION-DRIVER-R01.md`;
mail `2026-11-06_12-35-15_linux-extender_uart1-app-async-driver-author-delegation-one`.

Owner/source: `/Agon/mystuff/agon-mos/experiments/uart1-async/` on
`codex/uart1-app-async`. This is original application software using AgonDev;
it does not change this upstream MOS fork's ZDS II toolchain or modify firmware.
MechAgon owns its consumer and Extender owns any EMOS integration.

## Work

P-001 [x] Publish this task and branch before implementation; return its path
to Extender and consult MechAgon directly. Preserve the live bench and existing
UART0 work. No target, card, firmware, emulator or vector change is selected.

P-002 [x] Audit exact stock and matched EMOS UART1 TX/RX, GPIO CTS, vector,
admission, packet-lifetime and teardown seams. Pin donors, distinguish supported
public APIs from private symbols, and identify integration gaps explicitly.

I-001 [x] Transferred to Extender by Brandon: EMOS admission/IRQ/retry hooks and
its adaptation are downstream work, not a gate on this vanilla driver. Do not
change EMOS or current NM SUBMIT here. No guessed ROM address or syscall number.

I-002 [x] Agree first-consumer requirements with MechAgon: opaque 128-byte NM
records and up to 146-byte wire frames, immutable source, separate callback and
peer reply, independent UART0 graphics, stop/drain/uncertainty behavior, and a
matched synchronous/async workload. No game/P4/schema/checksum code here.

D-001 [x] Implement the independent application-owned TX core and focused
host checks. One outstanding full 24-bit positive nonwrapping source and a
prearmed callback. Explicit result codes, first-fault retention, bounded one-FIFO
service, source-release versus wire-drain state and positive detach. No queue,
allocation, implicit retry of payload, timeout cancellation or indefinite CTS
spin. A stop request refuses new work but does not revoke a borrowed source.

D-002 [ ] Add the native OTIRX leaf, callable assembly entry and C adapter.
Prefer ordinary CALL with HL=source, BC=full count, DE=assembly callback; A is
the documented result. A UART interrupt entry is distinct from an optional RST
restart entry; no reset-vector change is required. Keep install/restore adapters
separate from the generic engine, actual MB0/ADL/IFF and register saves explicit.
Default install uses documented vanilla MOS UART1/vector interfaces with an
otherwise unused UART1. Restore the previous vector after actual source/wire
retirement. No EMOS adapter or hooks are part of this driver tranche.

T-001 [ ] Exercise real core code with byte/callback/event oracles: 1/15/16/17,
146, 65535/65536-byte boundaries; CTS already blocked or changing during rearm;
RX-first service, full-count tails, early callback, busy/invalid rejection,
fault/stop retention, correct IFF, and detach refusal while source or wire lives.
Flow control requires explicit receiver reserve; 16-byte FIFO capacity alone
does not prove that CTS can safely be checked once per burst. GPIO CTS needs a
separately agreed bounded wake source; do not invent modem interrupts.

T-002 [x] Under actual Pi compiler FIFO, build/link the original library and
worked fixture, retain source/map/disassembly/size and check ABI boundaries.
Finite initial build limit: 180 seconds per child, 600 seconds total; one serial
compiler, below 80 C and at least 512 MiB available RAM, owned cleanup/release.
Preserve failed attempts. A compile or host model pass is not target evidence.

T-003 [ ] Prepare a vanilla-MOS Console8/ESP8266 appliance and matched ordinary
versus async throughput/useful-work/RX tests, after the no-handshake test protocol
is identified. Hardware execution/deployment remains separately coordinated
with Brandon. No MechAgon live bench, renderer or EMOS firmware change.

P-003 [ ] Identify the installed Console8 ESP8266 firmware/protocol, configured
baud, buffering and available replies/credits/echo. TX/RX-only wiring remains
unchanged. Do not assume ESP-AT, transparent forwarding, XON/XOFF or a receiver
buffer capacity. Document what a reply proves before selecting the first run.

D-003 [ ] Implement the standalone vanilla UART1 install/RX/TX/restore adapter.
No-flow-control mode must ignore unconnected CTS and need no CTS retry timer;
TX-empty interrupts drive bounded FIFO refills. Preserve normal UART0 MOS/VDP
interrupts. Record RX overflow/errors so incoming ESP traffic cannot fail silently.
Keep baud/peer pacing/command parsing in the app or protocol adapter.

T-004 [ ] Test no-flow-control implications in both directions. Begin with
bounded requests and positively identified replies/readback, then increase the
outstanding data window and baud only within the peer's supported protocol.
Separate sender callback, physical drain and verified reception. Lower baud or
fixed delays reduce offered load but do not prove losslessness under arbitrary
receiver stalls. No invented acknowledgements or new peer firmware assumed.

## Initial design boundaries

The app may reuse source only after the actual callback. A callback means that
the final byte has been loaded into the UART FIFO; it does not establish TEMT
or peer execution. Keep source release, physical drain and peer reply separate.
No timeout frees callback/code/storage while an interrupt could still use it.

Use bounded ISR work: at most one configured burst of at most 16 bytes per
invocation. Mask TX-empty when CTS blocks and use a supported bounded wake/rearm
path. The matched EMOS donor explicitly describes GPIO CTS and VBlank retry for
its optional telemetry sender; modem-status wakeup cannot be assumed here.
No-flow-control links require application/protocol pacing or a qualified receiver
rate/window; the generic driver cannot infer remote free space. Burst size and
the UART baud rate are different: OTIRX fills the local FIFO quickly, while bytes
leave serially at the configured rate. Absence of CTS does not prohibit OTIRX.

Extender's matched source donor is
`/Agon/mystuff/agon-extender/agents/net004/emos-uart-rfc25-source/src` at reported
`2c79c600`; installed-image identity is the owner's record, not our readback.
UART1 receive currently belongs to `_emos_keyboard_irq_entry` and its bounded
keyboard/NM parser. NM admission sets receive state before its synchronous send.
Those dependencies are retained historical findings for Extender's adaptation.
They no longer constrain the default vanilla implementation. No owner hook is
required merely to write an application UART1 driver for vanilla MOS.
