# TM-001 controlled sender comparison

[Source audit and scope](../../docs/tasks/TM-001/comparison.md).
[Task and pending checks](../../docs/tasks/TM-001/README.md).

The exact attachment is original/async_vdu.asm. src/tomm.src preserves its
scalar algorithm, including the DI/CTS wait. Changes are local-label/directive
syntax for AgonDev, C globals instead of the sample register caller, a named
A-only completion callback, and no embedded Lorem Ipsum example. The harness
arms that flag before submission to avoid the sample's early-completion race.
It only submits positive lengths with one source outstanding, uses no other
UART writer until completion, waits TEMT before restoring ownership, and keeps
application memory resident on a detected failure. The raw helper has not been
silently fixed for zero lengths, CTS pauses, callback clobbers or vector races.
Tom has not supplied a license in this attachment; do not assume our original
C harness's license grants redistribution rights to his code.

No MOS/VDP firmware changes are needed to build this app. The experimental MOS
comparison uses the already-qualified cb1d0f4e ZDS II image; standard output
runs with its async session closed. The Tom app installs/restores a RAM vector.

Prepare a fresh snapshot on Pi:

```sh
python3 experiments/uart0-tomm/prepare.py build/uart0-tomm/NEW
```

Build the staged fixture on Oryx using its existing AgonDev toolchain. stage_flexe.py
runs ONLY on Oryx, creates six stopped profiles from frozen inputs and emits
profiles.json. run_flexe.py starts processes: it requires UART0_ORYX_LEASE from
the shared FIFO, asserts ownership before each launch, caps each cell at180s
and preserves all raw results before owned-process cleanup. Do not run it
without checkout, or treat profile preparation as execution qualification.
The current request and staged paths are in build/uart0-tomm/run001.

The finite workload compares modes0 standard RST18,1 MOS borrowed/direct OTIRX16,
2 Tom scalar16, on both engines, with three repetitions each of:

- Bulk: one8448-byte stream containing32 framed256-byte appends.
- Paced: those identical bytes as32x264-byte writes at a nominal44100wire
  bytes/s producer rate; equal foreground arithmetic fills available time.

Each phase clears the receiver buffer and every8192payloadbyte is checked
using the existing negative/positive-controlled public VDP comparator. File
I/O, logging and verification are outside the measured interval. Both async
senders use the same A-only callback and immutable source. Reported ticks include
interrupt service, not isolated instruction cycles. Missed deadlines and useful
work counts accompany submit/source-release/wire-drain timing. No callback means
VDP command completion; verification uses the ordinary response fence afterward.

A physical appliance additionally needs sequential report naming and concise
operator instructions before deployment; the currently staged profiles have
fresh private cards and CREATE_NEW modeN.log files. Do not overwrite historical
logs or deploy this staging fixture over an existing SD appliance. Tom's DI wait
can strand the entire machine if CTS blocks; reset is the expected recovery for
that prototype, not an automatic retry. No hardware deployment occurred here.
