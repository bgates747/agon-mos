# U1-001 vanilla driver and ESP8266 fixture — source/build result

Applications can now link the standalone vanilla UART1 adapter, supply RX
storage, start one immutable transfer with a callback, read received bytes and
observe/close after actual wire drain. C and HL/BC/DE CALL entries are implemented.
No MOS/VDP/ESP firmware changes or EMOS hook are needed by this vanilla design.
The implementation has not executed on an eZ80: hardware qualification is next.

Source commit: `510ad1ab26ccd8f3b07b1135b690cf087a7443e0` on
`codex/uart1-app-async`. Identified build: `dac1a97aa944c49c`.

## Actual checks

Compiler 252 built the first vanilla candidate successfully. Inspection found
the new report lacked an exact source identity; this was added to the UI/report
and a separately retained compiler-253 build produced the selected r03. The
receiver-reserve documentation was clarified: no-flow-control batching bounds
local FIFO writes and is not a declaration of remote free space. Both attempts
and source/hash/log evidence remain distinct; no runtime data is relabelled.

ASan/UBSan checks run the actual core and adapter C against a status-acknowledging
fake UART/MOS backend. Core: 168,516 assertions; adapter: 49,635 assertions, plus
AT parser terminal/echo/version/overflow/+IPD negative controls. These assertion
counts describe finite deterministic checks, not independent trials or target
proof. Cases include full-count 65535/65536 transfers, no foreground TX fill,
early completion before submit return, RX-first collection, wrap/overflow,
first-error retention, stop/drain and refusing a live or foreign-owner close.
Foreign-owner refusal does not even acknowledge that owner's LSR error bits.

The native driver, library, simulated-port example and AT query fixture compile
with warnings as errors. Disassembly confirms full-BC initialization before the
bounded OTIRX leaf, register/shadow/index save frames, raw CALL argument stack,
IFF sampling before DI and EI only on the enabled foreground restore path.
No native frame/interrupt instruction was executed. T-001/T-005 retain that
runtime qualification; no overrun/latency/CPU percentage or throughput is claimed.

Object text: core 574 + copy leaf 30 + vanilla adapter 1801 + IRQ/register/I/O
assembly 137 = **2542 bytes of application code**. Internal adapter BSS is 34
bytes, plus caller-provided RX storage. These are object sums, excluding linked
SDK/CRT and caller callbacks, not a firmware-size increment or final link delta.
The earlier 567-byte figure described only the first independent core/copy leaf.

`u1test.bin`: 15,069 bytes; SHA256
`42410864fec9e492899d937152a5954a8b301d1e845449b29bdc26515fc34e5d`.
`libu1.a`: SHA256
`98ef7268b02cfa9d44a8f4f894025325710324a60a945ad932afa5cf4551a3aa`.
The simulated-port example remains `reference/u1check.bin` in the package, and
does not test an ESP8266. Exact input/map/disassembly/log receipts are retained
in `build/u1-001/vanilla-r02` and `vanilla-r03`, selected records in receipts/.

Both compiler checkouts were released with owned children stopped and no waiting
successor: 252 at 18:18:30 UTC, 253 at 18:24:27 UTC (13:18/13:24 EST). No Oryx,
bench, serial port, SD card, live app or firmware was touched.

## Prepared manual appliance

`build/u1-001/vanilla-prepared-r03.zip` contains the identified functional app,
library, exact maintained/generated source, pinned target SDK/notices, compiler
evidence, README.md and hardware-readable readme.txt. Archive/member hashes were
verified; current pin is receipts/vanilla-r03-package.json. It was subsequently
deployed to Console8's card as recorded in console8-r03-deployment.md, with no
hardware run or release publication. No firmware flashing is required.

The fixture compares ordinary/async AT and AT+GMR on unused vanilla UART1,
115200 8N1/no handshake, with complete matched response text, latched UART
errors/overflow, positive teardown and sequential Rnnnn.log/next.txt. No display
or SD writes during reply collection. It does not alter WiFi/echo/baud, connect
to a server or exercise CIPSEND/IPD traffic; unexpected IPD stops rather than
letting payload text mimic an OK line. Source release, wire drain and the peer
reply are separate. Raw MOS clock counts are retained; short AT queries are
functional evidence only. Bulk/CPU tests need a separately selected reception
witness and pacing protocol, as explained in console8-no-handshake.md.
