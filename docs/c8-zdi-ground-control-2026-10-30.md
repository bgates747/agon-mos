# Console8: tighter ground leads and crossed-function control

The Author declined a meter check because they were tired/annoyed, replaced
the ground leads with tighter-fitting leads and authorized another attempt.
No resistance measurement was made. No sniffers attached. The existing signal
wires remain physical BLUE on WROOM GPIO26 and GREEN on GPIO27, with series
resistors reported present;33 Ω is inherited from the last measurement.

## Matched comparison

First repeated the installed v11 probe, keeping firmware, signal assignment
and resistors unchanged after the reported ground-lead change. It sends one
HALT command despite invalid identity; RAM remains gated by three independently
read valid halt statuses. Result is unchanged allFF.

Next completed the previously queued software-crossed control, without any
physical wiring change. This assigns CLOCK to GPIO26 and DATA to GPIO27,
the functions used by the previously passing Olimex control. With the Author's
present wire colors, this deliberately makes BLUE the clock path and GREEN
the data path for this temporary test. Physical Console8 endpoints have not
been independently verified, so this does not certify which wire reaches
which eZ80 pin. It is not a new color convention.

| Software CLOCK | Software DATA | Identity | HALT status reads | RAM/flash |
| --- | --- | --- | --- | --- |
| GPIO27 / GREEN, v11 | GPIO26 / BLUE | FF FF FF FF | FF, FF, FF | Not attempted |
| GPIO26 / BLUE, v12 | GPIO27 / GREEN | 07 01 11 41 | 87, 70, 07 | Not attempted |

All three crossed-control status values violate the reserved-bit/active-state
gate from PS0153 Table125: bit7 must be set, bits6/1/0 clear. They do not verify
halt, even though87 includes bit7. The initial identity is also invalid: it
does not match product0007/revisionAA. Neither run reaches RAM mapping, memory
access, pattern writes or any flash operation. Both probes release outputs at
completion and host serial closes. Actual CPU halt state remains unverified.

The different reply patterns depend on GPIO function assignment in this
comparison. They do not establish a good ground, statistical randomness,
correct target pinout or a working target response. Replacing ground leads
alone did not restore communication in the unchanged v11 test.

## Installation, restoration and final state

Temporary v12 image269760bytes SHA256
14e113cf668c9dbffadf28b18ae8d2b78714a330120a9b6c2257adbd4ea92f5a.
Its app installation was backed up, exact old-image/MAC gated, verified by
esptool and full affected-span readback. It contains no flash API/payload.

Restored original quiet v11 afterwards, with the same installation/readback
checks:269760bytes, SHA256
7f60ec5e5ca17e2b82163e019652143deb566e5b2f6e34fab5c07548d0a68f76.
Whole270336byte restored span exactly equals the pre-control span, SHA256
4b684a84f609dc506df5239d980e48e49c2c888ce348209d6d4a9424b3151952.
No further target command was sent during restoration. Boot verifies both
WROOM outputs disabled; physical GREEN/GPIO27 reads LOW and BLUE/GPIO26 HIGH.
These are WROOM-side digital levels only. They do not prove which target pin
is connected, measured voltage, or the cause of the LOW. Current v11 boots
quiet and requires the exact host command; no polling or automatic retry.

The crossed control is complete and v11 restored. No board operation remains
running. Console8 stock MOS recovery is still incomplete. P4 normal-firmware
restoration remains deferred. No repeat meter/wiring request was made.

## Evidence retained on Pi and Oryx

- build/zdi-ram-probe-20261030/probe-ground-leads-002/
- build/zdi-ram-crossed-20261030/{wroom-v12-install-001,probe-001}/
- build/zdi-ram-probe-20261030/wroom-v11-restored-002/

Raw probe console and exact-runner hashes independently verified on Pi against
the original receipts. No waveform exists; there are no attached sniffers.

## Next Author-requested repeat: valid identity and halt, PC gate fails

After reconfirming BLUE=TDI/GREEN=TCK, the Author requested one more attempt.
No new physical change was reported. Run probe-repeat-003 with the same
restored v11 returns identity07 00 AA 1C and three validHALT statuses9C/9C/9C.
It then stops at `FAIL stable original PC`, before RAM mapping/access/write
or flash. The source short-circuits on first PC==FFFFFF or a subsequent PC
mismatch and does not print the samples, so these possibilities cannot be
distinguished from this log. Do not claim a particular PC value or mismatch.

This is the first valid Console8 identity/halt observation in this campaign,
not proof of sustained reliable communication or attribution to a particular
change. CPU last verified halted; no resume or reset requested. Both outputs
released, GREENHIGH/BLUELOW at WROOM, serial closed. WROOM remains v11,
GREEN CLOCK27/BLUE DATA26, exact-command gated. Evidence retained Pi/Oryx:
build/zdi-ram-probe-20261030/probe-repeat-003/. Console SHA256
cba7c76c7d93264413dfecbf22869582877680f245e42ed47ce3800d28234291.
