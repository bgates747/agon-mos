# Proposed UART0 CTS batching contract — BT-001

Executive summary: extend UTX1 with a session-scoped maximum number of writes
between CTS checks. Keep the existing 16-write refill cap and per-byte default.
Use append-only ABI 1.2 discovery, reject unsupported selections, and change
policy only with an empty published queue and an idle transmitter. This is the
contract for the next isolated candidate; installed MOS still implements 1.1.

## Discovery layout

Keep all ABI 1.1 bytes at offsets 0..45 and their meanings. Increment minor to 2,
length to 54, and add flag bit 3 (CTS batching controls). Offset 9 remains 16: it
is the refill cap, not the selected CTS interval. Existing major 1 callers that
honor table length/flags retain their old operation offsets and per-byte default.
Callers that require exactly minor 1 may decline the extension and use their
existing fallback; do not silently reinterpret their version checks.

| Offset | Bytes | Proposed meaning |
|---|---|---|
| 46 | 3 | ADL register-ABI pointer to `tx_set_cts_batch` |
| 49 | 3 | ADL register-ABI pointer to `tx_get_cts_batch` |
| 52 | 2 | Little-endian supported-size bitmap; bit (n-1) represents n writes |

Discover via the existing MOS getfunction 13h entry. Require magic UTX1,
major 1, minor >=2, length >=54 and flag bit 3 before reading these fields. A request
is supported only if the corresponding bit is set. Zero is invalid; it does
not mean automatic selection or disabled CTS. No extra global MOS function
number, RST entry or descriptor field is allocated.

The isolated experiment advertises sizes 1/2/4/8/16 (bitmap 808Bh). Size 1 must
always be present. Production-supported sizes will be selected from the
qualification evidence; discovery is implementation capability, not proof of a
particular receiver's reserve. Do not advertise larger sizes in this tranche.
The header and bitmap are immutable ROM data, not writable application state.

## Operations

Both use the existing ADL=1, MBASE=0 foreground register ABI, status values and
preservation rules. AF/BC/DE/HL are scratch; IX/IY, shadow banks, MBASE, ADL and
incoming IFF are preserved. No C stack ABI is implied.

| Operation | Input | Success | Failure |
|---|---|---|---|
| `tx_set_cts_batch` | B=requested unsigned 8-bit size; other inputs ignored | A=OK, B=effective size | CONTEXT, CLOSED, INVALID or BUSY; state unchanged |
| `tx_get_cts_batch` | none | A=OK, B=effective size | CONTEXT or CLOSED |

B is unspecified on failure. CONTEXT takes precedence through the normal API
entry checks. Setter then checks session open (CLOSED), supported B (INVALID),
then quiescence (BUSY). It rejects a same-value request too when not quiescent;
there is no special racy no-op exception. Query requires an open session but
may run with queued work; it returns the session setting, not residual allowance.

Quiescence requires no published descriptor (`tx_head==0`), LSR.TEMT=1,
no serialization barrier and, in production, `uart0_sync_depth==0`. Reserved,
released and cancelled descriptors may remain: unpublished reservations have
no policy bound to them. Any later publication uses the effective session
policy. This avoids requiring reaping merely to choose the next workload mode.

Setter holds the existing short interrupt-masked critical section, restoring
incoming IFF. Once software blockers are excluded, check TEMT through the
shared `read_lsr`, retaining its sticky error-latch semantics. Do not poll/wait,
read IIR/MSR, acknowledge modem wakeups, touch THR/IER, kick service or mutate
queue/source state as part of configuration. Query performs no hardware I/O.
The setter's one status read may latch RX diagnostics; this is consistent with
other driver status operations and is not a fresh diagnostic epoch.

## Scope and reset

Initialize an explicit `tx_cts_batch=1` in the production initializer and in the
isolated wrapper's initial state. A successful open starts at 1; failed opens
leave an existing session unchanged. A successful close resets to 1; failed
closes leave the setting unchanged. The return/OSCLI/callback fence drains
existing work with its active policy, then resets via successful close. Do not
reset early or discard borrowed source storage during a blocked return.

Closed legacy output and synchronous compatibility writes continue checking
CTS per byte. Only async descriptor copying in `tx_service` consumes the
selected interval. Compatibility output within a session drains prior async
work normally; it does not inherit unchecked groups. No other application or
MOS prompt inherits the old session's policy.

## Service semantics

Every service opportunity still requires THRE (whole FIFO empty) and admits
at most 16 total writes. Always sample CTS before the first write of every
service opportunity, including calls from publish/cancel, kick, ISR and the
foreground receive pump. Never carry unused CTS allowance into another refill.

Within an admitted refill, sample CTS before the next group and then permit at
most N writes, where N is the selected interval. Groups may cross descriptor
boundaries because the session owns one ordered stream; ending at a descriptor
boundary earlier is allowed. Empty queue and spent refill budget terminate the
service opportunity even if the group has unused allowance. No extra writes
are permitted merely because THRE becomes true again during the loop.

If a sample says stop, write nothing from that group and retain the existing
blocked-TIE/modem-wakeup reconciliation. Keep all reads through shared status
helpers. Preserve the existing post-budget return before another IIR read,
source accepted-byte accounting, release semantics and receive ownership.
No OTIRX, larger refill, global IRQ policy change or DMA is part of this change.

## Candidate acceptance boundary

The contract is concrete enough for BT-003 implementation. Qualification must
cover unsupported/zero sizes, busy/closed/context rejection, unchanged state on
failure, getter behavior while active, reserved-only quiescence, TEMT lag after
release, default on open/reopen/return, synchronous compatibility and fresh CTS
sampling at every refill. Preserve the existing default and masked-IFF/ADL=0
regressions. Publish the ABI change only with matching implementation evidence;
this document does not claim that firmware already contains the extension.
