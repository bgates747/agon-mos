# Isolated UART0 results — 2026-10-12

Executive summary: the native ZDS II-built driver passes **1,411 scenarios** and seven
negative controls. With identical 1,578-byte output and 20,000 useful producer
iterations, the unmasked async fixture uses **11.853% fewer model cycles** than
the blocking fixture. Long interrupt masking removes that benefit. These are
scripted functional and model results, not physical UART or game measurements.

## Qualification

The actual linked image is 1,915 bytes, including a 1,563-byte driver and
352-byte test fixture. [results.json](results.json) pins its SHA-256, source,
ZDS assembler/linker and copied instruction-model manifest. Native map/listings,
full input manifest, detailed logs and the per-instruction width audit are
under ignored `build/uart0-async`. Assembly/link runs through the canonical
Oryx Wine launcher. The source uses native ZDS syntax without a translation
step. Intel HEX is packaged with generic objcopy, and uninitialized trailing
fixture RAM is zero-filled to the map's 1,915-byte allocation.

The 1,411 scenario total comprises 26 basic length/IFF cases, one ownership
sequence, five full-width address cases, 235 CTS cases, seventeen reception
cases, one foreground barrier case, three timed full-duplex cases, 1,024
register cases and 100 randomized sequences of 300 operations each. Lengths
include 1..33 boundaries, 255/256/257, 6,720 and 65,535. Source addresses cross
a 64 KiB boundary.

Coverage includes queue saturation, publication order, cancellation of head/
middle/tail, invalid/stale tickets, generation exhaustion, source release
before TEMT, immediate reuse after release, blocked close, restored IER on
close, CTS cuts 0..34 and 200 low/high edge placements. It verifies empty/blocked
UARTs do not storm, all documented RX errors remain latched, RX/no-pending/TX/
modem causes do not fabricate receive bytes, and callback API reentry is rejected.

At ideal RX spacing 160/320/640 cycles, 256 reverse bytes coexist with a
1,024-byte TX transaction with no loss in the independent 16-byte RX FIFO.
Each ISR is checked for at most eight cause reads, seventeen RX bytes and seventeen
TX writes. Register sweeps cover all 256 flag values at MBASE 0/7/8/53h, both
register banks, indexes, both stacks, ADL and mixed-mode RETI.L return. Random
queue sequences inject interrupts at enabled API instruction boundaries while
respecting DI and the modeled EI delay. The width audit resolves all fifty
wide memory instructions to three-byte fields; there are no two-byte targets.

Seven mutants are rejected for their intended failures: missing CTS guard,
17-byte burst, no-pending misrouted to RBR, early source release, foreground
interleaving, the CTS lost-wakeup bug discovered by the sweep, and acknowledged TX-empty
after an entry exhausted its refill budget. The CTS bug
was acknowledging a new modem edge after spending this entry's TX budget; the
fix leaves that cause pending for a fresh ISR. Negative controls are checked
for a specific failure reason, not merely a nonzero process exit. Flexe
exposed the TX-empty failure: the corrected driver returns before another
IIR read once its TX budget is spent. The scripted model now acknowledges
TX-empty on IIR read, and the `txack` mutant reproduces the stall.

## General producer benchmark

Each variant emits three complete stock buffered-command transactions: clear
a buffer, then write a 512-byte block. It performs the same deterministic
20,000-step accumulator loop and verifies the exact complete byte stream,
source releases and final close. The blocking baseline is the fixture's
THRE-per-byte sender, not a compiled production MOS image. All costs below
include setup, API overhead and final release/close, with identical useful work.

| Masked producer host instructions | Total model cycles | Useful iterations during UART shifting | Wire completion cycles |
|---|---:|---:|---:|
| Blocking fixture | 412,653 | 37 | 252,506 |
| Async, unmasked | 363,742 | 7,707 | 263,812 |
| Async, 64 | 363,742 | 8,720 | 271,916 |
| Async, 256 | 363,742 | 9,646 | 282,053 |
| Async, 1,024 | 363,742 | 9,647 | 361,516 |
| Async, 4,096 | 410,302 | 2,477 | 408,832 |
| Async, 16,384 | 421,822 | 695 | 420,352 |

Every async variant performs 97 ISR entries totaling 196,597 modeled cycles.
Longer masks delay wire completion even where remaining computation hides the
delay in total elapsed cycles. At 16,384 host instructions the experiment is
slower than blocking. The 37 baseline overlapping iterations reflect its final
byte still shifting after the blocking sender returns; blocking return does
not imply wire completion.

Timing assumes 160 model host cycles per 8N1 byte and eight interrupt
acknowledge cycles. It excludes real wait states, VDP execution, physical CTS
headroom and game producer/bridge costs. The harness changes IFF for masked
variants without charging real DI/EI instructions. Mask intervals count **host producer
instructions**, not 6502 guest instructions. No FPS, recovered physical CPU
percentage, full-rate hardware guarantee or game speedup follows from this
experiment. The workload-specific overlap improvement supports integration
research while preserving the interrupt-latency warning.

## Reproduction and disposition

Run `experiments/uart0-async/build.sh` from this checkout. The recorded final
run took **7.234 seconds** for SSH staging, native ZDS assembly/link and
retrieval, cached offline Rust compilation and execution on Oryx,
qualification, benchmark, width audit and negative controls; initial dependency
copy is excluded. This is host tool duration, not target timing. The full
reproduction/ABI/backend contract is in [README.md](README.md).

TX-002/TX-003/TX-004 are delivered as an isolated tranche. Live MOS integration,
actual keyboard/reply parsing, production MOS ZDS link, callback/exit policy and physical
qualification remain open in the project's authoritative TODO. No upstream,
firmware, emulator profile, application or bench was changed. All source and
documentation changes were initially uncommitted; the Author subsequently
reviewed this tranche and explicitly authorized its commit and push.

These updated results include the TX-007 driver correction. Fab/Flexe actual
firmware qualification is recorded separately in `../uart0-flexe/results.json`.
The Author passed human review; the reusable runtime subsequently moved to
`flexe-agon-emulator` and both engines were requalified there.
