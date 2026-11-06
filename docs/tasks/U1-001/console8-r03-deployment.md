# U1-001: Console8 functional appliance deployed

Brandon authorized deployment on 2026-11-06 while the separate ESP8266 startup
utility still awaits its first hardware test. Both may run sequentially after
startup completes successfully. Neither utility nor the driver has a hardware
pass from this deployment.

The identified Oryx card is `AGONC8`, UUID `8658-1C23`, mounted at
`/run/media/smith/AGONC8`. The new, previously absent directory `/test/uart1`
contains only `u1test.bin`, `readme.txt`, `package.zip`, `deployment.json` and
`SHA256SUMS`. `package.zip` is the complete prepared source/binary/SDK-notice
and build-evidence archive, unchanged from receipts/vanilla-r03-package.json.
Binary build `dac1a97aa944c49c` and archive hashes match their retained pins.
All deployed payload hashes passed after copying and filesystem sync.

The existing Wi-Fi startup directory, including its private configuration,
and the existing `/test/mos-uart0` firmware, fixtures and reports passed content
hash preservation checks. No private configuration contents were retained in
the deployment receipt. No autoexec, firmware, serial device, network service
or emulator was changed or executed. The card remains mounted; no remount or
eject was attempted.

## Compatible manual sequence

```
cd /extender/network/wifi-start
wifi-start
```

Choose **1** to connect. Wait for **Finished** and the MOS prompt. A completed
ping warning is compatible: a terminal ERROR is consumed and treated separately
from Wi-Fi readiness. Stop if startup times out, is cancelled, or reports that
a module operation may still be pending; do not treat a prompt as proof that an
uncertain ESP operation has finished.

```
cd /test/uart1
u1test
```

No switches or firmware flash. Expect four progress cases, **U1AT PASS**, then
the MOS prompt. Allow one minute; more than two minutes or a stall is failure.
Keep `Rnnnn.log` and `next.txt` here and the startup utility's `progress.log` in
its own directory for inspection. Reset if the fixture requests it.

## Source compatibility review

The staged startup binary matches its own manifest: build
`wifi-start-b2026-11-06-17-51-28Z`, 31,856 bytes, SHA256
`557fb5787f880b9960910dd1a3267244021e8d5cc70483dadc3a7022756ac896`.
Its reviewed main source matches manifest hash
`9d9bd06da47860c91ec7fe5925a2ae2841574d3bce63273f7988655bf345e88d`.
Source: `/Agon/mystuff/agon-extender/tools/wifi-start/src/main.c`, with
`tools/wifi-setup/src/setup.c` supplying `ws_start`.

Startup opens normal polling UART1 and calls `mos_uclose()` after `ws_start`.
It leaves Wi-Fi associated and does not open a BBS connection or install an IRQ
handler. The selected nonsecret card settings are baud 115200 and clock 120
counts/s. The UART1 fixture independently opens 115200 8N1/no-handshake, installs
its temporary application-owned handler, and positively closes/restores it on
success. AT/AT+GMR queries do not require Wi-Fi connectivity or alter network
settings. This supports the sequence by source inspection; actual runs remain
pending. This is functional small-command coverage, not a throughput benchmark.

Receipt: `receipts/console8-r03-deployment.json`. Task T-005 remains open until
Brandon runs the appliance and the returned logs are inspected.
