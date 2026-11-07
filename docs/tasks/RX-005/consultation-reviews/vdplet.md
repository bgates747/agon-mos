# RX-005 — VDPlet return-data requirements

A counted return into an armed application buffer could remove repeated tiny
pulls and custom keyboard callback code. Preserve existing VDPlet framing,
identities, source/destination lifetime and completion meanings. This is
requirements input to UART's task, not a selected protocol, ABI or implementation.

RXVD-001 [x] Existing integration is the keycode packet channel, not the keyboard
state-map query. D8 accepts protocol1 requests; D9 discovers it. The sender uses
PACKET_KEYCODE1, framed as0x81/length. Legacy body10 is VDPL/version/kind/token16/
value16. Optional READ_BYTES op6 accepts count1..8 in a14B body (19wire bytes),
returns kind6 plus eight data positions in a fixed16B body (18wire bytes), padding
unused positions zero. Errors retain10B kind5/status; reply flag0 sends none.
INFO26 discovers8/0 or explicit older UNSUPPORTED. Native modules have no raw
serial access. No new service can be assumed from an unrelated installed image.

RXVD-002 [x] Stock tagged MOS3.0.2 callback supplies DE pointing at packet data,
not a length argument. Its normal key processing follows the callback. Existing
client contracts require controlled signature/version/kind before10/16-byte copies,
neutralize synthetic private key fields (including stale replies), preserve
genuine keys and register/restore ownership. Signature handling depends on known
firmware lengths, not validation of arbitrary hostile packet sizes. A dedicated
typed RX handler with length/capacity would remove this workaround. Do not
silently change existing user-kbvector context/register/keyboard behavior.

RXVD-003 [x] Actual consumers need one outstanding result at a time, but still
need identity: old or late replies cannot satisfy a newly armed operation.
VDPL tokens16 remain part of the application protocol. Clean token-epoch renewal
needs a consumed ordered INFO0 reply and a clean single producer. Timeout does
not prove unsupported capability or allow retry/token/destination reuse. A new
transport must define overflow, partial/truncated receive, duplicate/stale data,
cancel/drain and safe rearm. A cleared flag is not remote retirement. Preserve
uncertain state on failed reconciliation, with no implicit whole-system reset.

RXVD-004 [x] Minimal useful API shape, proposed only: arm destination+capacity
and expected byte count before sending the request; explicit pending/complete/
failed state, actual count/error; publish completion only after all counted
bytes are committed. Buffer remains owned until positive completion or qualified
cancel/drain. One outstanding operation is sufficient initially; no queue/channel
framework requested. Ordinary blocking callers can retain their blocking wrapper
over this split phase. Keep IRQ work bounded and let foreground do decoding,
file writes, module logic and application callbacks. Preserve ordinary VDU bytes
and legacy packet dispatch; demonstrate actual RX pacing/backpressure rather
than assuming UART FIFO size is an application message limit.

RXVD-005 [x] Concrete sizes:16B management/results,128B async status snapshots,
512B sector-like/export comparison payloads are useful first cases. Current
512B READ_BYTES exchange is64 pulls/2368wire bytes versus256 READ16s/7424bytes;
these counts exclude setup/file operations and are not hardware speed evidence.
Large output should be bounded/chunked without making every module result one
huge ISR copy. Receiver registration can support a larger total count than a
single old packet body. Exact chunk/packet limits, opcodes and namespace remain
UART/VDP agreement decisions. Preserve a coherent source snapshot or application
revision across chunks; transport alone cannot freeze a mutable result image.

RXVD-006 [x] Reuse the runtime's existing checked single-block/span read and
foreground request dispatch, capability discovery and controlled reply source.
Source bytes currently copy into a local packet before send; no module pointer
survives. A larger queued send needs an explicit copied TX owner or positive
borrow retirement, not a pointer to stack output or a module that may unload.
Return-transfer completion, module RUN/worker completion, source drain, swap
notification and physical presentation are separate. Existing redirect/suppress/
sending/sent callbacks can break ordered-route proofs and must be included in
admission. A new return route cannot inherit the old INFO0 fence automatically.

RXVD-007 [x] Experimental VDPL035 is source-built but not worker-qualified.
Active sessions currently admit only D8/D9 on the original foreground processor.
A new inbound reserved selector needs explicit integration before use during
OPEN; do not send it and expect it to be ignored. Pure receive-side registration
may avoid that input change, but reply routing/source ownership still need an
agreed contract. The compute task itself must not send packets or invoke old
services. Its status128B is copied coherently by foreground, then pulled through
the existing transport; actual357 OPEN refusedUNSUPPORTED9 before worker start.

RXVD-008 [x] Consult actual owners/code, not a broad list announcement:
6502 export/disk persistence and optional PCM replies; FSIM's source-qualified
PINGO071 client5109418 (94442B corrected size),128B status/keyboard coexistence;
Wolf results/loading/status; MechAgon16B results/profile tails/long-running
epochs and separate controller transport. Beyond those four, Rally/AgonArcade
and Wireframe are concrete VDPlet consumers; inspect their current request/
reply sources first. Golem is a separate language/compiler project with loader
integration, not the runtime owner. VDPlet's own benchmark/timer frontends are
additional small result readers. These are consultation leads, not claims that
every one uses READ_BYTES or needs bulk RX. No peer wakeup/workload requested.

RXVD-009 [x] References/pins: include/vdplet_protocol.h; maintained runtime
vdu_sys_vdplet/read_bytes; retained5d657 send_packet/agon.h; tagged MOSv3.0.2
src/vdp_protocol.asm::vdp_protocol_KEY; API-reference optional readback,
VDPL015 contract-v1, readback-token-epochs.md; FSIM's actual generated client-r4
callback and tracked client_backend.inc. Adjacent RX005-RETURN-PATH-PINS.json
records source bytes, not independent adoption/physical qualification. No code,
build/test/device/profile/reservation or existing pause changed by this reply.
