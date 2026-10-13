# Interrupt-based UART0 transmission project — handoff

Executive summary: the UART0 candidate is integrated into MOS and passes native
ZDS II, scripted, production-ROM and both headless Flexe engine tests on Oryx.
The Author selected callback/session exclusion and retain-and-wait exit handling.
The Author passed Oryx human review on 2026-10-13 and authorized committing
and pushing this tranche. Physical qualification remains pending.

Read `/Agon/mystuff/agon-dev-env/codex/AGENTS.md`, then `OWNERSHIP.md`, `TODO.md`,
`docs/uart0-async.md`, `docs/tasks/ASY-001.md` and the latest dated development log.
The sole unfinished-work checklist is TODO.md. Immutable IDs use the form
`TX-006 [ ]`; never renumber or reuse one. TX-011 Console8 preparation and
TX-012 human fixture acceptance passed on 2026-10-13.
Fresh-lease physical qualification TX-006 remains; TX-010 is complete.

## Source and contract

Branch: `codex/uart0-async`; remote: `bgates747/agon-mos`. The clean starting
checkpoint `b20af31` was already pushed when the Author said to commit/push dirt
and proceed. The Author subsequently accepted production-tranche human
validation and authorized its commit/push. Existing qsort edits were previously preserved and committed
separately as `564de93`; this tranche does not change them.

`src/uart0_tx.inc` is the common tested core; the isolated wrapper includes it.
`src/uart0_async.asm` supplies BSS/startup, parser routing, synchronous scopes,
polling, return fences and UTX1 discovery via existing getfunction index 13h.
No new high-level MOS call number is allocated. The register ABI and limits
are documented in `docs/uart0-async.md` and remain a development API in this fork.

C-001: async open refuses an installed user keyboard callback; installing or
clearing one first drains/closes an open session. Existing callbacks retain
ISR timing and synchronous output. Async apps use MOS keyboard state/map/polling.
C-002: return fences retain borrowed sources until queue empty and TEMT. A
permanent CTS stall waits indefinitely until explicit reset. OSCLI fences before
child loading. No automatic FIFO/parser flush or unsafe timeout is used.

RST38 drains/closes an intact foreground consumer. Panic during an open UART
consumer retains RAM in a stopped loop for reset. Closed-session legacy panic
behavior is retained. Corruption and direct private UART/state manipulation are
outside the normal-return guarantee.

## Build and evidence

`bash tools/zds/build.sh` builds the complete native MOS image on Oryx under Wine.
`bash experiments/uart0-mos/build.sh` reproduces native building, the 1,411-case
scripted suite and seven negative controls, 13 production-ROM scenarios, and
both full-image headless engines. All C/Rust/assembly compilation and emulation
run on Oryx; local Ruby/Bash only stage, inventory and check results.
No mos-agondev/AgonDev translation route is maintained. No C source workaround
was needed: do not reintroduce the incorrect compiler `-model:L` option.

Build artifacts are ignored under `build/uart0-mos`; durable summary and
commands live in `experiments/uart0-mos/README.md` and `results.json`. The final
full reproduction took 48.455 seconds, excluding initial runtime/tool setup.
Emulator wall times are scheduling measurements, not hardware performance.

The emulator has its own owner/agent in `../flexe-agon-emulator`; do not modify
its ongoing work. MOS uses cached copies of the previously qualified binaries
pinned by `experiments/uart0-mos/runtime.sha256`. Initial cache seeding can use
the earlier qualified MOS profile, and fails if its hashes differ. The original
emulator/source provenance is retained in the earlier Flexe manifest and logs.
The generated profile explicitly identifies and hashes this candidate MOS ROM;
it must not claim to contain stock v3.0.2. The old isolated fixture's profile
scripts can replace it, so rerunning them replaces the reviewed production fixture.

## Accepted Oryx human review

Run locally on Oryx:

```bash
cd ~/Agon/mystuff/agon-mos/.emulator
./flexe-agon-emulator --precise-interrupts
```

Expect legacy, ordered, masked, exit/return, short-mode and integration PASS
markers. The final invalid-command error is deliberate. At `/uart *`, type
`ECHO UART0 KEYBOARD PASS` and confirm the response and normal prompt.
The Author supplied the expected screen and a successful typed `dir` command,
then explicitly reported "passed". The agent ran only headless tests; human
review was performed by the Author. The Fab launcher is a compatibility
shim to the primary Flexe entry point.

No physical bench or firmware was touched. Obtain a fresh explicit bench lease
before physical qualification or firmware writes. Receiver headroom, physical
full-duplex timing, recovered CPU work and game integration remain unqualified.
Do not remove game DI blocks or modify another owner's profiles/sources.

## Console8 preparation — TX-011 / TX-012

The Author selected Heber Agon Console8. `experiments/uart0-bench/README.md`
owns the new fixture, exact installed-MOS backup/restore procedure and passive
CTS export format. `results.json` records native ZDS II and both headless
engines passing: 42.802 / 56.132 seconds, eight paired cases and 65,536 receiver
byte comparisons per engine. Offline report/ROM/trace readers pass 14 negative
controls. Timings are uncalibrated MOS ticks; no physical claim is made.

The Oryx review instance is separate from the accepted production
profile: `cd ~/Agon/mystuff/agon-mos/.emulator/uart0-bench`, then
`./fab-agon-emulator --precise-interrupts`. Expect BENCH FIXTURE / BENCH RETURN
PASS and `/uart0 *`; check keyboard output with `ECHO UART0 KEYBOARD PASS`.
The Author supplied the expected screenshot, typed a successful
`ECHO UART0 BENCH FIXTURE PASS`, and accepted it with "looks like pass to me".
This satisfies the canonical human gate; TX-011/TX-012 are complete.

The accepted off-device package is `build/uart0-bench/console8-package-20261013-accepted`
on Pi and Oryx; candidate CRC32 F7A575E8 and SHA-256 remain the accepted ROM's.
It includes pinned official flash v1.9 and original notices, but has not been
copied to a physical card or invoked. Obtain a fresh lease, installed versions,
specific SD identity and external Console8 ZDI recovery readiness before any
physical access or flash. No other bench owner's historical grant applies.

Untimed verification now fences every four comparisons at VDP execution.
Unpaced / 256-command groups stalled the pinned interpreter during legacy
closed-session output; root cause remains unestablished. Four-command groups
pass both engines. This fixture change does not modify MOS or emulator source
and does not settle physical CTS headroom.
