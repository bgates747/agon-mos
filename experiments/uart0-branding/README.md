# Visible experimental MOS identity

The custom MOS prints `Arthur - UART0 async EXPERIMENTAL` in its boot banner,
so an operator can distinguish it from stock MOS before running UART tests.
The version number remains Platform MOS 3.0.2; the label is not release approval.

On 2026-10-16 the original unbranded API1.1 MOS passed three physical Console8
A/B selections (90 phases) and compatibility. Results remain attributed to that
tested ROM. Branding does not invalidate sender results or require a full rerun.
The branded image/menu are staged in the same card directory with an optional
MOS flash. Leave the Author's other-project VDP unchanged. Physical branded
banner confirmation remains separate from the completed sender campaign.

The Console8 preparation deliberately retains the API1.1 sender that passed
the earlier hardware campaign. Its source foundation is commit
`5cb08284c93c17366ab9cd19c44acab04b92bc5e`. Rebuilding the unmodified native
source on Oryx reproduced the staged firmware SHA256 exactly:
`e7fc0732fba1ba6f94a30cc4bdab7e740c51a2b066cc35259f2abfc101fa848a`.
The branded native source changes only `src/version.h`'s subtitle.

The branded image is 110,722 bytes, SHA256
`67e58b197524db3fd275e5af88c36c6d59d230e8689de29f38690fe3ed905d75`.
Its file CRC32 is `AD9C0F96`. With erased flash padded to 128 KiB, the menu
reports ROM CRC32 `44BC5C07`, API1.1. Flexe's zero-filled tail instead gives
`DD9A1288`; the updated menu accepts both fingerprints alongside the two
original API1.1 fingerprints. The generic development source also carries
the experimental label, but its newer ABI1.2 sender is a separate candidate.

All MOS builds use ZDS II 5.3.5 under Wine on Oryx. The menu retains its existing
authorized AgonDev build, wrapped by native ZDS assembly. Firmware source
snapshots, compiler logs, maps, tool receipts and identity metadata stay under
`build/uart0-branding`. The native runner passes all 27 production-ROM scenarios.
`qualify.py` checks the actual boot label, discovery, integration and receiver
workload through disposable FAT16 media and the actual compiled candidate VDP
in both Flexe engines. Failed/interrupted attempts stay separately archived;
successful later attempts do not erase them or establish hardware qualification.
One interpreter attempt failed its integration phase before native report
creation; a fresh run passed all three phases. Its cause is unassigned,
and its evidence remains in `checks-interp-integration-failed`.

`package.py` verifies the pinned source and successful checks before creating
`build/uart0-branding/console8-branded`, including updated firmware, menu,
short instructions, licenses and a source companion. It performs no SD writes
or physical firmware operations. The Author withdrew the Console8 card on
2026-10-15 and reported it available on2026-10-16; that hold is lifted.
The hardware destination remains `/test/mos-uart0`, with menu9/1 flashing the
staged `mos-candidate.bin`. Do not replace the card's stock root `/MOS.bin`.
Preserve the compacted sequential log and all numbered results on deployment.
