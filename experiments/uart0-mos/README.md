# Installed MOS UART0 qualification

Executive summary: TX-015 adds API 1.1 diagnostic epochs after the first physical fixture exposed
an attribution defect. Current automated evidence includes 27 production-ROM
cases plus the unchanged 1,411-case core suite and seven negative controls.
The prior human acceptance applies to API 1.0; the diagnostic extension awaits
new human review. Physical framing/BREAK timing remains undetermined. No SD or
board access is performed for this revision while the Author uses another project.

The integrated candidate builds with native ZDS II under Wine on Oryx and
passes full-image headless Flexe JIT/interpreter testing. Physical qualification
remains in the sole project TODO.

Run from the MOS checkout:

```bash
bash experiments/uart0-mos/build.sh
```

The script stages source and exact native tool/link commands, builds the whole
ROM, executes the shared-core and production-ROM tests, then assembles two
MOS-loadable apps and boots the ROM through the project profile. It retrieves
listings/maps, exact UART transcripts, reports, engine/UART statistics, hashes,
and monotonic duration under ignored `build/uart0-mos`. `results.json` records
the delivered run; it is not automatically rewritten to claim new acceptance.
Rust dependencies use the existing locked offline model cache. The Oryx project
`.venv` runs Python profile/verification scripts; no system Python is substituted.

## Meaning of the evidence

The shared-core suite executes native assembled instructions against an
independent deterministic UART, including acknowledgment/wakeup mutants. Its
IRQ entry is injected because that CPU crate exposes no hardware IRQ input.
The original timing/model limits still apply; this is not silicon qualification.

Production-ROM scenarios execute the linked MOS instructions, including the
actual C stdout wrapper and formatted error output. Two foreground-IFF cases
exercise discovery, pointer/length validation, queue ordering, GP parsing,
callback installation, an actual synchronous-printing keyboard callback and
CONTEXT rejection. Four nonzero-MBASE cases verify that public async operations
reject that context while internal legacy output and fences work. Five stalled
return cases retain source/queue state until CTS resumes. Two panic cases retain
an interrupted open consumer and preserve closed-session legacy diagnostics.
C initialized data is copied from the native ROM layout for these scenarios;
full startup and boot are independently exercised by Flexe.

The ADL app discovers the installed API. It never replaces an ISR/vector, writes
UART registers, links a private driver, or substitutes the MOS receive parser.
It publishes a 4,366-byte whole-command batch, then tests ordered RST18 output,
status/reaping, real GP state, masked publication/output, callback/session
exclusion, and return with a buffer/ticket deliberately outstanding. Autoexec
reloads and reruns it, then runs an ADL=0 app that tests RST10, delimited RST18,
MBASE preservation, ADL-only discovery rejection and RET.LIS stack restoration.
The deliberate final invalid command exercises MOS error/stdout handling.

The headless verifier requires two exact ordered TX batches, 384 exact delivered
GP reply bytes, accepted lengths 128/4110/128, zero sticky RX errors, all markers,
TX/modem IRQ activity, zero TX drops/RX overruns, the requested mapped backend,
zero backend faults, a final MOS prompt and clean shutdown. Runtime hashes are
checked before and after. No graphical instance is launched by the agent.

## Runtime ownership and review

The emulator owner has independent ongoing work. `runtime.sha256` pins the
previously qualified emulator, adapter and ESP32 firmware binaries. MOS owns
copies in Oryx `build/uart0-mos/runtime`; the script can seed this cache only from
the earlier qualified MOS profile, and refuses differing artifacts. It does not
rebuild or repin another owner's working tree. Source provenance remains the
qualified owner revision (`e5c0539`, with later documentation-only commits through
`81fd40e`) and `experiments/uart0-flexe/reference.sha256`.

Profile generation uses the canonical helper, then explicitly identifies the
development ROM and hashes its bin/map. The stopped profile is the human-review
fixture too. On Oryx:

```bash
cd ~/Agon/mystuff/agon-mos/.emulator
./flexe-agon-emulator --precise-interrupts
```

Confirm the PASS markers, deliberate invalid-command error, and `/uart *`.
Type `ECHO UART0 KEYBOARD PASS`, confirm its response, and exit normally.
The Author supplied the expected screen, demonstrated keyboard input with `dir`,
and explicitly reported "passed" on 2026-10-13. This meets the pre-commit human
acceptance requirement in `agon-dev-env/codex/AGENTS.md`. Hardware remains untouched; physical CTS
headroom, timing/performance and game interrupt-mask changes are separate work.
