# Console8 balls demo — R0040

Background transmission made this hardware animation faster while doing the
same local physics and image rendering. Callback delivery did not add a
convincing speed advantage over collecting completion events in the foreground.

The interactive run ended PASS with511frames in48measurement blocks. It tested
24balls, bitmap upload, all three transports and both collision settings.
VDP-circle output, other ball counts and the automated full matrix were not
exercised in this return. No keyboard queue overruns were reported; that does
not establish lossless keyboard event delivery.

| Matched scene | Standard | Async events | Async callback |
|---|---:|---:|---:|
|24balls, walls only|3.120FPS|3.981FPS (+27.6%)|4.008FPS (+28.4%)|
|24balls, all-pairs collisions|2.960FPS|3.981FPS (+34.5%)|4.008FPS (+35.4%)|

Comparison uses identical scene steps: five complete12-frame blocks for walls
and two for all-pairs, for every transport. Excludes each block's dedicated
drain-calibration frame, partial blocks, and SD pauses between blocks. These
are active-window rates, not whole-session animation FPS. The sequence was
interactive, not randomized/repeated A/B; callback's approximately0.7% lead is
not evidence of a meaningful callback performance benefit.

The standard submission held the foreground for about215milliseconds/frame;
async submission returned after about0.128milliseconds. That demonstrates
where overlap becomes possible, not the total CPU cost of async transport:
MOS still services transmission interrupts and the application still renders.
The extra collision workload reduced standard FPS but left async near4FPS in
this selected workload, consistent with useful computation overlapping output.

Independent host C simulation reproduced all511physics/image checksums, pair
counts and contact counts. Both PRTs agreed at15.999861:1. Confirmation tokens
remain ordered; the seven skipped IDs occur only at control changes that
explicitly discard a prepared, never-submitted frame. There is no recorded
completion timeout or application FAIL.

The deployed application and all staged static firmware/license files still
match the deployment hashes. This fixture does not fingerprint installed ROM/
VDP firmware or read back every received hardware pixel byte; it verifies local
scene hashes and ordered post-flip replies. Do not claim physical byte-for-byte
receiver verification from this report.

Raw card archive and analysis are preserved on Pi and Oryx at
`build/uart0-balls/hardware-return001/`. Archive SHA256:
2b2002280c354f71de68f6fa67ac5068b27e27c17eb1272e1a79274072367c2c.
The original R0040.log, journal, counter41, staged binaries and manifest are
retained. Collection was read-only and the SD card was left mounted.
