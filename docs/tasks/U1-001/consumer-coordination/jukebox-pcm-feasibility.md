# Jukebox UART1 network PCM: feasibility consultation

2026-11-07. Planning only, responding to
`2026-11-07_01-12-38_jukebox_jukebox-uart1-pcm-stream-feasibility-one`.
Brandon requested this consultation through Jukebox. No implementation,
service, build, reservation, device access or firmware change is selected here.

An 8 kHz unsigned 8-bit mono stream is a useful first candidate. The existing
UART1 driver can provide interrupt-driven receive while Jukebox retains its
UART0 player. Sustained playback is not yet demonstrated: no hardware handshake,
AT transaction delays and RC3's interrupt-blocking CTS wait are real constraints.
The initial experiment should request finite blocks rather than accept an
unbounded server push. Preserve the working SD player and audio scheduler.

## Rate and baud limits

At 115200 baud, 8N1 consumes ten wire bits per byte: 11520 bytes/s maximum,
including AT headers/status. These are arithmetic ceilings, not measured rates.

| U8 mono rate | PCM bytes/s | Raw UART capacity used |
| --- | ---: | ---: |
| 8000 Hz | 8000 | 69.44% |
| 11025 Hz | 11025 | 95.70% |
| 44100 Hz | 44100 | 382.81% |

11025 leaves only 495 bytes/s before overhead and is unsuitable as the first
live target. Live 44100 is impossible at this baud; downloading first and playing
later is a different experiment. Stereo or 16-bit samples increase bandwidth.

The actual module has AT1.3.0.0/SDK2.0.0 and has passed short exchanges at
115200 without flow control. Higher baud is unqualified on this specimen.
Espressif's contemporary manual documents volatile `AT+UART_CUR` baud changes;
that establishes an available historical mechanism, not this module's tested
limits. No ESP reflash or baud change is proposed for the first test.
[Espressif 2016 AT manual](https://www.espressif.com/sites/default/files/4a-esp8266_at_instruction_set_en_v1.5.4_0.pdf).

There is also a host divisor trap. RC3 source commit
`97311c437093e416342a6c836cf9914f2ced027d`, `src/uart.c` and `src/uart.h`, uses
integer `18432000 / (16 * baud)`. Requested and actual rates can differ:

| Requested baud | Divisor | Actual UART baud |
| ---: | ---: | ---: |
| 115200 | 10 | 115200 |
| 230400 | 5 | 230400 |
| 384000 | 3 | 384000 |
| 460800 | 2 | 576000 |
| 576000 | 2 | 576000 |
| 921600 | 1 | 1152000 |
| 1152000 | 1 | 1152000 |

Any later speed trial must match the actual generated rate on both ends. Do not
set the ESP to literal 460800/921600 while asking this MOS for the same number.

## Reuse and exact interfaces

Project `/Agon/mystuff/agon-mos`, branch `codex/uart1-app-async`; driver/fixture
source `823bb91dd4c1af5a1488e3d3361648646b601445` under
`experiments/uart1-async`. API: `include/u1_vanilla.h` and `include/u1_tx.h`.

* Library: `/Agon/mystuff/agon-mos/build/u1-001/vanilla-r05/libu1.a`, SHA256
  `b7870dff9c979b5051aec6bdd4e177dbfa29f7b6e42c1a52992fca9e4b246831`.
* Source/binary/build-evidence package:
  `/Agon/mystuff/agon-mos/build/u1-001/vanilla-prepared-r05.zip`, 355785 bytes,
  SHA256 `53797bed1686fe1e7666ed31cbafd29235f3e07e6ed0dbe91b917a8efbc61fe1`.
  Its build-time qualification note predates the hardware result below.

```c
u1_vanilla_open(115200, rx_ring, 4096);
u1_vanilla_submit(source, positive_count, flag_only_callback);
u1_vanilla_read();           // -1 empty, otherwise an unchanged byte 0..255
u1_vanilla_snapshot(&info);  // RX count, overflow, buffered, phase/fault/errors
u1_vanilla_finish();         // nonblocking: OK only at actual UART1 TEMT
u1_vanilla_stop();           // refuse new TX; drain the accepted source
u1_vanilla_close();          // restore previous vector after safe retirement
```

Check every return: OK0, invalid19, busy31, unsafe-context32, fault/unavailable35.
RX capacity is a power of two, 2..4096; usable capacity is one byte less.
This application-owned adapter requires ADL1, actual MBASE0, EI and exclusive
UART1 ownership. It uses existing MOS UART/vector services, not a new MOS ABI.
The Wi-Fi connection utility must have returned and relinquished UART1 first.
Do not mix MOS UART1 writers with an accepted async source.

The IRQ saves primary/index/shadow registers, services RX first and bounds each
RX/TX service to at most 16 bytes. It takes no PRT. Callback is an assembly RET
routine that only posts a flag: no MOS calls, output, EI or reentry. Prearm flags
before submit because completion can precede return. Keep source immutable until
callback; keep code, RX storage and callback resident until positive close.
Source callback, TEMT, ESP SEND OK, remote reply and actual audio consumption are
different events. A timeout does not revoke a borrowed source.

Assembly has `CALL u1_vanilla_submit_regs`, HL=source, BC=full positive count,
DE=callback, A=result; it preserves BC/DE/HL/IX/IY/shadows/MB, flags unspecified.
Other functions currently expose C entries, not equivalent register entries.
Jukebox needs correct AgonDev C ABI bridges/link placement for these, not guessed
register calls. Check its existing reserved packet/analyzer memory before adding
library, ring or PCM buffers. This is not a drop-in include for its assembly build.

Existing R0002 Console8 evidence passes four ordinary/async AT/GMR cases: 230 RX
bytes, matching transcripts, zero errors/overflows/fault and close0. Physical TX
was only 4/8 bytes. It does not qualify sustained receive, 16-byte TX refills,
simultaneous audio traffic, or EMOS. See `docs/tasks/U1-001/console8-r02-pass.md`
and `docs/tasks/U1-001/receipts/console8-R0002.log` (hardware evidence 412e3a1).
Driver text is 2542 bytes plus 34 bytes internal BSS, excluding caller buffers,
SDK/CRT and any new bridges. EMOS adaptation remains Extender's separate work.

## Bound incoming traffic at the server

Use a single TCP connection and a small explicit request: offset plus maximum
PCM byte count. The Pi sends only the bounded response requested, with finite
length, sequence/offset and checksum. Permit one outstanding request. Metadata
also needs a finite bound. Start with 256-byte payload windows for integrity,
then measure 512-byte windows for playback. This is a proposed new test protocol,
not an existing driver service or an ESP firmware credit facility.

TCP backpressure alone does not protect an unhandshaked serial receiver. A server
window bounds the authorized response, but does not establish unknown module
buffer capacities. Reserve space for headers/status, parse continuously and do
not equate a server response, TCP segment and `+IPD` indication. Fragmentation
can split one response across indications or coalesce application data.

Use the observed active `+IPD` mode initially. Count every announced payload byte
as opaque binary, including NUL, CR/LF and text resembling AT status. Parse status
only outside counted payload. The Extender Wi-Fi setup parser at
`/Agon/mystuff/agon-extender/tools/wifi-setup/src/setup.c` substitutes dots for
nonprintable payload bytes; it cannot be reused unchanged for PCM. The current
U1 AT fixture deliberately rejects `+IPD` and is not a streaming parser either.
Reuse command sequencing/deadlines, not these payload policies.

Modern ESP-AT documents passive receive with `CIPRECVMODE`/`CIPRECVDATA`, but its
presence and buffer sizes cannot be assumed for this old specimen. A later
read-only capability query can establish whether a pull mode is available;
ERROR should lead back to bounded active-mode requests, not a speculative reflash.
[Espressif ESP8266 receive-mode documentation](https://docs.espressif.com/projects/esp-at/en/release-v2.2.0.0_esp8266/AT_Command_Set/TCP-IP_AT_Commands.html).

For the first service, plain TCP with a finite binary response is simpler than
HTTP chunking. If HTTP is chosen, bound the complete response and use fixed
Content-Length/ranges; do not stream an entire track unsolicited.

## Buffers, interrupt interference and playback

A proposed 4096-byte RX ring holds at most 4095 bytes. A separate 8192-byte PCM
queue with a 4096-byte start prebuffer gives about half a second at 8 kHz.
These are suggested application allocations, not measured requirements. Keep
Jukebox's existing immutable UART0 staging separate. Grant a request only with
space for its complete PCM body and framing, validate it, then publish PCM to
the queue. Preserve all original audio timer ownership and scheduling.

At 8 kHz, 256 PCM bytes cover 32 ms; 512 cover 64 ms. Wire transfer plus AT
request/prompt/response and Wi-Fi jitter must fit the average budget. A large
prebuffer absorbs jitter but cannot repair insufficient sustained throughput.

RC3 UART0 waits for CTS inside its ISR with interrupts disabled. UART1 RX cannot
run during that wait. At 115200, an initially empty 16-byte FIFO fills in about
1.39 ms; this is a scale estimate, not a guaranteed safe blackout. A software ring
does not help before the ISR can run, and faster baud tightens this constraint.
Current hardware evidence does not establish a combined-stream failure or pass.

For the first playback experiment, time-separate receive windows: retire the
previous UART0 source and reach TEMT; request/receive one bounded network body;
defer new UART0 uploads, synchronous VDU/UI output and SD logging until that body
is collected; then resume uploads from the prebuffer. The VDP can play already
buffered audio meanwhile. Jukebox must check that its existing deadlines and due
queue can bridge these windows. This tests a two-port pipeline without claiming
unrestricted simultaneous reception. Then test controlled overlap separately.
Defer directory scans/redraws that mask interrupts or prevent timely parsing
while a request is outstanding. Do not put network parsing/output in the PRT ISR.

Count underruns explicitly. U8 silence is 0x80 if the existing player can insert
it cleanly; otherwise stop/rebuffer rather than replay stale data or change rate.
For initial finite tests, a reported failure and orderly drain is sufficient.
EOF must honor exact byte count/checksum and a fractional last packet. Quit stops
new credits, retires the bounded in-flight response/connection and both TX borrows,
then closes/restores UART1 and the existing audio timer. UART1 TEMT alone does not
prove there is no pending network RX. Never unload still-live callback/code/storage.

## Proposed smallest sequence — not started

PCM-001 [ ] Build a separate finite receive-only fixture: 8192 tagged/ramp bytes,
256-byte maximum request payload, explicit offset/length/checksum and binary-safe
parser. UART0 audio stays inactive; report exact reconstruction, ring wrap and
UART errors before adding playback.

PCM-002 [ ] Establish an 8 kHz SD/preloaded control through the unchanged audio
scheduler, then use the finite network source with prebuffer and time-separated
receive windows. Measure request latency and queue behavior; do not attribute
existing one-second sample-boundary behavior to UART1.

PCM-003 [ ] Compare receive-only, audio with separated windows, and controlled
UART0/UART1 overlap. Add UI activity only after quiet operation passes. Choose
window/prebuffer sizes from measured average rate and worst observed stalls.
An interrupt-starvation failure needs a separate timing/transport decision;
increasing the software ring alone cannot solve FIFO overrun under DI.

Report total received/validated PCM, expected length, sequence/checksum failures,
AT/parser errors, UART line errors/overflows, observed RX-ring high-water, PCM
queue low-water, underrun events/missing samples, PCM staged to UART0, callback
counts and final drain/quit status. Existing snapshot gives buffered occupancy,
not an exact ISR high-water; foreground sampling can miss peaks. No existing
counter proves actual VDP consumption or audible underruns. Label estimates and
source-release counts accordingly. Gather reports outside active receive windows.

UART owns generic driver corrections and its ABI advice; Jukebox owns player,
parser, scheduling and application metrics. The Pi service is a new implementation
item whose owner should be selected if Brandon proceeds. Extender can advise on
known connection utility/module facts; it retains EMOS adaptation ownership.
No resident MOS change, ESP reflash, new wiring or EMOS hook is needed to attempt
the first vanilla receive-only test. Human setup would be the already working
connection utility, an explicitly selected bounded Pi endpoint, and manual
Console8 fixture execution. Service/network/device access still awaits selection.

## Delivery and concurrent owner update

Published reply `2026-11-07_01-18-42_agon-mos_jukebox-uart1-pcm-feasibility-return-one`
in thread `jukebox-uart1-pcm-stream`, followed immediately by native chat delivery
`u1001-jukebox-pcm-feasibility-return-one`. App-server acceptance is recorded in
`jukebox-pcm-chat-receipt.json`; acceptance does not confirm reading. No guest,
service or hardware execution was performed for this consultation.

Separately read Extender's
`2026-11-07_01-16-59_linux-extender_u1-emos-provisional-owner-plan-one`:
NET-004/EMOS-ASYNC-R01 and INTEG-024 are published at 0097525a/fa9daa1. The owner
plans unchanged generic core, separate opt-in gateway and a preconstruction
lifetime guard. Actual adapter/API and size remain pending; stopped MechAgon
bench74 recovery takes priority. No provisional driver has been deployed and
no generic core fault is reported. This does not alter the vanilla consultation
or authorize new bench work; no acknowledgement-only reply was sent.
