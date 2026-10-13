# Isolated MOS UART0 transmitter

Executive summary: this experiment executes an assembled queue and UART ISR
against an independent scripted UART. It provides a general producer benchmark
and adversarial tests before live MOS integration. It does not install a driver,
change firmware, modify games or qualify physical timing. See
[RESULTS.md](RESULTS.md) for the measured scope and limitations.

## Reproduction

From this project root:

```bash
experiments/uart0-async/build.sh
```

The script stages native ZDS II sources on Oryx Linux Lite and assembles/links
the ADL code at 040000h using the canonical Wine launcher, builds and runs the offline Rust
runner on Oryx, runs all scenarios and benchmark variants, audits every wide memory
load/store, and verifies seven deliberately faulty variants fail for the intended
reason. Native Intel HEX, binary, map, listings, symbols, hashes and negative-control logs
live in ignored `build/uart0-async`. No Python interpreter is needed.

ZDS II eZ80Acclaim! 5.3.5 under Wine on Oryx is the only assembly/link route.
Follow the canonical `agon-dev-env/codex/environment.md` and its referenced
private connection guide for SSH and the installed `agon-zds` launcher. The
build writes only fresh project cache staging directories on that host;
vendor tools remain there. Sources use native ZDS macros, segments and data
directives; no GNU assembly translation or mos-agondev machinery is used.
Generic host `objcopy` converts ZDS Intel HEX to bytes. `read-map.rb` reads
native exported addresses and zero-fills trailing uninitialized fixture RAM
to the native map's allocated extent; it does not translate instructions.

The initial instruction-model source defaults to
`/Agon/mystuff/agon-6502/build/ez80-model`; override with `EZ80_MODEL_SOURCE`.
That CPU model is independent of the MOS build toolchain.
The model is copied once into this project's ignored build area and checked
against [model.sha256](model.sha256) on every build. A changed source is rejected.
The BSD-3-Clause model's LICENSE is retained in the copy. No sibling build,
profile or source is modified. Cargo has no network dependencies here.

The driver began from the PERF-020 bounded-pump approach, but this experiment
adds its own queue, ownership API, dispatcher, synchronization barrier and
harness. The earlier leaf and results are identified in
[ASY-001](../../docs/tasks/ASY-001.md); their test counts are not added to ours.

## Actual experimental ABI

All entries use ADL mode, full 24-bit addresses, the long stack and an ordinary
foreground caller with IFF1=IFF2. NMI, short-mode entry and production MOS call
numbers are outside this fixture. IX/IY, alternate banks, MBASE, ADL and ordinary
caller IFF are preserved. AF/BC/DE/HL are scratch except specified outputs.

A returns OK=0, BUSY=1, INVALID=2, CLOSED=3 or CONTEXT=4. Calls from this
UART ISR's receive callback return CONTEXT without mutation. No callbacks are
invoked for TX completion; foreground status/reap makes lifetime explicit.

| Entry | Inputs | Outputs / contract |
|---|---|---|
| `tx_open` | None | Open singleton session. BUSY if already open or baseline IER uses unsupported sources. |
| `tx_reserve` | None | HL=nonzero 24-bit ticket or BUSY. Three descriptors, including completed-but-unreaped ones. |
| `tx_publish` | DE=ticket, HL=source, BC=length | Borrow immutable bytes; length 1..65535, reject address wrap. Publication orders work. |
| `tx_status` | DE=ticket | B=state, HL=bytes copied into UART. Snapshot is atomic. |
| `tx_cancel` | DE=ticket | Cancel RESERVED/QUEUED only. ACTIVE and completed tickets return BUSY. |
| `tx_reap` | DE=ticket | Free RELEASED/CANCELLED descriptor; stale ticket becomes INVALID. |
| `tx_poll_drain` | None | OK only when queue empty and LSR.TEMT; otherwise BUSY. |
| `tx_close` | None | BUSY until drained and every descriptor reaped; restore original IER on success. |
| `tx_kick` | None | At most one 16-byte service burst; works with interrupts already masked. |
| `tx_barrier_enter` | None | Acquire foreground serialization barrier, excluding publication. Does not itself wait. |
| `tx_sync_byte` | E=byte | Require barrier, earlier queue drained, CTS ready; otherwise BUSY. |
| `tx_barrier_leave` | None | Release barrier; INVALID if none held. |

States are FREE=0, RESERVED=1, QUEUED=2, ACTIVE=3, RELEASED=4, CANCELLED=5.
On a failed publication, the reservation remains caller-owned. Reservation
order does not constrain publication; reservations do not stall a foreground
barrier. Monotonic tickets persist across close/open and permanently refuse
allocation at 24-bit exhaustion until driver reinitialization. No ticket is
silently reused. The production session-handle API remains a draft; this
singleton fixture is not its final binary interface.

Each descriptor is exactly 19 bytes: state:u8 followed by six u24 fields
(ticket, current pointer, remaining, accepted, original length, next pointer).
All wide accesses target three-byte fields; counts have zero upper byte by
contract. Null pointers are tested over all 24 bits. No payload allocation or
copy is hidden in reserve/publish. Callers retain stable readable RAM until
RELEASED. Each published transaction must contain whole VDP commands or a
complete command batch; the driver does not parse command boundaries.

RELEASED means source reuse is safe, including mutation before wire completion.
It does not mean TEMT or VDP execution completion. Timeouts and failed close
retain pending source ownership. Partial commands cannot be cancelled. Sticky
`tx_rx_errors` and `tx_modem_deltas` accumulate acknowledged LSR/MSR events
across sessions until explicit driver reinitialization; they do not assert TX
failure or receiver execution success. The fixture exposes these diagnostic
bytes as symbols, not a finished MOS error API.

## Interrupt behavior

`tx_isr` dispatches IIR causes and exits on no-pending without reading RBR.
Each entry handles at most eight causes, sixteen actual RX bytes and one
sixteen-byte TX service burst. RX takes priority through IIR. The receiver
fixture records bytes; it does not replace or execute the MOS VDP parser.

Refill requires THRE (whole FIFO empty) and samples CTS before each byte.
Blocked empty FIFO disables TIE and keeps modem wakeups. Idle disables both
TIE and the session's modem source. CTS is reconciled after mask changes.
After this entry has spent its TX budget, a new modem cause is left pending
rather than acknowledged and forgotten. This prevents the lost-wakeup race
found by the boundary sweep. It also exits before another IIR read once its
TX budget is spent, preserving newly pending TX requests. Flexe exposed this
second lost wakeup; see `../uart0-flexe/README.md`. There is no OTIRX burst or
DMA claim.

## Test backend limits

The eZ80 crate executes actual instructions but exposes no maskable interrupt
input and applies EI immediately. The harness supplies interrupt acknowledge,
vector delivery, mixed-mode ADL return frames, IFF clearing and the EI delay
at foreground injection boundaries. Actual ISR saves, dispatch and RETI.L
execute on the model. This tests those instructions and injected frames; it
is not independent qualification of silicon interrupt entry.

The UART model acknowledges TX-empty on IIR reads while preserving IER. It
independently owns a 16-byte holding FIFO, a separate shift
register, IIR priority, IER masks, CTS level/delta, RX FIFO and acknowledged
status bits. Timing is idealized at 160 model cycles per 8N1 byte, with an
explicitly assumed eight-cycle interrupt acknowledge tax. Source reads and
instruction timings inherit the pinned eZ80 model's limitations. It does not
model ESP32/VDP execution or physically prove CTS receiver headroom.

Masked variants set IFF in the harness; they do not charge real DI/EI or
bridge instructions. Masked benchmark intervals count producer **host instructions**, not Apple
6502 guest instructions. They do not predict game performance. The current
stock Fab UART model and running real VDP firmware under Flexe are insufficient
to qualify an eZ80 interrupt implementation without checking the frontend UART.

The two compatibility decisions, production return fence, MOS API allocation,
production ZDS link and real keyboard/parser regression remain in the project's
[TODO](../../TODO.md). No hardware lease was requested or consumed.
