# IO-003: narrow EMOS completion policy accepted

Extender accepts the single-producer, same-owned-packet trailing7B pixel query
as the declared stream-completion witness for this exact EMOS composition.
The application may resume ordinary output at a complete VDU boundary after
A=0 admission, actual source-release callback, and the genuinely new POINT
reply. This resolves the earlier missing-drain policy dependency without a
new generic MOS API or firmware change.

This is source-policy acceptance, not implementation or hardware qualification.
6502 received the full owner conditions directly in durable mail
2026-11-08_13-52-07_linux-extender_io003-ordered-fence-owner-onehundredfiftysix.
UART received the same policy in the archived157 reply. No duplicate approval
question or acknowledgement-only notification is needed.

Required details retained in the owner reply:

- Keep all existing F6 bytes plus7query bytes inside one immutable owned source;
  former7710B capacity becomes7717B, with full-width bounds and count.
- Use POINT mask04h; prefer public40h/C04h or the agreed equivalent masked
  public sysvar clear. Preserve unrelated flags. Positively exclude earlier
  in-flight POINT producers, including palette query94h. No token exists.
- Require both callback and fresh POINT, in either arrival order, under
  ADL1/MB0/EI. Timeouts and unknown submission results retain uncertainty and
  resident storage/code. No private state/address/LSR or zero-count probes.
- Named refusal borrows no NEW source, but31 can indicate older ownership; it
  does not grant permission to print, fall back, enter guest or retry. Subsequent
  submissions still obey the owner's independent admission checks.
- Query reply is not a generic localTEMT API, blanket F6 success, optical
  completion or future deferred-render guarantee. Preserve F6 validity and
  semantic oracles. Ordinary output after a completed witness can create its
  own new tail; its return adds no TEMT guarantee.

The owner inspected the retained receiver's inline F6 blit and query ordering
as source evidence, with exact f2c083/7751dc binding; it did not claim a newly
reproducible receiver build or target pass. Platform-specific EMOS and bare C8
RC3 wrappers/guards remain separate. Consumer source/bounds/control freeze and
normal fresh bench admission still precede any later qualification. No new
owner build, firmware hook, physical case, grant or task is selected by UART.
RX-006 remains complete.
