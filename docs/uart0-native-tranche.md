# Native regular MOS UART implementation

## Delivery policy superseding the native port — 2026-10-31

The Author clarified the distinction: modifications/extensions of official
upstream ZDS II firmware/software retain ZDS II so existing developers and users
can readily build, test and approve the changes. Original software should
prefer free/open-source tools such as AgonDev. Therefore this UART modification
will be delivered in the upstream-style MOS fork using ZDS II under Wine on
Oryx; our original menu/test applications may use AgonDev independently.

The native AgonDev implementation, failures, fixes and receipts below remain
historical/reference evidence. They are not the selected firmware delivery
path. Reuse the startup trace and transport findings for BO-001..BO-004 in the
ZDS II fork. Do not carry over native compiler-port changes without a need in
the upstream build, or treat permission for an application as a compiler change
for MOS. This policy supersedes earlier prospective native-port instructions
in this document; it does not alter historical source or acceptance records.

2026-10-16 hardware hold: the first native candidate failed to boot Console8.
The [completed audit](../experiments/uart0-native/BOOT-FAILURE.md) identifies and
corrects a 24-bit overflow in startup baud calculation. The replacement passes
software checks but remains off-device. Earlier qualification/deployment text
is historical; N-006 governs fresh replacement qualification and acceptance.

2026-10-31 design revision: the Author requires proven stock startup and UART
handling until explicit CLI/application activation, with activation forgotten
on reset. The delivered candidate's closed-session state does not provide
this isolation: its replacement ISR and shared status helpers run while closed.
The [startup/activation contract](uart0-async.md#stock-startup-and-explicit-activation--author-requirement-2026-10-31)
and BO-001..BO-004 in TODO.md now precede N-006. Correcting the baud calculation
alone is insufficient to satisfy the new acceptance requirement. No revised
firmware or replacement package has been built or deployed for this revision.

Implementation update,2026-10-31: BO-001/BO-002 now restore the release startup
and handler, move initialization to explicit open and restore stock dispatch
on close/return in the ZDS II fork. The
[new candidate, fixture and qualification](../experiments/uart0-startup-safe/README.md)
pass actual-ROM and both-engine software checks. Functional human review also
passes R0001. That update supersedes the preceding design-only status; physical
acceptance remains open, including actual reset recovery.
The native-port results below remain historical evidence.

### Working release startup trace — 2026-10-31

The Author clarified that this means preserving the working versioned release's
startup code, rather than designing a replacement startup. The concrete source
reference is official MOS v3.0.2, commit
`8336409351ee5314e02801a7b72a4f1bb5282519`, whose release image was just restored
and boot-confirmed on Console8. Its image SHA256 is
`d564243283972690933a4554296ad6202ca4ef54572279533a942960846bebae`.
The isolated native foundation is a port of this release, not that released
binary. Use `git show v3.0.2:<path>` for the original routines; do not treat the
current modified working files as the stock reference.

The traced startup sequence and transport dependencies are:

| Stage | Release code | Preserve / move out of startup |
| --- | --- | --- |
| Reset entry | `src_startup/vectors16.asm`, `_reset` / `_rst0`: DI, STMIX, jump to `__init` | Preserve the release entry. |
| Hardware and C initialization | `src_startup/init_params_f92.asm::__init`, `__init_default_vectors`, `src_startup/cstartup.asm::__c_startup`, then `_main` | Preserve peripheral disable, memory/stack setup, flash protection, ordinary BSS/data initialization and default vectors. Ordinary BSS clearing already supplies a zero activation flag; no experimental startup initializer is needed. |
| Main initialization | `main.c::main`: DI; interrupt vectors, RTC, SPI, UART0/UART1 pin setup; EI | Remove our added `uart0_tx_init()` call here and initialize the experimental state only on explicit activation. Install the original UART0 handler at boot. |
| VDP handshake | `main.c::wait_ESP32` → `src/uart.c::open_UART0`, timer0, `putch` → `UART0_serial_PUTCH` / `UART0_serial_TX` / CTS checks | Preserve release behavior and its working baud configuration. Restore direct status-register reads while using stock transport. No experimental status helper or pump in this path. |
| VDP replies | UART0 IRQ → original `src/interrupts.asm::_uart0_handler` → `UART0_serial_RX` → `vdp_protocol` | Retain the original handler/body and receive parser at boot; do not replace the handler with an unconditional `JP tx_isr`. |
| Screen and banner | `main`: heap initialization, mode query, palette query, `bootmsg`; output through stock serial routines and C runtime | Keep these on the release path. Our unconditional RST18 synchronization hooks also belong outside disabled startup/output. |
| Useful CLI | `main`: SD mount, system variables, beep/history, ordinary startup files, then `mos_input` / `mos_exec` | Preserve normal release behavior; do not insert automatic transport activation. |

The existing release `set_vector(UART0_IVECT, ...)` updates a RAM interrupt
vector under interrupt exclusion. Explicit activation can use this mechanism
to install the experimental handler and normal deactivation can restore the
saved stock vector. This does not require rewriting the release's reset or
initialization sequence. Serial/RST compatibility and cleanup hooks still need
placement review so their inactive paths leave the original transport intact.

These are a source control-flow trace and identified deltas, not an implemented
patch or a claim that every library instruction has been compared. Protect the
transitive callees/runtime as well as `main`. The known compiler-port arithmetic
difference must remain explicit: unchanged C text produced different baud
instructions under AgonDev. Retaining that port requires the already-proven
arithmetic correction and compiled-result checks, not blindly restoring the
overflowing expression. Preserve the working release's behavior; no new startup
design or separate baseline-development project is required.

The next implementation brings the measured CPU-saving UART sender into a
maintained native AgonDev MOS variant, with explicit application opt-in and
unchanged legacy blocking behavior. It is a separately qualified experimental
regular MOS product; EMOS remains deferred and installed firmware is untouched.

The Author authorized implementation on2026-10-16 after a commit/push checkpoint.
Existing MOS work is pushed as d4569e8; the isolated EMOS budget assessment is
pushed as e147549 on its own branch. This authorizes the implementation tranche,
not a new production release or automatic hardware installation.

The only actionable task index is TODO.md; N-001..N-005 identify this tranche
in the development log, alongside existing BT/AB gates.
Our own agon-mos repository holds isolated source worktrees under
`../worktrees/uart-native-001/{stock,uart}`. The feature branch is
`codex/uart0-otirx-native`; no UART branch/source is added to either owner's
foundation or infrastructure repository. The original working fork is retained.

Selected foundation and canonical interface:
`ab95feee301d2cd40470cf2bda85a0fe1c3c008e` from private agon-mos-agondev.
Selected build helpers: `49dc33fee817cb184572351ee71dae7da9a139c4` from mos-agondev.
Use immutable local dependency exports and verified Oryx transport, not mutable
owner files. Build/behavior evidence names dirty source hashes until accepted.
The clean stock control must reproduce102055 bytes/SHA256
f891721bbb2a0bc2845dbb13edbeb449365a315f11be48500d8e65e2ab1aebb4.

The feature reference is frozen ABI1.2 source.tar SHA256
38321531d35faff356b065daab1b4ac64dea9a4acb4e3d1e0b72177937dacc9f.
Port its UART-only delta into maintained GNU source. Generated translation is
an encoding oracle and one-time aid, never the normal build's source of truth.
Keep macros, private scopes, comments and original provenance recognizable.

Consume canonical shared assembly/C bindings. UART discovery remains
mos_getfunction13, returning a discovery function before the UTX1 table.
Slot12 stays null/retired; qsort's experimental public API is excluded.
No new global number or range is allocated. Preserve ABI1.2 length54, capability
discovery, default1, short-mode/context checks, masked-IFF restoration, the sole
MOS receive parser, callback exclusion and return/OSCLI/crash lifetime fences.
CTS is checked before each positive bounded OTIRX block, within the16-write
service cap. The supported-size bitmap is not physical safety certification.

The root native firmware-check must invoke product linked-image checks and
retain shared runtime, flash/RAM/stack/provenance guards. Keep the stock control,
feature port and explicit branding measurements distinct. Validate actual
candidate machine code and complete payloads; do not substitute old ZDS test
results or mask arbitrary relocation-looking bytes. Known inherited defects
and failed attempts stay visible. Human emulator review and hardware acceptance
remain separate gates. Leave the other-project Console8 VDP untouched.

Implementation and software checks are delivered. The isolated native source,
exact image measurements, both-engine raw reports, retained failures and
stopped human review are described in experiments/uart0-native/README.md and
results.json. This does not complete the old menu/batching integration,
supported-combination selection, native physical acceptance or release gates.
