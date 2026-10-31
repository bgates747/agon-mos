# Console8 stock recovery: original Jeroen protocol attempts

LATEST: the Author subsequently explicitly removed all target readback checks
and requested a blind flash, with monitor boot as validation. Run-009-blind
completed MOS upload, flash-tool upload, execution command and ten-second wait.
The Author has been told to power-cycle Console8 and check the MOS banner.
No boot outcome yet. The checked attempts below remain historical failures;
their no-flash outcome must not be confused with the later blind execution.

The Author explicitly ordered stock MOS flashing, removal of the nonstandard
program-counter check, and use of Jeroen's original recovery protocol instead
of further custom diagnostics. That instruction supersedes the earlier custom
probe/recovery preparation. Do not resume those diagnostic admission gates.

## Outcome

**MOS has not been flashed.** The normal upstream recovery routine was invoked
with MOS-only menu2 and confirmationY. It uploaded MOS to eZ80 RAM, then printed
`CRC32 ERROR` and returned before the flash-agent upload/execution. This occurs
with both the slower signaling attempt and the final byte-identical upstream
ZDI driver. It is the original routine's uploaded-MOS verification failure,
not an added PC or RAM-parameter admission check. Do not claim an erase,
successful stock write, full-flash readback, recovery or successful boot.

The final raw transcript includes:

    Recover MOS (y/n)?
    Uploading MOS........................................................ done - CRC32 ERROR

No `Flashing MOS...` phase or `CRC32 OK` occurred. The final display's literal
`ZDI up - id 0x7F7F, revision 0x7F` is an inherited menu label, not evidence
of valid identification. The serial front end deliberately exposes the menu
despite invalid status, under the Author's explicit force-recovery instruction.

## What was used

Original AgonPlatform/agon-recovery commit
95d68464afd049945e1dfd780c1c07621d565450, complete source and README fetched
into a private project workspace. No upstream checkout or SDK was modified.
The complete upstream source was needed because the earlier retained snapshot
omitted headers and message.cpp.

Final source verification proves these are byte-identical to that commit:

- src/zdi.cpp, the complete signaling driver, with no added edge delays.
- src/cpu.cpp and the flashMOS(), init_ez80(), getZDImemoryCRC() function bodies.
- data/flash.bin, the original90byte flash tool.

Board/UI adaptations are explicitly separate from those recovery functions:
GREEN clockGPIO27, BLUE dataGPIO26; WROOM input sensing enabled; serial-only
front end without VGA/PS2 peripheral startup; normal menu2/Y exposed without
blocking on the status display. The only programming checks are those already
inside the original flashMOS routine: uploaded-MOS CRC, then final flash CRC.
The latter was never reached. Final source verification is retained verbatim.

Stock MOS3.0.2 payload108490bytes, SHA256
d564243283972690933a4554296ad6202ca4ef54572279533a942960846bebae,
referenceCRC32 15BD0583. The filesystem contains MOS.bin and the upstream
flash.bin. Both SPIFFS and the application were uploaded to the WROOM CP2102
serial0001, MAC40:22:d8:76:01:c8. Console8's CP2104 port was not used for
programmer uploads. No sniffer is attached and no target reset was requested.

## Attempt accounting

The earlier custom r03 preparation removed PC checks but still stopped at an
added RAM-parameter comparison. It was not the final requested original path
and is superseded. Its source and failed raw log remain intact.

Original-utility attempts retain sequential logs, including failures:

- run-001: app was still customr03 because the combined PlatformIO upload and
  uploadfs targets uploaded SPIFFS twice. Interrupted before menu input; corrected
  with a separate application upload. Original logs preserved.
- run-002: complete original utility, pin constants only; ZDI down/no menu.
- run-003: WROOM input initialization; transient menu, then ZDI down before
  accepting option2. No confirmationY or programming stage.
- run-004:1us edge settling; ZDI down/no menu.
- run-005:10us settling and input setup after peripheral initialization;
  ZDI down/no menu.
- run-006 was a prepared serial-only intermediate build, not an executed run.
- run-007: serial-only exposed menu with10us signaling;2/Y, MOS RAM upload,
  original CRC error, no flash phase.
- run-008: same front end and byte-identical upstream signaling driver;
  2/Y, MOS RAM upload, original CRC error, no flash phase.

## Final state and evidence

WROOM is running the final upstream-based serial-only recovery utility, **not**
quiet identityv3/v10 or RAM-probev11. Boot constructs ZDI/CPU and writes their
normal initialization registers. Its original BOOT-hold recovery action also
remains; do not assume a BOOT press is harmless or that startup is passive.
The serial front end no longer repeatedly polls ID in its idle loop. No host
serial process or recovery script remains running. The driver leaves its pins
configured as upstream does; no claim that both outputs are released. CPU
break was requested by normal recovery, but target state is not independently
verified after the failed transfer. No bench change requested at the end.
Console8 remains unrecovered; P4 normal firmware restoration remains deferred.

Raw transcripts, build/upload logs, source, stock payload and compiled images
are retained on Oryx. Pi/Oryx verified archive:
`build/c8-zdi/jeroen-stock-20261030-evidence-r01.tar.gz`,376186bytes,
SHA2563835f91fa619d4f82ea8224a529ec14629d0391ad047e7361f10a3ec4649fbde.
The Pi independently reads the entire archive, checks its SHA256 and verifies
both completed original-recovery run transcript hashes and CRC-error outcomes.
Final unmodified-driver run console SHA256:
2fc6492821fa5364f2bf9b19248fb78c3fb1e1e9d7ea1829613159266350b311.

## Explicitly authorized blind write

The Author's subsequent instructions were to remove all checks because the
readback might be corrupted, then validate only by powering on with a monitor.
Removed both target CRC/readback stages and their gates; removed menu ID reads
and discarded CPU reads from SetADL. The path now sends writes only: normal
CPU initialization, stock MOS upload, size parameter, original flash tool,
PC assignment, continue command and the normal ten-second programming wait.
No target ID/status/PC/memory read transaction is used by that path.

Run-009-blind executed menu2/Y once and printed:

    Uploading flash tool....
    Flashing MOS............. done - BLIND FLASH SEQUENCE FINISHED - NOT VERIFIED.

This proves the host/programmer sent the sequence and finished waiting, not
that the eZ80 received/executed it or programmed correct bytes. Receipt
completed=true, blind_sequence_finished=true, flash_phase_seen=true;
passed=false explicitly means no success verification, not a reported CRC
failure. Monitor boot is pending. The Author was told to power-cycle Console8.
No further device operation was requested after completion. Current WROOM is
blind recovery mode, not the checked original mode; no host serial process
remains. Its upstream driver may leave outputs driven, and BOOT-hold can
repeat recovery. No sniffer is attached, no automatic target reset requested.

Raw log/result retained Pi/Oryx at
build/c8-zdi/jeroen-stock-20261030/run-009-blind/. Console SHA256:
ca69178d844dce8749de20bc76529228e064afccff8d9585ddfce0c368f78b05.
Earlier r01 archive predates this blind run and remains unchanged.
