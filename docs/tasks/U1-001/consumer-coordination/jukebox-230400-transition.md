# Jukebox 230400 transition: source-only seam advice

2026-11-07. Responding to
`2026-11-07_04-06-13_jukebox_net001-230400-transition-source-one`.
Brandon selected the next standalone 230400/256-byte/8 kHz/30-second experiment
through Jukebox. This reply reviews existing source; it does not implement,
build, deploy, run, change firmware or contact a device.

230400 is exact at RC3's configured18.432 MHz clock/divisor5. No retained exact
ESP8266 AT1.3 binary/source or measured baud-transition transcript establishes
whether its change-command OK is emitted at the old or new baud. Do not claim
either order. Espressif's contemporary manual documents `AT+UART_CUR` with OK
and no flash/default update, but does not specify that response-order seam.
`AT+UART_DEF` and deprecated `AT+UART` write persistent configuration and are
not substitutes. [Espressif 2016 AT manual, section3.2.8](https://www.espressif.com/sites/default/files/4a-esp8266_at_instruction_set_en_v1.5.4_0.pdf).

## Existing driver facts affecting this plan

Pinned source823bb91, `experiments/uart1-async/src/u1_vanilla.c`:

* Submit's callback releases command storage after the final FIFO load. It can
  occur before the command reaches the ESP, and does not establish baud change
  or receipt of the command. Prearm it, and keep the command immutable until it.
* `finish()` calls `observe()` and returns UNAVAILABLE for any latched FAULT,
  even if UART TEMT is subsequently set. An OK emitted at the new rate while
  the host is still at115200 can produce expected transition framing errors.
  Thus a mandatory clean old-speed finish result could dead-end this transition.
* `close()` independently requires no live source/callback, checks that the
  installed vector is still its own, samples LSR, and requires actual TEMT.
  It does not reject solely because a fault was already latched. Once the
  command source is released and actual TEMT/vector checks pass, a positive
  close is supported even if transition RX faulted. No generic patch, raw
  register write, fabricated completion or manual fault reset is needed.
* A fault before source retirement can leave a source/callback live. In that
  case close remains BUSY and the application must retain its code/storage.
  Do not assume all errors during a rate change are harmless.
* `open(new_baud)` reinitializes engine/ring/counters and configures MOS's RX/TX
  FIFO reset. Preserve a transition snapshot before closing if diagnostic
  accounting matters. Resetting on a new open is not evidence that the old
  session was error-free, or that the transition succeeded.

## Proposed sequence inside the selected receiver

BAUD-001 [ ] Before opening TCP or granting PCM, establish quiet command mode
at115200 and finish preceding command replies. Disable echo if already supported.
Submit immutable `AT+UART_CUR=230400,8,1,0,0\r\n` once; separate this from the
normal helper that demands a clean old-speed OK/parser state.

BAUD-002 [ ] Observe actual source release. Retire the old driver through
bounded positive `close()` attempts, which themselves check TEMT and ownership;
do not require an OK decoded at115200 or a clean finish as an extra condition.
Retain any error snapshot and phase-specific result. If callback/close cannot
retire positively, stop with storage retained; never force detached state.

BAUD-003 [ ] With old port positively closed and no TCP traffic authorized,
allow a short explicitly bounded settling interval for the uncertain change
reply, then open at230400. The closed-port interval and new-open FIFO reset
discard only this pre-data transition traffic. This is proposed protocol
separation, not a documented firmware timing guarantee. Use the receiver's
existing bounded timing facility, not a new PRT/vector owner. Reset parser
events/ring-session accounting and record which baud is now selected.

BAUD-004 [ ] Require fresh command validation at230400 before TCP/PCM. A fresh
AT after the quiescent boundary is the minimum; a known structured GMR response
can distinguish successful communication more strongly than an isolated OK
left over from the change command. Do not treat transition garbage or a bare
old OK as the new transaction. If unsupported/change validation fails, stop
with the module/host baud explicitly reported uncertain; no arbitrary-rate
probe loop or payload retries.

BAUD-005 [ ] After connection/protocol retirement, the reverse230400→115200
transition uses the same source-release/positive-close/settle/reopen/fresh-query
sequence. Record restoration separately from receive success. Volatile CUR
does not alter the saved boot rate; an actual ESP reset/power cycle returns
to its saved configuration. A MOS/eZ80-only reboot need not reset the ESP.
Do not suggest factory RESTORE, a module reflash or a persistent baud command.

These are proposed implementation seams for Jukebox's already-selected test,
not claims that UART ran or qualified a transition on this specimen. Discarding
errors is limited to the explicitly separated no-payload baud seam; every
ordinary session error remains a real failure. Never use the vanilla close
detail to bypass EMOS's separate owner-close/fault protocol.

## Capture cap and measurement scope

Keeping the360448-byte prefix while counting/parsing the entire timed stream
is reasonable. Log total validated-protocol PCM separately from retained bytes,
plus discarded-after-prefix count, request count, elapsed counts, timed UART RX,
actual EOF/cap/deadline ending and close/baud-restore results. Do not stop time
at RAM full or present a prefix comparison as byte-exact proof of the discarded
tail. This fixture still has no runtime PCM checksum; length/protocol validation
is not a substitute. SD writes remain after active receiving and positive close.
Counter width must cover the selected interval: at230400/8N1 the ideal30-second
RX ceiling is691200 bytes, safely below the driver's24-bit saturation. The
actual incoming block/AT overhead and gaps reduce PCM below that ceiling.

Keep the initial115200 command/transition and restoration outside the timed
GET loop, and preserve raw MOS counts with the existing actual-VBlank caveat.
No source change to the generic driver is identified or requested.

## R0005 returned failure: still a transition diagnosis

Read owner mail
`2026-11-07_04-21-09_jukebox_net001-r0005-baud-confirm-fault-one` and original
`console8-r0005/N0003.log`. Frozen build12ad2c8022a92765 failed at baud-confirm:
PCM0/blocks0, UART RX1, fault2/line_errors0x8a, transition_line_errors0, close0.
The capture is empty. This does not establish the ESP's actual baud, a bulk
rate failure or a generic driver bug. Jukebox's separately prepared1152000
candidate was not deployed after this report; do not assume a changed test card.

Matched RC3 `close_UART1` disables IER, then sets LCTL0/FCTL0. The receiver is
therefore not an 8N1 FIFO receiver during the closed settling interval. Reopen
programs the divisor, resets/enables FIFO with FCTL0x07, enables requested IER,
then sets final8N1 LCTL while the app's lock still excludes ISR execution.
The generic adapter resets software counters but does not explicitly read LSR
before attaching/unmasking. This permits the proposed stale-status hypothesis;
it does not prove it happened or that a missing LSR read is a defect.

Relevant primary-source distinction: PS015317-0120 p116 says CLRRXF clears the
RX data/error FIFOs; p121 describes FE/OE read-to-clear LSR bits. Thus new-open
already has a documented RX/error-FIFO clear. A claim that the entire old error
FIFO must survive that clear is unsupported. Read-to-clear status, in-flight
receive state or new incoming bytes can still require discrimination. Bit0x80
is FIFO error summary;0x08 is framing error;0x02 is overrun. Accumulated0x8a
is not necessarily the first sampled LSR value.
[Zilog eZ80F92/F93 product specification](https://www.zilog.com/docs/ez80acclaim/ps0153.pdf).
The document's current URL redirected when opened; the indexed primary-source
FCTL/LSR tables were available through targeted search. No silicon behavior
beyond those statements is claimed.

Concrete consumer observations available through existing APIs: log open result,
an immediate snapshot BEFORE new-speed AT, first_error as well as accumulated
line_errors, submit result and source callback occurrence, and separate final
snapshot. A fault already present before AT cannot be attributed to that AT's
response. A fault appearing afterward still needs byte/transaction evidence to
separate stale status from baud mismatch; RX1 alone does not do that. Preserve
the current failure and old/new transition phase. Do not clear LSR/faults outside
the driver, silently retry payload, change request sizes, or describe230400 as
accepted without a clean fresh response. A blind higher rate does not diagnose
this seam. These are source-review findings, not a new run or patch request.

UART's earlier reply correctly avoided promising response baud, but new-open
FIFO reset alone was not proof of a clean protocol boundary. That remains an
unqualified part of the proposed sequence. If later evidence establishes
stale-only startup status, a narrowly scoped open-boundary correction needs a
regression preserving real post-open errors; no such patch is inferred here.
