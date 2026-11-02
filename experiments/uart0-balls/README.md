# Bouncing-balls UART demonstration — BD-001

The eZ80 calculates ball collisions and draws the next image while the
experimental MOS sends the previous frame. Keys select ordinary blocking
output, async events or async callbacks. Bitmap upload and VDP-circle output
perform the same local drawing/checksum work, so moving the drawing to the VDP
is a separate visible comparison. The callback is a source-lifetime notification;
it is not a promise that the UART or VDP has finished.

This is original C/AgonDev application code. No MOS or VDP source was changed
for this demo. It uses the previously Console8-qualified ABI1.3 experimental
MOS and matched receiver-fixed VDP. It is not stock-firmware/release approval.
Specification and delivery evidence: [task silo](../../docs/tasks/BD-001/README.md).

## Run

The workspace appliance is `build/uart0-balls/run008/appliance/`. Its short
`readme.txt` includes firmware identities, standard `flash` commands, controls,
finite sweeps and expectations. It has not been deployed to an SD card.
From that directory on Agon, `LOAD test.bin`, then:

- `RUN .`: interactive; `1` standard, `2` async events, `3` async callback.
- `B`: bitmap / VDP circles; `C`: wall-only / all-pairs collisions.
- `-` / `=`: remove/add four balls; `R`: restart; `Q`: save and quit.
- `RUN . quick`: 12 cases, four frames each,16balls.
- `RUN . sweep`: 24 cases, eight frames each,16/64balls.

Mode136 is320x240; the scene is160x120, one-byte opaque RGBA2222. Two source
buffers remain immutable until released. Only one presentation confirmation
is outstanding; the next frame's calculation overlaps transmission of the
previous. Frame commands end with raw `VDU23,0,&C3` and an ordered GP reply.
No eZ80 VBLANK wait is used. Presentation counts mean confirmed swaps, not
precise scanout timestamps. Final `DIR` verifies return to a useful MOS CLI.

`Rnnnn.log`, `next.txt`, and `runs.log` provide sequential report history without
the Agon's clock. **Interactive mode has no frame limit or periodic SD save.**
It stays in your selected scenario until you change an option, restart with R,
or quit with Q. Transport, output and collision changes preserve current ball
positions/velocities. Adding/removing balls preserves the surviving balls.
Only R starts the deterministic scene again.

Rates/stage means use a rolling eight-frame window, with initial results after
two measured frames. They do not blank every twelve frames. Logs are saved on
user-directed scenario changes or Q, after draining accepted traffic. These
explicit boundaries can briefly pause while SD data is written. A RAM ring
retains the latest128raw frames per scenario, with total/overwritten counts in
its summary. No silent memory growth or automatic stopping is used. Report v2
records scenario setup, frame ordinal and scene step so host replay can verify
retained data even across transport/output changes and record-ring rollover.

## Metrics and limits

PRT1 runs at1,152,000ticks/s, PRT2 at72,000ticks/s. Both extend hardware counters
under interrupt exclusion and cross-check their16:1 ratio. Timer0 is untouched.
Only initially disabled timers1/2 are claimed; restore disabled controls, input
routing and vectors at exit. Reload registers are write-only; later owners
configure their own reload values. PRT2 also samples keyboard state at100Hz.

A long VDU operation can delay key reporting until make/break arrive together.
The sampler checks MOS's event counter and last packet to recover that last
tap. Real20ms SDL taps through compiled VDP/MOS now pass. This is not a lossless
keyboard event queue: several rapid batched keys can coalesce. Interrupt-side
latching in MOS's receiver is the proper follow-up (KI-001); an application
keyboard callback currently excludes async sessions.

Live stage figures are duration means within the rolling eight-frame window, then
converted to equivalent FPS. Physics includes collision time. Stage intervals
include interrupt preemption and overlap; never sum them or call them pure CPU
cycle costs. The foreground-event release time includes observation delay;
the direct callback timestamps consumption in its bounded posting routine.
The checksum pass is identical in both rendering strategies and its significant
cost is reported separately. Packet preparation includes HUD formatting.

A dedicated first frame tightly observes drain through the public API and is
excluded from pipelined FPS. For standard output this probe briefly opens and
closes an async session only after the standard send, using open's TEMT guard.
Regular standard frames have no async session. Observation includes API cost.
Source release, UART drain and VDP execution remain separate measurements.

Every frame includes bounded fixed-width HUD output; its byte count is recorded
separately. Actual submitted and confirmed rates use PRT2. `analyze.py` reports
stage mean/min/max and reciprocal-of-mean FPS, bytes/s and matched checksums.
All rates are nominal guest time; hardware is required for performance claims.

## Reproduce

Freeze into a new directory on Pi:

```sh
.venv/bin/python experiments/uart0-balls/prepare.py build/uart0-balls/NEW
```

Transfer that snapshot to the same project-relative directory on Oryx using
canonical SSH. In its `fixture` directory, run `make` with
`AGONDEV_TOOLCHAIN=/home/smith/Agon/mystuff/agon-mos/build/uart0-suite/toolchain/agondev`.
The resulting `bin/balls.bin` is staged as `test.bin`; map/ELF and build logs
remain in the snapshot. MOS is copied unchanged from completion/run005 and
verified by hash, never compiled with AgonDev.

Portable tests use a host C compiler (no emulator):

```sh
cc -std=c11 -Wall -Wextra -Werror -Wno-misleading-indentation \
  -fsanitize=address,undefined -g experiments/uart0-balls/src/core.c \
  experiments/uart0-balls/tests/core_test.c -o /tmp/balls-core
ASAN_OPTIONS=detect_leaks=0 /tmp/balls-core
cc -std=c11 -Wall -Wextra -Werror experiments/uart0-balls/tests/keys_test.c -o /tmp/balls-keys
/tmp/balls-keys
```

For finite actual-firmware Flexe qualification on Oryx, obtain the shared FIFO
checkout first. `qualify_flexe.py BUILD jit --attempt UNIQUE --sweep --maintained`
and `qualify_input.py BUILD jit --attempt UNIQUE --maintained` require
`UART0_ORYX_LEASE`, assert it immediately before each process, and preserve raw
results/clean up owned processes. Input check additionally needs the host-only
SDL shim built from `tests/input.c` at `build/uart0-balls/input.so`; it injects
20ms taps and captures actual texture pixels without modifying guest firmware.
The old frozen runtime is retained as a historical cohort; its ASCII-only
keyboard adapter cannot populate MOS's held-key map. Do not pool cohort timings.

The separately pinned maintained pair is copied into our workspace from the
qualified Rally086 profile, read-only at source. Frontend7e7d0e1b and backend
0866265b full hashes are enforced by the runner. Firmware/MOS/app identities
are independent and recorded in every receipt. No fleet runtime/default repin.

Generate full independent host oracles by compiling `tests/oracle.c` together
with `src/core.c`, then run it with an existing output directory argument.
`analyze.py REPORT --wire MOS-TO-VDP.bin --oracle-dir DIRECTORY --output JSON`
validates every bitmap payload byte or complete circle-command sequence,
packet extent, flip/reply token, target hashes and timer accounting. Add
`--quick` for the short sweep. `package.py BUILD` stages files only in the
workspace and refuses to overwrite an existing appliance.


For v2 live returns, compile `tests/replay_oracle.c` with `src/core.c` using a
host C compiler, then use `analyze_live.py REPORT --oracle HOST-REPLAY --output JSON`.
It reconstructs every simulated step from the logged scenario changes and
checks retained frame hashes, counts, continuity and raw-ring retention. The
original `analyze_interactive.py` remains for v1 hardware R0040. A controlled
`qualify_continuous.py` run checks unchanged play past26frames,140frames in one
scenario, short-tap controls, record-ring rollover, scene continuity and quit.
