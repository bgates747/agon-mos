# U1-001: MechAgon provisional SDK lifetime feedback

Reviewed2026-11-07 after mail
2026-11-07_01-04-16_mechagon_async001-provisional-u1-consumer-feedback-two.
MechAgon independently verified Brandon's integration selection, records it in
ASYNC-001/PROVISIONAL-U1-R01.md at56ab0be, and verified the package/library pins.
Its frozen scheduler R02 and live bench scheduling remain separate.

The reported seam is real for the proposed asynchronous SDK adaptation; it is
not evidence of a current generic-core or synchronous-SDK defect. Reviewed
owner SDK: /Agon/mystuff/agon-extender/include/agon/net.h, functions
agon_net_submit, agon_net_take and agon_net_release. No peer file was changed.

TAKE clears pending after receiving a reply. A subsequent SUBMIT checks only
admission/pending, then increments query, clears the next header and copies the
payload into client.input before calling the gateway. If an async sender still
borrows input+1, that construction corrupts its source before any owner/generic
admission can reject BUSY. Therefore reject/defer BEFORE SDK construction, or
use a separately retained immutable staging span. A BUSY response from u1_start
or the gateway cannot undo earlier source writes. Keep the simple one-source/
one-NM contract; a new general queue is unnecessary.

Source callback, later positive TEMT and correlated peer reply remain independent.
An early peer reply cannot clear the TX borrow. Default next-SUBMIT eligibility
can require all three without changing the wire protocol. The source pointer
is client.input+1, so RELEASE's input[0] selector write is not itself a write into
that borrow; the actual risks are admission/ownership retirement and subsequent
reuse/unload. RELEASE must refuse unsafe detach and a refused timeout cleanup
must leave application source/code/IRQ/reply storage resident. Keep first faults
and never replay an uncertain NM payload.

Extender owns the supported EMOS attach/admit/service/drain/detach binding,
shared RX/LSR/CTS policy and exact SDK/ROM/map/capability/size pins; no such
qualified binding is manufactured by this feedback. MechAgon owns caller
adaptation once that interface exists. UART owns generic corrections if a
generic defect is demonstrated. No new build, reservation or target run.

Integration regression requirement: let the NM reply arrive while source
release is delayed; consume TAKE, attempt another SUBMIT, and prove the still
borrowed bytes and original transaction identity remain retained. Separately test
timeout/invalid-reply RELEASE refusal with a live source or wire tail. Both
ordering tests belong in the owners' already-selected integration work.
