# IO-003: exact a25f owner contract and unresolved drain binding

**Subsequent disposition:** Extender accepted the narrow ordered-query policy
without a new public drain API. See [accepted policy](ACCEPTED-EMOS-COMPLETION-POLICY.md).
The earlier dependency/review wording below is retained as consultation history;
consumer implementation and hardware qualification remain separate.

Extender verified donor commit2c79c600 and retained a25f artifacts, not current
HEAD. Its full source-only return is archived alongside this note. No new
firmware, source implementation, build, target selection or run was requested.
RX-006 remains complete.

The full padded131072-byte ROM has CRC32 B24AF611; the used129108-byte
mos.bin instead has CRC3FAA70A0. The published C8 RC3 image is a different
100879-byte prefix with CRC B08C80B8. Preserve exact byte scopes and images.

EMOS public25h accepts full ADL HL/BC/DE source/count/callback and returns A:

- 0: accepted; source is borrowed and callback will release it.
- 19: invalid parameter or span.
- 31: busy or owner/boot handover unavailable.
- 32: unsafe caller/context.
- 35: wrong route/backend.

A refusal borrows no source and schedules no callback. The wrapper preserves
BC/DE/HL, index/shadow registers and MB; flags are unspecified. It requires
actual application dispatch, ADL, MB0, entry IFF1, Legacy/backend0 and eligible
UART ownership. Source and callback lie in040000..0AFFFF application RAM.
Accepted and critical-section refusal paths restore EI; early unsafe refusal
preserves the original interrupt state. Prearm the flag and perform overlapping
host work only after A=0. Do not reuse RC3's void/ignore-A shim.

The key missing interface is local drain: a25f has no public finish/drain SDK
operation.42h/43h are unimplemented; zero-count25h is invalid, not a query.
The private ownership helper and its mapped address are not application APIs.
Do not use raw C5, repurpose a mode transition or assume ordinary output drains
it. An ordered receiver reply has separately declared semantic meaning, and
is not automatically the requested public local-TEMT operation.

Therefore bare C8 RC3 remains a distinct existing target with its documented
LSR recipe. EMOS integration needs its own admission-aware shim and an
owner-supported drain/completion policy before the proposed playable seam can
be qualified. This consultation identifies that dependency; it does not assign
a new firmware hook or authorize bypassing owner control. The completed
RX-006 receive test does not establish playable TX/F6/guest coexistence.

Both implementations retain CTS waiting under DI. A source callback means
FIFO fill completed, separately from TEMT and receiver execution. Preserve
EI/MB0 host-only overlap, then retire the required transport/receiver ownership
before guest DI/MB7/8, ordinary output or exit. Timeout is not cancellation.
