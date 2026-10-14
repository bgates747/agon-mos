# Unchanged-VDP Console8 receiver-recovery campaign

Executive summary: this test asks whether the real Console8 stops receiving
under sustained traffic, before we propose changing its VDP firmware. It keeps
the previously tested MOS image and stock VDP. The short and extended campaigns
save progress and check received data. A pass covers the tested workload only;
a stall needs further evidence before we can call it the receiver race.

HW-001 preparation/return is complete; AB-006 in the sole TODO retains receiver
attribution and repair. The [plan](../../docs/uart0-hardware-recovery.md)
and [recent mail correlation](../../docs/uart0-mail-correlation-2026-10-14.md)
distinguish the traced emulator race, compatible Rally symptom and unrelated
Fsim P4/ExCom protocol failure. No peer firmware or runtime is changed here.

The C/AgonDev menu retains its stable entry and earlier tests. Option8 now opens
numbered controlled experiments:1 A/B,2 short recovery,3 extended,0 A/B then
short. Top-level run-all includes short recovery when recovery.bin is present.
Command-line `RUN . rx` / `RUN . rxe` is for headless automation. Internal report
test IDs10/11 distinguish short/extended; no RTC is used.

The native ZDS II child uses the installed public UART0 API1.1, no private UART
owner or vector, and no batching extension. Six cases compare stock-style
blocking and experimental per-byte async across64 back-to-back8192-byte buffer
overwrite packets,32 acknowledged256-byte duplex groups, and32 paced256-byte
append groups. Extended repeats all six cases four times. Sources are immutable,
including32 distinct duplex-token headers. Three descriptors pipeline bulk
sending; release, accepted counts and TEMT are checked before reaping/closing.

All cases verify the final8192-byte buffer using the existing stock-command
comparator, including its mismatch/match preflight control. The bulk case does
not verify intermediate overwritten buffers. Short checks49152 final bytes;
extended196608. Only one GP reply may be outstanding. Async duplex requires
observed replies while TX is still BUSY. No electrical CTS or exact cycle
measurement is claimed.

A608-byte URXHOST1 version1 report contains a32-byte state header and24 records
of24 bytes. Header: stage9,count10,completed11,active_case12,repeats13,
failure_code14,baselineRX15; u24 checkpoint_tick16,last_progress19,
last_accepted22,packets_completed25,wire_bytes28; byte31 reserved. Stage0 is
complete,1 setup,2 transmit,3 verify,4 case complete. Failure code3 denotes a
reply deadline,6 lack of accepted-byte progress,1 a generic API/integrity failure.
Every record stores mode/kind/index/RX/reply counts, elapsed raw ticks,
wire/accepted/packet counts,8192 verified bytes and a success marker.

The menu reserves sequential R/Y/Z/C names before starting the child. Native
header slots73/89/105 are16 bytes each; byte121 selects1 or4 repeats. Progress
is truncate/write/close saved before cases, each8 packets and verification
quarters. Failure saves retain active sources in a stopped loop when required;
a timeout never authorizes returning borrowed RAM. Blocking MOS calls can still
stall inside the call, so the operator's two-minute no-progress boundary and
saved checkpoint matter. MOS clocks are raw observations, not reliable RTC time.

`build.sh` stages native assembly and the C menu for Oryx ZDS II/Wine and the
already pinned AgonDev SDK. `profile.py` clones an already frozen MOS-owned
profile into a separate stopped instance, preserving old reports off-profile.
Its Golem VDP snapshot uses stock command APIs but is NOT the exact official
release binary. Native qualification verifies transcripts and received bytes,
sequential reports, and corruption/missing-reply controls. Any failed attempt
is retained; later passes do not repair the known receiver race.

Physical runbook is [readme.txt](readme.txt). The bundle includes the unchanged
experimental MOS file SHA256e7fc0732fba1ba6f94a30cc4bdab7e740c51a2b066cc35259f2abfc101fa848a,
official stock VDP2.16.0 and recovery/notice files. Physical128KiB ROM CRC32 is
239097B7; the same110695-byte image with the emulator's zero-filled tail is
2A87C5B5. Both fingerprints are explicitly recognized without assuming either
padding proves a physical installation. Hardware VDP identity remains operator
confirmation. No flash or root /MOS.bin replacement is performed by preparation.

Final fixture checks pass: short JIT54.847s and interpreter66.390s; deliberate
corrupt payload21.799s and missing GP reply46.292s both produce saved FAIL
reports. Real SDL menu input exercises short+extended together in218.457s,
checks all30 cases/245760 final-buffer bytes, returns to MOS, preserves an
orphaned Y0001 report and allocates runs0002/0003. These are Oryx wall times,
not Console8 estimates or CPU-cycle measurements. Physical timing is unmeasured.

The first draft's ROM identity guard incorrectly rejected emulator zero padding;
both known padding identities are now explicit. A packaging dry run caught a
missing VDP manifest declaration before card writes. Both attempts are retained
in the workspace archive; neither was a receiver failure.

The guarded deployment is verified on UUID8658-1C23 at the stable entry above.
All16 prior operator/report files, including runs.log, were preserved. Root
/MOS.bin is unchanged. Full previous deployment is archived off-card at
build/uart0-suite/before-recovery-20261014. Evidence/package/source snapshots
are in build/uart0-recovery-evidence-20261014.tar.gz on both development hosts.
The Author's physical short/extended runs R0006/R0007 are now verified PASS:
30 cases,245760 final-buffer bytes,5422080 workload wire bytes (excluding
setup/verification/display commands), zero case RX errors, and160 GP replies
observed while experimental async TX was BUSY. Binary reports and final saved
checkpoints match; detail logs agree with runs.log. All fixture hashes, earlier
reports and root MOS remain unchanged. See [physical-results.json](physical-results.json).
Read-only capture/analysis is archived on both hosts at
build/uart0-recovery-console8-r0006-r0007.tar.gz. `inspect.py` selects the unique
Console8 UUID, captures the owned directory off-card and validates the return.

Entry RX flags98 in both suite journals are retained as prior history, distinct
from native setup baseline00 and all case epochs00. No origin is attributed to
those entry flags. Stock VDP identity is operator-labelled, not read back.
No external hardware duration was recorded; raw ticks remain observations.
These workloads did not reproduce the stall; no rare-race exclusion, receiver
repair, new batching MOS acceptance or release qualification is claimed.
Human approval to commit new emulator-related changes remains outstanding.
