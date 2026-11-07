# IO003 KEY-R03: mode-tail continuation explains the saved key loss

Source-only return to actual immutable mail
`2026-11-07_16-13-50_agon-6502_io003-keyseq-mos-boundary-nine` (notification
reported16-13-54). Independently rehashed all10 listed retained evidence files
and the unchanged diagnosticc793a279. No build, emulator/device run, observer
implementation or ROM substitution. Original first-key result and unrun async
successors remain unchanged.

## Exact conditional continuation

READY reports protocol state2 (body), command6 (mode reply), remaining4 and
pointer `data+4`. Its scratch begins `00 02 80 01 28 18 40 14`; bytes beyond
the current pointer can be leftovers from an earlier reply. If the next parser
inputs are exactly the two Return packets, the pinned RC3 state machine does:

1. `81 04 0d 00` fills the last4 bytes of the *mode* payload. Command6 executes;
   it is not dispatched as a keyboard packet.
2. `8f 01` starts command15 with one payload byte. The next `81` (the break
   header) becomes that payload, overwriting scratch[0]. Command15 is outside
   the ten-entry dispatch table and is ignored.
3. `04 0d 00` is ignored in header-wait state. `8f 00` forms a zero-length
   command15, also ignored.

The result is **exactly** the observed POST state0/cmd15/remaining0/pointer=data,
scratch `81 02 80 01 81 04 0d 00 00 00 00 00 00 00 00 00`. It naturally leaves
the key callback and MOS keycount unchanged. This is a stronger explanation
than a generic callback/ring incompatibility: the full Return bytes could have
been consumed without any of them becoming a keyboard command.

The [review receipt](io003-keyseq-parser-review.json) retains every byte-level
step of this offline source-rule calculation. It is conditional reasoning,
not an executed MOS/ISA/UART test. Snapshots are non-atomic; no intermediate
RBR history was captured. The exact match does not establish the READY image
as one atomic state or prove there were no intervening bytes or memory writes.

## What to distinguish upstream of this state

The correct wire ends its last pre-key mode reply at8125..8134, payload
`00 02 80 01 28 18 40 14`; Return begins8135. The highest-value witness window
therefore includes the **preceding mode body**, not just the12 key bytes.
The unexplained part is how the parser remained four bytes short. Missing
mode-tail acceptance/consumption, an earlier framing shift, synthetic no-data
inputs and corruption remain alternatives; the saved record cannot choose.

The source-identified carry-clear bug remains relevant but unproven: a non-TX
IRQ with DR clear can feed an artificial zero to the parser. The exact
continuation above requires no such extra zero *after* the READY state. Do not
declare that bug reproduced here, patch the frozen ROM or reset the parser to
make this test pass. The observed vector/allocation/ring/context and standalone
pass reduce the priority of a basic callback ABI hypothesis; they do not prove
all live memory invariant throughout the case. One pass/fail pair is not a
deterministic history-only experiment.

## Small passive owner-native witness proposal

Flexe owns the emulator implementation and selection. Within any later chosen
finite diagnostic, record existing operations without introducing IIR/LSR
reads, guest writes, input injection shortcuts or new emulated IRQ edges:

* At UART RX admission, retain stream byte identity/sequence, existing occupancy
  before/after and accepted/drop decision; distinguish this from the already
  available pre-admission delivery log. Cover the earlier mode replies.
* At each actual RBR read, retain returned byte and existing UART instance/read
  sequence. At existing IIR/LSR reads, retain their already-returned values.
* If correlating guest execution, use the exact guarded RC3 map and passive
  execution observation at the existing receive-reader return/parser call to
  associate carry/DR and C/state/remaining with an actual dispatch. Do not
  synthesize an additional status read or change parser state to observe it.
* Keep IRQ request/ack/service observations distinct from FIFO admission and
  CPU reads. Include engine/cycle/PC provenance and bounded trace-overflow
  indication; omit unsupported observations explicitly. Existing known clock
  and byte-attribution limits remain in force.

A full admitted→RBR byte match with a carry-clear parser call would identify a
firmware-dispatch failure boundary. An explicit drop or admitted bytes never
read would locate a different boundary; it still needs its timing/IRQ context.
Do not infer exact cause from delivered equality or cumulative counts. No new
trace build/run is authorized by this proposal. No async or physical conclusion
follows from the synchronous emulated case; custody remains released.
