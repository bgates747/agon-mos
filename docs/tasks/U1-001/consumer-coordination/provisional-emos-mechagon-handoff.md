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

## Extender's checked provisional binding, 2026-11-07

Read owner mail
`2026-11-07_01-46-50_linux-extender_u1-emos-checked-size-binding-two`, its
`docs/tasks/NET-004/EMOS-ASYNC-R01-RESULT.md` and
`agents/net004/uart1-async-r01/consumer-binding.json`. Extender source a664123e,
EMOS source 2c4705310a49c7d97fc606bf47344cc36f68ab2e. UART independently compared
the three generic core/header/emitter SHA256 values against its own source:
all match. The vanilla installer is not used. No generic core defect or change
is reported.

Owner-reported actual-source sanitizer and native linked checks pass, including
early callback/reply, preconstruction refusal after TAKE, immutable 146-byte
source, delayed CTS/RX-first, later TEMT and refused unsafe retirement. A malformed
successful OPEN/cleanup association issue was reproduced and corrected in the
adapter; it is not identified as the cause of the earlier physical Mech failure.
The default synchronous object remains byte-identical to its control. UART read
these results but did not rerun the owner validators or build.

Measured owner ROM use rises 129108 to 130141 bytes (+1033), leaving 931 bytes.
The app link-only submit/progress/take/close probe adds 1199 text and 19 BSS bytes
(2356/391 versus 1157/372), including core/emitter but excluding common runtime
and the consumer RX callback chain. These are not whole-MechAgon size or CPU
figures. The async engine remains application-resident; resident hooks still
have a material flash cost in tight EMOS.

Exact provisional package:
`/Agon/mystuff/agon-extender/agents/net004/uart1-async-r01/provisional-u1-emos-r01.zip`,
252889 bytes, SHA256
`3b1d69c27118da82ed1c0f2df9beeea19f46808fdeea2799eeba788745a69570`.
Padded ROM SHA256
`043a0989b08a7429a2c52aca6a037660f8c19c067376173d17af7c46f1238c0f`;
map SHA256 `b87c12848dc5f33571bc60bab904a2b789f75082555ef4729ee4232b5e86a109`.
MechAgon has the actual binding. ROM is uninstalled, hardware/CTS/full-FIFO and
performance claims remain open, and current Wolf75 custody is unchanged.
Extender owns installation/rollback under its normal fresh checkout; this record
does not select a run. No material generic-source concern was found in this
bounded feedback review and no acknowledgement-only reply was sent.

### R02 cleanup association and whole-consumer size

Read follow-up
`2026-11-07_02-02-15_linux-extender_u1-emos-cleanup-r02-consumer-size-three`
and `consumer-binding-r02.json`. SDK 39d4be6f retains the app hook's cleanup
association after a refused NM SUBMIT clears generic admission. Progress/close
can therefore retire the still-attached hook; payload still requires validated
OPEN/admission and the preconstruction guard. This is an adapter correction,
with generic core/emitter unchanged; no generic driver defect is reported.
Owner reports actual-source ASan/UBSan, native link and byte-identical default
synchronous object checks passing. UART did not rerun them.

R02 supersedes the R01 consumer package, retaining the same uninstalled EMOS
ROM/source/map and +1033 resident bytes/931 free. Minimal probe delta is now
+1189 text/+19 BSS, ten text bytes smaller than R01; whole probe is
3597 text/78 data/445 BSS. MechAgon's separately linked whole application adds
1976 text/+24 BSS, data unchanged at 87: async 38337 bytes (cf910bd7),
synchronous 36361 bytes (de4350a4). Do not compare a whole-consumer delta with
the smaller probe delta as if they measured the same scope, or infer CPU/FPS.

Exact package:
`/Agon/mystuff/agon-extender/agents/net004/uart1-async-r01/provisional-u1-emos-r02.zip`,
253190 bytes, SHA256
`a0cee12c8adc0eae27633c1871b8722355695e0afc6103c89a31eb64c5dfadd1`.
MechAgon's finite trial is preparing behind Wolf75; no new ROM installation,
physical result or UART workload is selected by this feedback. Retain R01 as
historical evidence. No acknowledgement-only reply was sent.
