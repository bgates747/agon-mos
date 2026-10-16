"""Package retained fixtures for an explicitly requested manual Console8 replay."""
import hashlib
import json
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[2]
base = root / 'build/uart0-repair/console8-receiver-repair'
out = root / 'build/uart0-repair/console8-ab-replay-20261015'
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = json.loads((base / 'manifest.json').read_text())
for name, pin in manifest['files'].items():
    assert digest(base / name) == pin['sha256'], name
assert not out.exists(), 'Preserve existing preparation; choose a fresh destination'
shutil.copytree(base, out)
shutil.copyfile(root / 'experiments/uart0-repair/ab-quickstart.txt', out / 'readme.txt')
cfg = (out / 'suite.cfg').read_text()
cfg = cfg.replace('vdp=vdp-race-diag.bin', 'vdp=vdp-rx-fixed.bin')
cfg = cfg.replace('vdp_label=UART0 recovery diagnostic REQUIRED for menu 8/4',
                  'vdp_label=RX sync candidate REQUIRED for this replay; confirm reboot banner')
(out / 'suite.cfg').write_text(cfg)
text = (out / 'firmware.txt').read_text()
footer = '\n'.join(line for line in text.splitlines()
                   if ': bytes=' in line)
(out / 'firmware.txt').write_text(
    'MANUAL CONSOLE8 A/B REPLAY; SAME DIRECTORY AND INSTALLED MOS\n'
    '9/7 candidate -> reboot -> 8/1 THREE TIMES -> 8/7 compatibility.\n'
    '9/4 stock restore -> reboot -> confirm normal stock 2.16.0 banner.\n'
    'Read readme.txt. No MOS flash; updater errors mean failure.\n\n' + footer + '\n')
manifest.update(
    experiment='uart0-race', subexperiment='uart0-repair',
    campaign='repaired-receiver-original-ab-replay',
    hardware_test_authorization='Author requested deploying the pending tests to the mounted Console8 card on 2026-10-15 for manual execution',
    hardware_diagnostic_status='ORIGINAL_AB_REPLAY_ON_REPAIRED_RECEIVER_PENDING',
    physical_repair_verified=True, original_ab_repaired_receiver_verified=False,
    new_test_code_built=False, new_firmware_built=False,
    preparation_scope='Existing hardware-tested menu and retained A/B fixture; instructions/configuration only; no new qualification claim')
manifest['files'] = {p.name: dict(bytes=p.stat().st_size, sha256=digest(p))
                     for p in sorted(out.iterdir())
                     if p.name not in ('manifest.json', 'SHA256SUMS')}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
(out / 'SHA256SUMS').write_text(''.join(
    f'{digest(p)}  {p.name}\n' for p in sorted(out.iterdir())
    if p.name != 'SHA256SUMS'))
for name, pin in json.loads((base / 'manifest.json').read_text())['files'].items():
    if name not in ('readme.txt', 'suite.cfg', 'firmware.txt'):
        assert digest(out / name) == pin['sha256'], name
print(out)
