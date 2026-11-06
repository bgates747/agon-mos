# Console8 ESP8266 test: no CTS/RTS

Brandon selected vanilla MOS as the default and the C8's configured ESP8266 as
the first physical peer on 2026-11-06. Extender's EMOS adaptation is separate.
No physical test, serial query, firmware change or new peer implementation was
selected by this discussion. The actual ESP firmware, baud and protocol still
were supplied in Extender's existing-source reply, summarized below.

## Existing specimen and protocol facts

Mail `2026-11-06_13-04-09_linux-extender_uart1-vanilla-esp8266-existing-facts-one`
reports Brandon's photographed AT 1.3.0.0 (2016-07-14), SDK 2.0.0 identity.
This is an observed self-report, not a retained BIN, exact source pin or flash
hash. Current accepted host setup is 115200 8N1, flow control disabled. Receiver
capacity is unknown. The original setup/BBS test passed small polling transfers;
it is not an async or continuous-throughput qualification.

Recognized read-only queries: AT -> OK; AT+GMR -> identity plus OK. Existing
network path: normal single TCP connection, AT+CIPSEND=n -> > prompt, exactly n
payload bytes, SEND OK, then a complete length-delimited +IPD reply from the BBS.
Existing payloads are small help/time/uptime/quit commands. Prompt, source
callback, UART drain, SEND OK and BBS response are different witnesses. Announced
length is not a continuously replenished receive credit. No transparent mode,
software flow control, raw echo service or arbitrary receiver reserve is proven.

A prior polling utility missed reception while doing display/SD logging; the
corrected one collected each full reply before logging. This motivates a
caller-owned RX ring and overflow/error accounting, with no foreground output
or SD writes during reply collection. MOS time is 120 counts/s at 60 Hz or 100
at 50 Hz on this setup; the fixture retains raw counts, not invented milliseconds.

The initial no-switch `u1test` fixture is a functional AT/AT+GMR comparison with
ordinary/async sending, exact matched reply text, UART errors/overflow counters
and sequential reports. It does not configure WiFi, start a connection, alter
baud/echo settings, flash the ESP or claim bulk/CPU performance. An unexpected
+IPD or command failure stops the case; no payload is replayed automatically.

## What remains possible

Interrupt-driven UART TX and FIFO-sized OTIRX work without CTS/RTS. Filling
the eZ80 FIFO quickly does not increase the configured wire baud rate: it removes
gaps and CPU work between bytes. The generic sender can offer no-flow-control
mode, ignore CTS and refill on TX-empty interrupts, with no CTS retry timer.

## What is no longer signalled

The ESP cannot request a hardware pause when its receiving software falls
behind. The eZ80 likewise cannot tell it to pause incoming replies/network data
through RTS. Both directions therefore need finite buffering and a protocol or
qualified operating rate. A local transmit callback means source release; local
TEMT means wire drain. Neither proves the ESP received or processed every byte.

Espressif's [ESP8266 UART SDK reference](https://docs.espressif.com/projects/esp8266-rtos-sdk/en/latest/api-reference/peripherals/uart.html)
separately documents configurable RX buffers, hardware flow control and FIFO/
buffer overflow events. It does not establish this installed firmware's buffer
sizes or behavior. Do not import ESP32 defaults or assume a particular ESP-AT
version from the chip name.

## Proposed first comparison

Keep the same baud, peer firmware, byte sequence, data window and response
requirements in ordinary and async cases. Use a bounded request and a positively
identified response/readback/echo if the existing peer supports one. A protocol
acknowledgement may mean only command acceptance, so its meaning must be checked.
Receiver credit or an agreed bounded transaction can control offered data;
waiting between transactions leaves CPU available to the app while TX proceeds.

Start with finite windows, then measure continuous sending separately if the
peer provides adequate reception evidence. Long streams may require an explicit
credit/window protocol. Arbitrary delays or lower baud can help establish a
practical operating point but cannot guarantee against an arbitrarily long peer
stall. XON/XOFF requires support and binary escaping; do not turn it on blindly.

Keep device-specific command parsing/credits out of the generic UART driver.
No new checksum, network protocol, invented ACK, wiring modification or peer
firmware update is assumed. If existing firmware lacks a usable test witness,
agree a separate peer fixture with Brandon before claiming end-to-end integrity.
