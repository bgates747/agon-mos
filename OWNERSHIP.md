# UART native MOS ownership

agon-mos owns this experimental regular MOS variant and its UART semantics,
tests and diagnostic VDP. The repository is bgates747/agon-mos; the native
feature branch is codex/uart0-otirx-native. It is not a branch of the shared
foundation/infrastructure repository and is not an EMOS integration.

mos-agondev retains the selected generic foundation, canonical API allocations
and reusable tools. Consume the immutable API export under src/shared-api and
the explicitly selected helper path; return generic changes to their owner.
Flexe retains emulator/model ownership. Existing release/hardware gates remain.
