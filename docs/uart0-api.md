# Experimental UART0 application contract

An aware application can hand MOS a stable buffer and resume other work while
MOS sends it to the VDP. Small block copies reduce CPU overhead. This is an
opt-in experiment: an unaware application keeps blocking output, and discovery
lets applications fall back when the service is absent. No application timer
or scheduling interrupt becomes a competing UART owner.

## Motivation and provenance

Tom Morton proposed the mechanism on Discord. The Author supplied this quote
and provenance; it has not been independently fetched:

> why not ask codex to use interrupt-based UART0 transmission?
> then you can enqueue 16 bytes using a single `otirx` instruction, and walk away to calculate other stuff
> maybe there is a good reason nobody has done it. 🤷‍♂️

[Supplied Discord provenance](https://discord.com/channels/1158535358624039014/1158537054959964220/1559209863954038915).
The last sentence remains an open caution, not evidence of safety or danger.
OTIRX is CPU-driven block I/O, not DMA. MOS owns the UART and returns the CPU
to application work while the hardware shifts bytes. Applications prepare and
publish data in foreground; their scheduling ISR must not call this API.

## Discovery and table

Import canonical mos_api.inc or the C/C++ agon/mos.h overlay. The reserved symbol
is mos_function_uart0_async / MOS_FUNCTION_UART0_ASYNC. It is an index for
existing mos_getfunction, not a new RST call. Set B to that index and C=0, call
MOS function50h and check A=0 and HL!=0. HL is a discovery function, not the table.
Call it in ADL with MBASE=0 to obtain the immutable ROM table. Global index12h
stays null/retired; this implementation reserves no new ID.

| Offset | Bytes | Meaning |
| --- | --- | --- |
| 0 | 4 | UTX1 |
| 4,5 | 1 each | Major1, minor2 |
| 6 | 1 | Length54 |
| 7 | 1 | Flags0Fh: callback exclusion, return fence, diagnostic epochs, batching |
| 8,9 | 1 each | Three descriptors;16 writes maximum per service |
| 10 | 3 | Maximum source length00FFFFh |
| 13..39 | 9x3 | open,reserve,publish,status,cancel,reap,poll_drain,close,kick |
| 40 | 3 | Pointer to sticky RX-error byte, then modem-delta byte |
| 43 | 3 | diag_take pointer |
| 46,49 | 3 each | set_cts_batch,get_cts_batch pointers |
| 52 | 2 | Bitmap808Bh; bit(n-1) denotes supported size n |

Check magic, major, minimum minor, table length and required flags before
reading extensions. All pointers/counters are little-endian24-bit values stored
in three bytes. A C pointer call needs an appropriate register-ABI shim; the
canonical C allocation overlay does not silently supply a C-stack wrapper.

## Calls and ownership

These are foreground ADL=1, MBASE=0 register-ABI calls. A returns OK0, BUSY1,
INVALID2, CLOSED3 or CONTEXT4. AF/BC/DE/HL are scratch; IX/IY, shadow banks,
MBASE, ADL and incoming foreground IFF are preserved. NMI, arbitrary application
ISRs and UART receive callbacks are outside the contract.

| Operation | Input | Result |
| --- | --- | --- |
| open | none | Exclusive session, default batch1; BUSY if callback or serialization active |
| reserve | none | HL=ticket, or BUSY; reservation does not order unpublished data |
| publish | DE=ticket,HL=source,BC=length | Queues stable borrowed data; failure retains caller ownership |
| status | DE=ticket | B=state,HL=accepted count |
| cancel | DE=ticket | Cancels reserved or wholly unstarted work; ACTIVE returns BUSY |
| reap | DE=ticket | Frees RELEASED/CANCELLED slot; stale IDs rejected |
| poll_drain | none | OK only when published queue empty and TEMT; otherwise BUSY |
| close | none | Requires drain and all tickets resolved; resets batch1 on success |
| kick | none | Bounded service opportunity for foreground masked-IFF callers |
| diag_take | none; closed session | Returns HL=00:modem:RX, clears only software latches |
| set_cts_batch | B=size | At quiescence chooses1/2/4/8/16; A=OK,B=effective size |
| get_cts_batch | none | A=OK,B=effective size; no hardware I/O |

States: RESERVED1, QUEUED2, ACTIVE3, RELEASED4, CANCELLED5. Tickets are monotonic
24-bit IDs; exhaustion refuses allocations until full reinitialization. Maximum
length65535, minimum1, with no address wrap. Source must be stable readable
application RAM in [040000h,0BC000h). There is one foreground producer and one
MOS consumer. The queue has no payload heap.

RELEASED means MOS copied the last source byte into UART hardware; the
application may reuse the buffer then. It does not mean the wire is empty.
Drain additionally requires TEMT. Neither means VDP execution finished; use an
ordered query/reply when that matters. Timeouts cannot free borrowed data or
discard partially transmitted commands. Diagnostic epochs sample pending LSR/MSR
and clear software latches only with the session closed; they reset no FIFO and
consume no payload byte or TX-empty acknowledgement.

## Batch setting and interrupt rules

Setter rejection order is CONTEXT,CLOSED,INVALID,BUSY. Size zero is invalid,
not automatic. Quiescence means no published queue, TEMT, no barrier and no
synchronous-output scope. Even a same-value request returns BUSY while the wire
is occupied. A reserved or completed slot alone does not prevent a setting
change. Query may run while work is active. Both restore incoming IFF; rejected
software checks do no I/O. An accepted setter makes one shared LSR read,
preserving receive diagnostic latches.

Every refill requires THRE, meaning the whole FIFO is empty, and permits at
most16 total writes. Each positive OTIRX block samples CTS first, including at
a descriptor boundary. Its count is bounded by selected size, remaining source
and remaining service budget. Accounting/release happens after copying. CTS can
change during a block: the bitmap does not certify physical receiver reserve.
No larger burst is advertised.

Line status and receive data have priority; one ISR consumes at most eight
causes,16 received bytes and16 transmitted bytes. Ready/blocked reconciliation
uses CTS levels and modem edges without an interrupt storm or lost wakeup.
After its TX budget the ISR returns before acknowledging an unserviceable
TX-empty request. MOS retains the sole VDP reply and keyboard receive parser.

## Legacy output and cleanup

RST10/RST18/stdout/errors remain blocking and check CTS per byte. With an async
session open, a synchronous barrier drains earlier published work before the
ordinary write; publication is BUSY during that scope. An entire RST18 call is
serialized. These semantics do not promise cycle-exact stock timing: the new
ownership/status helpers add execution overhead.

Callback installation first drains/closes the session. Execution entry/return,
nested OSCLI and crash handling fence borrowed storage before RAM can be reused.
The fence retains the active batch policy until drain, then closes/reset1 and
invalidates tickets. Permanently blocked CTS waits indefinitely and requires an
explicit reset, as selected by the Author. Memory is never silently freed.
Applications replacing UART vectors, writing UART registers or modifying private
MOS state do not satisfy this ownership contract.
