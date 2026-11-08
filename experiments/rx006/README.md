# RX-006 original hardware fixture

This app compares the existing private keyboard-reply data workaround with
the experimental counted receive service. It is not a game or a firmware image.
Build it for the exact receiving MOS/EMOS and map before running. Invoke
`test` from its staged directory; there are no command-line switches. Never add
it to a boot script. Firmware installation, launch and rollback on the shared
Olimex require the actual Extender-managed bench admission.

It first checks logical sizes 4, 8, 16, 32, 64, 128, 256, 1024, 4096 and 8092
with both synchronous and RFC25 asynchronous upload, then both read paths. A
single ordinary buffered-write command creates the immutable source. Larger
counted reads are serialized chunks of at most512 bytes, not a larger frame.
The offset-sensitive bytes and 16-byte destination guards are checked.

The benchmark repeats identical128/256/1024-byte pulls through:

* Legacy operation6, returning8 payload bytes in each16-byte `VDPL` body on
  packet81h. This is the existing eight-byte optimization, not READ16 or a
  literal held-key map.
* New operation8, with raw90h/u16-length/data replies of at most512 bytes.

Both fill the same guarded destination and run the same final byte check.
There are36 cells: three sizes, wait/work conditions, three paired rounds and
two methods. Method order alternates. Each size is uploaded once outside its
timed benchmark; source setup, print and SD work are outside the whole-batch
clock interval. Timings include request construction, IRQ delivery, adapter
copies and exact data verification, which is the useful complete-pull cost.
The public MOS clock is coarse; zero/short intervals are unresolved. There is
no PRT takeover or calibrated CPU percentage. Work counters describe completed
kernel iterations during waiting, not percent CPU saved.

Reports use collision-avoiding `R####.log` with `next.txt`, without the RTC.
Last `CHECK BEGIN`/`BEGIN` identifies a stopped case. Allow about two minutes;
a stalled case is a failure. Any unknown transfer failure keeps buffers and
callbacks resident, publishes `bench_witness[0]=2`, and halts for owner capture
and reset. No blind retry or cancellation occurs. On success it clears its
buffer and callback, records `RX006 SUITE PASS`, prints `RX006 RETURN PASS` and
returns. The host owner must separately verify real return and restoration;
the log alone does not prove them.

Only an idle/NULL application keyboard callback is admitted by this fixture;
the known slot is read from the exact firmware map. Unexpected ownership is
refused. Ordinary key packets pass through the normal MOS keyboard machinery.
The P4 input service is a separate owner facility. Both legacy capacities are
queried, and the full ROM CRC is checked before any test starts.

Build under the normal compiler FIFO with `build.py --rom IMAGE --map MAP
--kbvector ACTUAL_MAP_ADDRESS --tx-admission raw|guarded --sdk SDK --out NEW_DIR
--lease ACTUAL_LEASE`. It snapshots source, generates the exact-ROM guard,
compiles/links only the app and retains an ELF, listing, map, symbols and hashes.
Unmodified Eirene RFC25 has no admission-status return; the temporary EMOS
adapter returns guarded status. Do not interchange those configurations.

Analyze a returned log with `python analyze.py REPORT --build EXPECTED_BUILD
--out ANALYSIS.json`. `check_checker.py NEW_DIR` exercises manufactured positive
and corrupt/incomplete-log controls; those controls are not target tests.
Actual task, build/bench requirements and latest status are in
`../../docs/tasks/RX-006/`.
