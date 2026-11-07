# Historical consultation mail

These are unchanged copies of published questions and replies, preserved as
evidence. They are not current protocol documentation. File hashes are recorded
in [consultation-evidence.json](../consultation-evidence.json).

Some original questions and replies incorrectly call `0x88` a key-map packet.
The correct baseline interpretation is:

* `0x81`: keycode packet, also used by the private tagged VDPlet return workaround.
* `0x88`: five-byte keyboard repeat-delay/rate/LED status, not the held-key map.

Use the maintained [task](../README.md), [findings](../consultation.md) and
[running notes](../notes.md) for current information. Preserve the mail unchanged
when correcting maintained documents.
