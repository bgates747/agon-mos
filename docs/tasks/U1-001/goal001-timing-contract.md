# GOAL-001: CPU attribution and interrupt timing contract

Measure how much useful bot work can actually run between communication duties.
Elapsed transfer time includes interrupts, waiting and possible bot work; it is
not the CPU cost of sending. UART-only timing cannot produce an exclusive whole-
CPU budget. MechAgon's profiler owns the implementation; this supplies source
donors and the necessary measurement contract, without introducing a second
profiler or claiming calibrated hardware figures.

## Existing donors and immediate limits

Read MechAgon's new `native/profiling/{prt.s,prt.c,profile.h,profile.c}` and
PROVENANCE.json as a live development snapshot, not a frozen/qualified build.
Its selected PRT provider returns `irq_complete=0`. That correctly prevents
exclusive attribution when only a foreground hardware clock is available.
The existing `PfSample` fields can receive complete atomic IRQ totals later;
there is no reason to invent a UART-specific CPU percentage API.

The current single-pass PRT1 /256 clock at18.432MHz has72000 ticks/s,
13.889us resolution and a65536-tick period of about0.91022s. Reject a depleted
epoch/control mismatch, do not extend it with guessed wraps. A fresh epoch is
not continuous wall time across retirement/restart. For reference, /16 would
give1.152MHz/0.868us and56.889ms per65536 ticks, requiring an explicitly adapted
provider and validity/control checks. The current provider is hard-coded for
/256; changing only a setup byte is insufficient.

The historical UART donors are:

* `../eirene-mos/experiments/uart0-rfc-latency/src/api.src::_lat_down`: IFF-
  preserving low/high PRT1 read, no CTL acknowledgement or timer IRQ. Its
  periodic16-bit modular clock loses complete wraps unless regularly sampled;
  do not reuse it as a reliable long-stall timer without that condition.
* `experiments/uart0-balls/src/bridge.src::_bd_capture_clock` and platform.c:
  wrap-accounted IRQ timer, but one pending bit cannot count multiple wraps
  while IRQs are blocked. It also uses a second timer for keyboard polling.
  This is a reference, not a drop-in profiling clock for EMOS or a running PRT.
* MechAgon's current provider is adapted from VDPlet's polled PRT donor, with
  its explicit disposable-owner admission. Retain that attribution/provenance.

PRT0 is not available by implication. Claim only an explicitly disposable inactive
PRT1/source/vector; reload registers cannot generally be read/restored. Do not
replace another timer owner. Preserve incoming IFF, ADL/MBASE and interrupted
primary/index/alternate registers; an ordinary C timer reader is not an ISR ABI.
Foreground global snapshot scratch cannot be shared with an interrupt reader.

## Complete versus partial IRQ accounting

Use one physical clock, one epoch and a cumulative union-of-IRQ-time counter.
Owner firmware must bracket every enabled interrupt path that can execute in
the measured interval: UART0 RX/TX and its callbacks, UART1 RX/TX/parser/app
callbacks, VBlank/tick, any enabled PRT/I2C/other installed vector. Enumerate the
actual enabled vector set in the frozen composition. Defaults that cannot fire
need no imaginary cost, but an unaccounted active vector makes completeness false.

The foreground sample must atomically contain the same epoch's timer count and
IRQ total, with incoming IFF preserved. Separate non-atomic calls can straddle
an IRQ and create an impossible subtraction. For two samples:

```
elapsed = start_downcount - end_downcount   // same valid single-pass epoch
irq     = end_irq_total - start_irq_total
foreground_exclusive = elapsed - irq      // only with COMPLETE IRQ accounting
```

Require0<=irq<=elapsed and no counter wrap, depletion, ownership loss or invalid
order. Existing `pf_prt_sample` does not yet supply that atomic total. Keep
`irq_complete=0` until a concrete owner implementation and calibration establish
all required paths. App wrappers around only U1 or RFC25 produce partial/inclusive
observations, not a complete substitute.

If interrupts never nest, a single active IRQ span suffices, but prove that no
callback or helper enables interrupts. With nesting, count the union once with
depth0→1/1→0 boundaries; nested callbacks/IRQs must not be double-counted.
Callback duration is a subset of parent IRQ duration unless explicitly executed
in foreground. A callback subcategory must be subtracted from the parent's
exclusive remainder before presenting additive categories.

Entry/exit markers occur inside register-save/restore boundaries. Identify
unmeasured prologue/epilogue and exception-entry/return time, then bound/calibrate
them; otherwise label measured IRQ interiors rather than claiming every CPU
cycle. Full instrumented IRQ duration includes the instrumentation's own work.
Do not call the foreground C profiler, MOS, output, allocation or a general
timer ownership helper from a hot IRQ marker. Diagnostic hooks must use a
small register-safe leaf and app/owner-admitted storage; no new resident engine.

## Quantization, perturbation and practical alternative

At matched EMOS UART1=1152000, 16 empty-FIFO character times are138.889us,
about10 ticks at /256 or160 ticks at /16. This is not usable spare delay: FIFO
occupancy, peer in-flight bytes and CTS response reduce headroom. Many short
ISRs can quantize to0 or1 tick at /256; summing those durations cannot justify
precise cycle percentages without a quantization bound. More instrumentation
also increases the very RX-service latency under investigation.

Record reader/marker cycle or tick bounds from exact linked code, empty-window
read distributions, epoch/calibration assumptions and instrumentation-on/off
matched behavior. No defensible numerical low-overhead claim follows from C
line count. With931 bytes of free EMOS ROM, any owner debug hooks require actual
linked size accounting; do not presume full vector instrumentation will fit.

If complete IRQ accounting is too invasive, use the already-owned bounded spare-
work probe in the real foreground scheduler and report useful-work units per
valid wall interval against the same probe's quiet baseline. This directly
answers usable bot capacity while naturally paying actual interrupt costs.
It is a workload-equivalent capacity ratio, not exact instruction utilization.
Maintain real queue/decision deadlines and source/RX servicing; calibrate probe
call size, retain state checksum/work count, and never benchmark inside an ISR.
Report partial inclusive transport/IRQ brackets separately. This alternative
does not require a generic UART timing syscall or relaxing any safety contract.

UART has not built, installed or run a profiling variant for this contract.
Root/Extender select and freeze the concrete instrumentation and any finite
qualification through the existing goal/serial compiler/bench workflow.
