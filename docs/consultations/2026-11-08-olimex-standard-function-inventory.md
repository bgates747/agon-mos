# Olimex standard firmware: retained Eirene/EMOS function inventory

Source-only answer to Extender's standard-firmware query on November8. No build,
installation, default selection or target access was performed. Extender owns
the actual standard profile and its integration with VDPlet v0.1.2-alpha.

## What is latest upstream versus the fork

Live GitHub API inspection finds upstream main at
`3a7259c58bfa6f34f58afe24087f418cef0148e0`, including startup-table PR3.
The following proposals remain open and unmerged:

- PR1: reset-vector setter61h, head604640eb882c3dfeb870a8c4aaaa7e155c23d0ad.
- PR2: async UART0 sender25h, headffab9c9c84a31535d1ec976b7e6f23b2579ecb80.
- PR4: buffered keyboard event poll62h, head241ffbaee4bc7e3f814124b59e0b8c07207a9409.

The retained published fork UART release remains RC3/tag3.1.0_uart0_rc_3,
commit97311c437093e416342a6c836cf9914f2ced027d. It adds the pinned25h sender
and startup fix, not61h/62h or our private counted receive26h/90h. Bare RC3
100879B SHA d7a51147... is not an EMOS standard image.

Thus “all Eirene functions” must distinguish merged upstream functions from
open proposals and private UART receive work. There is no basis to call a25f
a build containing all three open proposals or all UART experiments.

## Exact retained EMOS images

**a25f donor:**

- Source2c79c6006d6bcb0c2b3f9d8d6aae3ef4b36c730a;
  build agon-emos-eirene-r04-b2026-11-06-09-02-21Z.
- Folder /Agon/mystuff/agon-extender/agents/net004/emos-uart-rfc25-r02/.
- Complete ROM.bin131072B SHA
  a25f1612f4aaa542c5488cf3266d968ad3d1d61e9df3b5ce2c680650f5d7a2ca,
  CRC32 B24AF611. mos.map91148B SHA
  11a296f09e1d2b7125e1a40ce0aea62042f299e93ea85afc6a6459a351866d20.
- Profile EMOS_UART0_RFC25=1, network_parallel=false. Used129108B/free1964B.
- Retains populated upstream MOS/FatFS API slots and EMOS51h gateway,
  startup initialization after BSS, synchronous RST10/RST18, guarded25h
  submission and existing EMOS route/input/boot ownership.
- Does not implement26h/count90h receiver,61h reset-vector setter or62h event
  polling.42h/43h old trial API is excluded in this profile. No public local
  drain/finish API. Public25h returns real admission errors, unlike bare RC3.

**171c counted-receive superset:**

- Sourceb581ac848e3c6c66d0e8d0fceb42efddbdfe7755, identified
  agon-emos-rx006-r01-b2026-11-08-04-51-09Z, based on exact a25f.
- Folder /Agon/mystuff/agon-extender/agents/rx006-receiver-r01/build595/on/.
- Complete ROM.bin131072B SHA
  171c7880c4c4e064293d67e41d4225d2112a13c690e49d803cf77899919f6914,
  CRC32 78D0DACF. mos.map91928B SHA
  ccbda4bc18bb16ef247d291338037ebdee4c3185c28b9ea25f9c32c44fe3b71f.
- Adds EMOS_RX006_COUNTED=1: private receive arm26h/raw90h frame parser,
  bounded available-byte drain, exact legacy16/10/4 reply support and
  separate RX/TX ownership. Used129605B/free1467B; +497ROM/+22BSS.
- Retains guarded25h and a25f core; still no61h/62h. Disabled control exactly
  reproduces a25f. Build manifest is ../manifest.json above the build folder.
- Actual132 ten-size synthetic suite and136/139 small consumer receive tests
  pass with exact old producer7d09. This is temporary experimental qualification,
  not an automatic promotion or a test against VDPlet v0.1.2-alpha.

Both ROMs and maps were independently rehashed for this answer. Presence of
upstream populated syscall slots was compared between exact donor2c79 and
upstream main3a7259: none is replaced by not-implemented. This establishes
table presence, not complete behavioral/source parity of every function.
The old mos_api.inc/docs42h/43h declarations in the donor are historical and
not the guarded25h image's SDK contract.

## Standard-profile conclusion

a25f is the known retained guarded-TX EMOS baseline;171c is the retained
UART receive-feature superset. No later combined image containing public61h
and62h has been supplied or qualified by UART. CPU-accounting f05c and other
owner diagnostics are distinct purpose-specific images, not automatically the
new standard because their build time is later. Extender owns their inventory.

If the selected standard means merged Eirene main plus the existing RC3-style
TX function, a25f has that public-slot inventory with EMOS-specific semantics.
If it also means counted RX, a25f is incomplete and171c is the concrete retained
reference. If it means all open Eirene proposals including61h and62h, neither
image meets that description; integration is a real missing item, not another
approval question or permission to relabel an older image.

VDPlet owns whether v0.1.2-alpha has the exact raw90h producer/INFO/legacy
reply support needed for counted receive. Do not substitute old7d09 qualification
for that new version. Existing narrow25h source-callback plus fresh ordered
POINT policy is owner accepted and had actual148 instrumented a25f/F6 consumer
qualification, separately from bare C8 or latest VDPlet behavior.

No new firmware implementation/build/test was selected by this consultation.
Reuse verified installed standards and restore the actual selected standard
after explicit exceptions under the new human policy; historical a25f/85f9
rollback bytes do not override that policy. RX-006 remains complete.
