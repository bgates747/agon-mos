# Interrupt-based UART0 transmission project — handoff

LATEST 2026-11-01 — Author approved logical commit/push checkpoint, then BO-004.
MOS implementation9754da6; qualified suite/resultsdfeb102; policy/task/hardware
notes form the final checkpoint group. Next develop the deliberate-reset fixture;
previous hardware round is complete and passed. See today's development log.
Older uncommitted/approval-pending statements below are historical.

LATEST 2026-11-01 — CONSOLE8 HARDWARE RETURN PASSES.
NEXT TASK: develop a fixture to test deliberate reset during active transmission
(BO-004), qualify it, then provide a separate hardware procedure. The Author
completed every test requested in the last round; no reset-during-send fixture
was supplied or expected in that round.
R0031/33/34 stock discovery PASS;R0032 activation/close/reopen PASS;
R0035/R0036 fullfourtests PASS. Exact reviewed menubuild32d6d885f3b8b8e0 and
firmware/children match deployment. Across eightpausecases:65536payloadbytes
verified,256orderedreplies, zero RX/orderingerrors, masked-IFF/app-exit/stock
handler restoration pass. No newfailurefiles; journal complete; oldreports
unchanged. Normal resetsteps operator-reported. BO-004 owns development of the
next deliberate-reset fixture. No new speed/CTS-margin/release claim.

AUTHOR LEFT EXPERIMENTAL MOS + TEST VDP INSTALLED deliberately; dedicatedConsole8
will not be used between tests. Do NOT treat stockrestoration as overdue.
No agentflash/boardcommand/cardwrite/emulatorlaunch ininspection. AGONC8 still
mounted onOryx, unchanged by inspection. Returnedautoexec nowcommentsJukebox
andCDs/test/mos-uart0 only, noautoactivation; rootstockMOSunchanged. Prefer installed `flash mos <filename>` / `flash vdp
<filename>` over longLOAD/RUNfallback. Verified /mos/flash.bin is EXACT official
bundled1.9 SHA480b4767...75eb57. Policy inAGENTS.md.

Full113files return verifiedonOryx/Pi; archive1,388,310bytes SHA
bf26310a96d97f5a6bbd45356cf307184d18ac3b234ef2f3d2bdf0c28ce399e3,
build/uart0-startup-safe/card-return001.tar.gz. Source/JSON offlineanalysis in
card-return001; per-run analysis in experiments/uart0-startup-safe/README.md.
New code UNCOMMITTED; Author reported tests complete, not commit/push approval.
Earlier hardwarepending/stockrestorerequired statements below are superseded
for this completed normal campaign. BO-004 stronger recovery and BT/AB remain.

LATEST 2026-10-31 — CONSOLE8 APPLIANCE DEPLOYED at Author request.
AGONC8 UUID8658-1C23 onOryx /test/mos-uart0, same activepath;23files verified.
Exact reviewed ZDSMOS89ea8694...12aa42b, fileCRC29DCC1FC/ROMCRC0C5886FC;
newtest.bin/menu32d6d885f3b8b8e0, same nativechildren/checks. Matched testVDP,
stockVDP2.16.0, stockMOSrollback, officialFLASH1.9 and shortreadmes supplied.
H-001..005: MOSbootwithstockVDPfirst, menu1/2+idlepowercycle, installmatchedVDP,
menu0 twice withidlepowercycle, thenrestorenormalstockVDP2.16.0. Explicit
LOADflash.bin &B0000 / RUN &B0000 mos mos-candidate.bin; rootMOS.bin staysSTOCK.
Oldwithdrawnpackage fully preserved173files/hashverifiedonPi/Oryx beforewrites;
75numberedreports retainedunchanged, nextR0031, journalcompactedworkspacehistory.
No newhistorydirectories oncard. Rootautoexec unchanged. CardLEFTMOUNTED.
No firmwareflashed/boardrun/emulatortouched. Physicalacceptance PENDING;
idlecompleted-sessionreset doesnotprove partial-command/crash recovery.
Buildartifacts/receipt/scripts: build/uart0-startup-safe/card-deploy001.
Newwork UNCOMMITTED; do not assume staging authorizes agent firmwareflashing.

LATEST 2026-10-31 — HUMAN REVIEW R0001 PASSES; ORYX RELEASED.
Exact startup-preserving ZDS MOS89ea8694...12aa42b/menu32d6d885f3b8b8e0.
Allfourtests PASS; four pauses each8192verifiedbytes/32orderedreplies,
32768totalbytes/128replies, full wire packets/checkcommands match. Masked-IFF,
queued-source app exit, stock handler return, Q/typedDIR/liveprompt pass;
0frontendfault/TXdrop/RXoverrun. Capture contains one boot, not independent
proof of close/relaunch. BO-003 functional/software review complete; BO-004
physical boot/activation/integrity/whole-board reset recovery still required.
Ready to prepare that focused hardware test after authorization; nothing newly
staged to a physical card/flashed. No new throughput/CPU performance claim.
New code remains UNCOMMITTED pending explicit commit approval.

Reviewgeneration48/requestc16e3260c12d RELEASED14:59:41EDT with new idleproof,
after verified Pi evidence retrieval. Next Rallyrequest5c6fe3061222 notified
through existing chat by immediate steering; it then checked outgeneration49.
Do not reuse old lease06a6... or launch review profile without a NEW reservation.
Raw verified23filearchive Pi/Oryx run004/human-return001.tar.gz SHA
c10d3e6308a07d076a10ca74a178f15dc40f7a71c000a038c5d91bf7630d18a2.
Analysis/evidence limits: experiments/uart0-startup-safe/README.md and today's
log; raw offline analysis under build/uart0-startup-safe/run004/human-return001.
Earlier human-review-pending/lease-held statements below are superseded.

LATEST 2026-10-31 — BO-001/BO-002 implemented OFF-DEVICE with ZDS II/Wine.
Working release startup, UART setup and original handler restored; initializer
runs only on explicit successful open. RAM vector switches then; close/app
return restores stock. Cold/retained-RAM reset leaves experimental state off.
Main/uart/interrupts/cstartup/init_params source matches v3.0.2 byte-for-byte.
Minimal serial/RST dispatch guards remain; do not claim identical whole ROM.

Candidate run004 MOS111239bytes SHA89ea8694194e0488337bf1dcbfa91e2b084b3afc75a9c3916f4acc9ae12aa42b,
erased-tailCRC0C5886FC/FlexeCRC16A52145, startup-safe EXPERIMENTAL subtitle.
Actual-ROM baud/reset/crashed-experimental-handler/RST18/vector controls pass;
27production+538batch cases per size1/2/4/8/16 pass. Both Flexe engines pass two
full suites each,65536comparedbytes/256replies each,0fault/drop/overrun. Real20ms
key taps and official updater USAGE/CLI return pass. Uses compiled repaired
DIAGNOSTIC VDP, not stock. New RST18 CALL.LIL repair rejects bad run003 control.
No new physical result, firmware approval, deployment, board/card operation.

New review profile STAGED AND STOPPED onOryx:
/home/smith/Agon/mystuff/agon-mos/.emulator/uart0-startup-safe-review
Menu1..4,0all,QCLI; opens WITHOUT activation. Reserve/check out Oryx when Author
ready; do not send launch instructions until checkout. Shared FIFO/lease policy
is linked in AGENTS.md; no Golem grant. New runners enforce lease immediately
before emulator launch. Other owner's checkout preserved; no lease claimed for
completed runs that predate this session's notice of policy.

Checkpoint/push completed BEFORE implementation: main d5268d2/a45912b; historical
native branch e493d97. NEW WORK UNCOMMITTED pending human review/commit approval.
N-005 checkpoint disposed; BO-003 human/BO-004 physical acceptance remain.
Full evidence archive verified onPi/Oryx f20322d4...e4ac9cd5,625regularfiles:
build/uart0-startup-safe-20261031-r01.tar.gz. README in
experiments/uart0-startup-safe/README.md; today's devlog records dispositions.
Stock MOS3.0.2 recovery is boot-confirmed. Console8 VDP was restored to official
stock2.16.0 and Author confirmed back up; leave physical hardware untouched.

LATEST 2026-10-31 — AUTHOR CONFIRMS C8 MOS BOOTS: “praise jesus, it worked.”
N-009 complete: stockMOS3.0.2 target RAM/flash CRC PASS plus physical boot.
Author attaches C8 SD onOryx and asks recover any missingdiagnostics. Confirmed
AGONC8 UUID8658-1C23; read-only snapshot257files/67,826,138bytes, allfiveUART
fixture directories plusrootMOS/startup. New loose-evidence matches absent for
R0030.log, runs.log, oldfailure.dat, oldbench.dat andautoexec.txt. R0030 captures
candidateflashHANDOFF PENDING, not success. Fullsnapshot/hasharchive verified
onOryx andPi; sourcecardUNCHANGED and LEFTMOUNTED. RootMOS.bin=knownstock3.0.2.
Evidence build/c8-sd-recovery-20261031/return-001; report:
docs/c8-sd-recovery-2026-10-31.md. ArchiveSHAe462d136...fd1634f3.
WROOM remains CHECKEDr01 quietterminal/pinsreleased unless Author powercycles;
no new programmer/target commands in SDcollection. P4 unused; its deferred
original-firmware restoration remains separatecleanup pending availability.
Withdrawn nativeMOS candidate is still onSD as historicalcapture, unchanged;
no new experimental firmwaredeployment or performance testing authorized here.
Older bootpending/N-009incomplete entries below are historical/superseded.

LATEST 2026-10-31 — Author requests RESTORE MOS. Completed one checked WROOM
stock MOS3.0.2 recovery on Oryx: identity0007/AA, RAM CRC15BD0583 PASS,
post-flash MOS CRC15BD0583 PASS. This is target CRC-VERIFIED programming,
not blind completion. Boot NOT yet confirmed; Author told to PRESS CONSOLE8
RESET now and check MOS banner. Target was left in break after flash CRC;
WROOM outputs released, host serial closed, no retry/reset ongoing. WROOM NOW
WROOM-CHECKED r01 (ac75fbb4...), NOT identity-onlyv3. Normal startup unarmed,
exact FLASH required; no BOOT shortcut. Keep wiring BLUE26clock/GREEN27data,
upper-middle ground, no resistors, improved breadboard; no physical change.
Same10us timing, original90byteagent and normal checks; no added PC/dump gates.
P4 unused and original restoration still deferred until physical MOS boot.
Report docs/c8-stock-mos-recovery-2026-10-31.md. Raw Pi/Oryx:
build/c8-wroom-checked-20261031/run-001; verified archive same prefix
-evidence-r01.tar.gz SHA b8ed26b7...c12d0355. Await Author reset/banner result.
All prior claims C8 unprogrammed or WROOM identity-only below are historical.

LATEST — Author moved CONSOLE8+WROOM toORYX with same proven wiring:
BLUE26clock/ZDI4, GREEN27data/ZDI6, upper-middle ground, no resistors, same
breadboard. Requested1000identity-only probes. Oryx run001 completed with
1000/1000correct0007/AA,996status1C/4status18(IEF1flag),13000local drive
checks pass; firstafterWROOMrestart10/10valid, all tenepochs100/100. Same
quietv3/S10us firmware; only runner target label generalized. NO Console8
reset/halt/RAM/flash. WROOM remains quietv3 onOryx, output drivers released,
BLUE/GREENHIGH, host closed, no polling. C8 MOS still NOT restored or boot
verified. Clean read link is established for these conditions; no flash/RAM/
high-speed qualification. P4 unused, original restoration deferred.
Evidence Pi/Oryx build/c8-wroom-identity-20261030/run-001; report:
docs/c8-wroom-identity-2026-10-30.md. No target writes under this read-only task.
Earlier invalidC8 ID results below are historical, not current link status.

LATEST — Olimex startup incident cleared without reflashing: Author reports
normal boot with WROOM disconnected, then restores direct upper-middle-ground
wiring (BLUE26clock/GREEN27data, no resistors), powers WROOM first/Olimex second,
and confirms MOS prompt. Explicitly requested repeat: same quietv3/S10us,
ten WROOM-only restart epochs,1000/1000correct0007/AA,998status1C/2status18,
all13000local drive checks pass, firstafterrestart10/10valid. No Olimex reset,
halt/RAM/flash. Outputs released, BLUE/GREENHIGH, host closed, no polling.
Latest evidence run004-ground3-ordered-power in campaign Pi/Oryx. Report:
docs/olimex-wroom-ground3-power-sequence-2026-10-30.md. Post-test physicalCLI
not observed by agent. C8 STILL unrecovered; P4 unused/restoration deferred.
Older INCIDENT HOLD entries below are superseded for this completed authorized
identity test; no new flash or investigation authorized by its success.

INCIDENT — Author now reports OLIMEX VDP branding but NO MOS branding after
last identity run. Confirms WROOM WAS STILL ATTACHED during this boot. All
hardware access STOPPED; audit inspected local files only. No recovery/reset/
readback or other device command sent. Asked Author to power BOTH boards off,
disconnect ALL WROOM-to-Olimex leads, then boot Olimex ALONE to check banners.
Await that result. Do not assume flash corruption or intact flash. No remote
reset/flash/test authorized by this report. Latest commanded WROOM state was
released outputs, not a proof of current physical state. Last wiring upper-left
ground and direct BLUE26clock/GREEN27data. Identity-onlyv3 stays installed.
Audit confirms only P/Q/S host commands and esptool writes to WROOM app, tenv3
banners in each run; actual wire effects not captured. Exactv3 source snapshot
not yet recovered; later v7/v8 source is not a substitute for executedv3.
Incident: docs/olimex-mos-startup-incident-2026-10-30.md. Older claims of
normal Olimex operation below predate this incident. Console8 also unrecovered.

LATEST — Author corrects prior clean run002: ground NEVER MOVED; actual
upper-middle(reportedpin3), not upper-left5. Raw result/filename preserved,
correction sidecar at campaignparent/operator-correction-run-002.json; previous
human report explicitly corrected. Author NOW moved ground alone to upper-left,
all other setup unchanged (direct/no resistors, BLUE26clock/GREEN27data).
Requested matched1000reads completed run003-ground5-only-change: ZERO correct,
1000×FF FF FF FF, all13000local drive checks pass; firstafterreset0/10.
Prior upper-middle run1000/1000correct. No cause established beyond association
with changed connection; do not assume physical pin identification/continuity
or chip damage. Current upper-left ground remains; do NOT blind flash.
Same WROOM quietv3/S10us, outputs released, BLUE/GREENHIGH, serial closed.
No Olimex reset/halt/RAM/flash. Evidence Pi/Oryx:
build/olimex-wroom-breadboard-20261030/run-003-ground5-only-change. Report:
docs/olimex-wroom-ground-comparison-2026-10-30.md. Older pin5-pass claims below
are superseded by Author correction; do not reuse them as pin5 success evidence.

LATEST — Author confirms rewiring complete, WROOM/Pi5/Olimex: BLUE clock
GPIO26->ZDI4, GREEN dataGPIO27->ZDI6, ground moved upper-middle3 to upper-left5,
NO INLINE RESISTORS. Same higher-quality breadboard. Author believes only
colors changed on signals, not signal functions. Same identity-onlyv3 and
S/10us firmware; ten100-read WROOM-only reset epochs:1000/1000correct0007/AA.
999status1C,1status18 (IEF1bit2 difference); all13000local drive checks pass,
firstafterreset10/10valid. No Olimex reset/halt/RAM/flash. Both output drivers
released; BLUE and GREEN bothHIGH; host closed, no polling. WROOM quietv3
remains. P4 not used; original P4 restoration still deferred. REWIRING HOLD
IS CLEARED for this completed authorized test, not blanket flash permission.
Observed clean identity setup, not flash/high-speed qualification or isolation
of ground/resistor effects. Earlier1000run had33ohms, now0. Evidence Pi/Oryx:
build/olimex-wroom-breadboard-20261030/run-002-ground5-direct. Report:
docs/olimex-wroom-ground5-direct-2026-10-30.md. Older states below historical.

LATEST — Author supplied upstream Jeroen ZDI connector and Console8/WROOM
breadboard diagrams and announces rewiring to match them: BLUE CLOCK GPIO26
-> target pin4/lower middle; GREEN DATA GPIO27 -> pin6/lower left, notch at
top. This SUPERSEDES earlier GREEN-clock/BLUE-data instructions. Own AGENTS.md
updated; old test logs remain unchanged. REWIRING NOT YET CONFIRMED COMPLETE:
NO HARDWARE COMMANDS while Author changes leads. WROOM remains identity-onlyv3;
last test ended with output drivers released. No new read/flash/reset performed.
Original diagrams, pinned provenance/checksums and upstream MIT notice stored
canonically in ../agon-extender/docs/mos-recovery/, embedded in its maintained
../agon-extender/docs/mos-recovery.md. Both pictures agree; WROOM26/27 labels
must not be applied to P4 (clock46/data47). Earlier statistical run is historical
under its reported wiring, not a post-correction validation or electrical cause.

LATEST — Author moved WROOM toPi5/Olimex, GREEN CLOCK26/BLUE DATA27,
33-ohm series resistors, improved breadboard; requested meaningful ID statistics.
Preserved WROOM incoming app span; installed archived quiet identity-onlyv3.
1000reads,10WROOM-only resets, S/10us edges:325correct0007/AA,675wrong,
280also have status1C. All13000local drive checks pass. Per100correct:
31,32,27,37,27,35,35,36,30,35. Firstafterreset3/10valid. No Olimex halt,
reset/RAM/flash. WROOM NOW quietv3 on26/27, outputs released; final local
GREENHIGH/BLUELOW; serial closed, no polling. P4 not involved; its original
restoration remains deferred. No physical cause assigned or direct P4 rate
comparison. Report docs/olimex-wroom-breadboard-2026-10-30.md; raw evidence
Pi/Oryx build/olimex-wroom-breadboard-20261030. Older states superseded below.

LATEST — Author installed100-ohm series resistors on Pi5/P4/Olimex and
requested repeated ID reads only. Same IDENTITY-ONLYr01; P4-only reset once
before ten batches of three reads, no reset between batches. Run005-100ohm:
16/30 full0007/AA/1C,14 corrupt. ALL TEN first reads invalid. Batches2and3
entirely corrupt; batches1and4..10 have correct reads2and3. No Olimex reset,
CPU halt, RAM access or MOS programming. Both signals released, host closed.
CURRENT WIRING IS100OHMS, not direct/33ohms. P4 remains identity-only on Pi5.
Observed baselines:33ohms4/6, direct0/9,100ohms16/30; unequal samples and
uncontrolled wiring changes do not rank resistor values or prove a cause.
Evidence build/olimex-p4-identity-20261030/run-005-100ohm. ConsoleSHA256
2fa12e69f8f92ec722cf96b2bcba2033962e690a2670dec1e61cd9cca859babb.

LATEST — Author removed series resistors: Olimex directly wired to P4 on
Pi5. Identity-only comparison: run003-direct console timed out before any
identity result; queued READY output was drained, no complete batch. Reset
P4 ONLY (not Olimex) and ran run004-direct, three batches/nine reads. ZERO
full0007/AA/1C matches; four product0007 but revisionAB/status1E or1F. Other
products83FF/83C1/FFFF/D8C4. This trial is worse than preceding33-ohm4/6
full matches; does not establish an electrical cause. No target reset/halt,
RAM access or MOS flash. Direct wiring remains current; do not assume33ohms.
P4 still IDENTITY-ONLY r01 on Pi5, GREEN46/BLUE47 released, serial closed.
Known idle console stalled and required P4-only restart; no automatic retries.
Evidence build/olimex-p4-identity-20261030/run-00{3,4}-direct.

LATEST — Author moved P4 to Pi5 and Olimex; explicitly IDENTITY ONLY,
DO NOT FLASH OLIMEX MOS. Replaced checked-recovery P4 app with dedicated
P4-IDENTITY-ONLY r01 (NO MOS/agent payload or CPU halt/write/flash API).
GREEN CLOCK46/BLUE DATA47, same transaction timing. Two IDENTIFY batches:
run001 [FFFF/FF/FF, 0007/AA/1C, 0007/AA/1C]; run002 without explicit P4
reset [6262/07/1C, 0007/AA/1C, 0007/AA/1C]. Four of six exact identities,
first reading of BOTH batches invalid. This proves communication is possible
on Olimex but not reliably on the first read after ZDI begin; cause unassigned.
No Olimex CPU halt, RAM access or MOS erase/program requested. GREEN/BLUE
released; host closed. P4 NOW identity-only on Pi5, not checked recovery on
Oryx. Original P4 restore still deferred; Console8 remains unrecovered.
Do not send FLASH on this setup or reintroduce a flash-capable build without
new scope. Evidence build/olimex-p4-identity-20261030; source
experiments/zdi-p4-identity-only. Prior state entries below are historical.

LATEST — Author confirms repeated blind P4 flash did NOT restore MOS and
explicitly requests Jeroen's normal checks. Built/installed P4-CHECKED r01:
identity(product7), MOS RAM CRC, post-flash MOS CRC; no custom dumps/PC gates.
Run001 IDENTITY product=FFFF revision=FF status=FF expected-product=0007.
RESULT identity_failed. Stopped BEFORE MOS upload/erase/program; flash agent
NOT started. P4 currently CHECKED r01, not FLASH-ONLY. GREEN46/BLUE47 released,
no serial host remains, no automatic retry/reset/P4 restoration. NO SNIFFERS.
Both33-ohm resistors and Oryx powered setup remain Author-confirmed. Console8
still unrecovered; no new power-cycle request needed for this identity refusal.
Evidence Pi/Oryx: build/c8-zdi/p4-checked-20261030/run-001/. Source:
experiments/zdi-p4-checked/. Checks/algorithm follow upstream95d68464; only
P4 GPIO/USB/isolation/timing and bounded host command UI adapted.
Older blind-sequence completion/monitor-pending entries below are superseded.

LATEST — Author explicitly ordered immediate Console8 restoration again.
Reset P4 ONLY to rearm installed FLASH-ONLY r01 and sent one FLASH command.
Run003 completed full stockMOS and flash-agent uploads, resume and ten-second
wait; GREEN/BLUE released. NO eZ80 read/identification/verification; no target
reset or P4 restoration. P4 message proves only sequence completion. Await
Author Console8 power-cycle/monitor MOS banner. No host process remains.
Evidence Pi/Oryx: build/c8-zdi/p4-flash-only-20261030/run-003/.

LATEST — Author reports WROOM blind flash left Console8 bricked. At Author's
request, built/installed P4 FLASH-ONLY r01 using GREEN CLOCK GPIO46/EXT2 pin7,
BLUE DATA GPIO47/EXT2 pin6, both outside normal Extender harness. Author wired
both 33-ohm series resistors and powered/connected both boards on Oryx.
P4 programmer verified; one FLASH command completed stock MOS108490-byte
upload, original90-byte agent upload, resume and ten-second wait. NO TARGET
READS or readback gates. Completion is NOT verified MOS success. GREEN/BLUE
released as inputs; P4 remains on one-shot programmer. No host process remains,
no automatic retry/reset, NO SNIFFERS. Await Author Console8 power-cycle and
monitor MOS-banner observation. Do not restore normal P4 firmware yet.
Raw run002, original P4 full backup and compiled artifacts preserved Pi/Oryx:
build/c8-zdi/p4-flash-only-20261030/. Run001 was USB permission denial before
any device access; run002 used authorized sudo. Source/host tools:
experiments/zdi-p4-flash-only/. Transcript SHA256:
b0b796dff68f2d04ca1bf6232a4ff554d26308ec24bf149cf2d1ba2b611816e5.
Original pre-recovery P4 backup from20261028 also retained unchanged.
Older state entries below are historical and superseded by this paragraph.

LATEST — Author explicitly ordered REMOVE ALL CHECKS, theorizing readback
corruption, and says monitor boot is the required validation. Implemented
write-only recovery: no target ID/status/PC/readback/CRC reads, SetADL write
only; retain original init/write/upload/size/flash-agent/resume/10secondwait.
Normal menu2/Y executed once. Run-009-blind completes MOS upload, flash-tool
upload, emits Flashing MOS and BLIND FLASH SEQUENCE FINISHED. This is a
COMPLETED BLIND COMMAND SEQUENCE, NOT VERIFIED FLASH SUCCESS. User informed
to power-cycle Console8 and check MOS banner. Await physical boot outcome.
Do not require a readback check contrary to the Author's explicit instruction.

Current WROOM is serial-only BLIND recovery mode, GREEN CLOCK27/BLUE DATA26,
unmodified upstream ZDI driver, target reads disabled, original BOOT-hold
recovery action remains. No host process/polling remains; do NOT assert pins
released or CPU state known. Flash agent was commanded to run and spins after
its work; physical reset/power cycle required. No automated target reset sent.
NO SNIFFERS. P4 standard firmware restoration deferred until repair confirmed.
Raw evidence Pi/Oryx: build/c8-zdi/jeroen-stock-20261030/run-009-blind/,
consoleSHA ca69178d844dce8749de20bc76529228e064afccff8d9585ddfce0c368f78b05.

LATEST AUTHOR DIRECTIVE — Stop custom diagnostic barriers. Author explicitly
ordered FLASH GOOD MOS and follow Jeroen's exact recovery protocol; no added
PC preservation/admission checks. Earlier customr03 stopped on added RAM
parameter check and is superseded. Ran original flashMOS/init_ez80/CRC code,
finally with byte-identical upstream ZDI driver, through normal menu2/Y.
MOS RAM upload completed then original CRC32 ERROR; no flash phase entered.
MOS HAS NOT BEEN FLASHED. No successful recovery/boot/full readback claim.

Current WROOM is upstream-based serial-only recovery utility: GREEN CLOCK27,
BLUE DATA26, inputs enabled, no VGA/PS2 startup, menu exposed despite status
display under Author force-recovery order. Actual recovery/ZDI/CPU code matches
upstream95d68464; final source receipt preserved. NOT quietv11/v10/v3: boot
writes normal ZDI/CPU initialization and BOOT-hold recovery remains active.
No host script/serial process remains; no ongoing ID polling in idle front end;
do NOT claim GPIO outputs released. Target CPU state unverified after normal
break request/RAM transfer. NO SNIFFERS. Physical wiring unchanged from Author's
tighter ground leads + series resistors; no further bench request pending.

Details/attempt accounting: [stock recovery](docs/c8-stock-recovery-2026-10-30.md).
Archive verified Pi/Oryx build/c8-zdi/jeroen-stock-20261030-evidence-r01.tar.gz
SHA3835f91f...4649fbde. Console8 remains unrecovered; P4 restore still deferred.
Do not resume the old custom PC/RAM diagnostic workflow without Author request.

LATEST BREAKTHROUGH — Author reconfirmed BLUE=TDI GPIO26/GREEN=TCK GPIO27
and requested one more repeat. Same restored v11 returns exact identity
07 00 AA 1C and HALT statuses9C/9C/9C, all valid. Then stops at original-PC
verification, before RAM mapping/access/write or flash. The firmware does NOT
print PC samples, so the failure may be first readFFFFFF or a mismatch between
reads; do not assert which. Both outputs released; local GREENHIGH/BLUELOW,
serial closed. CPU last verified halted (9C), no resume/reset requested.
Single valid run does not establish sustained reliability or prove the cause
of prior failures. No new physical change reported beyond previous ground-lead
replacement. Evidence Pi/Oryx: build/zdi-ram-probe-20261030/probe-repeat-003/.
Next software work: expose PC samples and audit CPU-register read timing/
protocol against upstream before another hardware probe. No board operation
remains running; WROOM remains quiet-command-gated v11 on GREEN27/BLUE26.

LATEST — Author declined meter check, replaced ground leads with tighter ones
and requested repeat. Same v11(GREEN clock27/BLUE data26): identityallFF,
HALT statusFF/FF/FF. Then completed queued software-crossed controlv12,
CLOCK26/BLUE DATA27/GREEN without changing wiring: identity07 01 11 41,
HALT statuses87/70/07, all invalid. Both send oneHALT but stop before ANY RAM
mapping/access/write or flash operation. No target reset requested; actual
CPU halt state UNVERIFIED. Restored original quiet v11 afterwards, full
readback and exact original app-span match. Both outputs released; final
GREEN27LOW/BLUE26HIGH at WROOM; serial closed, no operation running. NO SNIFFERS.
No repeat meter/wiring request pending. Evidence/limits:
[ground/control record](docs/c8-zdi-ground-control-2026-10-30.md).
Ground replacement alone did not resolve communication; crossed assignment
changes sampled data but does not establish correct target pinout or recovery.

LATEST — Author explicitly wired BLUE DATA GPIO26/GREEN CLOCK GPIO27, series
resistors, NO SNIFFERS, and authorized best-next diagnostics. Installed matching
identity v10, readback-verified;5reads allFF. Then installed quiet RAM-only v11
(SHA7f60ec5e...0a68f76), full readback verified. Sent one actual HALT request
despite invalid identity; three independent status reads FF/FF/FF, rejected
reserved bits, so NO RAM attempt and NO flash operation. Both outputs released,
inputsHIGH, serial closed; actual target CPU halt state UNVERIFIED. WROOM NOW
v11 RAM-only on GREEN27/BLUE26, not identity-only v10/v9/v3. It boots quiet,
requires exact host command, and has no automatic retry or flash API/payload.

Author then asked about ground. Further board operations HELD pending fresh
ground check; requested both boards OFF and both USB cables UNPLUGGED, then
resistance WROOM GND -> Console8 ZDI GND at board pins. Prior continuity check
predates replaced leads. Crossed-function v12(clock26/data27) built OFF DEVICE
but NOT installed/executed. Do not run during ground check/power changes.
Evidence Pi/Oryx build/zdi-ram-probe-20261030/{wroom-v11-install-001,probe-001}/;
source and stage dispositions in experiments/zdi-ram-probe/README.md.

LATEST — Author reports leads attached WROOM-side of series resistors and
explicitly confirms NO SNIFFERS ATTACHED. Do not ask again without evidence
of a new analyzer attachment. Same v9 GPIO18/19:5reads allFF,65 local drive
checks pass. Outputs released, local inputsHIGH, serial closed. No target
reset/halt/RAM/flash. Evidence Pi/Oryx:
build/zdi-unprobed-20261030/c8-wroom-side-attachment-five-001/.
Initial receipt said probe-state unknown because agent misread update;
operator-clarification.json preserves the correction without changing raw logs.

LATEST — Author replaced all leads with those that passed Olimex. Same v9
GPIO18/19 diagnostic still returns FF FF FF FF for all5reads;65 local drive
checks pass. Released both outputs, both local inputs HIGH, serial closed.
No target reset/halt/RAM/flash. Physical endpoints and retention of the last
reported33ohm resistors not independently reconfirmed after lead replacement.
Evidence Pi/Oryx: build/zdi-unprobed-20261030/c8-olimex-leads-five-001/.

LATEST — Author reversed GREEN/BLUE after alternate-pin test. WROOM remains
v9 CLOCK=GPIO18/DATA=GPIO19; series resistors retained. Five consecutive reads
all FF FF FF FF;65 local drive snapshots pass. Outputs released, both local
inputs HIGH, serial closed. No Console8 reset/halt/RAM/flash. Wiring remains
AUTHOR-REVERSED: logical GPIO/color receipt labels are not physical endpoint
verification. Evidence Pi/Oryx:
build/zdi-unprobed-20261030/c8-alt18-19-swapped-five-001/.

LATEST — Author authorized WROOM alternate-pin flash/test and restored series
resistors (last measured33ohms). Installed and fully readback-verified v9:
GREEN CLOCK GPIO18, BLUE DATA GPIO19, image SHA097b58aa...e248d08. Old v3
affected app span backed up and verified before write. First read allFF;
follow-up five consecutive slow reads also allFF, all78 local drive checks
pass across6reads. No valid identity. Both outputs released/local inputsHIGH,
serial closed. No Console8 reset/halt/RAM/flash requested. Actual pin endpoints
not independently measured; no probes reported reconnected. Pi/Oryx evidence:
build/zdi-alt-pins-20261030/wroom-v9-install-001/ and
build/zdi-unprobed-20261030/c8-alt18-19-{resistors,repeat-five}-001/.
WROOM NOW v9/18-19; the earlier preparation and v3 entries below are history.

PREPARED, NOT INSTALLED — Author proposed different WROOM pins. Off-device
v9 variant built on Oryx in build/zdi-alt-pins-20261030/: GREEN clock GPIO18,
BLUE data GPIO19. Exact v8 source transformation changes only26->18,27->19
and banner version; signaling/timing unchanged. Existing WROOM remains v3 on
GPIO26/27. Host identify_unprobed.py now supports --pins18-19 with an exact
v9 banner guard and corrected output-enable/input masks. No board firmware
or wiring changed during preparation. Author must power off both boards to
move wires; confirm GREEN at C8 CLOCK pin4, BLUE at C8 DATA pin6, since the
earlier swap was not reported reversed. No automated target programming.

LATEST — Author requested five identical direct-wire reads. Replies vary:
C6 7F FF FF; FF FF FF FF; FF FF FF FF; FF 88 1E 62. Trial4 additionally fails
local driven-bit input check, so stopped before fifth read. No resets between
reads. Both outputs released, GREEN HIGH/BLUE LOW, serial closed; no target
reset/halt/RAM/flash. Pi/Oryx evidence:
build/zdi-unprobed-20261030/c8-direct-wires-repeat-five-001/.
No resistors; preceding Author GREEN/BLUE swap not reported reversed.

LATEST — Author bypassed both series resistors; no reversal of the preceding
GREEN/BLUE swap reported. Direct-wire Console8 check still fails on first read:
C6 7F FF FF,13 local drive checks pass. Outputs released, both local inputs
HIGH, serial closed; no target reset/halt/RAM/flash. Evidence Pi/Oryx:
build/zdi-unprobed-20261030/c8-direct-wires-001/. Physical endpoints remain
unverified; do not assume standard color/function mapping has been restored.

LATEST — Author swapped GREEN/BLUE and requested repeat. Console8 identity
still fails: first read FF FF FF FF, all13 WROOM local drive checks pass.
Stopped, outputs released, both inputs HIGH, serial closed. Physical wiring
remains AUTHOR-SWAPPED; do not assume the prior color-to-function assignment
is restored. No target reset/halt/RAM/flash requested. Evidence on Pi/Oryx:
build/zdi-unprobed-20261030/c8-swapped-signals-001/. See the comparison in
[the C8 record](docs/c8-zdi-unprobed-2026-10-30.md).

LATEST — Console8 direct Oryx USB, no signal probes,2026-10-30: Author powered
Console8 after initial discovery found it off. Both board USB bridges now
enumerate directly; WROOM remains quiet original identity-only v3. First slow
identity returns F8 10 3E 46, invalid;13 local drive snapshots pass. Stopped
after that read, Q/P confirm both outputs released, GREEN HIGH/BLUE LOW;
serial closed. No target reset/halt/RAM/flash operation requested. Probe
removal solves Olimex identification but has NOT solved this Console8 link.
Raw receipt/transcript/runner copied and hash-checked on Pi/Oryx. See
[the unprobed C8 record](docs/c8-zdi-unprobed-2026-10-30.md). Console8 remains
unrecovered; no blind programming. Next physical comparison is TRY-003,
retaining the no-probe setup. P4 normal restoration remains deferred.

LATEST — Pi5 Olimex probe-control campaign,2026-10-30: Author authorized tests.
Current WROOM is exact original quiet v3 (SHAabaa0bc...84fd9), NOT v7/v8.
Both signal outputs released; GREEN/BLUE HIGH, serial/capture closed. Actual
GREEN/BLUE signal wires and33ohm resistors unchanged. ALL FOUR SNIFFER SIGNAL
PROBES DISCONNECTED; sniffer ground/USB retained. No Agon flash/reset requested.
No-probe result20/20 exact07 00 AA 1C. Two-probe tests pass in places but remain
intermittent; adding RED alone gives0/5. Measurement attachments perturb link,
mechanism unresolved. TRY-001/002/005 complete; see
[the campaign](docs/olimex-zdi-control-2026-10-30.md). Console8 is not tested here
and remains unrecovered. Await Author Console8 handback for minimal-probe ID
checks before any RAM/flash gates. P4 normal restoration remains deferred.

CURRENT HANDOFF — 2026-10-30: Author requests notes, commit/push, then wait
until they are ready for further tests. Do not run the queued diagnostics now.
TRY-001..TRY-006 are recorded in TODO.md with detailed scope in
[the next-test document](docs/tasks/C8-ZDI-next-tests.md).
Latest completed evidence: [four-probe diagnosis](docs/c8-zdi-four-probe-diagnosis-2026-10-29.md).
WROOM remains quiet identity-only v7, both outputs released. No C8 recovery
flash occurred; MOS remains unrecovered and P4 normal restoration is deferred.
Canonical probes: D0 GREEN/C8 clock, D2 BLUE/C8 data, D5 RED/WROOM clock,
D7 BROWN/WROOM data. The BROWN=D3 assertion in the older entry below conflicts
with the Author-confirmed map; preserve it as history, not current authority.
See [the audit](docs/audits/sniffer-color-audit-2026-10-29.md).

Historical entries below are retained unchanged.

LATEST C8 / ORYX, 2026-10-29: WROOM is directly on USB; Console8 and the
analyzer share a hub. User removed the two added probes; physical red maps to
D5, physical brown maps to D3, not the assumed D7. Do not treat the earlier
hypothetical D5/D3 comparison as verified resistor endpoints. Separate-register
reads fail as well as block reads. DATA B/O/B/O driver comparison also gives
0/5 valid per phase; open-drain adds some sustained bad levels and is not a fix.

Current WROOM is identity-only v6, app SHA256
42fe5a152d6b59ea195e8005f87f8e5167bb05190883c74f56b6a699acff66cd.
Source: experiments/zdi-wroom-diagnostic/. O/B selects DATA open-drain/push-pull;
clock stays push-pull. The reviewed handler changes pad_driver with output
released, preserving input/pull-up. Baseline push-pull/CAP2 is restored.

Author reset Console8 with WROOM clock held HIGH and DATA released. DATA idle
changed LOW to HIGH, but five subsequent reads repeat exactly the same invalid
five replies as the initial C8 run. Reset alone does not fix communication.
Author then moved ORIGINAL green/D0 to Console8 connector pin4 TCK and blue/D2
to pin6 TDI; actual wiring/resistors/grounds unchanged, added red/brown absent.
Connector-side five-read capture also fails, with 225 clock rises/falls and
92 DATA transitions. Independent settled inspection: 16/65 DATA bits wrong throughout +/-5us at
connector, while all65 WROOM local input/output/enable snapshots match command.
Ten intended LOWs observed HIGH, six intended HIGHs observed LOW. Reply bytes
match software throughout. Leading next checks: resistor value/contact/loading
or opposing drive; no specific component fault established. Asked Author for
resistance of both series resistors (boards OFF, one end disconnected), or band
colors. Author answers 33 ohms. Next pending physical check is complete powered-
off paths, resistors reconnected: Author reports both intended signal paths
measure33ohms. Cross-signal measurements are18.6kohms (Agon blue to WROOM
green) and17.96kohms in the opposite cross-combination. These are in-circuit
measurements; not evidence of a direct short or a precise intersignal resistor.
Author reports ground-to-ground has 'perfect continuity'. All intended paths
therefore pass the powered-off check; this does not measure powered ground
offset or isolate a dedicated lead from parallel USB returns. Asked Author to
restore power, keep meter black on C8 ZDI GND, and report DC volts at WROOM GND,
WROOM3V3, WROOM BLUE, and C8 BLUE. Author reports0V,3.3V,3.4V,3.4V respectively.
These are quiet idle readings: no substantial measured ground offset and BLUE
agrees HIGH at both ends. They do not establish driven/dynamic signal quality.
Author says USE COLORS: GREEN=clock, BLUE=data, both boards. See AGENTS.md.
WROOM v5 boots quiet with both GPIOs released. Preparing a brief bounded driven-
LOW control, avoiding a long push-pull hold against an unresolved target driver.
v6 now installed/verified in WROOM app0. C does max5 short BLUE open-drain LOW
pulses with GREEN held LOW, then releases/restores everything before printing.
First C source checks all pass (2/0/2), but NO passive capture was obtained:
sniffer USB is absent (confirmed lsusb/scan/kernel log). First host runner sent
C before noticing missing analyzer; evidence c8-line-control-01 is an INCOMPLETE
capture, not an end-to-end pass. Author reconnected sniffer USB. Guarded02 sends
no C while FX2 cold firmware reloads. Readiness-checked03 captures2M samples at
1MHz: BLUE already LOW throughout, so C aborts at0pulses; GREEN LOW222us only.
C01 post-control P had both lines HIGH. Sniffer loading/state remains unproved.
NEXT PENDING AUTHOR ACTION: keep all powered, remove ONLY BLUE sniffer probe
from C8 BLUE signal; actual BLUE interboard wire/GREEN/grounds stay connected.
After confirmation run prepared c8-blue-status.py (P only, no requested reset
or pin changes). Do not retry identity/control first; preserve this comparison.
Both signal GPIO outputs released, no serial owner/polling. No C8 flash.
Evidence: build/c8-zdi/c8-{both-added-disconnected-01,baseline-single-register-01,
data-mode-compare-01,park-for-reset-01,after-manual-reset-01,connector-five-01},
Pi/Oryx. No target programming requested. Final Q, both WROOM pins released,
serial closed/no polling. Stock MOS repair remains incomplete; P4 restore deferred.

LATEST C8/ORYX, PROBES WROOM-SIDE: Author addedsniffer,still0/5valid. Detailed
capture shows narrow41–83ns DATAglitchesatCLOCKrise, not persistent wronglevels;
all65 transmitbitscorrectat±1us. Prior 'corruption' wordingneeds thisrefinement.
Author confirmsprobesBEFORE33ohmresistors; Olimexprobeplacementuncertain.
Privatev4 nowinstalledWROOMapp0 SHA256
8ed6a8f980fae4973461e1a22b76683b853b213cb6d4d53ac788d2756cf731e8.
R/L/R/L drivecomparison0/5each; weakdriveWORSE(sustainedbadlevels). WeakI
individualreadsrepeat07 08 E0 83; becauseaddressesbad,thisdoesnotisolateblock
incrementfailure. Source/commandsinexperiments/zdi-wroom-diagnostic/.
NOW restoreddefaultCAP2(R),thenQ,bothpinsreleased,serialclosed,no polling.
NoC8flash/resetoperation. PendingAuthor USBhubhypothesis: WROOM+sniffershare
hub5-1,C8direct3-2; no railvoltagemeasurement. Proposed controllednextstepmove
ONLYWROOMUSBto directOryxport,keepresistors/probes/signalsfixed. Thenrepeat
five slowreadsv4, noautomatic firmwareprogrammingwithoutstableidentification.
Evidence c8-damped-sniffer-five-01/glitch-review.json,c8-drive-compare-01,
c8-v4-installed-01 onPi/Oryx; devlog2026-10-29 hasfullscope/caveats.

LATEST C8/ORYX STATE: Author moved C8+resistor-equippedWROOM toOryx, no sniffer.
Same v3 probe gives0/5slow,0/10medium,0/10fast valididentities. Slow65drive
snapshots allmatch commandedbits; no wire-level capture available. One host
READY-boundary abort is retained separately; corrected RESULT-boundary runner
completesboth10-readsets. Evidence: build/c8-zdi/c8-damped-20261029-{identify,
speed,speed-02}, Oryx/Pi. No C8 firmware/reset operation; repair NOT attempted.
WROOM remainsquietidentity-v3, Q/pinsreleased, serialclosed. Next dependency:
attach passive sniffer toC8/Oryx tocomparephysicalsignal and effectofprobe
loading; previous5/5successwasOlimexWITHsniffer. Otherground/pinchoicesretain
Author's confirmedwiring. P4 normalrestore remainsdeferred.

LATEST SUCCESS, 2026-10-29: after the Author's next physical adjustment,
same five slowT probes ALL return07 00 AA 1C (product0007/revAA/status1C).
Sniffer confirms5/5 exact matches, correct45clock framing/address/separators;
all65 driven-bit samples match commands. Evidence: today's sniffer build/
olimex-repeat-five-02. Author confirms the preceding change was adding33ohm
in series on BOTH signals, near WROOM. This damped setup passes5/5 versus the
previous undamped failures; long-run/other-rate tests remain pending. Only slow
identity reads on Olimex are now proven, not other rates or Console8 recovery.
WROOM remains quiet identity-only v3; both pins released, serial closed.
No target flash/reset was sent. Previous speed-failure state below is history.

LATEST SPEED COMPARISON, 2026-10-29: Olimex/WROOM/sniffer reconnected with
grounds confirmed. Same v3 session S/M/F/S,10reads each:0/40valid. Measured
reply clocks48.29kHz/328.77kHz/3MHz/48.29kHz; request corruption remains all
rates. Fast software sampling additionally disagrees with physical rising-edge
data; slower captures/software agree. Exact unmodified Jeroen application was
then installed/verified as control on same wiring: threeZDI-down messages at
about2.4MHz, no menu/identity. Its startup clears debug/breakpoint controls;
no recovery option, target reset or target firmware programming was requested.
Restored/verified quiet identity-only v3 afterward, SHA256
abaa0bc98876389f14a2f92a47115a5e95a5009dd1975f61a026d74978984fd9.
Both pins released/pull-ups, no polling, serial closed; physical wiring remains
Olimex+WROOM+sniffer. No Agon firmware write. Full details/evidence in today's
devlog and sniffer build/{olimex-speed-compare-01,upstream-control-01,
quiet-restored-01}. Increasing clock rate did not recover reliable communication.
Prior sniffer-only state below is history. P4 restoration remains deferred.

LATEST PHYSICAL STATE: Author disconnected WROOM; Olimex ZDI is connected only
to passive analyzer (greenD0clock, blueD2data, commonGND). Four seconds24MHz
capture confirms BOTH lines continuously HIGH, zero transitions/LOW samples.
Evidence: build/c8-zdi/olimex-idle-20261029/idle-01.{bin,json}. WROOMUSB absent.
No serial port/reset/target command used. Earlier connected state below is history.

LATEST REPEATABILITY RESULT: five identical slowT reads in one serial session
give five different invalid replies; no resets between trials. Sniffer confirms
four exact byte matches and an extra clock edge in the fourth frame. Driven-bit
mismatches recur; corrected ground did not establish lasting resolution.
Evidence: build/c8-zdi/wroom-20261029-sniffer/olimex-repeat-five-01.
WROOM v3 nowQ/quiet, both pins released, serial closed. No target flash/reset.

GROUND CORRECTION: Author found OlimexGND andRESET still connected toPi;
GND now goes toWROOM andRESET is disconnected, probesunchanged. Fresh single
slow read olimex-ground-fixed-01 has all13drive samples correct and correctly
framed address00/READ, but reply01 03 F0 E0 remains invalid. WROOM parkedH
again (park-high-02); await manual OlimexRESET with WROOMpowered, then retry
single read. No target flash/reset sent. Earlier drive conflict is absent in
this corrected-ground observation; reason for remaining bad reply unproved.

LATEST CONNECTED STATE, 2026-10-29: WROOM and sniffer are connected to Olimex
on Pi5. Author confirms exact previously successful ZDI wiring and viewing
orientation: notchTOP, uppermiddleGND, lowerleftblue/TDI, lowermiddlegreen/TCK.
Use docs/images/zdi-operator-view.svg for both Olimex and Console8.
Slow connected identity reads remain inconsistent. A single v3 traced request
confirms data input sometimes disagrees with commanded output even with output
enable set. Physical cause remains unproved; do not declare an Agon board fault.
WROOM now has identity-only v3, SHA256
abaa0bc98876389f14a2f92a47115a5e95a5009dd1975f61a026d74978984fd9.
No target firmware/reset operation occurred. WROOM is parkedH: clock driven
HIGH, data released, both input levels HIGH, serial closed. Await deliberate
manual Olimex reset, then a single slow read without resetting WROOM first.
Evidence: today's sniffer build/{olimex-connected-01,drive-test-01,park-high-01};
details in docs/devlog-2026-10-29.md. Older v2/disconnected state below is history.

LATEST WROOM DIAGNOSTICS, 2026-10-29: WROOM is now on Pi5, connected ONLY to
the passive logic analyzer; Author explicitly confirmed Agon disconnected.
Canonical green/D0=GPIO26/TCK, blue/D2=GPIO27/TDI; earlier swapped capture is
explained by Author. GPIO self-test passes, including data-pin local input.
Upstream recovery executable and bundled files verified intact; twelve changed
OTA metadata bytes explain whole-flash digest mismatch. Full incoming flash
readback retained on Pi/Oryx. No target firmware operation was performed.

CURRENT WROOM IMAGE IS IDENTITY-ONLY DIAGNOSTIC v2, app SHA256
3ba3b05424e82764498f50d8f2d59cd4ae2323dbcf97cd602f2823da491963f5,
not upstream recovery. It has no MOS payload, flash/halt/control writes or BOOT
shortcut. Both pins are released with pull-ups, no polling, serial closed.
H=clock HIGH idle, Q=release, S/M/F=ten identity reads with10/1/0us delays.
Disconnected control: slow/medium allFF, fastest all1F internally sampled;
analyzer confirms30 correctly framed read requests. This establishes settling
on the weak-pull-up disconnected line, NOT the reason for previous Agon failures.
Next dependency: Author reconnect Olimex+commonGND (retain probes if practical),
then a fresh slow identity/reply capture. Evidence, source and interpretation:
docs/devlog-2026-10-29.md, experiments/zdi-wroom-diagnostic/,
build/c8-zdi/wroom-20261029-sniffer/. Do not run old recovery-menu scripts against
this diagnostic. P4 recovery firmware remains installed; N-009 repair pending.

WROOM INSTALLED AND ISOLATED STARTUP PASSED, 2026-10-28: after the Author
changed USB connection, CP2102 enumerated and esptool confirmed the exact
historical WROOM MAC/chipESP32-D0WD-V3/rev3.0/4MiB. All GPIO remained
disconnected under the operator handback. Incoming4MiB flash was preserved on
Oryx and Pi, SHA256c36ad97a269b1cc32ee1d16b0a947a37a44292b8f4f38d8ec5c9db2515fe622e,
and verified against hardware. Unmodified upstream recovery image was installed;
the expected complete4MiB composition passes flash-digest verification, including
the unchanged last64KiB. A bounded zero-input startup capture has two expected
"ZDI down - check cabling" messages, no application fault. No Agon operation
was performed. The reader is closed; recovery firmware is running on WROOM.
Evidence: build/c8-zdi/wroom-20261028/{installation,startup-isolated}, both hosts.
Next Author action: power off WROOM and Console8; move the three P4 leads to
WROOM26/TCK(existinggreen),27/TDI(existingblue),GND. Leave P4 disconnected from
ZDI; no power rails joined. Restore power and report ready for target checks.
Do not hold WROOM BOOT while its recovery app is running. P4 normal firmware
was not restored. N-009 MOS repair remains pending.

WROOM ROUTE PREPARED, 2026-10-28: the Author has the WROOM DevKit used by
Extender Legacy and directed us to its pinout. Legacy REFERENCE.md points to
the frozen agon-hardware-wroom-reference checkout, commitc200d97. Its
extender/docs/esp32-devkitc-pinout.md identifies a38-pin ESP32-DevKitC/WROOM-32D;
esp32-wroom-32d.md records4MiB flash and ESP32-D0WD-V3. Use silkscreen26 for
TCK(existinggreen),27 for TDI(existingblue),GND for targetGND. No power-rail join.
First operator step is WROOM USB ONLY on Oryx, with GPIO disconnected, so its
incoming firmware can be replaced before moving any target leads. Do not wire
an old Extender image to Console8 as if it were recovery firmware.

Unmodified Jeroen upstream recovery firmware is prepared on Pi/Oryx under
build/c8-zdi/wroom-20261028,4128768 bytes,SHA256
15f6fa8a0ebe7363809a51597c69ea328994065d6d207ca74583e956a46de091,
offset0, matching both official web-installer and pinned repository bytes.
It bundles MOS3.0; stock3.0.2 remains available for normal update after recovery.
Startup clears debug/breakpoint registers and repeatedly probes ID; it does
not erase/program on boot. Serial option2/Y or a running BOOT-button hold over
2seconds starts MOS programming. No WROOM hardware operation has occurred.
Oryx's last read-only check had no /dev/serial/by-id directory. P4 standard
restoration remains deferred. N-009 continues; earlier P4 research is below.

RESEARCH UPDATE, 2026-10-28: the Author requested Internet research only; no
hardware was accessed in that research turn. Revise the simple power-cycle
dependency below: Zilog PS0153 Table110 says TCK sampled LOW during RESET
selects OCI/JTAG, HIGH selects ZDI. Both ZDI signals should be deliberately HIGH
or released to verified target pull-ups throughout a controlled target reset;
do not clock ZDI during reset. The present failure is NOT proved to be this
mechanism. Zilog TN0035 also recommends tristated idle drivers and short/good
ground connections. P4 output-high signals can feed an off target rail through
the C8 pull-ups, so target-only power-off with driven lines is not a clean
power-cycle experiment. This is a circuit-based inference, not a measured fault.

Jeroen Venema (envenomator) maintains AgonPlatform/agon-recovery. Its ready
firmware targets classic ESP32/esp32dev, not P4. A classic WROOM DevKit with the
upstream utility is the documented Console8 fallback, avoiding our P4 port.
It needs three wires and MOS-only recovery option2. The bundled MOS is3.0
(upstream commit95d68464); our selected stock3.0.2 payload must be deliberate.
His unlinked console8_zdi_pullup.png shows two10k pull-ups, but C8Rev2 already
shows R92/R93,10k to3V3, on its schematic. Do not assume missing resistors or
add them blindly. Detailed source links/research are in today's development log.

LATEST N-009 STATE, 2026-10-28: repair is NOT complete. No DUMP, target halt,
RAM upload, erase or MOS programming was reached. The stock-payload programmer
compiled and its application was installed/verified, but initial native startup
faulted before ZDI (Arduino NVS access with the startup stack in SPM). A16KiB
main-task stack corrects startup. The next build reads C1E0/83/83 and refuses;
explicit1us ZDI timing padding reads C1E0/84/83 and refuses. The timing hypothesis
is NOT established. The previously successful original programmer was then
reinstalled/verified as a read-only control: it ALSO fails, with7878/78/C4.
No further attempt followed that control refusal. The new build alone does not
explain the changed identity; wiring/target state remains unresolved.

CURRENT P4 is the original maintained RECOVERY application SHA256
0f609f95e0e8aae5f1a98de78d5d6476127e3e62682fbb65e09f1382da94191b,
NOT standard Extender firmware. Its embedded Olimex EMOS must NOT be armed on
Console8. The original16MiB P4 backup remains retained; standard firmware was
not restored. Prepared stock-payload application SHA256
56507082e09e2e189448a1ee3ce89deb2c7223a4bfd02e5a0c0600f4b8b9e616
is retained on both hosts under build/c8-zdi/repair-20261028 (Pi: returned/).
Next dependency: Author full Console8 power cycle, keeping P4/wiring in place,
then a fresh identity check. No remote eZ80 reset actuator is connected; do not
substitute a VDP/CP2104 reset blindly. Raw attempt receipts/logs are copied to
Pi. No active serial reader remains. N-009 remains unfinished.

REPAIR AUTHORIZED, 2026-10-28: the Author confirmed switched P4 wires caused
the initial identity refusal, then explicitly directed this agent to repair MOS
without another backup-only handback. N-009 now owns the target repair. Selected
known-good stock MOS3.0.2 is108490 bytes, SHA256
d564243283972690933a4554296ad6202ca4ef54572279533a942960846bebae.
The identification programmer contains an Olimex EMOS payload and must NOT arm
that payload on Console8. A private stock-payload build of the unchanged
maintained recovery algorithm is compiling on Oryx under
build/c8-zdi/repair-20261028. The maintained pre-write readback/full post-write
comparison are internal execution steps, not a separate Author task or gate.
P4 restoration stays deferred until MOS repair is complete. These instructions
supersede the earlier separate-authorization requirement below.

RECOVERY STATE, 2026-10-28: N-008 identity check PASSES after the Author's
"try now" instruction. A fresh P4-only startup capture records three consistent
product 0007/revision AA/status 1C reads and WAIT DUMP. This establishes the
functional ZDI identity path; no DUMP, RESTORE, target halt or flash write was
sent. Programmer stays installed. Capture/result (Pi and Oryx):
build/c8-zdi/identify-20261028/startup-ordinary-02. Earlier refusal below is
preserved history, superseded by this successful check. Further MOS recovery
requires a selected payload and separately authorized dump/repair operation.
The unarmed programmer may time out; do not assume this gate stays live.

The Author explicitly authorized the Oryx P4
backup/programmer installation and three read-only ZDI identity reads (N-008).
This narrowly supersedes the older no-board-access hold below. The full 16 MiB
original P4 flash was backed up, verified against the device and copied to Pi;
the recovery programmer was installed and its full flash composition verified.
The initial passive capture was empty. A corrected capture, open before one
P4-only reset, proves the programmer boots but reads product FFFF, revision FF,
status FF and refuses at its first identity gate. Expected product/revision
is 0007/AA. No working ZDI connection has been established; no automatic retry.
No DUMP or RESTORE command was sent and no Agon erase/program was attempted.
The Author then directed: DO NOT RESTORE THE P4 STANDARD FIRMWARE UNTIL MOS
REPAIR IS COMPLETE. Leave the recovery programmer installed, including after
failed identification. Original backup: build/c8-zdi/identify-20261028/
p4-before-16MiB.bin, SHA256
e479ca9d667e25f1c53f69e1553dd78b2de2d319336130114c97ba0f3155a76f.
At the preceding failed attempt, N-008 awaited a powered-off connection check:
Author-reported blue/TDI must reach P4 GPIO47 (EXT2 pin6), green/TCK must reach
GPIO46 (EXT2 pin7), with common ground. Do not guess Console8 connector positions
from schematic numbering. All-ones reads do not identify which lead or target
condition is responsible. Capture/result: build/c8-zdi/identify-20261028/
startup-ordinary-01. Target MOS recovery needs separate authorization.

HARDWARE HOLD,2026-10-16: the Author reports that flashing the native MOS
candidate left Console8 unable to boot MOS. The updater counted down but did
not reset; manual reset and two power cycles show only the VDP banner/cursor.
Candidate SHA2565543d6acaa64bebd3006cb034a8dda9b61cfe92c82cbbffe2c391a9392f0f4c9
is withdrawn from hardware readiness. Earlier software PASS/deployment records
are historical evidence, not authorization to flash it again. The Author and
Extender agent own recovery; this agent must not access boards or the card.
N-007's off-device audit is complete: the native C multiplication overflow
programs UART0/UART1 divisor 11 instead of 1 at the VDP boot rate. The same
defect exists in the clean native foundation. Both routines now widen before
multiplication; old images fail the same actual-instruction test that the
correction passes. Corrected uart-012-boot-audit is 104636 bytes, SHA256
680daf76d6a0e4073f43130fda48fdcf681a4570ac709f99dd3c9e04335e6e79,
ROM CRC4E326ABC. It remains OFF-DEVICE. N-006 holds replacement packaging,
fresh review and physical acceptance; no deployment/recovery is authorized.
Boot/startup checks, root/source checks, actual-ROM sender scenarios and both
complete Flexe campaigns pass. No additional defect was found in the reviewed
UART hooks. There is no physical flash readback, so an additional write failure
is not excluded. Preserve all original evidence and the withdrawn package.
Deploy/packaging tools now reject the old image. Full audit and receipts:
experiments/uart0-native/BOOT-FAILURE.md and incident.json. The earlier staging
instructions immediately below are HISTORICAL and must not be followed.

Latest Console8 deployment,2026-10-16: the Author's native emulator screenshot
shows four PASS cases, NATIVE UART REVIEW COMPLETE and typed DIR. The Author
authorized SD deployment. Guarded native package is verified at the SAME
/test/mos-uart0/test.bin on unique AGONC8 UUID8658-1C23. Root MOS.bin and
autoexec.txt, all existing numbered/operator reports and runs.log are unchanged.
Next run0030. Other BMOW media was not touched. Physical firmware is not flashed.

This is a NEW native MOS, not a branding-only update. Menu9/3 backs up installed
MOS;9/1 flashes mos-candidate.bin. Require Arthur - UART0 OTIRX EXPERIMENTAL
ABI1.2 and installed ROM CRC5B36B5B1. Menu9/7 installs supplied vdp-rx-fixed.bin;
confirm RX sync candidate banner after reboot. Then menu3 runs the reviewed
native16-byte fixture; repeat once for fresh numbered output. Optional1/6 are
diagnostics/compatibility;0 excludes old ABI1.1-only investigations for native
MOS. Old8 investigations are not this native qualification. Menu9/4 restores
supplied stock VDP2.16.0. Short on-card readme contains exact LOAD/RUN commands.

The menu now recognizes UBD1 with its FF reserved bytes, gates it on the exact
native image/API and retains per-run filename patching. Both engines pass
3,3,6,1,2 through actual FAT with the same repaired no-timing/rescue VDP staged
on card. Source/firmware companions and licenses are adjacent to the fixture.
New host native-return reader verifies journal/binary agreement and excludes
old runs; old Ruby stress reader retains default-zero padding and explicitly
accepts the native convention through package metadata. Both formats and a
corrupt-padding control are checked. Menu keyboard code is unchanged.

Predeployment166-file snapshot is SHA-verified on Pi/Oryx:
build/uart0-native-card-before-20261016.tar.gz, SHA256
e6578df1aec00c33e60c22082c619098b91efe3d55c4214b2e06fd13879f8d55.
Final deployed manifest SHA256
88b5f07621e9fcb1df98ada16123e044192a15af3a34ced74067cb1357ae23ff;
deployment/verification: build/uart0-native/deployment{,-final}.json.
Preparation scripts: experiments/uart0-native/{package_hardware,finalize_hardware,
check_hardware_menu,inspect_hardware}.py. The new native/MOS/menu work remains
uncommitted; no new commit approval is inferred from deployment. N-006 awaits
the returned physical reports. Older stop/no-card notes below are superseded.

Latest native implementation,2026-10-16: regular MOS source is implemented and
software-qualified in our own isolated agon-mos worktree
/Agon/mystuff/worktrees/uart-native-001/uart, branch codex/uart0-otirx-native.
The Author authorized full OTIRX and regular MOS implementation after committing
and pushing existing work. Checkpoints: agon-mos d4569e8; isolated EMOS assessment
e147549, both pushed. New implementation/profile changes remain uncommitted
pending the canonical human emulator review and explicit commit approval.
EMOS remains deferred. No card, physical firmware or graphical launch occurred.

Foundation/interface ab95feee301d2cd40470cf2bda85a0fe1c3c008e; infrastructure
49dc33fee817cb184572351ee71dae7da9a139c4. Both owner's sources remain untouched.
Regular byte-exact canonical exports are under native src/shared-api; forwarding
includes and C/C++ overlay consumers use them. No private global IDs;13h is the
two-stage UART discovery,12h remains null/retired. No qsort public experiment.
Normal builds use maintained GNU assembly directly, with no dialect translator.
The original ZDS tree here is the frozen reference, not the new build root.

Clean native stock reproduces102055 bytes/SHA256
f891721bbb2a0bc2845dbb13edbeb449365a315f11be48500d8e65e2ab1aebb4.
Final native branded ROM104658bytes/SHA256
5543d6acaa64bebd3006cb034a8dda9b61cfe92c82cbbffe2c391a9392f0f4c9,
from uart-010-final on Oryx. Its bytes equal tested uart-009-final. UART-only
cost2569 ROM/86 RAM; branding adds34 ROM. Core2497bytes/300 relocations match
the frozen encoding oracle exactly. Root shared/runtime/layout/stack/provenance
and product linked-image checks pass, including corrupt-image controls and
canonical C/C++ compilation. Nine source checks pass. Independent actual-ROM
runs cover policy/descriptor/address boundaries and intended fault controls.

Both Flexe engines complete CRC and full-duplex campaigns using actual native
MOS, actual FAT16 and privately compiled repaired diagnostic VDP. Per engine:
40960 CRC bytes,163840 final-buffer bytes compared,640 ordered replies, zero
TX drops/RX overruns. Intermediate stress buffer contents are not individually
receiver-compared. Original failed-validator receipts are retained: reserved
FF padding was wrongly treated as error flags. validated-receipt.json correctly
interprets the raw successful runs; corrupt report/wire controls are rejected.
The native stress client now drains before changing policy; a no-drain control
proves the prior setter BUSY status1. No driver rule was weakened. Initial
deadline and masked-IRQ harness failures remain in the archive history.

Details/results and reproduction: experiments/uart0-native/README.md/results.json.
Raw final runs: Oryx build/uart0-native/flexe-{jit,interp}-fixed2. Complete archive
is build/uart0-native-evidence-20261016.tar.gz; archive.json/verification records
its final checksum and verified Pi copy. Original .pio diagnostic build,
toolchain, exact native working source/API exports and all failed attempts are
included. Archive closeout follows its snapshot in the development log.

Stopped human review on Oryx:
cd ~/Agon/mystuff/worktrees/uart-native-001/uart/.emulator/uart0-review1
./flexe-agon-emulator --precise-interrupts
Expect experimental branding, four progressing batch16 pause/full-duplex cases,
UART0 STRESS FIXTURE PASS and NATIVE UART REVIEW COMPLETE, then usable help/dir.
Allow about two minutes. No generic-foundation probe/reboot drill is required.
Only TODO.md is actionable; N-005 holds review/commit approval. Remaining BT/AB
menu integration, native hardware acceptance, supported policy, application
integration and release approval are still open. Leave the Console8's
other-project VDP alone. Older entries below are historical, not new authority.

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
