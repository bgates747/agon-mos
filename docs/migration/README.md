# Initial native migration evidence

The first native source/direct-build candidate reproduces the selected stock
AgonDev image exactly. These receipts explain where source came from and what
was checked; they are not regeneration inputs, live task lists or a runtime
release certificate. Ongoing development edits maintained C/GNU assembly.

1. `initial-map.json` records assembly/include file hashes, original line
   origins, private symbols and macros at migration time. Later edits need not
   retain those file hashes or line numbers.
2. `upstream-files.json` records all 66 original tracked files and their
   first-tranche counterparts, preserving unchanged-versus-modified provenance.
3. `first-tranche.json` records the 102,055-byte image, matching 512 public
   symbols, matching 16 C objects, tools/tests and explicit qualification gaps.
   Its `supporting_controls` paths are relative to the separate persistent
   investigation workspace, not to this repository.

The initial binary SHA-256 is
`f891721bbb2a0bc2845dbb13edbeb449365a315f11be48500d8e65e2ab1aebb4`.
The control is clean official MOS v3.0.2 built with the pinned AgonDev
portability/runtime policy, **not** the official ZDS binary or the older
post-release-VDP-fix candidate. Per-file mechanical conversion and subsequent
readability controls both matched it. ELF private/debug naming changed; ROM
bytes and public symbol names, addresses and kinds did not.

The first tranche was authorized and implemented on 2026-10-15. Full command
logs, both intermediate source passes, failed diagnostic runs and an artifact
inventory remain in the persistent `worktrees/mos-build-005` investigation
workspace under the larger development workspace. The canonical coordination
task and dated report live in mos-agondev's BUILD-005; standalone source users
need not reproduce that directory layout to build this repository.

At the first-tranche evidence cut, native implementation and shared helpers
were uncommitted and the private remote contained official history only.
That historical state is preserved in first-tranche.json; later source promotion
does not rewrite the receipt or establish runtime acceptance. Follow root
STARTHERE for native setup, BUILD-005 in mos-agondev for current qualification,
and the upstream-origin/deviation documents for source maintenance.
