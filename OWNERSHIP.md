# Repository ownership

On 2026-11-06 Brandon separately delegated the reusable application-space UART1
async driver to this project (U1-001). Its original library, adapters and tests
live under experiments/uart1-async. Extender retains EMOS admission/routing/RX
and any minimal firmware integration; MechAgon retains its application consumer.
This adds no resident UART1 async engine or upstream toolchain migration.

The experimental native regular-MOS UART variant also belongs to this project,
on codex/uart0-otirx-native in an isolated worktree. It consumes the explicitly
pinned generic foundation, shared interface and reusable helpers; none of those
owner checkouts becomes our feature branch. EMOS integration remains separate.

For the interrupt-based UART0 project, this agent also owns diagnostic VDP
firmware preparation and physical receiver investigation in project-local build
copies. The Author explicitly clarified this on2026-10-14. Flexe owns emulator
code/models/regressions, not these VDP firmware tasks. Upstream VDP and ESP32 SDK
checkouts remain read-only references; diagnostic changes and provenance belong
here. The Author performs physical firmware flashing and board runs.

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
