# U1-001: first Console8 return and ordinary-byte correction

The Wi-Fi connection utility succeeded. Our UART1 fixture stopped after its
first ordinary byte because its selected SDK C wrapper reports successful MOS
transmission as failure. The asynchronous cases were never reached. This run
does not establish an ESP8266, MOS firmware or asynchronous-driver failure.

Brandon reported startup success and first-case failure on 2026-11-06. The
identified returned card was AGONC8 / UUID8658-1C23. Original files were retrieved
without copying private configuration or changing the card. Pins are retained
in receipts/console8-r01-return.json; raw archive and startup log are retained
under build/u1-001/console8-r01-return, not published with private network data.

The startup log identifies wifi-start-b2026-11-06-17-51-28Z and reports both
pings passed (7ms and5ms), Wi-Fi ready and its UART closing at7seconds. This is
one successful manual startup run, not BBS/continuous-traffic qualification.
The result was mailed and chat-notified to its Extender owner.

## Failure evidence

R0001.log identifies the deployed build dac1a97aa944c49c, result1, close31,
received0, overflow0, fault0 and errors0. Case1 has pass0/work0/reply0 and all
later cases are unstarted. The returned executable's hash matches deployment.

The linked `_mos_uputc` wrapper at0x431e8 contains, after RST.LIL08h:

```
ld a,1
jr nc,exit
xor a
exit: ret
```

MOS UART1_serial_PUTCH documents and implements carry SET if written, CLEAR
if the port is disabled. This wrapper thus returns0 on success and1 on failure,
opposite its C declaration's documented contract. `query()` checked that C
result, so it can send only the first `A` before returning, never completing
`AT\r\n`. Empty RX and an immediately busy close are consistent: the single byte
may still be shifting at close. Close31 alone does not identify a vector fault.
No native trace establishes the exact moment that hardware drained.

This inspection uses the retained SDK source at
/Agon/agondev/src/lib/libmos/mos_uputc.src and the actual returned binary.
MOS behavior was checked against serial.asm's UART1_serial_PUTCH in the existing
Eirene source. Extender's already separate wifi_try_put handles carry correctly.

## Correction and verification

The fixture-local at_putc.src wraps unchanged public MOS18h, returns1 on carry
SET and0 on carry CLEAR. It does not perform a direct UART write, change the
SDK or alter driver/firmware code. Reports additionally identify their failure
stage and accepted ordinary-byte count, keeping the same four queries.

Compiler255 built build/u1-001/vanilla-r05. The attempted r04 stopped before any
compiler/check child because the sandbox could not lock the lease registry;
its result remains retained. Native execution with ordinary escalation used
the actual lease and completed all finite host/native checks. The linked-byte
checker supplies both MOS carry outcomes to the actual post-syscall instruction
paths: returned old binary gives success0/failure1 (negative control), corrected
shim gives success1/failure0. This is static instruction-path verification,
not an executed eZ80 or UART simulation.

Core168516 and adapter49635 deterministic host assertions plus parser controls
pass under sanitizers. Native build links with warnings as errors. Actual
driver object text remains2542bytes, unchanged source. Compiler255 released at
19:35:23UTC with owned children stopped and no successor.

Selected corrected fixture: build1bfe14ccd35b03aa,15258bytes, SHA256
6ac253927f4d8c1c96109be2829665ce8ffed003d8b824f5de81b90f6302f593.
Hardware rerun remains pending. Power-cycle Console8 and its ESP8266 before
rerunning to clear the incomplete AT line and old app/IRQ state. The startup
utility remains unchanged; test it first, then run `/test/uart1/u1test.bin` by
typing `u1test` from that directory after startup finishes normally.

## Replacement deployed

The corrected app and complete source/build package replaced the five owned
payload files in `/test/uart1` on the same identified card. All old payload
hashes were checked before replacement; all new payload hashes passed after
copy/sync. R0001, next.txt and other reports passed preservation checks, as did
the entire Wi-Fi startup directory/private configuration. Card remains mounted.
No firmware or device was executed or changed during deployment.

Package source is pinned to commit823bb91dd4c1af5a1488e3d3361648646b601445.
ZIP355785bytes, SHA256
53797bed1686fe1e7666ed31cbafd29235f3e07e6ed0dbe91b917a8efbc61fe1;
157 members verified against the included manifest. Package and deployment
pins: receipts/vanilla-r05-package.json and console8-r05-deployment.json.
No old native result or successful startup result is relabelled as a corrected
UART1 hardware pass. That rerun remains the next manual task.
