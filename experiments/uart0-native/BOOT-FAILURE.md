# Native MOS boot failure audit — 2026-10-16

Executive summary: the firmware we supplied contains a definite startup error.
It configures the connection to the VDP eleven times too slowly, then waits for
a reply before printing the MOS banner. That explains the reported blank MOS
startup even if the flash completed perfectly. The calculation is corrected
and passes tests that execute the actual firmware instructions. The replacement
remains off-device; recovery belongs to the Author and Extender agent.

The error was already present in the adopted native foundation. Our qualification
failed to catch it before deployment. The background sender does not have to be
opened for this error to occur. Stock, approved MOS is not the native foundation
control discussed below.

## Incident and exact images

The Author reports an updater countdown with no apparent automatic reset,
followed by a manual reset and two full power cycles. The VDP banner appears;
the MOS banner does not. No physical flash readback was obtained by this agent.

| Image | Bytes | SHA256 | Status |
| --- | ---: | --- | --- |
| Deployed `uart-010-final` | 104658 | `5543d6acaa64bebd3006cb034a8dda9b61cfe92c82cbbffe2c391a9392f0f4c9` | Withdrawn; proven wrong divisor |
| Clean native foundation `stock-002` | 102055 | `f891721bbb2a0bc2845dbb13edbeb449365a315f11be48500d8e65e2ab1aebb4` | Same defect; not a hardware-qualified stock recovery image |
| Corrected `uart-012-boot-audit` | 104636 | `680daf76d6a0e4073f43130fda48fdcf681a4570ac709f99dd3c9e04335e6e79` | Software passes; not deployed or physically accepted |

The corrected image has file CRC32 `085DB775`, erased-tail 128KiB ROM CRC32
`4E326ABC` and zero-tail emulator CRC32 `1FC71F0A`. These identify an off-device
artifact; the existing card menu still targets the withdrawn image and is not
a replacement package.

## Confirmed cause and correction

In `src/uart.c`, both UART-open routines used:

```c
UINT32 cb = CLOCK_DIVISOR_16 * pUART->baudRate;
```

AgonDev's ordinary integer and `UINT24` are 24 bits. Assigning the result to a
32-bit variable happens after multiplication. At 1152000 baud,
`16 * 1152000 = 18432000` wraps modulo `16777216` to `1654784`.
Dividing the 18432000Hz clock by that result gives divisor **11**, not **1**.
The resulting physical line rate is about **104727 baud**, while the VDP expects
1152000. `wait_ESP32()` cannot complete its general-poll exchange, so execution
never reaches `bootmsg()`.

Both routines now widen an operand before multiplication:

```c
UINT32 cb = (UINT32)CLOCK_DIVISOR_16 * pUART->baudRate;
```

The change preserves source line endings and other UART behavior. No sender,
receiver synchronization, descriptor lifetime or public API rule was changed.
Only our isolated native worktree was edited; foundation/infrastructure owner
checkouts, upstream VDP and SDK sources remain untouched.

## Before/after proof

`boot_audit.rs` executes the actual linked UART-open instructions and records
DLAB-selected divisor writes, rather than evaluating a copied C formula.
The same final harness runs the withdrawn image, clean native control and
corrected image. Evidence is in `build/uart0-native/boot-{withdrawn2,foundation2,fixed2}`.

| Requested baud | Withdrawn UART0/UART1 divisor | Corrected UART0/UART1 divisor | Required divisor |
| ---: | ---: | ---: | ---: |
| 9600 | 120 | 120 | 120 |
| 115200 | 10 | 10 | 10 |
| 384000 | 3 | 3 | 3 |
| 576000 | 2 | 2 | 2 |
| 921600 | 1 | 1 | 1 |
| 1048576 | 65535 | 1 | 1 |
| 1152000 | 11 | 1 | 1 |

All three images execute reset/startup to `main` under both cold-memory and
retained-memory conditions. The minimal boot peer accepts communication only
with the correct divisor. Both old images keep polling with GP zero; the
corrected image receives GP, mode and palette replies and reaches `bootmsg`.
Its UART0 ISR preserves registers and the stack while parsing those replies.
The modeled boot timer reload is 11520, and minimum observed boot SP is BFFB2h.

The root linked-image guard now requires the pinned compiler's 32-bit shift
and division helpers in both UART-open routines and rejects the old 24-bit
shift. The full withdrawn ELF fails for the expected baud-calculation reason.
Suite deployment rejects the exact withdrawn MOS hash before discovering or
accessing media. Historical packaging/sealing helpers also reject that image.
The rejection was tested using a host temporary directory, without card access.

## Remaining code and image review

| Area | Audit result and limits |
| --- | --- |
| Reset, ADL entry, external/internal RAM setup, C startup | Reviewed source and executed the linked cold/retained-memory paths. Data copy, BSS clearing, default vectors and arrival at `main` pass. The test uses flat memory/register latches; it does not physically measure wait states or chip selects. |
| ROM layout and flash packaging | Shared linker/runtime guards pass; image is below 128KiB and starts at reset address zero. Original package, hashes, source and failed image remain archived. There is no board readback, so a second flash-write problem is not excluded. |
| RAM, vectors, heap and stack | Static state ends at BCB31h; heap stops at BF800h; the 2048-byte stack ends at C0000h. The heap uses the linked start dynamically, so the additional UART state does not overlap it. Initialized data and vector storage remain separate from cleared BSS. |
| Closed-session boot receive/transmit | Reviewed the new IIR dispatch, shared status readers, saved BC, sole MOS parser, initial IER and initialization order. The sender is closed, batch defaults to 1, and the corrected boot peer reaches the banner call without opening an async session. |
| Open-session ownership and lifetime | Reviewed descriptor spans, CTS admission/wakeup, bounded refills, parser exclusion, synchronous barriers and OSCLI/return/callback/crash fences. Actual-ROM policy, descriptor, source-boundary and integration checks pass with the corrected image. No additional defect was identified in these hooks. |
| Existing oversized VDP packet handling | The previously documented foundation defect remains excluded from this UART port. It is separate from the short boot replies and this proven baud error; no claim of a general MOS audit or release approval is made. |
| Automatic reset after updater countdown | The local upstream updating guide documents that automatic reset can occasionally be missed. That observation cannot establish an interrupted write. The firmware error is independently sufficient to prevent MOS startup. |

Nine native source/interface tests and the root firmware checks pass. The
actual-ROM oracle passes each batch policy 1/2/4/8/16 with 27 integration,
538 policy, 425 descriptor-boundary and 150 source-boundary cases per policy.
Missing CTS guard, excessive refill and early source-release controls still fail
for their intended reasons.

Both Flexe engines pass the corrected-image campaigns with actual compiled
repaired diagnostic ESP32 firmware and FAT media: per engine, 40960 receiver-CRC
bytes, 163840 final-buffer bytes compared, 640 ordered replies, 10 CRC cases
and 20 full-duplex cases. JIT took 119.768 seconds; interpreter took 266.403
seconds. These are host test durations, not hardware throughput measurements.

## Why earlier emulator checks passed

The serial link transports decoded bytes. Its UART model uses the divisor for
delivery timing, but the byte link does not model a mismatch between transmitter
and receiver bit rates as a physical framing failure. The existing isolated
sender oracle also seeds initialized UART state instead of booting hardware.
Therefore successful byte transfers did not validate the boot divisor. Our
acceptance checks should have asserted that register value; this was a gap in
our qualification, not evidence that the shipped image was physically sound.

## Evidence, reproduction and disposition

N-007 is the completed off-device audit. N-006 remains the separate replacement
qualification and physical acceptance task; hardware readiness stays withdrawn.
No board access, SD writes, firmware flashes, recovery action, commit or push
was performed during this audit. The Author and Extender agent handle recovery.

On Oryx, from the primary agon-mos directory, use a fresh attempt name:

```bash
.venv/bin/python experiments/uart0-native/boot_audit.py \
  --native ~/Agon/mystuff/worktrees/uart-native-001/uart \
  --mos-build uart-012-boot-audit --attempt newaudit
```

The runner records the exact ROM, ELF, harness and CPU dependency hashes.
It models register latches, immediate timer expiry and interrupt delivery with a
minimal boot peer, rather than actual ESP32 firmware or physical serial timing.
Both-engine campaigns separately exercise compiled ESP32 firmware. Neither
proves what bytes were written to the board's flash.

Retained early harness attempts include a wrong default-vector symbol and a
minimal peer that left timer counters at their reload values. Final matched
`*2` receipts correct those harness issues; no failed evidence was overwritten.
Earlier software PASS, deployment and source archives remain intact. The new
incident receipt and closeout archive index are `incident.json` and
`boot-audit-archive.json` beside this report.
