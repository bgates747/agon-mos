# Console8 stock MOS recovery — 2026-10-31

Stock MOS 3.0.2 was written through the WROOM programmer and passed Jeroen's
normal upload and flash-readback CRC checks. This is a verified programming
result, unlike the earlier blind attempts. The Author subsequently confirmed successful MOS boot (“praise jesus, it worked”).
MOS recovery is complete. No further remote target action is running.

The Author explicitly requested restoring MOS after the clean 1,000-read
Console8 identity control. Same Oryx-connected WROOM and proven direct wiring:
BLUE GPIO26/TCK, GREEN GPIO27/TDI, upper-middle ground, no inline resistors,
improved breadboard. No physical changes made by agent. P4 was not used;
its earlier results do not establish that every P4 implementation is unsuitable.

## Checks and resulting state

| Check | Expected | Actual |
|---|---|---|
| eZ80 product / revision |0007 / AA|0007 / AA|
| MOS RAM upload CRC32 |15BD0583|15BD0583|
| MOS flash readback CRC32 |15BD0583|15BD0583|

Target CRC checks cover the selected 108,490 MOS bytes. The original 90-byte
agent and ten-second programming wait were retained. After the wait, the CPU
was put in break for the flash CRC read. Both WROOM signal output enables were
then released. No automatic retry, target reset or P4 firmware restoration.
The Author reset/booted the Console8 successfully. Do not repeat FLASH to
restart the target; this paragraph preserves the programmer terminal state.

## Implementation and evidence

The normal algorithm follows AgonPlatform/agon-recovery commit
95d68464afd049945e1dfd780c1c07621d565450: initialization, MOS RAM upload/CRC,
three-byte size parameter, original flash agent, execution/wait, post-flash
MOS CRC. The adaptation keeps proven WROOM GPIO input sensing, DATA release
before the read edge and 10-microsecond timing. Transfers use 256-byte bursts
and watchdog yields. There are no added PC-value admission gates, pre-erase
dump requirement or blind fallback. Startup requires exact host FLASH; no
BOOT-button recovery shortcut or VDP update path. Only GPIO26/27 are configured.

Built on Oryx using pinned PlatformIO espressif32 6.7.0 / Arduino 2.0.16.
Preserved incoming WROOM application span and checked it against archived quiet
v3 before installing/verifying the new programmer. The stock payload and agent
were SHA-verified and found in the compiled application before installation.
One FLASH command executed. Host installation/capture duration:109.753 seconds.
No RAM/post-flash checksum failure, timeout or retry occurred.

Source and upstream MIT notice: experiments/zdi-wroom-checked-recovery/.
Generated payload header and ESP32 outputs are ignored by Git. WROOM NOW runs
WROOM-CHECKED r01, not identity-only v3. It waits quietly after completion;
reboot returns to an unarmed console requiring FLASH. It has no automatic
recovery or polling after completion. Physical boot was subsequently confirmed
by the Author, completing N-009.

Stock MOS SHA256:
d564243283972690933a4554296ad6202ca4ef54572279533a942960846bebae.
WROOM programmer SHA256:
ac75fbb4f59483b22d7dc384ebf0fe7b022245909782c26c2b68c8a8dc3fcd24.
Console transcript SHA256:
e0381073e276acaeea900a873517789c1b2c8f76fb1e35dacf40792d39360d76.

Raw logs, exact source/generated payload, binary/ELF, build log, selected MOS
and agent, and incoming WROOM bytes are retained on Oryx and Pi. Archive:
build/c8-wroom-checked-20261031-evidence-r01.tar.gz, SHA256
b8ed26b7c10338a885b8b236aab66e22043a4548080c5c361eca7403c12d0355.
Run: build/c8-wroom-checked-20261031/run-001.
