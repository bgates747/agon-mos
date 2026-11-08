# RX-005 implementation under qualification

The first experiment lets an application request a block of data from the VDP
and receive it directly into its own RAM while it continues other work. Existing
VDU output and ordinary keyboard replies retain their established paths. It is
a private synthetic trial; no game is migrated and no performance benefit has
yet been measured. The finite joint trial now passes both engines; see REVIEW.md.

The MOS feature is one new assembly source, `src/uart0_receive.asm`, plus two
small hooks in `mos_api.asm` and `interrupts.asm`. Its initial native build adds
378 executable bytes and22 BSS bytes to exact released Eirene RC3. Every other
compiled MOS unit, including startup and serial sending, matches the baseline.
The48-slot startup invariant passes. Eirene retains its existing AgonDev
toolchain; this is not a toolchain change to official ZDS II MOS.

One syscall registers a live destination, capacity and optional small IRQ
callback. A dedicated reply starts with private type90h and a16-bit count.
The receiver interprets exactly that many following bytes as data, including
bytes which resemble packet headers. On completion it publishes actual count
and terminal state, then invokes the optional callback once. An intact oversized
reply is consumed without writing any payload; an unarmed reply is discarded
without calling an old callback. Ordinary packets continue through the old
parser. Admission preserves incoming interrupt-enable state and refuses BUSY
or invalid/wrapping destinations/capacities.

The VDPlet owner supplies an opt-in producer, returning at most512 bytes from
an existing VDP buffer. It holds a temporary frame and uses one bulk write
through the HAL lock also used by ordinary writers. Its source validation and
native checks belong to VDPL-036. The old tagged management/error callback
remains in the synthetic fixture for discovery and controlled source rejection;
the new bulk data itself is not encoded as keyboard events.

The fixture verifies32 counted frames/2397 payload bytes and30 callbacks, plus
two genuine key packets. Cases cover0..512 bytes, null callback, BUSY, invalid
admission, unarmed discard, oversize discard, repeated rearm and source rejection
followed by a valid response to the same live arm. A separate host decoder
checks wire framing and every pattern byte. Its manufactured positive control
and eight negative controls pass; these are checker tests, not target results.
The checker scopes keys/data between ordered GP30/GP34 fences, preserving but
excluding unrelated startup releases and later CLI tail from case attribution.

Current limits: no queue, cancellation, timeout retirement, checksum protocol,
automatic retry, UART FIFO redesign or hardware pacing claim. A truncated or
uncertain response keeps storage live until reset. Source errors do not retire
an arm. Pending multi-byte counters are not atomic snapshots. The first trial
uses the selected ordinary VDP output route with its async worker disabled.
Final backend stats and byte oracles are retained; early IER-triggered eZ80 UART
counter snapshots are not end-of-case coverage.

The initial one-byte IRQ path lost nine modeled FIFO bytes at127B. A34-byte/
one-RAM-byte bounded drain correction handles at most16 currently available
bytes only while a counted frame remains active; legacy packets retain the
one-byte path. Same-fixture before/after evidence and zero final drop counters
are retained. Native MOS/app and both joint firmware-running emulator cells
pass. The goal is stopped for Brandon's review before any consumer prototypes.
