# IO003 first-cell keyboard boundary: saved-source return

Reviewed request
`2026-11-07_15-22-03_agon-6502_io003-first-cell-key-delivery-source-review-uart`.
No build, observer implementation, run, replay or firmware change was selected
or performed. First-failure stop and unrun successors remain intact.

## Packet and ABI are compatible

Independently rehashed the report's15 retained evidence files and parsed all
8147 source/delivered reply bytes:97 GP,47 mode,1228 point and3 keyboard
packets, with no trailing bytes. Logs are identical. Return make/break are
exactly `81 04 0d 00 8f 01` / `81 04 0d 00 8f 00` at8135/8141. These fit RC3's
command1/four-byte keyboard payload: ASCII13, modifiers0, virtual key143 and
down1/0. The third keyboard packet at301 predates those events. This parsing
is an offline wire-format check, not execution of MOS's parser.

The pinned RC3 `vdp_protocol_KEY` calls `_user_kbvector` with DE pointing at the
four payload bytes, then performs normal key-state/count bookkeeping after it
returns. The setter1Dh takes HL callback and C segment-conversion flag;
AgonDev's `kbuf_init(64)` uses its assembly callback and C=0, preserving the
full ADL pointer. Its ring callback copies4 bytes from DE, matching that ABI.
No packet/DE/setter incompatibility is identified.

The linked app0 bytes show the actual callback address48c61, setter4930b and
1Dh RST call; its map places ring length/start/end/data-pointer BSS at4db41..47.
Those are source/linked expectations, not observed live vector, allocation or
ring contents. `kbuf_init` does not validate malloc success. The private callback
does not call C/MOS or use indexes/shadows. The controller polls the ring and
reports HOST_KEY before filtering host/guest key choices when browser_test is
active. A wrong FabGL Return constant alone therefore cannot explain *absence*
of that report. The report itself remains a downstream observation boundary.

## Concrete conditional MOS hazard, not an established cause

Published RC3's non-TX `_uart0_handler` calls `UART0_serial_RX`, then always
passes A into `vdp_protocol`. The reader returns with carry clear and A=0 when
LSR.DR is clear; the ISR never tests that carry. Consequently a non-TX entry
with no readable byte feeds a synthetic zero into the protocol state machine.
In length/body/discard states that zero can alter framing or payload. It is
conditional on such an entry actually occurring; the saved wire does not show
IIR, LSR, RBR consumption or parser state. This run does not establish it.

The unconditional dispatch is also present in the retained pre-RFC base ISR;
it is not evidence that async25h caused this synchronous control failure. A
minimal source correction, if separately selected, skips parser dispatch on
reader carry-clear and uses the existing register/IFF epilogue. Do not reset
the parser on every empty read or change the frozen RC3 identity silently.
No patch is implemented by this consultation.

Separately, the existing guest core bridge deliberately holds DI/MB8, then
restores MB and incoming IFF before returning to C. Continued guest execution
does not prove adequate UART service during those slices. No measured blackout
or RX overrun follows from source alone. Async is disabled in this arm, so its
CTS-spinning sender is not the selected active mechanism to blame.

## Smallest useful discriminator for a later selected check

First use any existing Flexe admission/error/RBR observations: delivered-log
equality does not prove FIFO acceptance. If those are absent, keep acceptance
UNKNOWN rather than treating a correct producer packet as parser input proof.
The smallest application-side boundary observation would compare supported
public MOS keycount/ascii/code/down observations with a bounded RAM-only count
at the actual ring callback and its queue indices/data pointer. Report from
foreground, not from the IRQ. Confirm callback installation and allocation
before interpreting absent ring events. Any private parser/vector snapshot
must be tied to the exact RC3 map, not guessed from another MOS/EMOS build.

If MOS key bookkeeping advances but no app event appears, the ring/callback/
consumer boundary becomes the concrete focus. If it does not, UART acceptance,
IRQ service, framing and callback entry remain open; it does not by itself prove
an injector or MOS defect. A minimal callback counter would further distinguish
dispatch from ring publication without replacing the packet path. This is
diagnostic advice only, not a new observer, run or assignment.

Preserve the40 rendering passes, DOS/BASIC pass and first-key failure as separate
results. No physical, async, performance or teardown-success claim follows.
Pins and independent wire findings: [review receipt](io003-first-key-review.json).
