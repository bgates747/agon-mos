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

Jukebox's follow-up correctly adds a second limit when receive and upload windows
are fully disjoint. At UART1=576000 and RC3 UART0=1152000 (8N1), the input and
output ceilings are 57600 and 115200 bytes/s. For each second of 44100 Hz U8 mono:

```
receive wire time = 44100 / 57600  = 0.765625 seconds
upload wire time  = 44100 / 115200 = 0.3828125 seconds
sum                                  1.1484375 seconds
disjoint ceiling  = 1 / (1/57600 + 1/115200) = 38400 PCM bytes/s
```

That excludes all AT/VDU headers, CTS pauses, request latency and software work.
Thus 576000 makes 44.1 kHz plausible on the input link alone, but cannot sustain
it with the fully separated windows proposed below. Those windows explicitly
require UART0 TEMT before incoming data, so they contain no hidden wire overlap.
VDP playback continuing during receive does not remove either transfer's cost.

44.1 kHz therefore needs actual RX/TX overlap, a faster qualified UART1 rate,
or another change. The mathematical minimum UART1 baud for disjoint 44.1 kHz is
greater than about 714532 before overhead; that is not a recommended or directly
representable baud setting. If both links actually ran at 1152000, the ideal
disjoint ceiling would be 57600 PCM bytes/s, with 0.765625 seconds wire time per
second of 44.1 kHz audio. That input rate is unqualified on this module and leaves
only about 139 microseconds to fill an initially empty 16-byte RX FIFO. Neither
larger prebuffering nor additional CPU alone can overcome an average wire-time
deficit. The 8 kHz separated-window baseline remains useful. Keep higher-rate
overlap and higher-baud trials as distinct possible follow-ons, not measured
capabilities or implementation authorization.

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

Read subsequent owner introduction
`2026-11-07_02-59-06_linux-extender_u1-jukebox-stream-owner-introduction-five`.
Jukebox is included in common UART1/API/lifetime coordination; it owns the
stream/player, UART the generic driver, Extender EMOS glue and MechAgon its
caller. Extender's 115200/no-handshake ESP8266 notes agree with this retained
baseline, but do not establish the actual baud/protocol of a future stream.
The failed EMOS/P4 1152000 hardware-flow-control trial remains separate.

Extender additionally clarifies that a positively drained source and coherent
IDLE/no-FAULT state may skip redundant foreground EMOS op4 for TX scheduling
only. This does not establish continued hook ownership: EMOS demand0 abort can
remove a hook while the app still appears IDLE. Preconstruction SUBMIT admission
and positive owner close remain mandatory. No new cached-ownership API or vanilla
driver change is inferred; this is not an overrun correction. Existing Jukebox
vanilla finish/source-release/close distinctions remain as documented above.

## First finite binary receive pass: NET-001-R0003

Read Jukebox's
`2026-11-07_03-09-46_jukebox_net001-console8-r0003-receive-pass-agon-mos`
and retained `console8-r0003/review.json`, `N0001.log`, `N0001.pcm` under
`/Agon/mystuff/AgonJukebox/.emulator/net-001-worktree/docs/tasks/NET-001`.
Brandon ran receive-only netrecv build 7a134655af4e3e7b, executable 21128 bytes,
SHA256 `0ad22c3d0ef0590e03def140cd2c5958634d9d8ebd88dffa594955fe3ae353a9`.
Unchanged U1 r05 at 115200/8N1, 4096-byte ring, 32 requests of 256 PCM bytes.

Result0/complete, close0, parser_error0, UART received10376 bytes (including setup
and framing), overflow/fault/line_errors all0, sampled RX high-water21,
socket closed and AT-ready. Capture8192 bytes SHA256
`9399ecf25dfb3fded216ece1e6cd852f78d89ef4d95a04af8b17b0fcfb308a82`.
UART independently verified retained capture length/hash. Jukebox reports its
offline comparison matches the first8192 raw PCM bytes of Africa_8000.wav exactly;
UART did not independently repeat that WAV comparison. There was no runtime PCM
checksum. This is a first physical binary +IPD/JPCM receive pass, not audio or
simultaneous UART0/1 evidence. Original files and failed prior evidence remain.

The receiver logs134 MOS counts for the GET/receive loop, outside connection
setup and disconnect. At nominal120 counts/s that is about1.1167 seconds and
7336 PCM bytes/s, versus1.024 seconds of 8 kHz audio. RC3's VBlank handler adds2
counts per VBlank: 120 counts/s requires actual60 Hz delivery and is not a
universal centisecond clock. No calibration was made. Also,10376 RX bytes cover
the whole session, not just that timed loop; do not subtract8192 and label the
remainder timed framing overhead. The small sampled high-water is not an exact
peak, nor is foreground_passes a CPU percentage.

The result supports Jukebox's proposed512/1024-byte credit comparison at fixed
115200/source/sample rate before paced playback. It does not isolate how much
time belongs to AT overhead, network delay, parsing or driver costs, guarantee
larger windows achieve sustained8k, or select another build/run. Driver source,
firmware, EMOS work and custody are unchanged by this feedback.
