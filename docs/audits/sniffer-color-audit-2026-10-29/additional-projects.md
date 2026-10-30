# Audit scope addendum

The unfinished broad local content search was deliberately stopped after 5,228
candidate paths so that large nested SDK/source snapshots would not continue
loading the Pi. Its earlier inventory files are explicitly partial snapshots.
Stopping a broad search does not turn its unread candidates into reviewed files.

An additional read-only pass reviewed all 457 candidate files from these roots:
mos-agondev (319), tomm (107), agon-emos (16), trs-80 (10), agon-utils (2),
agon-testing (2), agon-6502 (1). No further physical probe/channel color
contradictions were found. The independent first pass of other project roots
had already read 1,659 candidates (409 distinct contents), as recorded in the
main audit. Reviews of MOS, Extender, Hardware and Oryx are separately scoped
there; do not sum these into a claim of exhaustive unique-file coverage.

Confirmed canonical mappings include:

- `/Agon/mystuff/tomm/vga-ez80/docs/tom_vga_breadboard_wiring.md:70–77,93–95`.
- `/Agon/mystuff/tomm/vga-ez80/test/palette/README.md:10–16`.
- `/Agon/mystuff/tomm/golden-256x192/test/signal/README.md:9–15`.
- `/Agon/mystuff/tomm/golden-256x192/test/wide480-signal/README.md:11–15`.

The first document explicitly distinguishes input-side and output-side probe
attachments. Different signal assignments there are not probe color reversals.
“Suite green” status phrases and filenames inside hash manifests are unrelated
search hits. All pre-existing source documents remain unchanged.
