# GOAL-001: actual92 first-status overrun interpretation

Requested by `2026-11-07_10-47-10_mechagon_goal001-r07-first-oe-uart-sixtynine`.
Read its companion context mail, the saved R07 decoder output, owner recovery
receipts and matching owner source. Independently rehashed RAM1cd930b5 and
record3b289774; all46455 immutable native bytes match8184. Six source files
match owner commit1727fa19 exactly. Pins are in
[the review receipt](retry-r01/actual92-source-review.json).

The root's explicit initialization/case/recovery join supports its actual92
interpretation. The generic decoder still says RAW_FORENSIC: the record has no
embedded session identifier. Do not relabel this post-reset RAM as an untouched
running snapshot or infer that reset preserved all mutable application state.

## What the first error locates

The exact drain order is: full IRQ saves; owner/fault checks; assert PC2 STOP;
outer marker3; initialize B=16; read LSR into C; check errors; marker40 on error;
fault callbacks. The first RBR and parser/TX-service work follow only a clean
status. Thus remaining16 and saved LSR0x63 place this error before any RBR in
this invocation, before its packet callback, generic U1 step or OTIRX emitter.
They exclude those later operations as the preceding cause *within this drain*.
Earlier invocations are not excluded.

LSR0x63 is OE+DR+THRE+TEMT, not framing/parity error. OE is latched until an LSR
read; with FIFO enabled it reports an incoming character that could not enter
the full FIFO. It does not timestamp that loss or count lost bytes. THRE/TEMT
describe UART1's outbound side; they do not say its receiver was empty.
See Zilog [PS015317-0120, UART LSR pp120–121](https://zilog.com/docs/ez80acclaim/PS0153.pdf).
The official indexed text was available; direct PDF retrieval redirected and
failed. No electrical or cycle behavior was inferred from that retrieval.

Consequently **before first RBR does not mean before handler entry**. Loss could
precede entry, occur during the unmarked saves/STOP path, or occur while the
entry marker runs before the first LSR read. STOP does not clear a prior OE.
Already buffered or in-flight peer bytes may still consume receive reserve.

## What the observed spans do and do not measure

Previous U0RX:64728→64725,3 counts. Current U1 entry→first-fault sample:
64722→64719,3 counts. Each is nominal41.67us at72kHz with the stated endpoint
quantization. The current prefix is valid separately; its ordinary closed span
still has no end. Neither measurement is a complete IRQ blackout or read gap.

The first timestamp lies *inside* the begin marker: register/bridge saves and
the marker preamble precede it; record rotation and its return follow it.
Likewise, the fault timestamp is sampled only after the LSR read and the fault
marker's saves/context copies. It is an observation after detection, not the
instant the UART dropped a byte. The current41.67us includes diagnostic work,
not just the handful of instructions from B=16 to the error branch.

The previous span excludes earlier IRQ acceptance/dispatch/saves and later
marker return/restores/EI/RETI. The arithmetic between its end sample and the
current start sample is also3 counts, but crosses those tails/prologues. It is
not an IRQ-pending latency measurement. Even the9-count/125us distance between
the earliest retained sample and fault sample omits prior FIFO accumulation.
No sum proves either a safe or an excessive receive blackout.

PC_DR f3 at both U0RX samples has PC2 clear (READY); f7 at current entry/fault
has PC2 set (STOP). PC3 is clear in both, reporting the opposite-direction
peer permission. These software port samples are not physical STOP edge,
peer-observation or last-transmitted-byte measurements. Hold0 means no outer
foreground RX hold, not that the drain failed to assert STOP. The matched
parser layout decodes [2,143,106,32,74,26] as payload state, NM command0x8f,
length106, remaining32, used74 and partial_at26;106=32+74 is consistent. It
does not identify the dropped byte or establish an intact packet.

## IRQ priority and the smallest useful owner direction

Zilog [PS015317-0120 p45, Table11](https://www.zilog.com/docs/ez80acclaim/ps0153.pdf)
places UART0 vector18h ahead of UART1 vector1Ah. This selects among pending
maskable sources when interrupts can be accepted; it does not let UART1
preempt these DI handlers. Repeated short UART0 services can therefore delay
UART1 without any one retained UART0 span exceeding a FIFO-fill interval.
This record does not prove simultaneous pending sources or starvation.
Internal UART IIR source priority is a separate matter from UART0-vs-UART1
arbitration. The shared UART0 vector covers TX as well as RX.

The smallest concrete owner review target is the receive-protection boundary:
READY remains advertised during the observed UART0 RX path; U1 asserts STOP
only after its own IRQ prologue. Extender can assess protecting that interval
earlier and ensuring a supported RX-first drain before advertising READY
again. Any such change must preserve existing STOP/hold/fault ownership and
register/IFF rules; do not unconditionally clear STOP on a UART0 exit or add
nested EI. It may help service reserve but will not repair already lost bytes.

An existing matched lower-baud control would change the available character
time, not isolate IRQ priority, marker perturbation or physical STOP tail by
itself. Retain the observed diagnostic overhead in that interpretation. No
new marker, profiler, generic-core change, case or baud selection is made here.
Moving/removing hot-path markers would itself change the experimental arm and
needs the owner's matched control; this result alone cannot establish an
observer-induced failure.

The finding is a real reported receive overrun with a useful first-check
boundary, **not a demonstrated generic U1 defect or a proven UART0 cause**.
Preserve the first LSR sample and refused drain/close state; do not mask OE,
discard it through a second status read or weaken source lifetime rules.
Extender retains recovery/firmware/custody and MechAgon the consumer. UART
performed no build, decoder execution, target access, replay or installation.
