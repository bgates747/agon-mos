# RX-005 / VDPL-036 — Private first-trial contract

Binding selected by UART following VDPlet's initial9d8926a source proposal.
These are experimental values for the pinned donors, not upstream allocations.
VDPlet owns producer implementation and the whole-frame serialization audit;
no case may be frozen before that audit and matched component checks pass.

## Wire

Reply: `90h, count:u16LE, payload[count]`. No legacy one-byte length byte or
trailing DONE. The initial VDP producer accepts at most512 payload bytes. Empty
count is a positive empty return; header-looking bytes inside the payload have
no framing meaning. MOS can count up to65535 bytes without an application FIFO
limit; this trial does not certify that larger producer operation.

Request reuses private D8 protocol1/common six-byte prefix. Operation8 adds
`bufferID:u16, offset:u32, count:u16`, all little endian; total payload14/wire19.
Flag1 and reserved0 required. Opt-in INFO27 advertises512. The disabled donor
retains its prior unsupported-field behavior. One source block, validated span
and foreground original output route; no live async worker/session in this slice.

Source errors occur before a counted header and use the existing tagged VDPL
ERROR reply. **That error does not retire a registered receive.** A controlled
synthetic rejection case keeps the same arm alive and sends a later valid read;
only its complete counted reply retires that arm. No cancellation/rearm after
uncertain output. This first trial therefore retains the old small-error callback
adapter; the new bulk payload itself is independent of the keyboard callback.
Do not claim this first slice removes all legacy error handling from clients.
If output is deliberately redirected/suppressed, even the old ERROR can follow
that route or disappear. Such an inadmissible route guarantees neither a MOS
error notification nor receive retirement; it is outside the positive trial.

Producer buffer/source must remain stable through synchronous byte enqueue.
Whole-frame serialization must include ordinary keyboard/legacy writers, not
just a private mutex nobody else observes. Default RTS-only VDP setup is not
proof of CTS transmit stopping; native source facts and actual byte integrity
must establish the qualified limits. No new flow-control policy is assumed.

## MOS trial syscall26h

Foreground ADL1/MBASE0 caller, valid owned writable RAM and live callback code.
Input `HL=destination`, `BC=capacity (0..65535)`, `DE=callback or NULL`.
Destination must be non-NULL even for capacity0; span must not wrap24-bit RAM.
The caller remains responsible for memory ownership and valid accessible RAM.

Return `A=0` admitted, `1` BUSY, `2` invalid. `HL` always points at the read-only
MOS result record. BC/DE/IX/IY/shadows/MBASE and prior interrupt-enable state
are preserved. AF and HL are outputs. No separate query/cancel syscall is needed.

Record offsets:0 state byte (0idle,1pending,2complete,3oversize);1 reserved0;
2 actual stored count:u24;5 announced wire count:u24. Data/counts are published
before terminal state. Do not interpret a pending multi-byte snapshot as atomic.
The record remains valid; its contents may change at the next admitted arm.

At an intact frame's end, one optional UART-IRQ callback receives A0 success
or A3 oversize and BC actual stored count. The outer MOS IRQ saves primary
registers. Callback must preserve indexes/shadows/MBASE if it touches them,
return normally and do bounded flag publication only: no MOS/VDU/wait/file/
allocation work or rearming from the callback. A tiny assembly wrapper suffices
for the synthetic fixture; no C callback scheduler is added.

An intact unarmed frame is completely discarded without changing a previous
result or calling an old callback. An armed frame larger than capacity is
completely discarded, stores no payload, then reports oversize once. While any
counted frame is incomplete, or an arm is pending, admission refuses BUSY.
Rearm only after positive completion/discard and application observation.
Truncation/unknown peer state does not release memory; first trial requires
reset after such uncertainty. No deadline or automatic cancellation is claimed.

## Local integration

Feature logic/state in one new MOS assembly file. Register26h in mos_api.asm
and route successful UART0 reads through its dispatcher in interrupts.asm.
Unmatched bytes tail-call the existing legacy parser. Use the reader's carry
result so an empty/status-only IRQ cannot invent a zero byte. Preserve startup,
the RFC25 sender, old parser and ordinary API behavior. The two hooks are the
only existing MOS source files selected for change.

Actual127-byte trial loss required a bounded receive drain within the new file:
at most16 already-available bytes per entry while a counted frame is active,
returning on empty FIFO, frame completion or budget exhaustion. It does not
wait for more data or drain ordinary legacy packets. This changes no public
record, callback or buffer-lifetime rule.

VDPlet owns its opt-in producer file/registration/build; UART owns only the
standalone synthetic app, MOS branch and shared emulator runner. No game edits,
consumer prototypes, installed/default firmware or upstream publication.
