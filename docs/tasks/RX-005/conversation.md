# RX-005 conversation record — 2026-11-07

This preserves the user-visible discussion beginning when Brandon raised
incoming traffic. Role labels identify the speaker; message wording and
technical qualifications are retained. Tool execution logs are not reproduced.

## Brandon — receiving-side question

we need to talk about what happens when devices are sending bytes *to* the ez80. so far the focus has been on sending.

## Codex — initial explanation

Receiving creates a deadline: **the eZ80 must collect incoming bytes before its UART’s small hardware buffer fills.** Having plenty of spare CPU on average doesn’t guarantee that it services reception soon enough.

The path is:

1. A device sends bytes over the wire.
2. The UART receives them into its hardware FIFO, even while CPU interrupts are disabled.
3. An interrupt handler—or polling code—reads those bytes into RAM or processes them.
4. Application code acts on the resulting data.

There are two distinct ways to lose information:

- **Hardware overrun:** the FIFO fills before software empties it. Incoming bytes are lost.
- **Software handling failure:** bytes leave the FIFO, but the parser, queue or application mishandles them.

Our recent 6502 investigation is distinguishing those boundaries. Its intact “delivered” trace ends before FIFO admission, so it cannot yet prove that MOS read every byte.

At 1.152 Mbaud with 8N1 framing, a byte arrives every **8.68 microseconds**. An initially empty 16-byte FIFO fills in roughly **139 microseconds**. That is not a safe interrupt-disable allowance: existing occupancy and bytes still arriving after a stop request reduce the available margin.

This makes **RC3’s wait for CTS inside its transmit interrupt** particularly relevant. While it waits with interrupts disabled, incoming bytes can accumulate on either UART. The receiver needs service regardless of whether our outbound transmission can proceed.

Flow control is directional. Checking CTS tells us whether **we may send**. Protecting reception requires telling **the other device to stop**, allowing for its reaction time, and continuing to drain our FIFO. With the ESP8266 connection lacking that hardware handshake, we instead need bounded requests, credits or agreed pauses.

The receive-side design question is therefore: **how do we guarantee timely collection, while deferring expensive parsing and application work?** That deserves separate latency and integrity tests alongside our throughput and CPU-headroom measurements.

## Brandon — stock MOS behavior and possible tradeoff

right. so, the first example to look at is how stock MOS handles incoming traffict on UART0 from VDP. we may or may not assume that's been peformance optimized; it may have been designed for safety ... at the possible expense of making the ez80 wait in a polling loop until the transfer is complete?

## Codex — source-check progress message

I’ll trace stock MOS’s UART0 receive path and the calls that wait for VDP replies, so we can separate interrupt handling from application-level polling.

## Codex — stock-source findings

**Partly, yes. Stock MOS receives bytes through interrupts, but some calls then busy-wait for the complete reply.** I checked stock MOS **v3.0.2**, rather than our modified branch.

The receive handler:

1. Saves registers and disables interrupts.
2. Reads **one available byte** from UART0.
3. Passes it to the packet parser.
4. Restores registers and returns.

The parser remembers how much of the packet has arrived. **It does not sit inside the interrupt waiting for the remaining bytes.** Once the packet is complete, it updates the relevant system variables, sets a completion flag, or invokes the keyboard callback.

The polling happens higher up. For example, “get mode information” clears a flag, sends the request, then calls `wait_VDP()`. That function repeatedly checks the flag until the receive handler sets it or the loop times out. The foreground spends that interval spinning instead of calculating.

Keyboard events don’t require that foreground wait; they arrive and are dispatched through the interrupt path.

That gives us two separate opportunities to investigate:

- **Receive overhead:** stock handles one byte per interrupt, including register saves and parser work.
- **Waiting overhead:** synchronous request/reply functions consume foreground cycles polling a completion flag.

The code establishes those costs. It doesn’t establish whether its authors deliberately chose them for safety, simplicity or performance.

## Brandon — task creation and preservation instruction

please open a new investigative task for this, and record in it our conversation since i raised the question so that we don't forget anything

## Record boundary

The task created from this instruction is [RX-005](README.md). Creation records
the investigation; it does not assert a selected optimization or measured gain.
