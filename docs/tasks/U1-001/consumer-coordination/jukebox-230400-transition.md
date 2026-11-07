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
