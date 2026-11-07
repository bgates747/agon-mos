# IO003 RC3 adapter: source review return

Requested in
`2026-11-07_14-02-27_agon-6502_io003-rfc25-adapter-source-review-four`.
No blocking source defect found in the selected normal-entry, single-producer,
bare-MOS RC3 shadow-copy overlap path. This is not target qualification or a
new build/run request. UART did not edit the consumer or rerun its71 checks.

## Admission and transport

`io3_begin` checks IDLE first, so disabling async cannot authorize synchronous
output over a borrowed source. Positive/full-width count is bounded7680 before
the+30 arithmetic; pointers are checked and the226-byte threshold boundary is
correct. The complete11-byte header/payload/19-byte tail is copied into the
dedicated7710-byte packet before submission. The generated caller finalizes
length/page/color before that copy. These are valid caller-owned sources, not
an arbitrary-address or alias validator.

Earlier ordinary output drains before the release flag is cleared and ACTIVE
is published. Retained target disassembly shows those stores before the submit
call. The bridge loads full24-bit count+30, HL packet, fixed non-null callback
and A25h. It ignores raw A and does not invent MOS admission/finish statuses.
The local IO3_ACCEPTED means this valid caller submitted once. Immediate
callback before return is safe: the flag is already armed and no later clear
erases it. The callback only stores one flag, returns normally and touches no
index/shadow/MB state; the ISR's primary saves cover its AF use.

`io3_poll` does not probe LSR before source release. After release it separately
requires TEMT before returning IDLE. The packet remains immutable even longer
than the minimum borrowed-source lifetime. Rejected overlap and poisoned state
cannot recopy/resubmit/fall back to synchronous output. A pending/stuck path
has no invented cancellation or unsafe exit. The bare-MOS LSR sampler is not
exported as an EMOS owner interface and retains its error-acknowledgement caveat.

## Generated drawing and guard

The original dirty-row shadow commit runs after submission, reading packed
rows and writing the previous-page shadow, not the borrowed packet. Required
loop registers/IX are reconstructed after the C call; the enclosing drawing
entry retains its saves. The end of that commit calls poll until drained before
returning to redraw/normal-output paths. Small/no-change/raw-fallback paths do
not leave an outstanding async source. No guest DI/MB07/08 execution is added
inside this ownership window. A shadow update still means submitted state,
not proven receiver execution; existing semantic fences remain separate.

Generated controller checks MB/IFF silently before printable ROM refusal and
before configure/assets/keyboard/render work. The ROM guard is the exact
published100879-byte RC3 prefix/CRC B08C80B8, including assembly byte0. Actual
ADL1 loader entry remains a precondition; this is not arbitrary-context recovery.
Do not broaden its allowlist to EMOS, stock, private bounded-CTS variants or
RC2 merely because those share some syscall conventions.

## Retained evidence and limits

Independently rehashed all8 reported source inputs and compared each with the
frozen source copy, all8 reported objects, generated controller/hires, retained
disassembly/maps and both images. The42895-byte pair differs only at startup
mode immediate28372 (0→1). The original relink is byte-identical to the retained
baseline. Receipts: [review pins](io003-rc3-review-r01.json). Existing command
logs report all compilation/link/host-check commands successful; no command
was rerun by this review.

The71 checks run actual adapter C with mocked submit/LSR, not real IRQs, assembly
execution, ROM guard, keyboard or receiver. The retained combined disassembly
is relocatable evidence, not an executed final program. Packet/map fit and9392B
linked free address range do not measure runtime heap/stack or nested IRQ space.
No speedup, hardware pass or bounded keyboard/RX/timer latency follows. Published
RC3 still spins on CTS under DI; the test must retain that attribution and the
exact legacy F6 receiver selection. Normal controls, byte/pixel correctness,
refusal/exit and target allocation behavior remain the consumer's separately
admitted qualification. Production, card, firmware, EMOS and queues unchanged.
