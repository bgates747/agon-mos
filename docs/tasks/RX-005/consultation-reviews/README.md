# Historical owner-report snapshots

These are unchanged snapshots returned during the consultation, with exact
hashes and original locations in
[consultation-evidence.json](../consultation-evidence.json). They are evidence
copies, not maintained protocol specifications or automatically refreshed mirrors.

The original 6502 review repeats our incorrect label “key-map packet0x88”.
Correct interpretation: private VDPlet returns use `0x81` keycode packets;
`0x88` carries keyboard repeat-delay/rate/LED status, not the held-key map.
The source owner's maintained note, JSON annotation and HANDOFF were corrected
and verified after this snapshot. This historical copy retains its original bytes.

Use the maintained [task](../README.md), [findings](../consultation.md) and
[running notes](../notes.md) for current information and later corrections.
