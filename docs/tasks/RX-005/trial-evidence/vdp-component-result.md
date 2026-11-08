# VDPL-036 — Counted-return component qualification

The opt-in VDP producer passes its host and native firmware checks and is ready
for UART's shared synthetic trial. It adds608 image bytes and no static DRAM.
The joint receiver/keyboard/byte-integrity trial has not run here; passing it
still stops for Brandon's review before application prototypes.

1. RES36-001: Selected enabled image is
   `build/vdpl036-producer-r05/enabled/firmware-src/.pio/build/esp32dev/firmware.bin`,
   1100320B, SHA256
   `7d09dfeac4e7a1654dca486a8e86cd7b5d283f0d53bac0ab128cb8dd33e10087`.
   Matching ELF25049816B:
   `2918727ad256389e3ac0d9074e736acdbbde3a9ce6f95a280fd7fa3673d6fd92`.
   Exact paths, all source/header/config/tool identities and evidence hashes
   are in [the structured result](COMPONENT-RESULT.json).
2. RES36-002: Retain original disabled BINc7978a74/ELF24d76d14 as selected control.
   Fresh disabled companion6c2dc561/7ad7e2db is separately identified. All loaded
   ELF sections match exactly; only three nonallocated debug sections differ.
   Embedded full-ELF hashes, final image hashes, narrowly bounded BIN difference
   locations and esptool checksum/image validity pass. Raw identities remain
   distinct and compiler503's original failed raw-identity gate is preserved.
   Amendment3a6148a and UART's18:52:17 disposition select this treatment.
3. RES36-003: Actual producer/info/D8 dispatcher checks pass18 disabled,
   658 enabled and666 enabled-with-async-shim assertions under ASan/UBSan.
   They cover exact complete0..512B frames, header-like payload, error/no-prefix
   effects, strong source/temporary lifetime and one bulk write. Old readback
   passes76/615 assertions; numeric package449b2558 reproduces with build123.
   Actual double-prepare export regression and mismatched-feature reuse refusal
   pass. Unlocked HAL configuration is compile-refused. Shims do not model IRQ,
   driver pacing, hardware or receiver completion.
4. RES36-004: Enabled minus disabled sections: flash text+560B, rodata+48B,
   IRAM-12B, static data/BSS unchanged. Exact native entry instructions allocate
   48B producer and144B dispatcher frames; these are not total stack peaks.
   The compiled producer calls the buffer overload once, after its checked
   copy. Fresh compiled uartWriteBuf and legacy uartWrite use the same HAL
   semaphore around uart_write_bytes. No SDK/HAL/IRQ/flow-control change.
5. RES36-005: Semantics remain the agreed private90/u16/count payload, max512;
   D8op8/body14/flag1, INFO27=512 only when enabled; sole counted success and
   existing tagged errors. Old ERROR does not retire MOS's armed receive.
   Synchronous source-copy completion differs wire TEMT and receiver completion;
   HardwareSerial does not expose a failure-atomic receiver guarantee.
6. RES36-006: Failed attempts retained:501 extractor before compile;502 wrong
   legacy build-ID invocation after passed host checks;503 debug identity gate;
   507 duplicate enabled declaration during prepare/build reuse. The last was
   a builder integration defect, corrected with a real repeated-prepare test.
   Original failed exports/logs/source snapshots remain unchanged. Final508
   qualification passes152.873s; owned children joined, released23:56:49UTC and
   actual next FSIM509 notified immediately before analysis.
7. RES36-007: No VDPlet emulator/bench lease or target process is held. UART owns
   the next frozen shared synthetic fixture and normal Oryx checkout. This is a
   component handoff, not deployment, physical acceptance, prototype distribution,
   game modification, version increment or publication approval. Coupled code
   and results remain uncommitted pending the applicable human gates.
