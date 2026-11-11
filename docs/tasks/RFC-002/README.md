# RFC-002 — Review three Eirene MOS syscall proposals

**Status: deferred until Brandon returns for review on November 15, 2026.**
This task records the review and test plan. No firmware builds, test runs,
bench reservations or upstream comments are part of this preparation.

Tom Morton invited feedback on three syscall RFCs. Review them independently,
then check how they interact. Give each proposal an API and compatibility
assessment, a reproducible test result, and a recommendation for upstream.
Treat Tom's approximately 82% free CPU figure as a measurement to reproduce,
with its workload and denominator stated.

| RFC | Proposed API | Head verified November 11 |
| --- | --- | --- |
| [PR #4: Buffered keyboard events](https://github.com/AgonPlatform/eirene-mos/pull/4) | `62h`, poll the next key event | `241ffbaee4bc7e3f814124b59e0b8c07207a9409` |
| [PR #1: Override RST.L vectors](https://github.com/AgonPlatform/eirene-mos/pull/1) | `61h`, replace a restart handler and return the previous one | `604640eb882c3dfeb870a8c4aaaa7e155c23d0ad` |
| [PR #2: Async UART0 send](https://github.com/AgonPlatform/eirene-mos/pull/2) | `25h`, submit a borrowed source buffer and callback | `ffab9c9c84a31535d1ec976b7e6f23b2579ecb80` |

All three were open and unmerged when recorded. Recheck their heads and
review discussions before starting. Pin the exact base, candidate, firmware
binaries, toolchain, platform and fixture for every result. Keep an upstream
baseline, one isolated candidate per RFC, and a combined candidate only after
the individual checks pass. Account for [PR #3's startup fix](https://github.com/AgonPlatform/eirene-mos/pull/3)
when comparing older RFC bases. [Fork RC3](https://github.com/bgates747/eirene-mos/releases/tag/3.1.0_uart0_rc_3)
already combines that fix with PR #2; preserve its identity as a separate
reference. Reuse the existing [UART evaluation](../../../../eirene-mos/docs/tasks/RFC-001/README.md)
and retained results where the revision and workload match.

## Review and test cases

### Buffered keyboard events (PR #4)

- Review the four-byte event layout, empty return, queue capacity and overflow
  policy, and what happens when the interrupt producer and poller overlap.
  Check how the new queue coexists with the legacy callback and held-key map.
- Poll empty, then replay a known sequence of key down/up, repeats and modifier
  changes. Compare all event bytes and order against that sequence. Fill the
  queue, cross its wrap boundary, and verify its documented overflow behavior,
  empty transition and recovery. Check output-buffer guards and caller state.
- Compare existing key reads and callback behavior on baseline and candidate,
  with and without polling. Include a tagged display reply where supported:
  private data must not become a user key event, and existing consumers must
  still see their expected callback data.

### RST.L vector override (PR #1)

- Review which vectors the API accepts, the caller and handler modes, register
  and interrupt-state preservation, and ownership of the installed handler's
  storage. Check initialization, restoration and the contract for unsupported
  inputs in source before planning any execution of those cases.
- In an isolated emulator fixture, install a resident counting handler on a
  supported vector. Verify the returned previous handler, exactly one dispatch,
  and normal return with the documented register/stack behavior. Exercise
  chaining and replacement, restore the previous handler, and verify ordinary
  dispatch again. Check the default after reset. Keep callable code resident
  until restoration is confirmed.
- Verify ordinary syscall and VDU output remain usable before and after the
  fixture. Exercise syscall-vector replacement only after the review establishes
  a supported route for invoking restoration.

### Async UART0 send (PR #2)

- Verify exact received bytes and one source-release callback for short,
  FIFO-boundary and multi-burst transfers, including 1, 15, 16, 17, 32, 256
  and 1024 bytes. Check completion before submit returns, source reuse after
  release, and separate wire drain before ordinary output. Review valid caller
  context and unsupported calls; do not assume the raw A register is status.
- During finite receiver backpressure, measure keyboard/RX and timer service,
  then confirm byte integrity, completion and normal return. Separate modeled
  behavior from hardware evidence. Preserve the first failure.
- Reproduce Tom's reported tight assembly loop over a fixed number of VSyncs
  with and without sustained transfers. Report foreground iterations during
  transfer divided by idle iterations over equal windows, plus measured
  payload rate. Compare with matched synchronous sends and include a fixed-rate
  case so a throughput change is visible. Use repeated samples and report
  spread. An idle-normalized loop ratio measures available work in that
  fixture; it does not directly measure game FPS.

## Execution order and handback

1. On revisit, review source and prior evidence first. Specify expected
   outcomes, bounded timeouts, test artifacts and the smallest useful matrix.
2. Use Alexe for the isolated correctness cases first. For the combined
   candidate, check key-event delivery during async TX and legacy output after
   vector restoration. Keep renderer/game changes outside this task.
3. Select a finite Console 8 confirmation for hardware-sensitive keyboard,
   UART and CPU results. Use normal scheduling and firmware ownership rules;
   keep boot scripts intact and record firmware restoration or handback.
   Distinguish bare Eirene from any separately selected EMOS composition.
4. Return a short per-RFC verdict with exact revisions, expected versus actual
   outcomes, raw evidence and unresolved cases. Draft upstream feedback for
   Brandon to review before posting.
