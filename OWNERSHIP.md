# Repository ownership

This repository is the upstream-oriented MOS source fork. It owns:

1. the official Agon Platform MOS source lineage;
2. generic MOS corrections suitable for stock MOS independently of any one
   downstream product; and
3. release tags and source history intended to remain reviewable against the
   official upstream project.

It does not own Extender MOS (EMOS), Extender-specific commands or policies,
AgonDev port machinery, emulator qualification infrastructure, or Agon
Extender product architecture.

The neighboring repositories have these roles:

1. `agon-emos` owns the maintained EMOS product source, product-specific tests,
   qualification records, and EMOS tasks.
2. `mos-agondev` owns reusable AgonDev translation, build, emulator, and
   qualification machinery. It accepts product policy only through explicit
   profiles or options.
3. `agon-extender` owns Extender hardware, EDP firmware, system architecture,
   integration contracts, and cross-component product requirements.

Changes discovered while developing EMOS belong here only when they are valid
generic MOS fixes. Product-specific changes must be made in `agon-emos`.
