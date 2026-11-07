# IO003: published fork RC3 contract, 2026-11-07

Source-only reply to
`2026-11-07_13-53-40_agon-6502_io003-current-accepted-abi-update-three`.
No consumer changes, builds, runs or firmware selections are made here.

## Acceptance and exact reference

Live GitHub API inspection on November7 found upstream main at
`3a7259c58bfa6f34f58afe24087f418cef0148e0`, incorporating startup-table PR3.
Async [RFC2](https://github.com/AgonPlatform/eirene-mos/pull/2) is still OPEN,
unmerged, head `ffab9c9c84a31535d1ec976b7e6f23b2579ecb80`. There is no
upstream-accepted async ABI to substitute on the strength of that wording.

The published fork reference is
[3.1.0_uart0_rc_3](https://github.com/bgates747/eirene-mos/releases/tag/3.1.0_uart0_rc_3),
source/tag commit `97311c437093e416342a6c836cf9914f2ced027d`. It combines the
startup fix with the pinned RFC sender, not the private bounded-CTS derivative.

* MOS100879 bytes, prefix CRC32 `B08C80B8`, SHA256
  `d7a51147f3381cd68d56f3fbe4605434a897dfae1b049269afeba09ec2b7eb50`.
* Map SHA256
  `48dae5890af7b49fe6bcb535a20e9b6432069c8d84666e3d0e8e7e1070282be9`.
* ZIP1887937 bytes, SHA256
  `9c8a9a28b0f597e6a9294d806491ffca3902c16cf1876b092ae8944f65368061`.

On Pi, the immutable downloaded ZIP is
`/Agon/mystuff/eirene-mos/build/rc003/downloaded/3.1.0_uart0_rc_3.zip`.
The expanded package is the same basename under `build/rc003/packages/`.
UART independently rehashed ZIP, MOS and map against published package pins.
It includes `mos-rc3.bin`, map/ELF, complete `source/`, `fixture/`, `example/`,
SDK, README, licenses and retained evidence. The working checkout is on a
different experimental branch; do not use its live source/docs as RC3.

Authoritative contract: `git show 3.1.0_uart0_rc_3:docs/uart0-async.md` in
`/Agon/mystuff/eirene-mos`, or `source/docs/uart0-async.md` in the package.
Worked caller: package `example/src/{main.c,bridge.src}`; exact guarded fixture:
`fixture/src/{main.c,api.src,rom_crc.h,identity.h}`. Sender lives in tagged
`src/serial.asm`, dispatch in `src/mos_api.asm`, ISR in `src/interrupts.asm`.

## Migration from the reviewed RC2 adapter

Use one foreground producer in actual ADL1, MB0, IRQ-enabled context, with the
normal UART0 owner and no competing ordinary writer. Arm the volatile done flag
BEFORE submitting. Set HL=immutable contiguous source, BC=positive full24-bit
length, DE=non-null ADL assembly callback; A=25h; `RST.LIL 08h`. Source must not
wrap address space; keep callback/state resident. A zero/NULL/overlapping call
is outside the contract, not a supported refusal probe.

The raw A result is IER-derived despite the upstream A=0 comment: ignore it.
There is no BUSY/INVALID admission result, queue, transfer ID, NULL callback,
cancel or43h finish syscall. Enforce IDLE/borrowed/poisoned admission in the
application; do not mark shadow state committed from an invented A=0 success.
One valid submission means the application has handed its source to MOS.

The callback can occur before submission returns. It runs under DI after the
final bytes are copied into the UART FIFO, and returns with ordinary RET in
this supported ADL contract. A flag-only assembly callback is the supplied
recipe. The ISR saves primary AF/BC/DE/HL; callback code must preserve any
IX/IY/alternate registers/MB it uses. No MOS/C-runtime/wait/output/allocation,
recursive submit or owner change in the callback. A generic C callback needs
its own proven bridge. At the submit call boundary treat AF/HL as clobbered;
BC/DE/index/shadows/MB are untouched by the valid MB0 submit source, but retain
the actual C ABI's save rules. Do not transfer the ISR's saves into a claim
that foreground submission preserves HL.

After observed callback the source may be reused. Separately wait for physical
UART0 TEMT before ordinary output, exit and the conservative next-packet
boundary used by the recipe. RC3 has no public drain API; its bare-MOS example
reads LSR bit6 at portC5h. This is a platform-specific bare-MOS policy, not an
EMOS adapter contract. LSR reads can acknowledge RX error evidence, so do not
introduce another sampler into a composed shared UART owner. A normal ordered
receiver reply/fence is still distinct from source release and wire drain.
It can supply its own semantic completion evidence when the owner's supported
protocol defines that ordering. Preserve existing F6/receiver lifetimes.

Ordinary RST10/RST18 remain synchronous. Do not interleave them or normal query
headers with the borrowed packet. Local shadow-copy overlap remains possible
with disjoint memory while actual MB0/IRQs remain enabled; do not enter the
DI/MB07/08 guest core while a source is outstanding. A timeout does not cancel
the source or authorize return/unload. Keep the current quarantine policy.

CTS waits inside the RC3 ISR under DI; RX, keyboard and timers may be delayed.
There is no arbitrary blackout bound, stuck-CTS recovery or higher-baud safety
promise. The private UART/EMOS bounded-CTS work does not change published RC3.

## Guard and owner boundary

The fixture hashes exactly100879 bytes from address0 for CRC `B08C80B8`, with
byte0 read in assembly to avoid C null-pointer undefined behavior. Its fixture
also checks exact linked vectors/context from its pinned map; there is no
public async capability/version negotiation. Banner/version alone is not an
ABI guard. The worked example instead relies on verified deployment and tests
context; it is not a ROM allowlist. Select the consumer's explicit deployment
policy, and refuse RC2/foreign ROM before issuing25h if using the exact-image
fixture policy. ADL1 is the normal loader precondition, not proved by MB/IFF
checks alone. Invalid MB/IFF rejection must not itself call ordinary MOS output
or secretly enable interrupts in an unsupported context.

RC2.1 remains published, startup-fixed, with42h/43h at commitb2194860;
CRC `DBE3E21E`,100950 bytes. It is not an alias for RC3. Original RC2 CRC9E08D539
retains the inherited startup defect. Keep any old results labelled as run.

EMOS integration remains Extender-owned and separately pinned/admitted. There
is no universal accepted EMOS ROM/API guard supplied by RC3. Its Legacy/routing,
UART0/1 RX, keyboard, IRQ and ordinary-output ownership must come from the
selected owner composition, not a raw RC3 substitution. The short Mech actual94
pass used private RX-protected owner47dadc29 plus a specific WAIT1 app/P4/VDP;
it neither installs that ROM for6502 nor qualifies a generic EMOS async ABI.
Ask Extender for the exact existing owner interface when an EMOS composition
is actually selected; do not guess private drain/vector addresses or take over
its UART/RST tables. The paused Mech GOAL is not resumed by this consultation.
