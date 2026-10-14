# Experimental UART0 session batching — BT-003 / AB-003 / BT-005

Executive summary: we want apps such as AgonJukebox to spend less CPU time
sending sound to the VDP, leaving more time for graphics and other work. The
experimental app-controlled switch now lets MOS send small batches in the
background. Legacy apps keep their stock behavior.

An earlier Console8 comparison let the test program complete about 31% more
other work during regularly scheduled sending than our experimental sender
that checks permission before every byte. Batching did not make bulk transfers
faster than that sender. The new app-controlled implementation passes extensive
software and receiver checks, but is not ready to approve or install: the VDP
firmware under the emulator can still stop receiving permanently. Resolve that
fault, finish the remaining test-suite work and validate the new version on
Console8 before trying it in Jukebox.

The append-only [ABI contract](../../docs/uart0-cts-batching-api.md) defines
setter/getter, bitmap and rejection precedence. Configuration requires an open
session, empty published queue, TEMT, no serialization barrier and no synchronous
scope. Query does no I/O; setter makes one shared LSR read only after software
checks. Both preserve incoming IFF and existing register-context rules. Open,
close and return reset policy to 1 without abandoning borrowed sources. Legacy
and synchronous compatibility writes keep their per-byte CTS checks.

The block path checks CTS before each block, including each descriptor boundary.
It clamps length to the selected size, remaining source span and remaining
service budget. BC is the positive count, HL the source and DE the fixed UART
port. Native `OTIRX` executes under existing DI/sole-consumer exclusion, and
progress/release is accounted only after copying. The isolated scalar build
uses the same controls/accounting and replaces only the block copy operation.
Neither the setting nor the capability bitmap certifies receiver reserve.

## Reproduction

All native ZDS II/Wine compilation, Rust instruction tests and Flexe execution
run on Oryx. Local Ruby stages inputs. Run `bash experiments/uart0-async/build.sh`,
`bash tools/zds/build.sh`, `ruby experiments/uart0-mos/symbols.rb build/uart0-mos`
and `bash experiments/uart0-batching/build.sh` from the project root. Stage the
new MOS image/map/symbols into the matching Oryx `build/uart0-mos` directory;
these are off-device build products, not SD firmware deployment.

`prepare_native.rb` generates the CRC child from the existing diagnostic host
and full-duplex children from the suite's corrected acknowledged-reply source.
This intentionally avoids the historical standalone fixture's GP mailbox
assumption. The receiver firmware is the already reviewed MOS-owned diagnostic
image; no receiver recovery fix is included. Native build commands are in
`native_remote.sh`. `profile.py` uses the canonical generator to create a new,
stopped `.emulator/uart0-batching` profile and checks frozen runtime identities.
It does not change earlier profiles or another project's runtime.

On Oryx, `.venv/bin/python -B experiments/uart0-batching/qualify.py jit` and
`interp` execute the combined campaign. The optional `crc` and `noend` controls
must be rejected by the compiled receiver fixture. Use `baseline.py profile`,
then `baseline.py jit` / `interp` to run the established legacy, parser,
masked-IFF, callback/return and ADL=0 regression in a separate profile. The
receiver-race gate remains open even when these commands pass.

## Coverage and limits

The independent instruction/UART oracle checks each CTS group's allowance and
the overall 16-write cap, exact wire equality, descriptor boundaries, source
reuse after release, continuous full duplex, cut/resume edges, IRQ bounds and
register preservation. Setter/getter tests cover every 8-bit request, rejection
precedence, reservation-only quiescence, queued/busy states, TEMT lag, barriers,
context, IFF preservation and session reset. Production-ROM checks exercise the
real parser and stalled-return retention at all five sizes. Fault controls
mutate missing group guards, a 17-write refill and premature release; each must
fail for the intended reason. The previous seven per-byte controls remain.

The native CRC fixture sends 4096 nonzero bytes plus EOT across three
noncontiguous descriptors (15/17/4065 wire bytes), at stock threshold64 and
5/20ms receiver pauses for all five sizes. It verifies requested/effective policy,
full count/CRC and source accepted counts. Ten cases verify 40,960 payload bytes.
The full-duplex fixtures compare every byte of four 8192-byte receiver buffers
per size and require 32 acknowledged replies per case, including replies while
TX is still busy: 163,840 compared bytes and 640 replies across all sizes.
Their payloads cover zero and all other byte values. CRC raw-payload tests use
the diagnostic EOT protocol and do not claim to verify the earlier A/B fixture's
entire 16KiB command workload. That matched benchmark integrity extension and
numbered menu packaging remain in AB-003/BT-005.

One full-duplex reply may be outstanding because MOS GP is a last-value slot,
not a queue. Earlier replies must be observed and the current source drained
before the next group is published. CRC/failure files have fixed 16-byte header
slots for future sequential menu naming; standalone off-device qualification
uses private directories and preserves each previous attempt in workspace
history. These children are not a new SD deployment or finished menu package.

No native pass establishes physical CTS margin, exact CPU-cycle saving,
calibrated throughput, Jukebox benefit or release readiness. The known receiver
race, menu-keyboard investigation, full menu integration and manual hardware
qualification retain their existing task IDs in the sole TODO.md.
