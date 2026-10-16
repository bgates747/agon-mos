# Interrupt-based UART0 transmission project — handoff

Latest, 2026-10-16: Console8 replay PASSES. R0026/R0027/R0028 pass all 90
original A/B phases with zero late feeds/case RX errors; R0029 passes candidate
compatibility and verifies 49,152 final-buffer bytes. Tested MOS is unbranded
API1.1/ROM CRC239097B7; do not relabel this as a physical branded-ROM test.
OTIRX yields 31.87% more median paced useful work than per-byte async, with
equal bulk time (58 median ticks; stock-style blocking is 98). Full A/B bulk
byte verification and supported ABI1.2 qualification remain unfinished.
The Author installed a different VDP for other testing; leave it unchanged.
Interpretation: experiments/uart0-branding/physical-results-20261016.json.

Raw archive on Pi/Oryx: build/uart0-console8-ab-pass-20261016.tar.gz,
54,544,623 bytes, SHA256
0cf62c4b069f1b2030d8c9a1c1f2f9f03cad2aad107b8e0a1b226a3b1461ba19.
After archiving, staged branded MOS/menu at the SAME card directory. No flash
or hardware run. Short readme marks the campaign complete and offers optional
menu9/1 branding installation; no full rerun or VDP change is requested.
All detailed reports/root boot files are intact. Index is compacted through
0029; next run0030. New baseline: build/uart0-branding/deployed-card-state-20261016.
Manifest SHA256 5c606c70efd7a334b377b9d7e64fd296153ab716edb6141e4d57e0bd2d84d993;
running-log SHA256 badd0b9ae09e4842ac71eb0725e6871df71fc072b4ea3da1f140c9b076bb3644.
BR-001 retains optional physical banner confirmation. EMOS remains stopped.

Latest preparation, 2026-10-15: the Author requested a visibly branded custom
MOS to prevent stock/experimental confusion, then said the card is absent and
will report when available. NO card writes until that notice. Off-card package
on Oryx: build/uart0-branding/console8-branded. Boot subtitle is
"Arthur - UART0 async EXPERIMENTAL"; native file CRCAD9C0F96, physical erased
ROM CRC44BC5C07, API1.1. It retains the earlier hardware-tested API1.1 sender,
NOT the newer ABI1.2 implementation. The unmodified pinned source reproduced
the old firmware hash exactly; only version.h subtitle differs in the branded
native snapshot. Both final Flexe checks pass tests1/6/10 through actual FatFS,
and the native runner passes27 production-ROM scenarios. One earlier interpreter
integration failure is retained/unassigned; passing repeats do not erase it.
Menu accepts branded physical/zero-fill fingerprints, retains original ones,
and keeps the hardware-confirmed keypress code. BR-001 tracks deployment at the
same /test/mos-uart0, preserving reports/compact log. No flash/hardware run.
Branding evidence is SHA-verified on Pi/Oryx:
build/uart0-branding-evidence-20261015.tar.gz, 66,909,919 bytes,
SHA256 a50245803d17354194ab1ad1409124e2213d6814f5b17b4a9f2631746fa3d77d.

Latest card maintenance, 2026-10-15: Author requested shorter on-card text,
with complete history retained in the project. Full pre-change card snapshot
is SHA-verified on Pi/Oryx in build/uart0-card-before-short-text-20261015.tar.gz
(54,497,587 bytes), SHA256
c92e978135ad95b6f9a9af711407c5c413d06f59d9cac608a3846cc08f22ff04.
readme.txt is now843 bytes, firmware.txt343, runs.log907 (one summary per run).
Detailed numbered reports remain unchanged on card and in the archive.
The unchanged menu's run scanner still finds24, so next report is0025.
Current manifest SHA256 a16101e21189c0e88467a6cd95ad636c308daab1af85cad516af10ba9de94b83;
current running-log SHA256 ba3ace4ee5b2c601ee8f9d790742ef89129fb1cdfebf9908089a623e5db3a0f3.
Use build/uart0-suite/short-text-20261015 as the new post-compaction baseline
when checking future append-only returns; comparing against the old full log
would incorrectly flag this explicitly authorized maintenance. All other card
files, compiled code and boot files verify unchanged. Quickstart now explicitly
requires MOS CRC239097B7/API1.1 and includes menu9/1 to install it if absent.

Latest return inspection, 2026-10-15: Console8 replay did NOT execute.
R0021..R0023 record TEST 8 SKIP; R0024 records TEST 15 SKIP. All report
MOS_ROM128K_CRC32=466F018D API=0.0, unlike the earlier passing API1.1
image CRC239097B7. Root stock MOS.bin padded with erased FF to 128KiB
has CRC466F018D, matching the reported installed fingerprint. The staged
experimental mos-candidate.bin remains correct (file CRC7E66FD09, padded
ROM CRC239097B7). This identifies a missing prerequisite, not a failed
receiver test. No new VDP stock-restoration handoff is recorded after R0020.
All staged files and earlier reports verify unchanged; only workspace evidence
was written. Archive on Pi/Oryx: build/uart0-repair-console8-ab-return-20261015.tar.gz,
SHA256 2551ae29c80e7539fc7ecfbda9c5b0e856929a70b324c8be03f605b1339f2391.
For a future manual run, menu9/1 installs the staged experimental MOS; require
reboot/menu CRC239097B7 API1.1 before replay. No card update/flash was performed.

Latest action, 2026-10-15: the Author requested the pending tests on the mounted
Console8 card while toolchain review proceeds. Staged the retained original
30-phase A/B workload and repaired VDP candidate at the SAME /test/mos-uart0
entry, with new readme/configuration only; no new binary or firmware build.
Instructions: 9/7 flash candidate and reboot, confirm RX sync candidate banner;
8/1 three times, 8/7 compatibility, then 9/4 restore stock and confirm banner.
All 54 existing result/log/backup files, root MOS.bin and autoexec.txt verify
unchanged. Card UUID 8658-1C23, label AGONC8. Manifest SHA256
74c69beb964143f59258383d41ac19f7ac8ee92c40716914a77801b90e44fb8b.
Receipt/verification: build/uart0-repair/ab-replay-{deployment,verification}-20261015.json.
Manual hardware results are pending; EMOS implementation remains stopped.

Current stop,2026-10-15: the Author requested finishing the interrupted native
EMOS build/flash-budget assessment, then stopping for review. Assessment is
complete; no unattended UART hardware test or firmware change was performed.
The new Extender test-appliance procedure was found/read and linked in chat;
the Author confirms it is correct. Real EMOS Legacy integration is required.
Saved installed EMOS has2450 bytes free; native ZDS size baseline overflows
ROM by3442 bytes before the generic2497-byte sender module and integration
accounting. Two minimal C compatibility edits permit compilation, but no fitting
native image or native-linked behavioral qualification exists. Retain ZDS;
no EMOS-only compiler exception was authorized by the Author's "I do not know".
Recommended next scope is measured EMOS ROM compaction using existing owner
diagnostic MOSlets; its backport saving is unmeasured and no such change started.
All native build processes are finished. No automatic continuation after stop.

Evidence archive verified on Pi and Oryx:
build/uart0-extender-native-assessment-20261015.tar.gz, 28,411,507 bytes,
SHA256 85a465ac8fb2ca04d2171b1de03735036ad40914d824a52f0a29bfa938169b1b.
The full archive stream was read; all 1,740 entries are accessible, including
source snapshots, isolated EMOS changes, installed baseline ROM, native build
logs/maps and assessment notes. These completion notes follow that snapshot.

EX-001..EX-004 are recorded in the sole TODO. Research and results:
docs/uart0-extender-tranche.md and experiments/uart0-extender/budget-results.json.
Isolated EMOS-owned source is branch codex/uart0-legacy at sibling
agon-emos-uart0, based on installed sourcecf10f0b, with UTX-001 task/compatibility
changes/native wrapper uncommitted. Maintained agon-emos/Extender source is
unchanged. The Author confirms Olimex idle CLI/inserted SD/available; only three
read-only status queries were made. No keyboard, transfer, serial, reset, flash,
startup edit or test occurred. Temporary private bench reservation is released;
future use needs fresh ownership/state checks. No commit, push or peer message.

Completed receiver work before this assessment:

Executive summary: the receiver synchronization repair now passes matched tests
on physical Console8. The baseline strands66 FIFO bytes and needs rescue; the
repaired diagnostic receives both4096-byte payloads without rescue or receive
errors. The candidate without timing/rescue hooks passes its five-phase
compatibility campaign. Stock VDP2.16.0 is restored and its normal boot banner
is confirmed by the Author. This resolves the tested receiver defect; resume
original A/B and batching qualification before making performance/release claims.

Latest authorized work: inspect/archive the returned Console8 card. The unique
removable UUID remains8658-1C23, label AGONC8. All86 staged package files match;
all29 prior report/config files are unchanged, and runs.log retains its previous
prefix while appending runs0011..0018. Root /MOS.bin is unchanged. Inspection
wrote only workspace evidence, never the card. Other BMOW media was untouched.
No firmware flash/reset/run, peer message, git commit or push was performed.

R0012 is the baseline pair: control normal, forced fault captured/rescued.
R0014 is the repaired pair: outcomes1/5, CRC87897582 on both complete payloads,
zero case receive errors, rescued=0, RX reenabled with no unread FIFO bytes.
Both physical U/O files and menu/running journals agree. The repaired diagnostic
has no linked rescue function. R0017 passes phased RX, API/callback/masked-IFF/
exit/ADL0, eight benchmark records, four pause/full-duplex cases and six receiver
pattern/mode cases with49152 final-buffer bytes checked. R0018 records stock
restoration; the Author separately confirms the normal stock2.16.0 reboot banner.
Firmware return0 alone remains unverified. No natural stock failure frequency,
electrical CTS timing, new CPU-cycle result or release approval is established.

Interpretation: experiments/uart0-repair/physical-results.json, generated by
hardware_return.py from build/uart0-repair/hardware-return-001. Generic operator
VDP labels are stale; evidence uses pinned images and enforced variant/candidate
protocol gates, without independent flash readback. Software results.json and
audit.json remain the frozen preparation snapshot. Notes and completed IDs are
in docs/devlog-2026-10-15.md and docs/uart0-receiver-sync-fix.md.
RX-001..RX-003 and HW-002 are complete and removed from the sole TODO. AB-006
retains original-workload replay, emulator coordination and renewed human
qualification. Broader supported MOS batching, receiver integrity, performance
and release work remain open. All work stays uncommitted pending explicit
human approval to commit; stock MOS remains the approved production baseline.
Installed MOS during tests is unchanged experimental API1.1/ROM CRC239097B7.

The stable card entry remains /test/mos-uart0/test.bin with firmware/readme beside
it. Menu SHA cfc6480b35cbfeaf212a326c86501e9ea1ffb6869c2827ea24fe503a94c182bf;
repair.bin SHA3d9d6f2e4a24dfd723eeb28b356b469c2299b4bb0aab76cd4945e2558b511091.
No new SD deployment was needed. The repaired Oryx human emulator profile
.emulator/uart0-repair-fixed remains separate from automated evidence; no
new graphical launch was performed. Prior complete software/build archive on
Pi/Oryx is build/uart0-receiver-repair-evidence-20261014.tar.gz,188345070bytes,
SHA256fcaa507f2fc610fb3bca7538427a0f38ba46fc880bd76ff04d6eb48c5b7c4766.
The physical return archive is verified on Pi/Oryx:
build/uart0-repair-console8-r0012-r0018.tar.gz,54562278bytes, SHA256
1b171c90f76b77d31f18848413c85f280f163bd4f14438302e9a9d859b5d7445.
It includes raw reports, all staged firmware, source companions and interpretation.
Volume rename receipts are build/uart0-repair/card-check-20261015-before.json
and card-relabel-20261015.json; the new return confirms AGONC8 mounts normally.
The earlier remount failure was desktop authorization; the Author then ejected
it. Do not reuse a stale /dev/sd name or assume a label alone identifies the card.

Previous physical reproduction:

Latest physical return: Console8 R0010 PASSES the controlled receiver diagnostic.
The Author confirms the menu keypress repair, closing UI-001. Both4096-byte
payloads match CRC87897582 with zero case receive errors. The forced timing
case captures reader recovery on core0 followed by ISR RX-disable on core1,
then66 unread FIFO bytes with RX masked/full flag false. Diagnostic rescue
reenables RX and recovers the whole payload. This establishes the mechanism
under a deliberate hardware timing trigger; natural stock-failure frequency
and a production receiver repair remain unestablished.

All returned assets, prior numbered reports and root MOS are verified unchanged.
No SD writes or firmware actions were performed during inspection. New raw
evidence is build/uart0-race/hardware-return-002, archived as
build/uart0-race-console8-r0010.tar.gz; interpretation is
experiments/uart0-race/physical-results.json. The Author confirms diagnostic VDP
is STILL INSTALLED, so HW-002 remains open for stock restoration confirmation.
Next AB-006 work is the receiver synchronization fix plus matched before/after
hardware tests; keep all diagnostic waits outside the UART lock. No new fix
implementation, deployment or peer message is started by this return review.

Previous preparation:
Latest authorized work: prepare a substantive hardware receiver test together
with the menu repair; the Author declines a separate menu-only bench visit.
UI-001 now uses a menu-only key-down queue and immediate choice
echo, qualified with both Flexe engines and complete physical-format keyboard
packet tests. Updated test.bin is staged at the SAME /test/mos-uart0 on unique
removable UUID8658-1C23, SHA841045e1b78aa3d6f3191f0bad46c19ef96c50e4ec9f496942201b2c4cef30ac.
All26 numbered/operator reports are verified preserved; root MOS and VDP images
are unchanged. The repaired native race.bin is now SHA
ac3f8a7ef9bf50e371f3c7319a6c877c4f225b4a489d9f55f22cedcfdef4db3f.
Use9 then0 to check menu input, then8 then4 for the actual two-case diagnostic.
If the recovery diagnostic VDP remains installed, no reflash is needed.

HW-002 physical run R0009 HUNG in the first case, with zero completed records.
R0008 records diagnostic VDP flash handoff/return0, which alone is unverified.
R0009 reached the diagnostic handshake and saved O0009 stage1 and L0009.
The old fixture deterministically halts on its second MOS SAVE because that
API uses CREATE_NEW and cannot replace the progress file. Actual MOS FatFS/SPI
emulator regression reproduces the same returned checkpoint; hostfs concealed
the error. The repair also avoids FatFS RTC commands during raw payload transfer.
Both-engine FatFS native checks and full real-key FAT-menu integration now pass
all bytes/CRCs and expected diagnostic ordering. Corrupt/missing payload,
missing handshake and checkpoint-write failure controls are rejected.
The repaired fixture is staged for one meaningful retry; no receiver repair
or new physical race result is claimed. Restore stock VDP afterward and confirm
its normal banner. Raw return is preserved under build/uart0-race/hardware-return-001;
new evidence is build/uart0-race/checkpoint-fix-20261014 and
experiments/uart0-race/checkpoint-results.json. See docs/uart0-checkpoint-failure.md.
The broader stop remains outside this authorized repair/retry preparation.
Outstanding work before
implementation was committed/pushed as 0e01958. New diagnostic/menu/deployment
changes after that checkpoint are uncommitted, with no implied human emulator
acceptance or release approval.

Previous diagnostic preparation (physical run has since hung): `/test/mos-uart0/test.bin` on Console8 SD
UUID8658-1C23, hash-verified with all22 existing reports/journals preserved.
Menu9/2 stages the manual flash of `vdp-race-diag.bin`, file CRC3039EE5C,
1081344bytes; reboot must show "UART0 recovery diagnostic". Then menu8/4
runs the two-case diagnostic. Menu9/4 restores official stock VDP; reboot and
confirm the normal banner. Required old experimental MOS remains API1.1,
physical ROM CRC239097B7. Root /MOS.bin is unchanged; no new MOS flash needed.
Firmware copies, `firmware.txt` identities and `readme.txt` are beside test.bin.

Native protocol JIT/interpreter checks pass9.040s/9.335s; integrated menu
checks14.053s/14.303s. Corrupt payload, missing end marker and absent handshake
controls reject as intended; contradictory core/interrupt/full-flag evidence
is rejected independently. Real SDL menu input passes16.335s, preserves an
orphan U0001 and refuses emulator firmware flashing. Both engines capture the
controlled recovery-before-disable ordering and verify both4096-byte payloads.
This is emulator evidence from the compiled diagnostic, not physical proof.
The fresh Oryx `.emulator/uart0-race` profile is prepared and stopped.

Evidence: experiments/uart0-race/results.json and Oryx build/uart0-race/
contain receipts, all attempts, actual firmware/ELF/map, original and linked
driver disassembly, bundle and deployment receipt. Prior complete SD contents
are backed up on Oryx at build/uart0-suite/before-race-20261014. The Author's
subsequent archive-only follow-up is complete: full raw build/evidence is now
mirrored and SHA-verified on Pi and Oryx as
build/uart0-race-evidence-20261014.tar.gz, with .sha256/.contents.txt and a
Pi .receipt.json. Missing Oryx AGENTS/OWNERSHIP and stale notes were synchronized;
the failed user archive was preserved as .incomplete-1.tar.gz on Oryx. No new
test/deployment/flash was started during the archive-only follow-up. The later
R0009 physical run hung; diagnosis, restoration confirmation and return
analysis remain open under HW-002. No receiver repair is implemented.

Latest instruction: the Author clarified that this agent owns VDP firmware
diagnostics as well as MOS, while Flexe owns the emulator. HW-002 and
docs/uart0-recovery-diagnostic.md define the controlled physical race test.
The Author explicitly directs committing/pushing all outstanding work before
implementation; this overrides the prior commit hold without implying emulator
acceptance or release approval. New work after that checkpoint retains the
normal human-validation boundary. No automatic physical flash/run is authorized.

Previous baseline tranche: the Author selected MOS-first preparation of a Console8 test
with unchanged stock VDP, before controlled receiver instrumentation/repair. Outstanding work
was committed/pushed as 0bda05b before execution; the related canonical mail and
English-summary preference were pushed as b660a7c in agon-dev-env. The new
receiver-recovery fixture is now prepared and staged at the SAME
`/test/mos-uart0/test.bin` on uniquely verified SD UUID8658-1C23. Reports and
root `/MOS.bin` are preserved; no firmware was flashed. The Author completed
short/extended hardware runs and returned the card. R0006/R0007 are verified
PASS: all30 cases,245760 final-buffer bytes, zero case RX errors. The traced
emulator stall did not occur in these runs; a rare physical race remains
unexcluded. HW-001 is complete. See experiments/uart0-recovery/physical-results.json.

Menu8 then2 runs six cases;8 then3 runs24. Keep the old experimental ABI1.1 MOS
(physical ROM CRC239097B7) and normal stock VDP2.16.0 banner without diagnostic
suffix. JIT/interpreter short campaigns, interactive short+extended and deliberate
corrupt/missing-reply controls pass. The frozen emulator VDP is a Golem snapshot,
not the exact official release binary; these checks validate the fixture, not a
receiver repair. A hardware pass cannot exclude a rare race. Baseline fixture/
profile/deployment work was committed in0e01958 at the Author's instruction.
New HW-002 work remains uncommitted pending the standing human-validation gate.
The stopped Oryx review profile is `.emulator/uart0-recovery`: locally cd there,
then `./fab-agon-emulator`. No graphical instance was launched by the agent.

The new off-device ABI1.2 session batching controls and bounded OTIRX remain at
0bda05b; they are NOT used by this hardware investigation. Both async transports
remain experimental, not stock/production approved. The earlier combined JIT
receiver campaign reproduced the recovery-deadlock state at batch8; later passes
do not clear AB-006. Menu integration and matched A/B full integrity remain.

Latest return: R0006 short and R0007 extended reports, final progress checkpoints
and running journal agree. All deployed fixture hashes, earlier reports and
root MOS match their expected identities. Read-only capture is archived on
both hosts at build/uart0-recovery-console8-r0006-r0007.tar.gz. Raw entry RX98
is preserved separately from zero setup baseline and zero case diagnostic
epochs; its origin is untraced. VDP stock identity remains an operator label,
not independent readback. No card changes or firmware actions during review.

Previous performance return: Console8 R0005 passes all30 A/B phases with zero late feeds and
case RX errors. Paced OTIRX useful work is31.3% above experimental per-byte async; both take58
raw ticks for bulk versus96 for blocking. No tick-rate/CPU-cycle assumption.
Card inspection/archive was read-only. See experiments/uart0-ab/physical-results.json
and build/uart0-ab/console8-run0005.tar.gz. UI-001 tracks the Author's separate,
unexplained menu keyboard delay; do not attribute it to getch without evidence.

Remaining priority when resumed: HW-002 manual controlled hardware diagnostic
and return analysis, after the passing unchanged-VDP baseline. This agent owns
the VDP firmware work. Physical reproduction and matched repair evidence remain
outstanding; Flexe owns only emulator/model/regression work.
Qualify the new experimental session API
(BT-003), extend matched A/B integrity and integrate numbered menu reports
(AB-003/BT-005). AB-006 receiver-owner correction remains a qualification gate. Stock MOS is the
approved baseline; neither async implementation is approved for production.
The exploratory Console8 comparison is complete. AB-006 still requires a
receiver-owner correction/regression for the traced VDP cross-core RX race;
UI-001 retains the unexplained keyboard delay. See TODO.md and
 docs/uart0-ab-tranche.md for the reconciled roadmap. The Author authorized
committing/pushing outstanding work, then proceeding with this tranche.
New emulator-related work still requires human review before commit unless
explicitly overridden. Do not deploy or flash new firmware without the
applicable manual hardware-test authorization.

Earlier accepted work: UART0 suite, firmware menu, receiver diagnostics and
batching goal were committed/pushed as a776668 after explicit authorization.
Console8 R0003 verifies all 42 receiver trials; stock threshold 64 leaves 62
observed FIFO slots. The Author confirms reboot into normal stock VDP 2.16.0
without the diagnostic subtitle after restoration. TX-018/019/020 and TX-006
closeout are complete; electrical/worst-case timing remains explicitly deferred.
BT-001/BT-002 deliver the concrete proposed ABI and hardware budget audit.
BT-003 isolated batching implementation is next; installed MOS remains ABI 1.1.

Read the canonical environment instructions, OWNERSHIP.md, TODO.md,
docs/uart0-async.md, docs/uart0-cts-batching-api.md and
docs/uart0-cts-batching-audit.md. TODO.md is the sole unfinished-work checklist.
Do not increase the 16-write refill cap; experiment with CTS intervals within
that cap. Per-byte checking remains the default and compatibility behavior.
No firmware/profile/SD contents changed during the design/audit tranche.

Hardware deployment uses the stable `/test/mos-uart0/test.bin` path, with
firmware copies and `readme.txt` beside it. The Author explicitly prefers
history and returned results preserved in the project workspace, which is
sufficient; future deployments should not create SD history directories or
change the active path. Follow the standing preference in
[`hardware-deployment.md`](../agon-dev-env/codex/hardware-deployment.md#authors-sd-deployment-preference).

The earlier temporary SD hold was lifted. The Author authorized MOS-first
hardware preparation and supplied the Console8 card. HW-001 staging is complete;
rediscover the correct unique card before any later deployment. Historical
no-write/hold statements below refer to their earlier tranches.

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

No physical board or firmware was touched. Obtain a fresh explicit bench lease
before agent-operated physical qualification or firmware writes. Receiver headroom, physical
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
`./flexe-agon-emulator --precise-interrupts`. Expect BENCH FIXTURE / BENCH RETURN
PASS and `/uart0 *`; check keyboard output with `ECHO UART0 KEYBOARD PASS`.
The Author supplied the expected screenshot, typed a successful
`ECHO UART0 BENCH FIXTURE PASS`, and accepted it with "looks like pass to me".
This satisfies the canonical human gate; TX-011/TX-012 are complete.

The accepted off-device package is `build/uart0-bench/console8-package-20261013-accepted`
on Pi and Oryx; candidate CRC32 F7A575E8 and SHA-256 remain the accepted ROM's.
It includes pinned official flash v1.9 and original notices. The Author then
specified manual Console8 flashing without Extender and authorized staging on
the SD card mounted on Oryx. The new manual bundle adds official stock VDP
2.16.0 and `readme.txt` beside the firmware/fixture files; see the dated log for
deployment evidence. TX-013 deployed and verified 19 files under
`/test/mos-uart0` on the Oryx card (UUID 8658-1C23); the host mount is
`/run/media/smith/AGON`. Read `readme.txt` on hardware with MOS TYPE.
`experiments/uart0-bench/manual-deployment.json` records hashes and receipt.
The official VDP binary differs from the Golem-built emulator snapshot;
exact-stock-image physical testing is pending. Agent-operated board/USB/firmware work still requires a
fresh bench grant. No other bench owner's historical grant applies.

Untimed verification now fences every four comparisons at VDP execution.
Unpaced / 256-command groups stalled the pinned interpreter during legacy
closed-session output; root cause remains unestablished. Four-command groups
pass both engines. This fixture change does not modify MOS or emulator source
and does not settle physical CTS headroom.

## Prior progress-only fixture — TX-014

That revision used `LOAD test.bin`, `RUN` from `/test/mos-uart0`. Only the fixture
changed at that point; firmware images were identical. The SD refresh archives the complete
old directory at `/test/mos-uart0-before-progress`, including `bench.bin` and
`failure.dat`. No test.bin collision was found. Native ZDS II and both headless
engines passed startup clear/expectation and ordered pair/mode/drain/quarter
breadcrumbs. Engine durations: 42.615 / 56.377 seconds, not hardware estimates.
For emulator review use the same dedicated Oryx profile and generated launcher.

The Author reported the old physical run stalled for at least five minutes.
Its saved failure report shows stage 2, RX bits 0x98 and the first blocking
record populated: verification had returned, then the RX diagnostic check
failed and the old fixture silently held for reset. Root cause is not yet
established. The new fixture prints FAIL when reaching that path. See
`experiments/uart0-bench/progress-deployment.json` and the dated development log.

## Diagnostic attribution correction — TX-015

The original RX latch accumulated since boot and was never reset by open/close.
Native execution against the exact accepted ROM reproduces 0x98 surviving clean
transmit/drain/close. This confirms an attribution defect, not the electrical
origin/timing of the board's framing/BREAK flags. Zilog LSR 0x98 is ERR/BI/FE;
OE (overrun) is not set. The old report has no baseline to date the event.

API 1.1 keeps old offsets and appends `tx_diag_take` at table offset 43,
table length 46, feature bit 2. With the session closed, it atomically samples
LSR/MSR, returns HL=00:modem:RX and clears software latches only. Open sessions
return BUSY without reading/acknowledging UART status. No FIFO/parser is flushed.
The test saves prior flags in baseline.dat and checks independent case epochs;
fresh recurrence of identical bits remains a failure. Old API 1.0 is rejected
with an explicit new-MOS installation message.

All 1,411 core scenarios, seven negative controls, 27 production-ROM cases and
both installed-MOS engines pass. The bench passes both engines in 42.409 /
55.116 seconds. ROM: 110,695 bytes, CRC32 7E66FD09, SHA-256
e7fc0732fba1ba6f94a30cc4bdab7e740c51a2b066cc35259f2abfc101fa848a.
The off-device package `build/uart0-bench/console8-diagnostics-20261013` exists
on Pi and Oryx. The Author returned the card and the corrected bundle is now
staged at /test/mos-uart0, with the previous directory archived intact.
No physical firmware has been changed by the agent.
The Author subsequently authorized commit/push of this tranche after physical success.

For review when the Author is available, on Oryx use
`cd ~/Agon/mystuff/agon-mos/.emulator/uart0-bench`, then
`./flexe-agon-emulator --precise-interrupts`. Verify prior RX flags, breadcrumbs,
PASS/return and keyboard operation. Keep the old physical bundle on hold; a
future diagnostic physical test requires manual installation of this new MOS.
See `experiments/uart0-bench/diagnosis.json` for evidence and unresolved scope.

## Diagnostic SD retest staged

The Author returned the Oryx card and requested the next hardware test. On
2026-10-13 the diagnostic package was staged and verified at /test/mos-uart0,
UUID 8658-1C23. The previous owned test.bin and directory were archived at
/test/mos-uart0-before-diagnostics. See experiments/uart0-bench/diagnostic-deployment.json.
Manual flashing of the new MOS (CRC32 7E66FD09) is required before test.bin.
VDP 2.16.0 is unchanged. Human emulator review/commit remains pending; the
original framing/BREAK origin remains unresolved. No agent flashing occurred.

## Completed physical benchmark

The Author returned the card after a completed diagnostic run. All eight
records pass: each sent 8,210 bytes, verified 8,192 receiver bytes and recorded
zero case RX errors. Baseline RX is zero. Every pair is 24 blocking / 16 async
raw ticks. See experiments/uart0-bench/physical-results.json and latest log.
failure.dat is the unchanged prior wrong-MOS discovery failure, not a new
failure. No installed-ROM/readback/restore dump was supplied. The card was
inspected/copied only, not modified. Physical CTS margins and wider testing
remain pending. The Author explicitly authorized committing this tranche.

## Next tranche authorization

The Author said to commit/push all dirt, then proceed with preparing physical
CTS/headroom and full-duplex fixtures. This overrides the prior commit hold for
TX-014/TX-015 only. Their human emulator review is not falsely marked complete.
Future emulator-related changes retain the canonical human review gate.

## Pause/full-duplex tranche — human review passed

Prior diagnostic work is pushed as 5cb0828. TX-016/TX-017 are promoted in the
sole TODO and now completed in the development log. New experiments/uart0-stress builds natively on Oryx and passes both
headless engines (25.717 / 32.396 s) plus compiled-app wrong-token/bad-payload
controls. It uses the same accepted MOS, CRC32 7E66FD09, and stock VDP APIs.
It checks all 128 ordered replies (31 per case before TX finishes), 32,768
stored bytes and fresh RX diagnostic epochs. Four stimuli wait 0/1/4/8 frames.
Source memory is retained through TEMT, including failure handling.

The new human-review profile is stopped at .emulator/uart0-stress on Oryx.
Run locally with `cd ~/Agon/mystuff/agon-mos/.emulator/uart0-stress` then
`./flexe-agon-emulator --precise-interrupts`. Review the clear/title, two-minute
expectation, four cases/progress, final PASS/return and keyboard DIR. The Author
passed this review with a screenshot on 2026-10-13; the retrieved human report
also passes offline validation. The review gate is satisfied. No graphical
instance was launched by the agent.
The accepted package is build/uart0-stress/console8-accepted-20261013 on Pi
and Oryx. At the Author's request it was copied and verified on SD UUID
8658-1C23 at /test/mos-uart0-stress, with no filename collision. See
experiments/uart0-stress/deployment.json. Firmware copies and readme.txt are
beside test.bin/checks.bin. Installed MOS/VDP need no change if still the same
as the passing diagnostic run; all firmware installation remains manual.
The prior /test/mos-uart0 package/reports and root /MOS.bin were preserved.

The Author has a logic sniffer, model unknown, and doubts UART0 probe access.
Manufacturer schematic confirms no TX/RX/CTS on EXP1. UART-EN1 is buffer enable,
not CTS; USB serial is ESP32 debug. Component-pad candidates are documented in
capture.txt but safe practical CTS attachment remains unestablished. Software
fixture requires no probes or board changes. Physical headroom remains open;
stock source threshold 64 and software ring 256 are not a measured reserve.

## Stable hardware test path correction

The Author's next hardware photo showed the old UART0 TRANSMISSION TEST,
not the new pause/full-duplex fixture, and objected to the changed directory.
Keep /test/mos-uart0 as the stable location for all subsequent UART fixtures.
The old benchmark reached its baseline print and failed at SAVE baseline.dat:
the file already existed from the passing run, and MOS uses FA_CREATE_NEW.
Baseline, bench and failure reports on the card are unchanged hashes from the
previous run; the displayed prior RX 0x98 is not the tested case error (0x00).
See experiments/uart0-stress/misdirected-run.json. No new stress result exists.

Both original directories were copied to host storage before changing the SD.
The old /test/mos-uart0 was archived intact as /test/mos-uart0-before-stress.
The accepted, unchanged stress fixture now occupies /test/mos-uart0, with updated
readme/firmware paths, required firmware copies and no baseline/stress/failure
report collisions. Copy/sync/hashes and report absence verified. Receipt:
experiments/uart0-stress/stable-deployment.json. No firmware flashing occurred.
The off-device package is build/uart0-stress/console8-stable-20261013 on Pi/Oryx.
Run CD /test/mos-uart0, LOAD test.bin, RUN; expect UART0 PAUSE / FULL-DUPLEX TEST
and final UART0 STRESS FIXTURE PASS, not the old TRANSMISSION TEST title.

## Physical pause/full-duplex run passed

The Author reported PASS and returned the SD for review. All four saved cases
validate: 128 replies in order, 31 per case before TX finishes, all 32,768
receiver bytes checked, zero case RX errors. Raw ticks are 10/12/16/24 for
0/1/4/8-frame stimuli; these are not calibrated seconds. Baseline RX 0x98
recurs before the trial epochs and is recorded separately; its origin is
unknown. No failure.dat exists in the current directory. Packaged fixture,
checks and firmware copies match the deployed manifest. No independent
installed-firmware readback is supplied. See physical-results.json.

Evidence is preserved only in project workspace: the complete current test
directory is archived on Oryx at build/uart0-stress/physical-completed-20261013.tar
and extracted on Pi at build/uart0-stress/physical-completed-20261013. The card
was inspected read-only and left unchanged. TX-006 remains for physical CTS
reserve and calibrated timing; this moderate full-duplex workload now passes.

## Reusable UART0 suite — staged, human review pending

The Author authorized a numbered C menu with individual tests/run-all, explicit
firmware choices and sequential reports. AgonDev is permitted only for the menu;
MOS/native fixtures still build with ZDS II under Wine on Oryx. New source is
experiments/uart0-suite. Keys 1–6 select checks, 0 runs all, 9 firmware/backup,
Q exits. Flashing never runs automatically; real upstream prompts retain Y/N.
Numbered Rnnnn.log plus runs.log reserve IDs before tests and avoid the RTC.
Keep runs.log when moving old reports; native results/baselines are numbered.

Both engines pass two whole suites plus individual diagnostics (124.401 s JIT,
166.360 s interpreter), including all 196608 receiver bytes and 256 stress
replies per campaign, zero drops/overruns/backend faults and final MOS prompt.
Real-key controls (81.588 s) prove menu/calibration input, verified MOS backup,
both actual upstream N cancellations, safe missing/corrupt-child failures,
orphan/interrupted IDs skipped and journal sequence retained after removing
individual old reports. Test source build ID bbf6b8cbadd97332. See results.json.

Full-duplex observation now uses one outstanding GP request preceding each
256-byte write, waiting for the observed token and TEMT before the next round.
The dense single-byte GP observer could miss values despite complete ordered
wire delivery. A trial with extra per-block VSYNC waits stalled the frozen
interpreter and was not staged. See observer-diagnosis.json. Prior dense
physical evidence is retained; revised suite workload still awaits hardware.
Initial pauses 0/1/4/8 and complete payload comparisons remain. The alternating
benchmark and accepted MOS/VDP images are unchanged.

The Author lifted the SD write hold. UUID 8658-1C23 was rediscovered and checked
against the exact prior UART manifest and fixture despite another attached
card. The current verified bundle occupies the SAME /test/mos-uart0/test.bin;
readme.txt, firmware copies and capture/readback readers are beside it. Host
package: build/uart0-suite/console8-suite-ready-20261013. Prior contents/results
are verified in project workspace, starting sd-before-suite-20261013. No SD
history folder was made, root /MOS.bin stayed unchanged, and no other card was
written. Current receipt: experiments/uart0-suite/deployment-complete.json.
No physical firmware flashing occurred; existing passing MOS/VDP need no update.

The stopped Oryx human-review profile is .emulator/uart0-suite. Launch with
`cd ~/Agon/mystuff/agon-mos/.emulator/uart0-suite` then
`./flexe-agon-emulator --precise-interrupts`. It has its own pinned runtime and
instructions, truthful Golem snapshot labels, no shim and no graphical launch
by the agent. Review menu selections/run-all/progress and Q return; ESC can
skip stopwatch timing, N cancels either firmware prompt. Human review remains
pending and all new emulator-related changes remain uncommitted/unpushed under
the canonical gate. TX-018/TX-019 remain in the sole TODO for that acceptance.
Physical independent clock calibration and CTS reserve/capture remain TX-006.

## Emulator flash review failure — corrected suite ready

The Author's screenshot was a VDP firmware update failure at esp_ota_begin,
error 258 (invalid argument), followed by upstream flash return zero. Human
logs show firmware operations only; the Author has not run this suite on
hardware. The frozen app-only emulator has no qualified VDP OTA update path.
A missing eligible target is consistent with the error, but the rejected
partition pointer was not directly captured. Preserve that limit. Original
human evidence is in build/uart0-suite/human-flash-failure-20261013; durable
summary: experiments/uart0-suite/human-review-failure.json.

Agon Flash v1.9 can return zero after an updater failure or cancellation. The
suite now records returned zero as UNVERIFIED/PENDING, command/load errors as
FAIL and reset handoffs as PENDING. Generated emulator profiles disable VDP
flashing with vdp_flash=0; menu 9/2 reports SKIP without launching it. Hardware
config keeps vdp_flash=1. No emulator/VDP backend or upstream utility was changed.
The Author closed the old human instance before refresh; the generator now
refuses live-profile replacement, with a tested unchanged-files guard.

Corrected build b0827de750c023bb passes both complete headless campaigns:
125.130 s JIT, 165.595 s interpreter, plus 93.607 s real-key controls. New controls
cover UNVERIFIED zero returns, unavailable VDP SKIP and missing utility FAIL.
No automated Y confirmation or physical firmware write occurred. Local report
readers pass, including the pending reset-handoff case. See results.json.
The same stopped Oryx .emulator/uart0-suite is ready for another human review;
choose 0 for UART tests, ESC to skip stopwatch timing if desired, Q to exit.
Menu 9/2 should now report SKIP in this profile. The earlier two firmware logs
remain retained and future run numbers continue sequentially. Human review of
this corrected build is pending; no commit/push is authorized by a passing
headless result alone. The Author has not yet tested this suite on hardware.

Current SD staging is now the corrected build, verified at the SAME
/test/mos-uart0 on rediscovered UUID 8658-1C23. Current receipt supersedes the
previous one: experiments/uart0-suite/deployment-flash-report-fix.json. Package:
build/uart0-suite/console8-suite-flash-report-fix-20261013. Prior files are in
workspace sd-before-flash-report-fix-20261013; root /MOS.bin stayed unchanged,
no SD history directory was made and no other card was written. Physical config
keeps VDP flashing enabled; the emulator review config disables it. Firmware
images are unchanged and no hardware firmware was flashed.

## Corrected human software campaign passed

The Author completed emulator work, including figuring out manual timing.
Saved run R0004 on build b0827de750c023bb passes tests 1,6,2,3,4 and correctly
leaves physical CTS test 5 PENDING. All eight benchmark and four stress cases
validate, with zero RX errors, 128 ordered stress replies and 98304 receiver
bytes across fixtures. Q returns to MOS; review binary hashes match. Calibration
is 1226 ticks / 10560 operator milliseconds = 116.098 ticks/s in the emulator,
not a physical Console8 calibration. Human evidence: human-results.json and
build/uart0-suite/human-completed-b0827de750c023bb on Pi/Oryx.

results.json records the passing human software campaign. No explicit new
commit approval was supplied; retain the commit/push hold. TX-018/TX-019 now
await that approval, rather than another emulator software campaign. The staged
SD contains this correct build at /test/mos-uart0/test.bin and needs no update
or firmware flash. Its bundle metadata reflects its earlier staging time.
Next: the Author runs menu 0 on Console8 and uses an independent stopwatch for
calibration (about 30 seconds is reasonable); physical CTS capture/reserve stays
pending. No hardware suite has yet been run and no physical card write occurred
while reviewing the emulator reports.

## Console8 suite passed — only physical CTS reserve remains

The Author completed Console8 menu 0 and returned the SD. Saved R0001 on build
b0827de750c023bb passes tests 1,6,2,3,4. Overall PENDING is solely test 5's
unmeasured physical CTS margin. All eight benchmark and four stress cases
validate, with 98304 receiver bytes, 128 ordered replies and zero trial RX
errors. Stress BUSY reply counts are 32/31/32/31. Blocking takes 24 ticks in
every pair; async takes 16/16/16/14. Physical manual-key calibration is 7304
ticks over 60730 external ms, approximately 120.270 ticks/s in mode 0. Use this
as an approximate stopwatch reference, not precision timing or game performance.

Entry RX 0x98 occurs before test output and stays separately recorded. All fresh
before/after-mode and VSYNC diagnostic epochs are zero. Entry origin is still
unknown. Installed full-ROM CRC is 239097B7; no independent chip readback exists.
Packaged fixtures/images match all manifest hashes; VDP version is operator
labelled. No numbered failure reports exist. Embedded/raw reports and journals
agree. See experiments/uart0-suite/physical-results.json.

Unique card UUID 8658-1C23 and exact manifest were verified before read-only
copying. Full evidence is build/uart0-suite/console8-completed-20261013-run0001
on Pi/Oryx, with an exact-copy receipt alongside. Agon timestamps are wrong
(2035); sequence/content identify the run. No card write, cleanup, flashing,
physical board access or emulator changes occurred during this inspection.
TX-006 now covers only physical CTS margin/receiver reserve. TX-018/TX-019
remain for explicit commit approval; human and physical software campaigns pass.

## Stopped at the Author's request

Olimex Agon Light 2 Rev B is recorded as a possible CTS measurement target:
eZ80 U1 lead 71 / ESP32 GPIO13 and two CTS-net PCB vias, plus TX/RX resistor
pad candidates. Board revision and practical solderless access remain
unverified. An Olimex result would not automatically establish Console8 margin.
See TX-006 and the development log for official source references. The Author
asked to record this possibility and stop. Do not resume investigation or
other project work without a new instruction.

## TX-020 current continuation: receiver experiment

The Author resumed work to try probe-free Console8 firmware inference. Olimex
probing stays deferred. `experiments/uart0-margin/` owns the diagnostic VDP,
ZDS native fixture, offline analyzer and reproducible Oryx build. Menu option 7
runs 42 threshold/hold trials; option 9/4 restores the supplied stock VDP.
Normal MOS CTS stays enabled and production MOS is unchanged. No physical
flash/SD deployment has occurred in this continuation. Human review profile:
Oryx `~/Agon/mystuff/agon-mos/.emulator/uart0-margin-menu`, launch its
`./flexe-agon-emulator` manually and select 7. Emulator VDP flashing is blocked.
Use its README/readme and qualification receipts; emulator counters cannot
prove physical margin. Keep new changes uncommitted pending human approval.

TX-020 human review completed and evidence archived. The reviewed bundle is
now staged on the Console8 SD at /test/mos-uart0/test.bin; numbered results and
runs.log preserved. See experiments/uart0-margin/deployment.json. The next
physical run requires manually flashing the diagnostic VDP via menu 9/2,
confirming successful update/reboot, then running 7. Diagnostic CRC32 19236414;
stock restoration is menu 9/4, CRC32 FFFBFADE. No MOS reflash is required.
Prior no-SD-deployment notes describe preparation before this accepted staging.

Console8 diagnostic run R0003 passed all 42 valid receiver trials, 172032
compared bytes and zero UART errors. Stock threshold64 settles at66 bytes in
all six stock trials (5/20ms ×3): 62 observed free FIFO slots. High thresholds
saturate at128 without data loss, so no failure boundary was measured; this is
empirical reserve, not worst-case/electrical timing qualification. Evidence:
experiments/uart0-margin/physical-results.json; full off-card archive in
build/uart0-margin/console8-receiver-run0003.tar.gz. Inspection was read-only.
Stock VDP restoration was requested in R0004; successful installed stock boot
version is not independently confirmed by the updater's zero return.

## Planned opt-in CTS batching — BT-001 through BT-007

The Author requested a design goal and task plan, not firmware implementation.
See docs/uart0-cts-batching.md and the sole checklist TODO.md. Aware apps may
request a session-scoped bounded batch between CTS checks; per-byte default and
legacy behavior remain. Select sizes only after hardware/in-flight audit and
measure recovered CPU work as well as throughput. Observed62 spare FIFO slots
are evidence for investigation, not a supported batch allowance. No failure
boundary was observed. First close existing TX-018/019/020 evidence/release work
and TX-006 qualification scope, including stock VDP boot confirmation. No
commit/push authorization or new physical access is implied by planning.

BT-001/BT-002 are delivered in docs/uart0-cts-batching-api.md and
 docs/uart0-cts-batching-audit.md. The Author confirms restored stock VDP boot;
TX-006 closeout is complete with electrical/worst-case timing deferred. The
proposed table is minor2/length54 with setter/getter at46/49, bitmap at52.
Service still admits at most16 writes after THRE; selectedN changes checks
within that cap, never allowance across calls. No firmware implementation yet.

## Original OTIRX goal restored explicitly

The Author supplied Tom Morton's verbatim comments and Discord provenance:
https://discord.com/channels/1158535358624039014/1158537054959964220/1559209863954038915
They now anchor docs/uart0-async.md. BT-003/BT-004 explicitly compare default,
grouped scalar and bounded OTIRX refills, including per-chunk progress accounting.
The previous exclusion of OTIRX from the batching contract was an agent planning
error and is superseded. Its DE-port/BC-count requirements mean the scalar
D-counter suggestion is not a block-copy register allocation. Tom's final
sentence remains an open caution; no definite intent is attributed to it.

## Next tranche — A/B stream benchmark and Jukebox workload

The Author requested the A/B plan and immediate skins-branch inspection. See
 docs/uart0-ab-tranche.md and docs/uart0-jukebox-skins-audit.md; AB-001..AB-005
are in the sole TODO alongside driver tasks BT-003..BT-007. Inspected current
GitHub skins f3cd5925a14778f8c5ed4666bac10b2e109731b3 in a MOS-owned reference,
without modifying the other checkout. Audio is735-byte chunks at60Hz for44.1kHz
unsigned8-bit mono. Current timer ISR reads SD, sends blocking MOS uploads and
flushes UI under DI; foreground blocks in mos_getkey. The WAV reference prose
describes a restructuring not reflected in that source. Synthetic testing must
use a short due-work ISR and foreground immutable packet publication; a future
Jukebox integration must separately restructure scheduling. Compare that change
against OTIRX gain using identical adapted scalar/OTIRX schedules. Actual app
changes, firmware builds, emulator runs and SD deployment were not performed.

## Controlled A/B initial results available

experiments/uart0-ab contains native ZDS kernels, instruction-model cycle tests
and a real-VDP native fixture. See RESULTS.md/results.json for scope and evidence.
Paced modeled UART service cycles fall11.43M→3.00M over two seconds (~74% saved);
toy useful work rises~33%. Unpaced model throughput110.7k→108.5k data bytes/s:
no throughput win yet. Only interval16 candidates were tested, not all proposed
API settings. Production source/public ABI unchanged; public batching API,
physical timing and complete bulk receiver verification remain pending.
Final native image passes two campaigns in each Flexe engine (120 phases total),
following bounded untimed comparison barriers and atomic dispatch updates.
Earlier timing-sensitive stalls are retained without a definitive causal claim.
Stopped Oryx review profile: .emulator/uart0-ab; readme.txt in sdcard/uart0.
No SD write or flash. New changes remain uncommitted pending human review.

## A/B human failure — 2026-10-14

The Author confirmed a stall and closed the human emulator at repeat2/mode1/
phase0 (current scalar async bulk kernel). Readiness is revoked despite the
four prior successful headless campaigns. No causal fix has been established.
Closed-run artifacts are preserved on Pi and Oryx in
build/uart0-ab/human-stall-001.tar.gz. Counters report zero TX drops/RX overruns
and no backend fault; those counters do not explain the stall. Do not deploy
this fixture to hardware or commit it as qualified. Investigate separately;
production MOS and the physical SD remain unchanged.
