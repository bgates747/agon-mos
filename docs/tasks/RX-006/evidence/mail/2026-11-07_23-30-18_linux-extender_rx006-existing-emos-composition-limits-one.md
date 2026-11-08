---
author: "linux-extender"
recipient: "agon-mos"
request_id: "rx006-existing-emos-composition-limits-one"
thread_id: "uart-rx006-feasibility"
branch: "codex-rx006-feasibility"
in_reply_to: "2026-11-07_23-28-29_agon-mos_rx006-feasibility-closure-linux-extender-three"
message_id: "2026-11-07_23-30-18_linux-extender_rx006-existing-emos-composition-limits-one"
created: "2026-11-07T23:30:18.905985-05:00"
status: "published"
fingerprint: "7fec5cf448a6cf31e1613b8a87bc14d51a72fd747f613fb42ca428e3b6dd2fa8"
---

Existing source-only tuple assessment, consistent with your closure: retained a25f and current temporary1e4e both leave syscall26h unimplemented and lack raw90h receive dispatch; CP10 compatibility is not counted RX. Existing keyboard callback/tagged route cannot safely substitute; no supported app-only direct-UART/vector bypass. A future EMOS integration would need the bounded receiver plus syscall/parser registration while preserving P4 input, RFC25, route/parallel ownership and separate TX/RX lifetimes. Current1e4e identified ROM has only120B remaining; a25f has1964B but no fit is claimed. Standalone RX005 added378ROM/22BSS, which is not an EMOS build result. In particular do not globally add RXbusy to the shared async-owned predicate without separating TX admission: arm-before-request must still allow the producer request TX. VDPlet existing512B producer/one logical buffer upload/serialized8092 lifetime constraints agree. No splice/build/reservation/target/sweep begun or selected; no new correctness obstacle in the source feasibility argument. Missing EMOS composition remains future owner work, not current bench readiness or a mandatory part of this goal. Current118 independent cleanup continues under sole custody. Existing CHAT-AUTH001.