# UART0 fidelity audit — Fab/Flexe

Executive summary: the existing Fab/Flexe export needs an eZ80 UART correction
before it can test async transmission. The separately owned Flexe Agon Emulator now models
TX-empty acknowledgement, modem CTS deltas and bounded RX/TX FIFOs. Actual
firmware testing exposed a driver lost wakeup hidden by the original scripted
UART; the corrected driver passes both Flexe engines and the revised independent
suite. These are functional model results, not hardware timing qualification.

## Inspected boundaries

Fab 1.2.5's Golem-owned source export supplies the eZ80 CPU, UART registers,
interrupt routing and stock MOS filesystem/frontend. Its optional interface
loads Golem's Flexe native adapter, which executes the real ESP32 image and
exposes the existing Fab serial-link ABI. UART0 on the eZ80 connects to UART2
on the emulated ESP32. Exact inspected source/binary inputs are pinned in
`experiments/uart0-flexe/reference.sha256`; Golem and upstream files are untouched.
The source audit below describes the original Golem export; the corrected
UART/bridge and runtime now live in `../flexe-agon-emulator`. MOS no longer
maintains an exported frontend or duplicate UART source.

The inspected frontend has the Golem native-frame/cleanup changes over Fab
commit `c22876d1f7ad903537c308cf65afd6553b37cdb8`. The Flexe source export is
based on `fbda8e905ccff36a090e4e33b0ffc2337dd79c52`. Full frontend-source
hashes, the adapter and real firmware/ELF identities accompany the receipts.

| Behavior | Reference frontend | MOS-owned experimental correction |
|---|---|---|
| No pending interrupt | IIR reports RX even without data | IIR bit0 is set when no enabled cause is pending |
| TX cause | Any enabled TIE fires; IIR read clears the IER bit | Holding-empty request is latched, IIR acknowledges the request and leaves IER unchanged |
| CTS changes | Level-only MSR; no modem IRQ | Sticky DCTS, MIE routing, MSR acknowledgement; GPIO level reads preserve the delta |
| RX capacity/rate | One byte, arbitrary fourfold slowdown | Sixteen-byte FIFO at the ideal configured byte interval, overrun latch |
| RX dispatch | Single ready-byte flag | Line status, RX threshold/timeout, TX and modem priority |
| TX completion | Data delivered on shift start | Sixteen holding slots plus separate timed shift register; THRE and TEMT distinct |
| FIFO reset | Control byte stored without reset action | RX/holding clears, active TX shift retained |

The register bridge calls the corrected IIR/IER methods for both UART instances,
but only UART0's interrupt vector is added to the existing dispatcher. UART1
interrupt support, transmission-complete interrupts and other peripheral work
are outside this fixture.

## Newly reproduced driver failure

The earlier scripted UART treated TX-empty as continuously pending. Real IIR
acknowledges a TX-empty interrupt when read; it does not promise another IRQ
while the FIFO remains empty. During a busy ISR, the driver could spend its
one-burst TX budget, read another TX cause, then exit without refilling. That
consumed the only wakeup with queued data, ready CTS and an empty UART.

The first interpreter run stalled after 51 ISR entries. Updating the independent
scripted UART to acknowledge TX causes reproduced a deterministic failure with
16 bytes written, CTS ready, IER=0Fh and the queue still active. Removing only
the new budget exit from the corrected binary reproduces that same stall as
the `txack` negative control.

The driver now returns before another IIR read once its TX budget is spent.
RX retains priority on the next entry, and late modem causes remain pending.
The prior modem-specific guard remains defensive. The additional instructions
also pushed the dispatcher loop beyond a relative branch's range; native ZDS
caught that, and the loop now uses a full-address conditional jump.

## Evidence and practical limits

The original 1,411 assembled scenarios pass with the corrected interrupt latch
model; all seven negative controls fail as intended. The driver/fixture has
fifty audited wide memory instructions, and including the foreground app
resolves seventy-one to explicit three-byte fields. Both Flexe engines execute
the ZDS-built app, transmit 4,366 bytes exactly once in order, capture 192 exact
reply bytes, exercise TX and modem causes and return to the stock MOS prompt
with no modeled RX overruns or TX drops. A missing backend is rejected before
boot by the pinned canonical launcher.

The frontend uses idealized 8N1 baud-derived timing, sampled CTS and a subset
of UART control features. The Flexe adapter counts queued bytes plus modeled
128-byte ESP32 FIFO occupancy for CTS; host queues can absorb in-flight traffic.
That is not physical RTS threshold/headroom proof. The existing eZ80 CPU core
applies EI immediately, so hardware interrupt-entry/EI-delay qualification
remains separate. Host thread scheduling changes cause counts between runs.

The application temporarily replaces the receive handler with a capture sink;
it does not qualify the live MOS VDP parser, callback output or abnormal exits.
No new MOS ROM, physical firmware, upstream checkout, game or other owner's
profile was changed. The project-owned profile is stopped on Oryx for the
review command described in the [fixture README](../experiments/uart0-flexe/README.md).
The Author passed the functional review and requested the separate runtime
repository and rebrand; both engines were requalified against that owner.
