# Native MOS foundation ownership

This repository owns maintained native MOS source and its upstream lineage.
It supplies a reviewed foundation to EMOS; it does not own Extender behavior
or replace the shared build infrastructure.

Project-wide policy lives in the selected mos-agondev dependency's
`docs/POLICIES.md`, not a competing local policy document. This file retains
the source repository's ownership boundaries.

1. The mos-agondev agent owns this generic foundation's source, upstream ports,
   source/deviation mappings, foundation tests and qualification evidence.
2. mos-agondev owns reusable compilation/link/runtime/provenance/comparison
   tools. This repository declares its source composition and profile in
   `build.json`; no translator runs in its normal build.
3. agon-emos owns EMOS source, APIs, behavior, profiles, linked-image checks
   and release evidence. linux-extender directly owns downstream adoption
   within separately authorized scope and preserves existing owner fences.
4. agon-extender owns product architecture, EDP/P4, transports, modes and
   system qualification. It consumes qualified pins, not mutable current output.
5. Official references and the independent experimental UART fork stay
   untouched. No experimental UART enters the foundation by implication.
6. Every custom MOS variant lives in its own project/repository; do not create
   a special foundation branch for it. This repository's default `main` branch
   owns `api/reservations.json` and shared generated bindings. A reservation
   records ownership, not implementation or release acceptance. Custom owners
   consume the selected canonical interface package and qualify their variants.

The workspace's central foundation contract owns cross-agent negotiation.
The new repository remains private. A source commit or matching binary is not
an accepted firmware release or authorization to change an installed product.
