# MOS UART0 Flexe Agon Emulator qualification

Executive summary: the native ZDS II driver runs as an isolated MOS application
against real ESP32 firmware through Flexe Agon Emulator on Oryx. Both engines pass exact
transmit/reply checks and return to stock MOS. Testing exposed and fixed a
second driver lost wakeup, previously hidden by the scripted UART. The Author passed human review, then selected the separate
`bgates747/flexe-agon-emulator` repository and product name.

## Reproduce

From the MOS project root:

```bash
experiments/uart0-async/build.sh
experiments/uart0-flexe/build.sh
```

Both commands compile and execute their tests on Oryx Linux Lite. Local Bash
and Ruby only stage inputs, package maps and audit storage. Follow the canonical
`agon-dev-env/codex/environment.md` and private connection guide for access and
ZDS II installation; this project owns no alternate connection configuration.

The reusable emulator now belongs to the separate
[flexe-agon-emulator repository](https://github.com/bgates747/flexe-agon-emulator),
checked out beside MOS. Its `make` command builds the frontend, patched Flexe
core and adapter on Oryx. MOS's Flexe command consumes and hash-checks those
outputs; it no longer copies or patches a frontend source export. The UART
model and bridge changes have moved to that owner, removing duplicate source
from this experiment. Seven focused UART tests run from its pinned test binary.

[reference.sha256](reference.sha256) pins the runtime owner's source/binaries
and the frozen Golem-built ESP32 firmware/ELF used by this fixture. Golem's
standard tagged MOS/SD resources remain read-only inputs to the canonical
profile generator. No consumer command rebuilds or changes another owner.

The foreground application, unchanged shared driver and receive fixture are
assembled/linked natively with ZDS II under Wine. There is no MOS source
translation or mos-agondev build path. The app is loaded at 040000h by stock
MOS v3.0.2; no ROM is replaced. Canonical profile generation uses a snapshot
of `agon-dev-env/scripts/setup_emulator.py`, then pins copied frontend, adapter,
ESP32 firmware, MOS/map, launcher, app and autoexec identities. The profile
is under this project's ignored `.emulator` on Oryx.

The canonical generator and headless verifier run with this project's Oryx
`.venv/bin/python`. On initial setup the existing Golem virtual-environment
interpreter bootstraps that isolated standard-library-only environment;
`UART_VENV_BOOTSTRAP` can select another explicit venv interpreter. No system
Python substitution, package installation or Pi compilation is performed.
Build outputs, native listings/maps, runtime/source hashes, tool identity,
transcripts and failure artifacts stay under ignored `build/uart0-flexe`.
Compact final receipts are retained in [results.json](results.json).

## What the fixture proves

The app temporarily saves/replaces UART0's vector and IER, opens the singleton
experimental driver and publishes three immutable transactions. They contain
32 stock general-poll commands, a buffer clear and 4,096-byte write, and another
32 polls. The poll command is normally MOS-internal; this MOS-owned fixture
uses it only as a deterministic transport echo, not a proposed application API.

The receiver sink captures the 64 three-byte firmware replies while TX proceeds.
The verifier requires the exact 4,366-byte ordered transaction stream once in
the wire trace, all 192 reply bytes in order, accepted counts 128/4110/128,
RELEASED/reaped tickets, drain/close success, actual CPU interrupt entries,
TX and modem IIR causes, and zero modeled TX drops, RX overruns or sticky RX
errors. It verifies the requested adapter was mapped and the requested engine
ran, all backend fault counters are zero, the app returned to the MOS prompt,
shutdown succeeded and every pinned runtime input stayed unchanged.

The app restores the original vector/IER before normal MOS output. On an
unexpected transport failure it writes a failure record and retains its
sources rather than returning into reclaimed RAM. A failure is not treated as
a safe recovery policy for production applications. Callbacks inside the real
MOS receive parser are not exercised while the experimental vector is active.

The seven focused UART tests cover IIR acknowledgement without changing IER,
CTS delta acknowledgement and GPIO reads, FIFO versus shift-register emptiness,
already accepted bytes despite CTS deassertion, RX interrupt priority/overflow,
trigger/timeout behavior, FIFO resets and non-FIFO holding capacity. The
independent assembled suite now models acknowledged TX-empty interrupts too;
its `txack` mutant reproduces the newly found stall.

## Review on Oryx

The profile is stopped. Run locally on Oryx:

```bash
cd ~/Agon/mystuff/agon-mos/.emulator
./flexe-agon-emulator --precise-interrupts
```

Expect stock MOS to boot, run the fixture, display `UART0 ASYNC PASS`, and
return to `/uart *`. Type `dir` and confirm keyboard input and normal MOS
output still work; then close the window. The earlier functional review passed. The old
`./fab-agon-emulator` command remains a shim to this primary entry. No agent launches a graphical review instance.

## Model limits and integration boundary

The audited reference frontend cannot qualify async UART0: IIR reads clear TIE,
no modem delta source exists, RX has one byte with artificial fourfold slowdown,
and enabled TIE interrupts regardless of FIFO state. The project-local
correction is required for these tests. See [the audit](../../docs/uart0-flexe-audit.md).

This remains a functional emulator result. The UART model assumes 8N1 and
ideal baud-derived time; it does not implement every UART control bit or inject
physical parity/framing/break faults. It samples CTS at model boundaries.
The existing eZ80 core supplies interrupt entry and has immediate EI behavior;
it is not independent silicon-entry or EI-delay qualification. Flexe's adapter
uses host queues and modeled ESP32 FIFO capacity for CTS, not physical receiver
headroom or pin-level RTS timing. Thread scheduling changes ISR/CTS counts
between runs, so they are observations rather than stable performance metrics.

No speedup, real MOS parser/callback compatibility, application-exit policy,
full keyboard regression or hardware timing is established here. C-001/C-002
and TX-005/TX-006 remain separate integration/physical work in the sole [TODO](../../TODO.md).
