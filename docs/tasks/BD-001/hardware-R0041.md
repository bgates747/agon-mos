# Console8 continuous balls demo — R0041

The continuous demo works on Console8, and background sending remains useful
across both rendering strategies. Sending circle commands instead of pixel
images usually gives the larger improvement; combining that with async output
is the best-performing route seen here. Callback delivery and foreground-event
collection again perform essentially alike. Nothing in this run suggests
choosing callbacks for extra speed; choose them for application structure.

R0041 ended PASS after1,530frames and36user-selected scenarios. It exercised
both bitmap uploads and VDP circles, all three transports, ball counts24..76,
and wall-only/all-pairs physics. All1,528retained raw records match independent
host replay, including physics, raster hashes, pair/contact counts, scene steps
and confirmation tokens. Two early records in a130-frame scenario were
intentionally replaced by the128-record RAM ring; no frames were discarded to
make room. Total frame counts remain in the scenario summary.

Only the first scenario started a fresh scene; all35subsequent option/count
changes preserved it. There were no periodic12-frame scenario boundaries and
no reported keyboard queue overruns, completion failures or timeouts. The final
application record says normal completion. The intended continuous-play fix is
therefore exercised on hardware, including bounded-log rollover. This does not
prove every physical keypress was retained or independently verify the CLI.

## Observed rates

These are weighted rates across the available scenarios with matching count,
collision setting, output and transport. Unlike the earlier restarted-scene
comparison, ball states keep evolving: these are interactive observations,
not a randomized or identical-frame A/B experiment. Initial drain calibration
and user-directed SD saves are excluded.

| Balls / physics | Output | Standard | Async events | Async callback |
|---|---|---:|---:|---:|
|44 / ball collisions|Bitmap|2.45FPS|4.00FPS|4.01FPS|
|44 / ball collisions|VDP circles|4.04FPS|4.92FPS|4.89FPS|
|76 / ball collisions|Bitmap|1.76FPS|2.50FPS|2.50FPS|
|76 / ball collisions|VDP circles|2.44FPS|2.79FPS|2.79FPS|
|76 / walls only|VDP circles|4.62FPS|6.25FPS|6.17FPS|

At44colliding balls, async bitmap output is approximately63%faster than
standard bitmap output. Keeping async but using VDP circles gives another23%;
together the observed4.92FPS is about twice the standard bitmap rate.
At76colliding balls, those combined choices improve1.76to2.79FPS, about58%.
At24balls/walls, standard bitmap3.05FPS becomes6.22with standard circle commands
and8.22with async circle commands; no callback sample exists for that setting.

The two async variants differ by roughly1%or less in these groups, with no
consistent winner. Those differences do not establish an intrinsic speed gain.

## Where the time goes

With76balls, all-pairs collision work checks2,850pairs/frame. Circle-mode
physics is about208ms standard or212ms async, versus about3..4ms for wall-only
motion. This makes the heavy case primarily a computation workload; shortening
an already-small command stream cannot remove that physics work.

The demo deliberately keeps local rasterization and its whole-image checksum
in circle mode, as requested. At76balls those take about47ms and68ms/frame.
The checksum alone limits the demo and is instrumentation overhead, not useful
application graphics. These figures must not be presented as the maximum FPS
of an application that omits that work.

Standard bitmap submission occupies the foreground about215ms/frame; async
submission returns in about0.13ms. That is call-return latency, not total UART
CPU cost. MOS still spends time in transmit interrupts. Stage wall times
include those interruptions: for44colliding balls, physics measures about70ms
under standard bitmap output and93ms under async bitmap output. This is
consistent with preemption by background sending, not proof that the physics
algorithm itself became slower. Actual frame rates include that cost.

## Scope and preservation

The two PRTs agree at15.999584:1 initially; per-scenario cross-checks range
15.999920..16.000026. They share the same oscillator, so this is accounting
consistency rather than independent clock calibration.

All staged static application/firmware files match deployment, and old R0040
is unchanged. This application does not fingerprint installed MOS/VDP ROMs or
read back every pixel received on hardware. Successful ordered post-flip replies
and local hashes are the checks available here; no hardware byte-readback or
visual pixel-comparison claim follows.

The exact continuous build790222e035a1fed1 has now exercised the intended normal
interactive paths on real hardware. The queued redundant emulator check was
cancelled (requestdb18783ba736), without touching Wolf3D's active human review.
No new firmware, SD writes, flashing or reset tests were performed.

Raw files, verified archive, replay and detailed per-configuration/stage metrics
are at `build/uart0-balls/hardware-return002/` on Pi and Oryx. Card archive SHA256:
052f45545395f831206d30c196b6c663ac23edb38390ad14124dc37334920c7d.
The card remains mounted and untouched, with next report42.
