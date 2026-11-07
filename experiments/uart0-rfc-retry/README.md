# Bounded CTS retry: private RFC25 derivative

Replace the UART0 sender's indefinite interrupt-disabled CTS wait with immediate
deferral and later VBlank rearm. Original and candidate native ROMs assemble/link;
source/linked structural and startup checks pass. No ISR/guest/hardware execution
has occurred. This is not an installed, released or physically qualified MOS.
The failed EMOS trial76's receive-overrun cause is still unresolved.

Donor Eirene source97311c437093e416342a6c836cf9914f2ced027d preserves Tom Morton's
RFC25 implementation and MIT attribution; modifications are MIT. This Eirene
donor itself uses AgonDev; no ZDS II firmware toolchain is changed. Published
RC3 remains unchanged. Owning scope/plan: ../../docs/tasks/U1-001/goal001-rfc25-retry-plan.md.

## Implementation and exact cost

`bounded-cts.patch` changes serial.asm and interrupts.asm only. Source snapshots
normalize CRLF to LF for the portable patch. `prepare.py` reconstructs the exact
private source pair from the pinned donor, avoiding mutation of a live checkout.

* CTS admission precedes any source/count mutation. STOP disables only TX-empty,
  sets retry_pending and returns through the original saved-AF/EI/RETI frame.
* `uart0_async_retry` under the existing VBlank saves/exclusion does no I/O while
  inactive, samples CTS once while pending and only rearms TX-empty when ready.
  UART0's normal TX ISR remains the sole copier; no extra timer/syscall/queue.
* Positive admitted copy, mixed-mode callback thunk and FIFO-final callback ABI
  remain the donor's. Source callback still precedes possible wire drain.
  The donor retains its one-outstanding valid-caller precondition; no BUSY API
  or input validation has been added. Legacy synchronous paths are untouched.
* Paired native object text: serial390→438 (+48); interrupts378→382 (+4).
  Total+52 ROM bytes/+1 BSS byte. No cycle/CPU/throughput result is claimed.

VBlank retry may delay resumption by a full refresh interval. It removes the
unbounded masked spin, not a specified amount of receiver latency or a proven
physical failure. The one CTS check per16-byte fill still needs receiver reserve.

## EMOS owner splice requirements

Extender owns the derivative integration. The standalone patch does not install
in EMOS unchanged. Map its helper/flag into the guarded owner composition and
retain RX-first/LSR/serializer/mode/callback/register rules. In particular:

* `_emos_uart0_async_owned` must check retry_pending BEFORE IER/TEMT; disabled
  TX-empty and empty wire do not retire a still-deferred source. Admission,
  route/reset/exit retirement must not mistake that state for completion.
* Owner abort/reset must atomically clear deferred retry with its existing
  actual teardown. A later VBlank must never rearm an abandoned source. Do not
  add a silent cancellation that frees storage while an active ISR owns it.
* Call the rearm helper only under existing admitted VBlank exclusion and full
  saves. Its vanilla version uses only A; owner glue must preserve its C/IRQ
  contract and actual register sets. No new timer ownership is needed.
* Retain source callback plus later TEMT and the consumer's reciprocal UART0/NM
  gate. This derivative does not establish live UART1 health or solve trial76.

Only Extender's actual linked composition determines fit within its931 free
ROM bytes and integration behavior. This standalone result is not that build.

## Reproduce offline

Prepare source copies in a new output directory:

```bash
/Agon/mystuff/agon-dev-env/.venv/bin/python \
  /Agon/mystuff/agon-mos/experiments/uart0-rfc-retry/prepare.py \
  --donor /Agon/mystuff/eirene-mos --output /tmp/new-rfc25-pair
```

Compile only under actual Pi serial compiler FIFO: `build_pair.py` requires
`--pair`, `--toolchain` and a real `--lease`, asserts ownership, enforces finite
limits and releases after owned processes join. The release may automatically
grant a successor; notify that actual owner immediately. No guest or device
action is part of that script.

`verify.py` is read-only source/linked inspection; it requires `--pair`,
`--toolchain`, `--donor`. It rejects original unbounded async WAIT_CTS plus seven
malformed candidates, checks exact final linked defer/rearm/branch bytes and
the VBlank hook, and runs the existing startup invariant plus six mutation
controls on both ROMs. It does not execute the eZ80 instructions or emulate CTS.
IER preservation over256 values is bit algebra, not256 executed interrupts.

Retained pair: /Agon/mystuff/agon-mos/build/goal001-uart0-retry/pair-r01.
Compiler318 released after3.875s actual paired build, all owned children joined;
Extender319 actually autogranted and immediately notified. Structural checks ran
as brief retained-source/binary inspection after release, not a second compile.
No emulator/device/SD access occurred. The current installed SDK can differ from
the frozen RC3 release SDK; original here is a paired source rebuild, not a claim
of byte-identical reproduction of the published RC3 artifact. Exact pins/results
are retained under docs/tasks/U1-001/retry-r01 in this project.
