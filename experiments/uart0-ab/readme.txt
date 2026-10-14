UART0 CONTROLLED A/B EXPERIMENT - EMULATOR REVIEW CANDIDATE

No MOS or VDP flash is required for this emulator review. Production MOS,
AgonJukebox, and the Console8 SD have not been changed.

Run test.bin. It clears the screen and runs 30 phases automatically:
Mode 0: blocking MOS output
Mode 1: current async scalar kernel, CTS checked per byte
Mode 2: grouped CTS checks, scalar copying and per-byte accounting
Mode 3: scalar copying with per-chunk accounting
Mode 4: OTIRX copying with per-chunk accounting
Phase 0: unpaced bulk output
Phase 1: paced 735-byte data feeds on two-MOS-tick boundaries
Three passes; the middle pass reverses mode order.

Allow about one minute. Headless successful runs take approximately 44 seconds
with JIT and 69 seconds with interpreter; host and graphical overhead vary.
If it takes over two minutes, something is wrong. Record the last repeat/mode/
phase line and close the emulator. A stall is not a PASS.

Expected ending: UART0 A/B PASS, UART0 AB MOS RETURN, then the MOS prompt.
Raw phase ticks, useful-work counts and IRQ counts are saved in ab.dat.
These emulator timings do NOT establish hardware bytes/second or exact CPU
cycles. The separately executed instruction-model campaign supplies cycle
estimates with its stated limitations. No actual audio playback or graphics
stress is claimed by this initial transport experiment.

Bad-byte and matching-byte receiver controls run before timed phases.
Transmitter errors or failed checks hold memory rather than returning while
source bytes may still be borrowed. A failed run requires emulator restart.

The test temporarily owns UART0 only during each phase and restores MOS's
handler before output and file I/O. It is not yet the public batching API.
Do not deploy this standalone review profile to hardware yet. Its reports are
not the reusable suite's sequential format. Hardware/menu packaging, complete
bulk receiver verification and calibrated timing remain subsequent work.
