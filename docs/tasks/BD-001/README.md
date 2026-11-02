# BD-001: bouncing-balls UART demonstration

Build an interactive demo that makes the value of background transmission
visible: the eZ80 calculates ball motion/collisions and draws coloured balls
while MOS sends the previous frame to the VDP. The viewer can increase the
load and compare ordinary blocking output, async output without a callback,
and async output with a callback. Show where time is spent, rather than imply
that callbacks or OTIRX necessarily improve every workload.

**Status: Author approved execution on 2026-11-02.** The pre-task checkpoint
was committed/pushed as four logical commits ending7218650. Original C source,
builds, finite sweeps and raw evidence now live in `experiments/uart0-balls/`
and `build/uart0-balls/`. Delivery/physical qualification are still separate.
The actionable checklist remains [TODO.md](../../../TODO.md), BD-001..006.

## Application and display

Use **C targeting AgonDev**. C is sufficient for the physics, software renderer,
UI and measurements and keeps the demo approachable. Reuse the tested assembly
register-ABI bridge or minimal compiler-required interrupt/callback stubs;
keep the substantive application in C. This original application does not
change the MOS requirement to retain ZDS II/Wine or VDP's upstream toolchain.

Use mode136:320x240,64colours,double-buffered. Draw an **unmagnified160x120**
scene with coloured, filled balls. Leave the rest of the display for clear
instructions, selected configuration and live statistics. Start with no affine
scaling; enlargement is outside the initial tranche.

Use opaque one-byte RGBA2222 pixels for the eZ80 image, not four-byte RGBA8888.
One scene is19200pixelbytes. At1.152Mbaud,8N1, the theoretical payload ceiling
is115200bytes/s, or6full scene uploads/s before headers, drawing, replies and
other overhead. This is a ceiling, not a promised demo rate.

Keep two eZ80 image buffers so one frame can be transmitted while the next is
rendered. Keep submitted command/pixel storage immutable until MOS releases it.
Bound the number of frames in flight; do not overwrite a source, drop accepted
bytes, silently drop simulation steps or build an ever-growing queue.

## Controls and physics

Use `-` to remove balls and `=` to add them. Proposed remaining keys are
`1`/`2`/`3` for transport, `B` for bitmap/circle output, `C` for wall-only versus
ball collisions, `R` for repeatable scene restart and `Q` to quit. Display them
on screen. Poll MOS keyboard state with press-edge handling; do not install a
MOS keyboard callback that excludes an async session, or require key spamming. A100Hz PRT sampler also checks MOS's public event
counter, ASCII and final up/down state: a long VDU operation can delay reporting
until a press/release pair is delivered together. Recover that last complete
tap when both transitions occurred between samples. This is bounded last-event
recovery, not an unlimited queue for arbitrarily many simultaneous taps.

Wall-only motion has a fixed amount of work per ball. Optional all-pairs
ball-to-ball collision detection checks N(N-1)/2 unique pairs per physics step.
Use squared distances for detection. Implement a documented, stable collision
response with an explicit rounding/overlap policy; choose appropriate integer/
fixed-point widths and avoid overflow. Do not introduce a spatial acceleration
structure: predictable quadratic workload is useful here. Display pair checks
and actual contacts separately.

Use reproducible initial conditions, colours and random seed, with the same
physics timestep and arithmetic in every mode. Interactive changes start a
new measurement/configuration epoch; matched recorded comparisons restart
from the same seed/count. Choose useful ball sizes and count limits so the
scene remains legible rather than immediately becoming solid overlapping balls.
Do not alter simulated speed according to transport mode to conceal slowdown.

## Two output strategies, three transport modes

Every frame performs identical physics and local framebuffer rendering in
both output strategies:

| Strategy | Bytes sent to VDP |
|---|---|
|Bitmap upload|Upload the completed19200-byte image, create/select the bitmap as required, plot it and request a screen-buffer swap.|
|VDP circles|Retain the locally rendered image, but send scene clear, colour and filled-circle commands for the same ball positions; then request the swap.|

Keep local rendering observable so the compiler cannot discard it in circle
mode. Use the same measured framebuffer checksum pass in both strategies and
report its overhead separately from rasterization. Match clipping, colours,
background and draw order. VDP scene clear/drawing must not erase the HUD.

Both strategies use each of these transports, giving **six combinations**:

| Transport | Behaviour |
|---|---|
|Standard|Unmodified synchronous RST18 output path, with no async session.|
|Async without callback|Batch16 borrowed convenience writes with foreground completion-event taking; no direct callback.|
|Async with callback|The same batch16 borrowed convenience writes, with a bounded direct callback posting release flags/IDs.|

Use the **same MOS image, packet contents, logical submission boundaries and
source buffers** when comparing transports within one output strategy. Only
transport/completion handling changes. Both async cases use the same borrowed
interface; copied-RST18 mode is excluded from the initial comparison so payload
copy cost does not confound callback cost. Record this distinction on screen
and in reports; this is not a comparison of every experimental API variant.

Direct callbacks may run before submit returns or in the MOS UART ISR, with
interrupts disabled. They only post bounded state. No rendering, SD access,
waiting, output or recursive async API calls occur there. MOS remains the sole
UART owner. On transport/configuration changes, drain accepted traffic and
resolve source lifetimes before closing/reopening or replacing storage.

Changing bitmap upload to VDP circles also changes VDP work, not just byte
count. Treat that axis as a comparison of complete rendering strategies with
matched eZ80 computation, not a pure UART benchmark. Expect the large visible
gain, if present, to come from overlapping work or reducing bytes; callback
and no-callback async modes may legitimately perform almost identically.

## Instrumentation

Use a continuously running PRT timebase for stage timestamps, with documented
clock/divider/tick frequency, wrap handling and measurement overhead. Audit
timer/vector ownership before selecting timers: the AgonDev delay helper uses
timer0, so do not silently combine it with timer0 measurement. Preserve and
restore any borrowed timer/vector configuration. Reload registers are write-only: claim only initially disabled
timers, restore their disabled controls, source routing and vectors, and require
future owners to configure their own reload values normally.

Capture raw ticks for these named intervals:

| Metric | Boundaries |
|---|---|
|Collision detection/response|Start pair/wall checks to completed collision work; state exactly what it includes.|
|Total physics|Position integration plus all collision/wall work; collision time is a subset.|
|Local rendering|Framebuffer clear plus filled-ball rasterization.|
|Framebuffer checksum|Separate observable checksum pass, identical in both output strategies.|
|Submission|Enter the complete frame's send sequence to foreground regaining control after its submissions.|
|Source consumption|First frame submission to all that frame's borrowed sources released; report completion-observation delay where foreground collection affects the timestamp.|
|Transmission|First frame submission to the final frame byte leaving UART hardware, including UART queueing/CTS stalls.|
|Frame confirmation|First complete-frame submission to receipt of its verified post-flip reply; includes payload transmission, flip waiting and reply/observation latency.|

For each duration, display raw ticks or milliseconds and **equivalent FPS**:

```text
seconds = ticks / tick_frequency
equivalent_FPS = tick_frequency / ticks
```

Equivalent FPS describes that stage alone. Handle zero/below-resolution samples
explicitly. Do not add FPS figures, count collisions twice, or sum overlapping
async intervals as if they were sequential. Stage wall times include interrupt
preemption unless separately accounted; do not label them pure CPU cycle costs.

Use a **second PRT** to measure elapsed wall time across a window of completed
frames and calculate actualFPS=frames/seconds. Keep submitted-frame rate and
confirmed-presentation rate distinct. The second timer cross-checks accounting;
it shares the eZ80 clock and is not independent oscillator calibration.

Track frame IDs and event timestamps so overlapping rendering/transmission can
be related to actual frame intervals. Show a stable rolling result and retain
aggregate totals, sample counts and variability. Compare mean stage duration
before taking its reciprocal rather than averaging instantaneous FPS values.
Use finite windows and identify mode/count/seed changes so samples do not mix.

A final source callback is not UART TEMT, and TEMT is not VDP execution. First
establish a per-frame wire-drain observation that cannot be confused with the
next queued frame. If truly nonintrusive per-frame TEMT timing is unavailable,
label a dedicated drain-measurement run and its scheduling effect rather than
silently serialize the main overlap demo to obtain that number. Do not add MOS
instrumentation without first bringing the concrete need back for review.

Display bytes/frame and achieved bytes/s alongside the rates. Keep HUD output
bounded, use the same refresh policy in all modes, and count its bytes separately.
No SD logging, printing or expensive arithmetic in timing/UART callback ISRs.
Buffer measurement records in RAM and save at safe boundaries outside measured
traffic; report timer, checksum and confirmation overhead honestly.

## Non-blocking flip and actual frame counting

Send the normal three-byte `VDU23,0,&C3` command after that frame's drawing
commands, with **no eZ80-side VBLANK wait**. The VDP synchronizes its swap; the
application starts useful next-frame work. VDP-side waiting can still cause
later CTS backpressure, which belongs in the measurements.

Do not use a blocking MOS/library pacing helper. No predictive PRT flip
interrupt or just-before-VBLANK scheduling is needed or planned. Any timer ISR
only records time/posts state; it must not become a second UART producer.

Verify that an ordinary general-poll reply ordered after the flip confirms
that the VDP has completed the swap before counting a presented frame. Preserve
IDs/order and bound outstanding confirmations so a single MOS GP state byte
cannot hide missed events. A reply timestamps confirmation after presentation,
not the exact scanout edge; note boundary/latency limits of finite FPS windows.
If the stock protocol cannot support a defensible confirmation, report submitted
FPS separately and resolve the metric before claiming displayed FPS. Do not
introduce a private VDP feature merely to make the demo's counters convenient.

## Firmware, verification and delivery

Target the separately branded, startup-preserving ABI1.3 experimental MOS
already tested by the callback fixture: build/uart0-completion/run005/MOS.bin,
SHA256cb1d0f4e066395533a2f07c7454246fa3a1ed46134bf155b883bb8c6e8353128,
FILECRC6E17923C / physical ROMCRCFA47120E. Require discovery/capabilities;
fall back to standard mode on an incompatible MOS and identify unavailable modes.
Keep standard output genuinely standard on the same image.

Initial acceptance uses the matched RX-repaired VDP:
build/uart0-startup-safe/provenance/frozen-runtime/esp32-firmware.bin,
SHA256201ad8ab4af807c261cb92634286b2fbaedcf3879f140e820b60ab54cf707e2a.
The demo's graphics/flip/reply operations use public VDP commands. No diagnostic
VDP API, new protocol, synthetic RX syscall or firmware feature is required.
Label the installed pair explicitly. A stock-VDP comparison is useful only when
separately run and identified; do not transfer the repaired pair's acceptance.

Verify deterministic physics/framebuffer checksums for matched modes, packet
order and complete buffer source lifetimes. Test real short key taps, mode/load
changes, normal quit and return to working CLI. Check timer arithmetic/wraps
against the second timebase and expected wire-rate ceilings. Avoid a new
adverse-reset/recovery campaign; this tranche is a convincing performance demo.

Provide interactive operation plus a finite, reproducible sweep of ball counts
across six combinations and both collision settings. Use identical seeds and
recorded configuration, not ad hoc snapshots from different animated scenes.
Comparisons need representative transmit-bound and compute-bound counts; report
negative/equal results without tuning unrelated workloads to manufacture gains.

Keep full source, build instructions, exact binary/firmware identities, raw
versioned sequential reports and analysis in this silo/project workspace.
Plan hardware-facing test.bin, matching staged firmware and short readme.txt;
retain the established /test/mos-uart0 location if deployed and keep history
off-card. Inspect/archive the actual card before replacing anything. Physical
Console8 flashing/execution remain Author actions; an eventual deployment is a
separate explicit step. Any emulator run follows the shared Oryx FIFO. This
task does not assign Jukebox work, publish another PR or authorize new bench use.

## Consulted implementation references

- /Agon/agon-docs/docs/vdp/Screen-Modes.md: mode136 and swap command.
- /Agon/agon-docs/docs/vdp/Bitmaps-API.md: buffer-backed RGBA2222 bitmaps.
- /Agon/agon-docs/docs/vdp/Buffered-Commands-API.md: uploads and buffer handling.
- /Agon/agon-vdp/video/agon_screen.h: switchBuffer and VDP-side waiting.
- Frozen vdp-gl lib source, canvas.cpp: swapBuffers queues and waits for a primitive.
- /Agon/agondev/src/lib/libtimer/timer.c: timer0 ownership by delay().
- experiments/uart0-completion/README.md: API, callback/lifetime contract and
  Console8 R0039 correctness results; not a demo performance claim.

## Input follow-up requested during implementation

On2026-11-02 the Author pointed out that latching keyboard events in the
keyboard receive interrupt avoids losing taps. That is the reliable full-event
solution. The selected MOS ABI currently excludes an application keyboard
callback while an async session is open. The demo's bounded public-sysvar
recovery is an interim application-only solution, not an all-events guarantee.
KI-001 in TODO.md records a compatible MOS-side event latch/queue follow-up;
no MOS/VDP firmware change is included in BD-001's demo implementation.

## Implementation and off-device return —2026-11-02

The demo now makes the comparison visible: coloured balls animate beside live
controls and timing figures, and increasing the ball count adds real collision
work. Background output can overlap that work with sending the previous frame.
Both async modes work in the finite emulator tests; callbacks do not show a
consistent frame-rate advantage over foreground completion collection. The
remaining acceptance step is Console8 execution and performance comparison.

Original C/AgonDev build **b57893f6a9450c82** is frozen at
`build/uart0-balls/run007/`. Application SHA256:
`9677bd86a8feba29205214fd0168e9728d5d0b2a477cc8bd54957e243ee0e993`.
Compiler15.0.7/AgonLLVMc76386c, build logs, map/ELF, exact source hashes and
unchanged firmware are retained there. No firmware source change was made.

[Evidence manifest](evidence.json) records the exact runtime/firmware identities,
raw-file hashes and stage summaries. The final192-frame/24-case sweep passed;
all1,902,240bitmap/circle scene bytes matched independent host-generated
oracles. A corrupted-pixel negative control was rejected. The measured PRT
ratio was15.999306:1. Portable arithmetic/raster/packet tests passed480frames
under address/undefined-behaviour sanitizers; key-edge tests cover delayed taps,
holds/releases and counter wrap. The real SDL20ms tap sequence passed every
control through compiled VDP/MOS, including normal quit/CLI return. These are
functional emulator results, not hardware timing or visual acceptance.

The first frozen runtime's ASCII-only keyboard path failed key-map input.
A separate maintained runtime cohort uses frontend7e7d0e1b/backend0866265b,
keeping the same MOS/VDP/app pair. Its input test exposed batched make/break
loss; the application's bounded last-event recovery fixed the tested sequence.
Old cohorts and failed attempts remain untouched in run001..006. Do not pool
cohort timings or call this a receiver/emulator repair.

Within the final nominal-guest sweep, bitmap output with16balls/walls was
3.34FPS standard,4.27FPS async events and4.36FPS callback. With64balls/all-pairs
it was2.26/3.19/3.20FPS. Those short windows illustrate overlap, not calibrated
hardware gains or a callback speedup. The identical full-image checksum pass
costs substantial foreground time and is reported separately. Interactive SD
logging between twelve-frame windows pauses animation; that time is excluded
from the displayed within-window FPS.

[Captured emulator display](preview.png) is the actual SDL texture, not a mockup.
The first confirmation token is chosen to differ from MOS's existing GP state;
all tokens are logged and checked, avoiding a stale startup reply.

The workspace-only [appliance readme](../../../build/uart0-balls/run007/appliance/readme.txt)
is ready beside test.bin, matched candidate MOS/VDP, stock restoration files,
flash fallback and licenses. The installed standard flash MOSlet is preferred.
The [review ZIP](../../../build/uart0-balls/run007/balls-demo.zip) contains that
appliance, exact original application source, ELF/map, build identities,
verification helpers and raw final reports/traces. Size1,571,691bytes;
SHA2569af5bc0f8a25436582ccd5dd1b3aa219cf2963938dc28f9c5ba29f60281bf354.

No SD deployment or physical run of the balls demo has occurred. BD-006 keeps
those steps open. The shared Oryx checkout was released after fresh idle
inspection; the next waiting Golem request5178bcbae8bc was notified in its
recorded chat. No emulator remains owned/running by this task.

## Authorized SD deployment —2026-11-02

Author selected `/test/mos-uart0/balls`. Identified AGONC8 UUID8658-1C23,
archived all17existing UART files on both machines, then moved them byte-for-byte
into `/test/mos-uart0/callback`. The UART root now contains only those two
subdirectories. Deployed the final demo and matched firmware/licenses into
`balls`, with report counter40 and a short path-correct readme. All deployed
files and moved originals were independently hashed after sync. No firmware
flashing or board execution occurred; no remount/eject was attempted.

Archive/receipt: `build/uart0-balls/card-deploy001/`. Before archive SHA256:
5894142445b3c05f0ffc1a183af3e1757bcc4675a14156a624d1559453b52588.
The card's autoexec was changed externally during deployment to CD into balls;
our deployment did not edit it. Both original and final versions are retained.
BD-006 remains open for the Author's physical run and returned-report analysis.

## Console8 return — R0040

Author returned an interactive24-ball bitmap run. All511reported scene hashes
matched host reference simulation and the application ended PASS. Matched
active-window performance improved about28% without ball collisions and35%
with them; direct callbacks showed no convincing advantage over foreground
completion collection. [Hardware analysis and limits](hardware-R0040.md).
Circle mode and the automated matrix remain unrun in this return.

## Continuous interaction correction — BD-007

Author reported that repeated stops and resetting rates made the demo difficult
to explore. The original live mode did retain selected options, but it saved SD
logs, closed/reopened transmission and cleared statistics every12frames. It
also reseeded the scene on any control change. That behaviour is superseded.

Interactive operation now has no frame/scenario timeout and no periodic SD
writes. Rolling eight-frame rates stay visible. A selected scenario runs until
a user action; changing output/transport/collision mode or count preserves the
surviving ball state. Only R restarts. Option changes and Q drain accepted bytes
and save reports. Raw storage is a128-record RAM ring with explicit total and
overwrite counters, not a reason to stop animation. Automated quick/sweep runs
remain finite and explicitly selected. Version2 records scenario setup, frame
ordinal and scene step for independent host replay. No firmware change.

Continuous build790222e035a1fed1 compiles with the same Oryx AgonDev toolchain.
The real C application loop was exercised with mocked MOS I/O under ASan/UBSan:
187frames,9user-directed scenarios,140frames in one scenario, no periodic disk
writes, and12old raw records overwritten while continuing normally. Host replay
independently verifies all175retained frames, configuration/scene continuity
and confirmation tokens. This tests application control flow, not eZ80/MOS/VDP
execution. [Readiness](continuous-readiness.json) records the binary identity.
The finite end-to-end emulator regression is prepared and first in the FIFO
behind Wolf3D's active human review; requestdb18783ba736. No takeover or emulator
run on Pi. The updated appliance is workspace-only; the card still has the
previously tested build. Deployment waits for the end-to-end check.

Author explicitly requested deployment before the queued emulator check.
Continuous build790222e035a1fed1 is now on AGONC8 at `/test/mos-uart0/balls`.
Only test.bin/readme.txt and the checksum manifest changed. All prior reports,
journal and next-counter41 are preserved; firmware is unchanged. Before archive
and verified deployment receipt are in `build/uart0-balls/card-deploy002/` on
both machines. No flashing, remount or eject. End-to-end emulator check remains
pending; the on-card readme states that limitation.

## Continuous Console8 return — R0041

Continuous build790222e035a1fed1 ended PASS after1,530frames/36scenarios, both
output strategies, all transports and24..76balls. Independent replay verifies
all1,528retained raw records; bounded retention replaced two older records as
intended. Scene continuity survives all35option/count changes. The old automatic
stops are gone. [Hardware findings and performance](hardware-R0041.md).
The redundant queued emulator check was withdrawn after this physical return.
