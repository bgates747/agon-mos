# U1-001: provisional driver for Extender integration and MechAgon trial

Brandon directly selected this on2026-11-07 in UART chat
01a132e0-4787-7310-93e9-f5248ffb2ff8:

> for now, tell extender we have a provisional driver it can use for EMOS integration, and for mechagon to try. that will give us valuable feeback.

Please proceed with provisional EMOS adaptation and a coordinated MechAgon
consumer trial through your existing task, ownership and bench workflow. The
longer vanilla benchmark suite is not a prerequisite to starting that work.
Return concrete integration problems and consumer feedback to UART; UART owns
generic-driver corrections, Extender owns EMOS integration and MechAgon owns
its caller. This selects a provisional trial, not a production qualification.

## Exact available source and artifacts

Project /Agon/mystuff/agon-mos, branchcodex/uart1-app-async. Driver/fixture source
commit823bb91dd4c1af5a1488e3d3361648646b601445; hardware evidence412e3a1.
Maintained source: experiments/uart1-async. Task: docs/tasks/U1-001/README.md.

Owner-neutral reusable components are include/u1_tx.h, src/u1_tx.c and the
bounded UART1 OTIRX emitter src/u1_emit.src. The C core installs no vector and
has no RX/route/UART ownership policy. The public app shape is an immutable
source pointer/full count/flag-only callback, with source release distinct from
wire drain and receiver completion. One outstanding source; prearm callbacks
before admission. Owner exclusion covers admission/publication and service.

Complete source/binary/SDK-notice/build-evidence ZIP:
/Agon/mystuff/agon-mos/build/u1-001/vanilla-prepared-r05.zip,355785B, SHA256
53797bed1686fe1e7666ed31cbafd29235f3e07e6ed0dbe91b917a8efbc61fe1.
This is a frozen build-time package: later hardware evidence below supersedes
its pre-run qualification notes without relabelling the original build.
Native library: build/u1-001/vanilla-r05/libu1.a, SHA256
b7870dff9c979b5051aec6bdd4e177dbfa29f7b6e42c1a52992fca9e4b246831.

The stock vanilla installer/IRQ1Ah implementation is a reference, not the EMOS
adapter. Adapt the core under EMOS's supported admission/IRQ ownership instead
of reopening UART1 or replacing its receive owner. Keep the engine and state in
application RAM. Extender may make its own necessary EMOS integration hooks as
already delegated; no new resident UART1 engine is requested.

## Evidence and practical integration contract

Console8 R0002 passes all4 ordinary/async AT/GMR cases, matching230 reply bytes,
zero UART errors/overflow/fault and close0. Async pass requires callback, later
TEMT and complete OK reply. Report: docs/tasks/U1-001/console8-r02-pass.md;
raw receipts/console8-R0002.log. Native/sanitizer boundary checks and exact source
pins are in the same task. Actual physical TX spans were4/8bytes at1152008N1
without CTS/RTS; this is a first functional pass, not sustained-performance,
full16-byte/multi-FIFO or EMOS evidence. Use integration trials to gather those
missing real-consumer observations rather than waiting for a broad UART suite.

Preserve EMOS's keyboard/NM RX and single-writer/route admission. Agree shared
LSR/error sampling, actual CTS policy and bounded wake/rearm if needed; the
vanilla no-handshake policy must not be assumed for the EMOS link. Service RX
first and at most one authorized FIFO burst per TX service. Keep source/code
resident through actual callback and positive final retirement; a deadline
does not revoke a source. Keep peer reply/token storage until its own completion.
No new syscall number is prescribed.

MechAgon's current synchronous NM SUBMIT and renderer-idle gate need owner-led
adaptation; see async001-source-advice.md for the concrete source seams and
independent UART0 source/TEMT versus VDP-DONE lifetimes. Report integration costs,
missing hook details, source/reply correctness and actual useful foreground work.
Keep the working baseline for comparison and use normal finite checkout,
cleanup and firmware recovery procedures for any selected physical trial.

Consumer feedback identifies an SDK construction/lifetime seam: a new NM packet
must not overwrite client.input before its still-live async borrow can reject
admission. See mechagon-provisional-lifetime-feedback.md for the exact SDK path
and early-reply/timeout regression requirements. No generic core change is
identified by that finding.
