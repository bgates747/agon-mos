# Application-space UART1 sender — U1-001

Default: vanilla MOS, an otherwise unused UART1, ADL1 and actual MB0 while the
driver is installed. This original library lives in application RAM. It uses
normal MOS UART1 open/close and vector 1Ah APIs; no MOS patch, new syscall, RST
edit, private ROM address or resident engine. Extender owns its separate EMOS
adaptation. Do not use this standalone installer on EMOS or a resident-owned port.

Implementation and host/native checks are prepared, but neither native fixture
has run on hardware/emulator. This is not yet a qualified deployment/release.
First physical peer is the Console8 ESP8266 at 115200 8N1 without CTS/RTS.

## Calling the driver

Use include/u1_vanilla.h and link libu1.a plus the normal AgonDev target SDK.

- `u1_vanilla_open(baud, rx_storage, capacity)` installs the app IRQ and opens
  UART1 as 8N1/no flow control. Caller-owned RX storage must remain resident;
  capacity is a power of two, 2..4096, with one slot reserved.
- `u1_vanilla_submit(source, full_count, callback)` starts one positive immutable
  span. Prearm the callback flag BEFORE calling: callback can precede return.
  Result A/C uint8 is 0 accepted, 19 invalid, 31 busy, 32 unsafe or 35 unavailable.
  These are library results, not a numeric MOS syscall ABI. No payload retry.
- `u1_vanilla_read()` returns 0..255 or -1 for empty/closed. RX runs independently
  of foreground calculation. RX overflow and line errors are latched/reported.
- `u1_vanilla_finish()` is nonblocking: 0 physically drained, 31 busy, 35 closed
  or faulted. It does not perform foreground TX. Callback releases source;
  finish observes wire drain; peer acknowledgement/execution is separate.
- `u1_vanilla_close()` refuses borrowed source, nonempty wire or a later vector
  owner. Only positive close allows unloading driver/RX storage. Stop refuses
  NEW work while continuing the accepted span. A live fault retains source/code;
  a timeout never cancels it. Snapshot exposes phase/first fault/RX counters.

A flag-only assembly callback with RET is the initial target convention: no MOS,
output, EI, wait, MB change or reentrant submission. The example is
fixture/at_callback.src. Keep MB0 and interrupts enabled for the installed driver;
no competing MOS uputc, ugetc, vector or UART configuration calls. UART0 is separate.
The comparison fixture's ordinary sends occur only with async TX idle.

Assembly CALL `u1_vanilla_submit_regs` accepts HL=source, full BC=count,
DE=callback and returns A=result, preserving primary BC/DE/HL, indexes and shadows.
Use the C function for ordinary C callers. Neither entry is a MOS syscall.
Interrupt wrapper saves primary/index/shadow registers; RX drains at most sixteen
bytes first, followed by at most one sixteen-byte TX refill. No UART wait loop
runs under DI. Incoming IFF is preserved by foreground lock/unlock helpers.

## No handshake and peer pacing

The vanilla adapter ignores absent CTS and refills the LOCAL FIFO on TX-empty.
It does not need a CTS retry timer. OTIRX does not raise the wire baud rate.
No-flow-control mode cannot infer the remote buffers or guarantee reception of
an arbitrary continuous stream. Protocol pacing/credits and peer responses stay
in the application. Both directions can overflow without adequate servicing.

The portable core's reserve parameter is a backend-authorized burst ceiling.
For CTS-based adapters it must include receiver headroom after CTS changes.
For no-flow-control adapters it bounds local writes only and does not establish
remote credit. Extender's GPIO-CTS retry and shared receive integration belong
in its adapter, not this vanilla driver. The core never reads LSR or installs
vectors; all actual UART accesses are confined to the vanilla adapter/copy leaf.

## Prepared fixtures

`u1check` is a simulated-port core example. It never calls the hardware emitter.
`u1test` is a Console8 functional AT query check: ordinary/async AT and AT+GMR,
matched complete replies, source/drain observations, UART errors/overflow counters
and sequential Rnnnn.log/next.txt reports. No switches. It requires idle AT command
mode and unused UART1. It makes no WiFi/network/flash configuration changes.
Unexpected +IPD, ERROR/busy, overflow, reply mismatch or timeout stops the suite;
uncertain live ownership retains the app until reset. Allow one minute; more
than two minutes is wrong. The screen clears and prints case breadcrumbs.

Only source/build work is complete. No card deployment, ESP query or physical
pass is implied. Small AT queries are FUNCTIONAL evidence, not throughput/CPU
capacity measurements. Full-stream tests need their own reception witness.

## Rebuilding

After obtaining a real Pi compiler checkout, supply its actual token/generation
and a NEW output path to preserve previous attempts:

```
python3 build.py --lease ACTUAL_TOKEN --generation ACTUAL_GENERATION --out /absolute/new/output
```

The finite script runs actual-core/adapter/parser ASan/UBSan host tests, links
both native fixtures, and archives library/maps/disassembly/hashes/logs. It
embeds the source-set identity in u1test's screen and report. No guest or device
is executed. Compiler executables are external; the pinned SDK used here is
/Agon/mystuff/eirene-mos/build/rc003/toolchain, with libagon.a SHA256
04e340186590810dd490d01655b50baaca557b7764006598890e845e6fc1252c.
Release after owned children stop; notify the actual successor if any.

See [U1-001](../../docs/tasks/U1-001/README.md) for task and evidence boundaries.
