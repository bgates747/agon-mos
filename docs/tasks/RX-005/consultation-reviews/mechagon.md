# RX-005 — MechAgon return-path requirements from actual source

MechAgon's mainboard replies use the keycode callback route: wire packet0x81,
with10-byte VDPlet bodies. They do not use a literal0x88 return path. One
outstanding typed return is sufficient for the current application. The most
useful bulk-return demonstration is exact replay-buffer verification: the checked
candidate currently needs56663 READ16 transactions to compare113326 bytes before
START. This is a concrete transaction-count opportunity, not a measured speedup
or a request for a new framework.

This response answers the bounded source consultation in owner mail
`2026-11-07_17-36-47_agon-mos_rx005-mechagon-return-requirements-one`. GOAL-001
has actually resumed by direct human instruction; the mail's paused-goal wording
is stale. This consultation still selects no implementation, build, run, resource,
deployment, new task or owner source edit. Root will send the substantive response.

## RXM-001 — Exact path:0x81, not0x88; renderer is not the old getter

1. Retained installed profile8 runtime `vdplet_runtime.h:709–712` constructs
   `VDPL,protocol,kind,token:u16,value:u16`:10 body bytes. It calls
   `send_packet(PACKET_KEYCODE,10,body)`. Retained `agon.h:93` defines KEYCODE1,
   and `vdu_stream_processor.h:520–532` emits code+0x80,length,body. Thus the
   wire envelope is **0x81,10,10bytes**,12 bytes in total. Optional READ_BYTES
   at runtime757–768 instead uses16 body bytes,18 on wire, with1..8 useful data
   bytes. Retained build configuration enables this runtime feature, but that
   alone does not qualify its16-byte callback on the selected EMOS composition.
2. We do not consume the literal0x88 route. In the exact retained mainboard
   source, PACKET_KEYSTATE8 is repeat-delay/rate/LED status (`agon.h:100`), and
   `vdu_sys.h:582–595` sends its5-byte body. That is not our arbitrary data
   return. Do not describe MechAgon's code as reading a key-map packet merely
   because private data shares the keyboard **keycode** callback.
3. Current renderer `render_link.c:11–40` owns static BRClient receiver; its
   `receiver.c` includes the shared `native/readback/src/client.c`, rather than
   another copied implementation. `packets.s:4–22` preserves all entry registers
   and passes borrowed packet pointer DE to C. `br_receive:27–43` identifies
   VDPL/version/token/expected kind, copies10 or16 bytes into reply[16], publishes
   ready last, and zeros the first4 bytes of consumed private bodies so MOS does
   not publish them as keys. Genuine key bodies remain untouched. The callback
   has **no supplied body-length argument**; it relies on the frozen sender and
   admitted route. The new typed return should remove that implicit-length
   dependency, not imitate it with a larger blind copy.
4. Renderer startup requires callbackzero (`render_link:46–54`). With UART1,
   the matched optional NM router installs above the renderer callback and
   chains non-NM packets to it (`transport_uart1:55–67,183–187`, SDK router13–40).
   NM is a separate UART1/network protocol with its own token/query/payload;
   sharing an application callback chain does not make it a VDPlet bulk reply
   or impose its128-byte payload ceiling on RX-005.
5. Old stopped readback `main.c:63–67` installs a keyboard-buffer handler and
   its own chaining adapter; it **forces legacy READ16**, without INFO26.
   Its reusable `mos_transport.c:33–58` optionally negotiates1..8-byte READ_BYTES,
   otherwise loops2 bytes at a time. `wait_reply:16–21` busy-polls ready with
   independent clock/spin bounds and uses synchronous mos_puts. That is not
   current renderer steady-state behavior: renderer start/progress uses RFC25
   with foreground work and checked WAIT_APP wakeups while awaiting completion.
   The portable token decoder is shared; the wait/sender/admission adapters differ.

## RXM-002 — Actual payloads, source-selected rates and useful data

|Operation|Useful information / existing return|When/how often|
|---|---|---|
|Normal MP RUN entry0|RUN return status2B in a10B VDPL body. Module independently writes16B state to VDP buffer5003.|One reply for each admitted MP record, not per primitive. A simple scene is one FRAME; overflow can require up to4 BULLETS records before FRAME.|
|INFO / READ16|A2B value in the same10B body; full wire reply12B.|Setup/metrics/fences and stopped reads. Normal frame loop does not read all16 result bytes every frame.|
|Normal module result5003|16B status/resource/failed/framecount/turn/roster/bank/bullet summary (`module.c:612–613`).|It remains VDP-buffer data; RUN's status acknowledgment does not automatically transfer it. Metrics reads4B framecount and2B bullet summary via3 READ16s (`render_link:194–201`).|
|Stopped phase profile entry2|15 selected16B pages, total240B; each selector RUN writes one page to5003.|Current code performs15 RUN replies plus120 READ16 replies after positive cleanup, before UNLOAD (`render_link:282–302,353–366`). This is stopped export, no per-frame profile return. A larger receive API alone does not magically aggregate all240B: the current producer still exposes separate16B pages.|
|Replay source verification candidate|113326 exact bytes in buffer5004, compared against the still-open MOS source.|56663 READ16 request/reply transactions before first START (`replay_extension.inc:24–40`). Actual-C/check460 proves mocked integration; no physical replay return-rate measurement exists.|
|Replay chunk result candidate|64B in buffer5006 after positive RUN entry3.|32 READ16 replies after each positively retired chunk RUN; args24 in5005. Nonzero RUN or uncertain transport never authorizes result interpretation/resume.|

The presentation target is30Hz. With one FRAME per tick, normal RUN completion
traffic alone would be30 replies/s or360 UART0 return wire bytes/s; with the
maximum5-record scene it would be150 replies/s or1800 bytes/s. These are
**source-selected demand calculations**, not measured sustained rates or total
UART traffic. Lifecycle/fences/keys/other replies add traffic. Saved actual100 ON
completed613 frames/617 MP records, with host frame mean13.347Hz; that older
serialized/profiled workload is not the new overlap candidate's rate or an
optical measurement. Actual103 never reached UART1 OPEN and supplies no steady
reply rate. No new running-service observation was made for this consultation.

The replay baseline spends56663*17=963271 UART0 request bytes and56663*12=679956
reply wire bytes to compare113326 useful bytes, excluding setup/fences. Request17B
comes from br_begin's11-byte prefix+6 read fields. These counts do not include
callback cost, scheduling/IRQ latency or VDP compute, and do not predict elapsed
time. Fixed16B legacy scratch is not an application requirement. A bounded1024B
return would match replay's existing1024B file scratch and reduce the same data
comparison to111 positive data requests (110full blocks plus686B), if a future
supported producer operation supplies it.256B is also useful (443 requests).
No whole113326B eZ80 receive allocation, large queue or large IRQ callback is needed.

## RXM-003 — Minimum practical contract

1. **Destination and capacity:** arm an app-owned RAM span before sending the
   operation. Validate pointer/range/nonwrap and an explicit maximum count;
   require returned actual byte count<=capacity and equality to the selected
   operation's expected count where appropriate. Current uses want2B/16B/64B,
   and bounded256–1024B readback. There is no consumer reason for a universal16B
   ceiling or for allocating the entire clip in mainboard/eZ80 internal RAM.
2. **Storage lifetime:** registered destination, descriptor and callback code
   remain live until positive completed reception and retirement, or a positively
   quiesced close/cancel. No return/unwind/unload/reuse while the receiver or peer
   may still write. Completion must publish data,actual length and status before
   the ready/notification flag. Foreground may parse/use the buffer while it is
   not rearmed; no next receive overwrites it implicitly.
3. **Completion context:** one bounded notification is sufficient. If called in
   IRQ context it should publish a flag/length/status and wake foreground work;
   no MOS/VDU calls, waits, allocator, logging, decoder or game policy there.
   Register saving/prior-IFF/context conventions must be explicit. A deferred
   callback is also acceptable; the consumer does not require a new callback
   scheduler. New receive must be split-phase so foreground can compute while
   waiting; unaware synchronous APIs may remain unchanged.
4. **Separate milestones:** RFC25 source callback releases its immutable TX
   input; TEMT means that UART TX physically drained; positive RUN status means
   that defined module operation/normal return completed; counted RX completion
   means received bytes are safely published; application reply validation and
   retirement finally permit reuse. These are distinct. Presentational C3/scanout
   and useful bot work have further endpoints. A new receive completion must not
   silently substitute for source/TEMT/module lease retirement or optical display.
5. **Bounded error:** distinguish unadmitted/unsupported/busy, malformed/oversize,
   short/truncated/transport error, timeout and normal remote operation error.
   Never silently truncate to capacity or leave a success-ready flag on partial
   data. Define whether/when writes have stopped after a fault, how remaining
   frame bytes are retired, and how ordinary packet framing resumes. Existing
   policy stops/reconciles or quarantines uncertain work; no automatic request
   replay or new destination admission after an unresolved late return.
6. **Readiness/pacing:** a peer may start only after destination admission. With
   one receive span, send only the current admitted transfer, then await explicit
   retirement/rearm before another overwriting transfer. The implementation must
   establish actual FIFO/flow-control reserve and peer stop latency under DI;
   registered RAM or a large ring alone does not prevent a hardware overrun.
   We do not need a new echoed acknowledgment for every ordinary VDU command.
7. **Coexistence:** route typed return bytes apart from genuine keydown/up,
   keyboard state,MODE/ordinary legacy replies and UART1 NM. Preserve unaware
   applications, startup, ordinary VDU byte streams and previously registered
   owners. The active renderer still needs UART1 NM callback routing even if
   VDPlet data stops using the keyboard callback. Require positive detachment
   before a callback/destination owner disappears. Qualification must exercise
   the real matched EMOS composition; stock MOS capability is not an implicit
   current-install claim or a cure for the separate UART1 overrun/IRQ issues.

## RXM-004 — One outstanding receive and identity

**One outstanding mainboard receive is sufficient.** The current graphics stream
has one tagged transaction and controlled producer; it does not pipeline bulk
returns. NM has its own outstanding query on the other UART, which must remain
independent. No application queue/channel/session framework is requested.

Current VDPL tokens are useful now: BRClient verifies pending,version,kind,token
and retains a single response. Its ordered INFO0 renewal/reconciliation separates
late replies from legal reuse; it is not safe to delete these checks merely
because a new destination is registered. We do **not** require an additional new
RX-005 wire request identifier when one strictly ordered admitted operation,
positive retirement and no post-timeout rearm already establish association.
Keeping the existing producer's tag or returning its typed data is sufficient.
If the proposed transport instead permits old/unarmed replies to arrive after
rearming a different destination, an explicit causal fence/identity rule is
needed; one outstanding at the instant of registration does not solve that
late-return case. Choose the smallest actual mechanism, not duplicate both a
new generic ID and VDPL token without demonstrated need.

## RXM-005 — Useful future matched demonstration, not selected execution

Use the immutable113326B saved-scene clip already checked460: upload it to one
contiguous application-owned VDP buffer and compare **every source byte** back
against the same saved file before START. Compare current READ16 with a separately
selected typed bounded return using the same immutable input, expectedlength,
producer memory, stopped state and destinationcap. Include an odd final byte,
exactcap,oversize/unarmed/read failure, and real keys plus ordinary short replies
without bogus key publication. Retain no automatic fallback/retry after an
uncertain transfer. A small positive/nonzero RUN control can separately establish
notification semantics; a faster data copy alone proves no module completion.

Measure complete verified bytes/transactions, total/inclusive latency, foreground
useful work/CPU attribution, maximum service blackout, code/RAM/stack and errors.
Keep request TX source/drain, VDP work and return retirement clocks distinct.
This directly replaces awkward word loops, repeated roundtrips and borrowed
fixed-body parsing, without moving game rendering to eZ80. It does not establish
30Hz, sustained async gameplay or a general disk API. Other actual consumers are
not asserted here; shared readback's donor comments name historical origins,
which are not current owner/run evidence. VDPlet owns generic runtime semantics.

## Exact source and evidence pins

All paths below are relative to MechAgon unless starting `../`. Retained firmware
root **V** is `../agon-vdplet/build/vdpl028-profile8-r02/firmware/firmware-src/video/`.
Owner header/router pins below are read-only current-source references, not a
claim they alone identify the currently installed EMOS ROM. The selected frozen
owner package/actual readback remains the physical authority. No private args or
credentials were read/copied for this response.

|Path|Bytes|SHA256|
|---|---:|---|
|`native/renderer/src/render_link.c`|19295|`c5b14c20245e5723e21f86778c8267a53a771bac78bb310ef89171d92f0aea7d`|
|`native/renderer/src/receiver.c`|161|`7ef2fa011ad7d40a72f6212a2b90e2299ea3fb0e35acd92f5daadddb7df09c12`|
|`native/renderer/src/packets.s`|616|`cbbe5d7906ed9161e0a66f9f3ab5f1727d557acb30a4692ef1d62f0945065117`|
|`native/renderer/src/rfc.s`|1069|`2ce59061e8f2b3e5ee6d3249635b8f8f74034f39e1072b60be20359e3892cf21`|
|`native/renderer/src/transport_uart1.c`|13207|`3a120ec99c67ca3c79062ecaa0483c5f5089c018883817257c89ec3b0aabe124`|
|`native/renderer/src/net_callback.s`|184|`a3ea7ef6bebde6e5df3e18a8380e4401ce1d439482e069ac1a251c44f1b8f589`|
|`native/readback/src/client.c`|3477|`e758fecd6b952e1c94849f32124a0e663084327f6fd1af9fd0f28d3ed8874505`|
|`native/readback/include/client.h`|1792|`dc87ce7df06dad799f2f2c5a70542b544e5f5a60a1b186c606546d8eca2a0456`|
|`native/readback/src/mos_transport.c`|4608|`b943b6d35e11ad44945e9ade00a1aa455e985c9e29813c6b389496d99a60275d`|
|`native/readback/src/packets.s`|906|`b4fae215ee22864d9f13e3ef91d3a606bea2ebdc2f06ced2056cc0fe97c1c10f`|
|`native/readback/src/main.c`|5080|`3fcc464b8cd85863e511930d20f4b15d7dd8a6debe7be024befe6e3acc80f199`|
|`renderer/module.c`|32964|`55c606d030ea51f8aaee82749901055522ea756a3f1075e9f524cdfbd70eb93a`|
|`docs/tasks/GOAL-001/replay-native-candidate/replay_extension.inc`|4632|`213bd8f997056e27ffbe1e98f830206e6987848f73c0707515700146b769eea2`|
|`docs/tasks/GOAL-001/replay-native-candidate/replay_contract.h`|874|`c02d67a5eb051c56a0023660745cb396f449b14aacf4ea902d5c181745a3d19f`|
|`docs/tasks/GOAL-001/replay-driver-candidate/CHECKED460.json`|18755|`2e23d8e582098da4cd6f7c3bd42eaca4603b3441b4a0e3938177b98a7ea6c488`|
|`.runtime/render001/sidebar001/r01/on/run-native-r01/collected.json`|64397|`f2798da453f27b33efd2d29bceee0a4341b3cb5e55599ba5b738a7a6577a3ec8`|
|`../agon-extender/include/agon/net_callback.asm`|1138|`10fdde5cc800d54bb9f6caae795f802e6422149c4513e8446521bb5dd9ec6459`|
|`../agon-extender/include/agon/net.h`|8404|`83c5e00f3c085496449f8d160505988ef62c1512cb1866b889e090a996bd2dcf`|
|`V/vdplet_runtime.h`|38315|`f1de4973f4146653d4de65e11d84d41b5a93c3e5f426ae8297466edeb45fbafa`|
|`V/vdu_stream_processor.h`|26557|`93b17e8c57bc0679226bf823967aa77c46e69d4972ce90d3bd6b6bc593ea1edd`|
|`V/agon.h`|32195|`9cd4c9d11a7138f282e9e64122d652b98277894f1ae0e61c696f7732d92377e4`|
|`V/vdu_sys.h`|25442|`35fff838a0942826fd8b63a69bbde9bae17a0d428e6a9289dd03607b225817ef`|
|`V/vdplet_build.h`|244|`bd962b6d2a8bd2d2347ebeca528d339308ccc1cb3a805117f686339485a62415`|
