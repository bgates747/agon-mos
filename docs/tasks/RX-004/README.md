# RX-004 — VDP UART receive-race maintainer handoff

Prepare a brief, self-contained pull request and a reproducible source/binary
bundle for the UART receive-recovery race demonstrated on Heber Agon Console8.
The proposed fix serializes the buffer-full flag update and receive-interrupt
masking under the UART driver's existing lock. The PR must make sense to a
maintainer with no knowledge of our asynchronous MOS transmission work.

## Task silo

- [pr.md](pr.md): submitted PR title/body, including the proposed diff and ZIP link.
- [uart-rx-race-reproducer.zip](uart-rx-race-reproducer.zip): complete source,
  binary, fixture and evidence bundle, with README.md at its root.
- [bundle/README.md](bundle/README.md): the same operating/build instructions
  embedded in the archive; bundle/ also holds the exact patch and assembler.
- [publication.json](publication.json): PR, commit, release and archive identities.
- [Receiver repair evidence](../../uart0-receiver-sync-fix.md): existing physical
  test interpretation and pointers to the original raw records.

The sole actionable checklist remains [TODO.md](../../../TODO.md). RX-004 is
complete; its disposition is recorded in the dated development log.
This document defines its scope and acceptance requirements rather than creating
a second checklist. After approving the draft, the Author authorized packaging
and submission, then explicitly approved public release hosting for the ZIP.

## Required deliverables

Keep the PR brief: describe the unlocked flag-update race, move the flag store
inside the existing critical section, include the diff and summarize controlled
physical before/after results. Do not put internal preparation instructions or
unexplained project names into the reviewer-facing text.

Before submission, assemble a reproduction bundle in this silo containing
matching MOS, VDP and test-application sources and binaries, build/run
instructions, applicable notices, checksums and raw results. The detailed
contents and original input locations are in bundle/README.md. Use matching
unpatched/repaired diagnostics and the paired test application, not the newer
callback suite. Check source/binary correspondence and dependency identities;
do not present an incomplete Pi mirror as a complete source delivery.

The production fix changes an ESP-IDF4.4.6 UART driver used by VDP2.16.0.
Document how the supplied VDP build selects that repaired driver; distinguish
this minimal change from the diagnostic timing/recording/rescue hooks. Verify
the relevant dependency version and integration point before a public proposal.

Retain ZDS II for MOS and the upstream toolchain for VDP. The package must have
enough source/build inputs to reproduce its binaries without our private
workspace; proprietary compiler installation remains an explicit prerequisite.

## Evidence and acceptance

The matched physical baseline R0012 captured reception disabled with the full
flag clear and66FIFO bytes pending, then required diagnostic rescue. Repaired
R0014 received both4096-byte payloads with correct CRCs, zero receive errors
and no rescue. R0017 supplies additional normal-command compatibility evidence.
These are controlled-interleaving tests; natural failure frequency is unknown.

Preserve those identities and raw reports. Validate an unpacked bundle against
its instructions and manifest, including complete sources, firmware/test
binaries and restoration files. Any newly substituted firmware/test combination
needs fresh qualification rather than inheriting the old pair's acceptance.
Emulator execution uses the shared Oryx lease; physical Console8 operations
remain Author actions. Local drafting and packaging do not grant publication,
firmware flashing or another project's source changes.

## Status — 2026-11-02

Submitted [AgonPlatform/agon-vdp#354](https://github.com/AgonPlatform/agon-vdp/pull/354)
as bgates747, head1a0840e58f380e0c802981e4a95ebed025032691. The production change
supplies the minimally repaired ESP-IDF4.4.6 driver as a project C object with
provenance and Apache-2.0 license; it does not include diagnostic hooks.

The 34,661,114-byte ZIP contains5369files. All extracted file hashes and the
unpacked physical-pair decoder pass. All three VDP source variants materialize
and match their complete original source manifests. Clean ZDS II MOS and native
fixture rebuilds match the hardware-tested binaries byte for byte. The actual
production PR builds successfully with PlatformIO; its map confirms the local
driver is linked and the original SDK archive object is excluded. No new
physical execution or emulator session was performed for packaging/submission.

ZIP SHA256 e4babd18fa38620aa38900b4a60f298cea17479168ce4e3995180d820659ad79.
Published on the Author's explicitly approved public fork as a prerelease asset:
https://github.com/bgates747/agon-vdp/releases/tag/uart-rx-race-reproducer-2026-11-02.
GitHub's asset digest matches the verified local ZIP. Submission is complete;
maintainer review/merge and general release approval are separate outcomes.
