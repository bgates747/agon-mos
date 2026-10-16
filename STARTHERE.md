# Developing the native AgonDev MOS foundation

Edit the C and GNU assembly directly. The source is maintained, not generated
build output. This candidate targets official MOS v3.0.2 behavior with the
documented portability changes; it is not an accepted replacement firmware and
contains no experimental UART or EMOS enhancements. Matching the translated
AgonDev control does not prove unrestricted C/runtime parity with the ZDS build.

## Python and build dependencies

Create a project interpreter using Python 3.14 or newer:

```bash
python3.14 -m venv .venv
```

No Python packages are required. Provide a mos-agondev checkout that includes
`projects/native-foundation/build.py` and `scripts/generate_api_reservations.py`,
plus the pinned AgonDev release layout
(`bin/`, `include/`, `lib/`). A self-contained clone may keep both under ignored
`.local/`, which is the root Makefile's default:

```text
.local/mos-agondev/   shared infrastructure checkout
.local/agondev/      qualified toolchain release tree
```

Existing locations are equally valid. Pass `MOS_AGONDEV_ROOT` and
`AGONDEV_TOOLCHAIN` explicitly to Make; neither has to be a sibling checkout.
The first control uses Clang 15.0.7 / LLVM
`c76386c0083e6a6236ff774275227e2389f85538` and `libagon.a` SHA-256
`5de7878342ab6780593fbf8d54d8005960e2471bd0e34c0e307fbcfe42fef28a`.
Accepting a different toolchain/runtime is a separate qualification change.
The shared helper's exact consumed source hashes are recorded by each build;
select an immutable helper revision for qualification rather than an unrelated
current checkout. BUILD-005 in mos-agondev records the selected candidate pins.

## Edit and build

```bash
make firmware-check
make test
```

Or supply your selected dependency paths:

```bash
make firmware-check MOS_AGONDEV_ROOT=PATH_TO_INFRA \
  AGONDEV_TOOLCHAIN=PATH_TO_TOOLCHAIN
```

Paths may be project-relative. Each build creates a fresh ignored `.build/`
run directory and prints its output path. ELF, BIN, HEX, map, logs, runtime
audit and per-target provenance stay there. No converter, preparation script,
Windows tool or ZDS installation is involved. A failed run is retained, never
reused as success; `BUILD_DIR` may select another fresh output directory.

`build.json` declares exact source/link order, optimization exceptions and
product-owned linked-image checks. FatFS `ff.c` uses `-Os` because the pinned
compiler cannot allocate registers at `-Oz`. Do not remove a checker or weaken
runtime/link guards to make a build pass. Fresh builds are intentional during
this first tranche; incremental-build behavior has not been introduced.

For migration-equivalence qualification, provide the pinned translated control:

```bash
make baseline-check REFERENCE_BIN=PATH_TO_PINNED_CONTROL
```

The control must be exactly 102,055 bytes with SHA-256
`f891721bbb2a0bc2845dbb13edbeb449365a315f11be48500d8e65e2ab1aebb4`.
This is the AgonDev build of clean official v3.0.2 with documented portability
edits, not the post-release VDP-fix candidate or the official ZDS binary.
Normal intentional source development uses `firmware-check`, not an attempt
to change the reference hash until a mismatch disappears.

## Understanding and updating the source

Start with [upstream origin](docs/upstream-origin.md) and the
[deviation register](docs/deviations.md). `docs/migration/initial-map.json`
records original and native assembly/include paths, initial hashes, macro/local
symbol mappings and line origins. It is a frozen initial migration receipt,
not a requirement that future source edits retain those file hashes forever.

Use recognizable native macros and descriptive `.Lroutine_name` labels.
Anonymous `1f`/`1b` branches are supported; macro-local `\@` labels prevent
different expansions from colliding. Add a focused explanation and stable
deviation ID for a meaningful change from upstream, preserving notices and
unchanged source where practical. New behavior fixes remain distinct from
mechanical syntax/readability changes.

Future upstream updates are reviewed ports against recorded ancestry, not
overlays over the maintained source. Downstream EMOS adopts an explicitly
reviewed qualified pin. Builds do not authorize firmware flashing, EMOS rebasing
or hardware-timing claims. Emulator acceptance is a separate gate; see the
[selected candidate review](docs/qualification.md) for current fixture inputs,
launch commands and qualification limits.
