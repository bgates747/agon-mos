# MOS TODO

Executive summary: the isolated ASY-001 driver and producer benchmark are
qualified against a scripted UART. Production integration still requires
compatibility review, a production ZDS link and physical qualification.
This is this repository's sole authoritative unfinished-work checklist.

Subtask IDs are immutable: a short namespace followed by a hyphen and three
zero-padded digits, then a checkbox. Reordering never renumbers an item.
Use `[x]` for completion; record other dispositions and their rationale in the
development log before removing an item. Never reuse a disposed ID.

## Compatibility decisions

C-001 [ ] Resolve synchronous output from callbacks inside the UART ISR; see the draft's compatibility decision C-001.

C-002 [ ] Resolve safe application return and recovery during a CTS stall; see the draft's compatibility decision C-002.

## Implementation and validation

TX-001 [ ] Review the production contract and resolve C-001/C-002 before live MOS integration. The Author authorized the isolated implementation tranche on 2026-10-12; its completed work is recorded in the development log.

TX-005 [ ] Integrate API discovery, startup/reset state, every UART0 output/status reader, synchronous barriers and application-return fences after compatibility review. Build and qualify the integrated MOS image using native ZDS II under Wine through the canonical Oryx launcher; isolated driver assembly/link already passes there. Use isolated headless Fab/Flexe testing on Oryx first, auditing eZ80-side UART interrupt/FIFO/CTS fidelity before relying on its results. Regress boot, real MOS VDP parser/keyboard/replies, stdout, errors, RST10/RST18 and exit with async enabled and disabled. The isolated experimental ABI is not the final MOS ABI.

TX-006 [ ] Obtain a fresh explicit bench ownership/lease before hardware access or firmware writes. Qualify CTS headroom, full-duplex traffic, timing and recovered CPU work physically. Emulator changes retain the canonical human-validation gate. Coordinate game integration separately; do not remove DI here.

## Provenance

TX-001 and C-001/C-002 continue original ASY-001-004. Completed TX-002,
TX-003 and TX-004, together with pending TX-005, continue ASY-001-005.
TX-006 continues ASY-001-006. Original IDs remain valid provenance references.
See [the MOS-owned task](docs/tasks/ASY-001.md) and
[the development log](docs/devlog-2026-10-12.md).
