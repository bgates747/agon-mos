# Finite RX-006 hardware benchmark preparation

Brandon requires actual own hardware qualification and matched old/new pulls,
then small selected-consumer trials. Source reviews alone do not close the goal.

UART owns the synthetic fixture and result analysis; component owners retain
their source/API responsibilities.

Physical Olimex bench procedures are defined only by the
[authoritative bench guide](../../../../agon-extender/docs/operations/olimex-bench/README.md).

## Selected finite checks

1. Positive send/receive correctness at logical sizes 4, 8, 16, 32, 64, 128,
   256, 1024, 4096 and 8092. Upload each as one ordinary buffered-write command;
   keep the resulting single source block immutable during both read methods.
   Compare exact bytes and guards with a deterministic offset-sensitive pattern.
   Check synchronous and RFC25 asynchronous sending. Use an ordered GP reply to
   establish upload parsing; source callback alone is not wire drain.
2. Matched receive benchmarks at 128, 256 and 1024 bytes. Compare existing
   operation6 READ_BYTES (eight payload bytes in each 16-byte private body on
   keycode packet81h) with operation8 counted replies (at most512 bytes each).
   The old method is the existing eight-byte workaround, not an artificially
   weaker two-byte READ16 baseline. Both methods read the same source bytes,
   validate identical output and retain management/error handling.
3. Use whole batches of repeated logical pulls, with upload, source setup,
   printing and SD logging outside the timed interval. Three paired rounds,
   alternate method order, and matched wait/work conditions. Public MOS counts
   give a coarse aggregate clock without taking over any PRT or vector. Do not
   sum individually quantized four-byte intervals or claim calibrated CPU
   percentages. Include batch payload, request/reply counts and kernel work.
   A very short elapsed interval is unresolved, not instantaneous/infinite rate.
4. On success, retire transfers, detach only the admitted application callback,
   clear the owned source buffer and return normally. The results include the exact log and app witness. Any uncertain
   transfer failure keeps source/destination/callback/code resident; no automatic
   replay, false cancellation or MOS return. Bench failure handling is defined by the authoritative guide.

The fixture runtime target is under two minutes; bench operation follows the canonical guide.
One finite attempt at the prepared matrix; failures stop successors for analysis.
Correctness repairs may be followed by a separately frozen necessary retry, not
an optimization sweep. Later owner trials use the measured findings and normal
independent FIFO admission.

## Native build boundary

Build only the original app using the retained existing AgonDev SDK at
`/Agon/mystuff/eirene-mos/build/rc003/toolchain`. One serial `make -j1` plus
listing/map inspection, timeout180s, owned process-group cleanup on failure.
No emulator or hardware is launched by the build. Reserve/assert/release the
normal Pi compiler FIFO and immediately steer the actual next owner on release.
Keep source snapshots and all commands, logs, ROM/map identities and hashes.
An initial build against exact RX005 Eirene may check the app, but is not an
EMOS-qualified artifact. Rebuild/pin the final app against Extender's actual
temporary ROM/map and documented RFC25 admission semantics before bench READY.

## Pending owner tuple and admission

Current EMOS images do not implement26h/90h; no fit or installation is assumed.
The owner must supply receiving-ROM and map, retained rollback and exact producer
pins, active input/route constraints, legacy16-byte callback support and allowed
application keyboard callback state. The app must not silently replace another
callback. Its narrow legacy adapter consumes only tagged VDPL bodies and leaves
ordinary keys to MOS; initial builds require the pinned application callback slot to be NULL;
any necessary forwarding must be explicitly integrated with its owner.
