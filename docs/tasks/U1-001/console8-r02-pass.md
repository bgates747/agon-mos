# U1-001: first successful Console8 UART1 functional run

The standalone UART1 driver sends small AT commands in the background, receives
the ESP8266's replies by interrupt and closes normally on Console8. Brandon
reported an apparently good test and returned the card on2026-11-07. R0002
confirms all four cases passed on corrected build1bfe14ccd35b03aa.

This is the first hardware pass for the vanilla driver. It demonstrates the
small-command interrupt/callback path on the configured no-handshake ESP8266.
It is not a bulk-transfer, full16-byte TX burst, multi-FIFO TX, CPU-headroom or
EMOS-adapter qualification: these commands are only4 and8 transmitted bytes.
The109-byte version replies do exercise interrupt reception beyond one FIFO.

## Verified report

| Case | Send method | Command | Reply bytes | Result |
| --- | --- | --- | ---: | --- |
|1|Ordinary public MOS byte calls|AT|6|PASS|
|2|App-owned async UART1|AT+GMR|109|PASS|
|3|Ordinary public MOS byte calls|AT+GMR|109|PASS|
|4|App-owned async UART1|AT|6|PASS|

Each case has pass1/stage4. Both AT transcripts match byte for byte; both GMR
transcripts match byte for byte and report AT1.3.0.0(Jul14,2016),
SDK2.0.0(656edbf). All230 received bytes are accounted for by the four retained
transcripts. Header and final marker both report result0, with close0, fault0,
errors0 and overflow0. next.txt is3. Original R0001 is byte-identical to the
archived failure, not overwritten or relabelled.

The fixture's async pass condition requires its prearmed callback flag, a later
positive TEMT observation and a complete OK reply. Thus both async callbacks
and drain were observed, but callback exact counts/register stress were not
instrumented in this run. close0 follows the checked ownership/wire-empty path
and executes UART close/previous-vector restoration. No independent post-close
vector readback is recorded. The logged successful close selects the normal
return path rather than the retained-RAM halt. There is no screenshot or direct
live-console capture here.

The raw call/total MOS counts are0 for three cases and2 for ordinary GMR;
foreground loop counts are11/20/11/11. These short operations and clock-phase
quantization cannot establish throughput or CPU recovery. No percentage is
derived from them.

## Provenance and archive

Card label AGONC8, UUID8658-1C23. Its current host mount is
/run/media/smith/AGONC81; the suffix is a host mount-directory distinction, not
a renamed volume or a different card. Identity was checked before retrieval.
No card file, firmware, running hardware or private configuration was changed.

u1test.bin15258B, source823bb91dd4c1af5a1488e3d3361648646b601445, SHA256
6ac253927f4d8c1c96109be2829665ce8ffed003d8b824f5de81b90f6302f593.
All payload hashes match their card manifest and retained project pins; full
package SHA25653797bed1686fe1e7666ed31cbafd29235f3e07e6ed0dbe91b917a8efbc61fe1.
No MOS/VDP installed-image readback is implied by application identity.

Raw UART report: receipts/console8-R0002.log. Retrieval hashes:
receipts/console8-r02-return.json. Byte-level report checks:
receipts/console8-r02-analysis.json. Full returned appliance, autoexec and Wi-Fi
progress archive: build/u1-001/console8-r02-return/returned.tar. The private cfg
was not copied. Raw progress data remains outside public notes; the new startup
session reports both pings9ms/7ms, Wi-Fi ready and normal UART close at7seconds.

T-005 is complete. T-001's wider interrupt/length/register cases, T-003's matched
bulk/compute tests and T-004's larger no-handshake windows remain open. Extender
still owns any EMOS adapter; this does not qualify replacing its UART1 RX owner.
