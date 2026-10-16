# Native MOS deviations from official v3.0.2

These are the bounded changes needed to maintain and build the official source
with AgonDev. Native syntax/readability edits preserve emitted firmware bytes;
C/ABI/runtime portability requirements are recorded separately. Experimental
UART and EMOS policy are absent. Unfinished work belongs in the owning TODO,
not this register.

Each identifier is permanent. Qualification here describes the initial offline
binary comparison, not emulator/hardware acceptance. Reasons remain valid until
the relevant upstream source, compiler or build contract changes and a reviewed
replacement proves equivalent or deliberately corrected behavior.

| ID | Location and upstream form | Native change and reason | Removal or replacement condition |
| --- | --- | --- | --- |
| DEV-001 | C includes use eZ80/CTYPE/String spellings | Match the case-sensitive AgonDev header names in main/mos/editor/timer/uart | Reviewed header contract changes; do not rely on a case-insensitive host |
| DEV-002 | main/defines/mos declare linker addresses as `void []` | Legal byte-array declarations preserve symbol addresses without allocating storage | An explicitly typed upstream linker-symbol interface replaces them |
| DEV-003 | main quickrand writes registers without a C return | Clang volatile inline-asm output plus explicit widened integer return; obsolete ZDS branch removed | A reviewed portable implementation with the same intended result/ABI |
| DEV-004 | clock.h assumes its includer's MOS typedefs | Include defines.h explicitly so the header is self-contained | Upstream header becomes independently well-typed |
| DEV-005 | diskio shifts an int year by 25 | Cast to 32-bit DWORD **before** shifting; eZ80 int is 24-bit | Upstream explicitly widens the arithmetic before the shift |
| DEV-006 | Three JR spans rely on ZDS relaxation | Explicit JP in mos_api/sd/vdp_protocol; GNU as rejects the original long spans | Reviewed control-flow/layout change makes the spans short or a qualified relaxation contract replaces them |
| DEV-007 | ZDS register names are volatile byte lvalues | Reuse shared checked ez80.h address-space-I/O wrapper with numeric SDK constants | Qualified compiler/header ABI supplies equivalent lvalues; physical baud checks remain product-owned |
| DEV-008 | ZDS directives, scopes, local/anonymous labels and structure declarations | Native sections, globals/externs, offsets and scoped private names/numeric labels; ADL widths stay explicit | Native source is authoritative; future upstream ports refresh mappings rather than regenerating it |
| DEV-009 | Repeated project includes and identical SDK register declarations | Guard native includes; matching hardware aliases use `.equ` so SDK `.set` can redeclare them; project-only constants remain `.equiv` | A single reviewed register authority removes overlap; tests reject differing values |
| DEV-010 | ZDS macro names include `TIMER_EXP?` and invocation-local dollars | Keep native macros/calls recognizable; use legal `TIMER_EXP` and unique `\@` private targets | A reviewed macro API change replaces the original names/semantics |
| DEV-011 | ZDS compiler runtime/printf and automatic linker placement | Pinned shared restricted AgonDev runtime, nanoprintf configuration, i48 helpers and explicit linker assertions | Separate toolchain/runtime/layout qualification; no floats are promised by current formatter |
| DEV-012 | ff.c compiles under ZDS without the AgonDev allocation constraint | Per-file `-Os`; other C uses `-Oz`, with exact inventory/order in build.json | A qualified compiler passes ff.c at the chosen optimization with regressions/size reviewed |
| DEV-013 | Official interfaces have no coordinated custom-project reservation register | Include generated identifier constants from api/reservations.json; canonical C overlay imports the unchanged SDK header. No UART code, dispatch slot or firmware feature is added | Replace only through a reviewed shared/upstream allocation authority, preserving compatibility and collision checks |

The shared linker also retains the existing Fab hostfs descriptor in reserved
reset-page space as part of the selected AgonDev control. This creates no new
ROM extent and does not configure or run an emulator. The direct build reuses
the exact checked implementation from mos-agondev; no product check is bypassed
by invoking a lower-level linker.

Original notices and comments remain in each converted file. The build helper
records actual target commands, consumed source/header/tool hashes, runtime
closure, final ELF/map/binary and checker outcomes. Matching the control proves
the initial native source transformation, not unrestricted runtime parity of
AgonDev versus ZDS C compilation or correction of inherited stock defects.
