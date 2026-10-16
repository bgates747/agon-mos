# Receiver synchronization fix and matched Console8 checks

The receiver could switch itself off just after the other CPU recovered it.
The repair puts the “buffer full” update inside the lock already used when
disabling receive interrupts. The reader uses that same lock when clearing the
flag, so it can no longer recover halfway through the interrupt handler's update.
This removes a receiver failure that must be resolved before qualifying the
CPU-saving UART transmitter. Matched Console8 tests now confirm the repair:
the original driver needs rescue under the controlled timing trigger, while
the repaired driver recovers every byte without rescue. The candidate also
passes the normal-command compatibility campaign. Stock VDP is restored.

Physical return on 2026-10-15: R0012 captures66 pending FIFO bytes with RX
masked/full flag false and rescues the complete payload. R0014 completes both
4096-byte payloads, CRC87897582, with zero receive errors and no rescue; its
masked event retains full=1 until the other-core reader recovers. The repaired
image has no linked rescue function. R0017 passes phases1/6/2/3/10, including
all six receiver pattern/mode cases with49152 final-buffer bytes verified,
eight benchmark comparisons and four pause/full-duplex cases. Independent
offline parsing agrees with final/progress reports and the running journal.

R0018 records the stock restoration handoff. The Author separately confirmed
the normal stock2.16.0 reboot banner; utility return0 alone is not proof.
Package identities, prior reports and root /MOS.bin remain unchanged. Raw
return is build/uart0-repair/hardware-return-001; interpretation is
experiments/uart0-repair/physical-results.json. This closes the controlled
hardware repair test, not natural stock-failure frequency, original A/B
performance requalification or production release approval.

The change is in a private source copy of Espressif's IDF4.4.6 UART driver,
used by a private VDP2.16.0 build. Upstream VDP and installed SDK sources were
read-only. The exact transformation is in
experiments/uart0-repair/uart-rx-full-lock.patch and patch_driver.py. No new lock,
per-byte work, FIFO size, flow threshold, MOS image or app API is introduced.
Actual linked disassembly places the candidate flag store at400d1170, between
the lock call400d1159 and unlock400d1182; the RX-mask store400d117c is inside
the same region. The original UART archive object is excluded from all builds.

Matched diagnostics use the same payload and driver operations apart from the
repair. Their bounded wait remains outside the UART lock: before locking in
the unpatched image and after unlocking in the repaired image. Publication and
mask observations inside the repaired lock do not wait. Moving the wait under
the lock would block the reader and invalidate the experiment. The baseline
must capture the original stuck state and rescue it; the repaired diagnostic
must recover every byte without rescue, with RX enabled afterward. The linker
removes the repaired diagnostic's rescue function completely.

A third candidate contains the same repaired driver without timing, event or
rescue hooks. A private identity query lets the suite refuse the wrong image;
normal VDP commands are retained. Its campaign covers phased receive errors,
API/callback/masked-IFF/exit compatibility, the legacy/async benchmark, pause
and full-duplex traffic, and six receiver cases spanning all three traffic
patterns in both blocking and experimental async modes. All final buffers are
checked; intermediate bulk overwrites remain outside that fixture's claim.

Both engines execute the actual firmware with MOS's real FatFS/SPI path on
disposable FAT16 images. Native paired checks pass in about10seconds; full menu
checks pass in about23seconds. The candidate campaign passes in119.349seconds
JIT and154.554seconds interpreter during concurrent Oryx qualification. The
initial24-case candidate run was still progressing at its180second harness
limit (12 cases complete, no failure); it was retained and not treated as a
firmware stall. The final bounded campaign uses all six pattern/mode cases;
the earlier24-case fixture remains separately accessible.

Corrupt payload, absent end marker, opposite diagnostic variant, old D6
diagnostic, and wrong candidate identity are rejected. The byte-valid oracle
also rejects rescue use, same-core recovery, a cleared flag at masking, or RX
still disabled afterward. All headless checks retain zero emulator faults,
TX drops and RX overruns. Firmware/native/menu/source identities and every
attempt are under build/uart0-repair; results.json/audit.json provide the gates.
Those software checks preceded the matched physical confirmation above.
Human emulator acceptance and production release approval remain separate.

The complete package remains at the same /test/mos-uart0/test.bin on Console8
UUID8658-1C23, now labeled AGONC8. All29 earlier report/config files are unchanged;
the30th preserved item, runs.log, retains its old bytes and appends new runs.
Root /MOS.bin is preserved. Every flash/reboot/run was a manual Author action.
Return inspection wrote only to the project workspace, never the SD card.

The repaired source, native fixture, matched diagnostics, uninstrumented
candidate and menu are kept uncommitted pending the standing human acceptance
gate. R0010 remains the initial reproduction; R0012/R0014 are the matched pair.
RX-001..RX-003 and HW-002 are complete and recorded in the dated development
log. AB-006 retains the original A/B replay and emulator qualification work.
