"""Prepare the branded Console8 package off-card after retained checks pass."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[2]
b = root / 'build/uart0-branding'
h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
identity = json.loads((b / 'identity.json').read_text())
assert identity['ABI'] == '1.1' and identity['ROM128K_CRC32'] == '44BC5C07'
assert h(b / 'branded/MOS.bin') == identity['rom_sha256']
source = json.loads((b / 'branded-source.json').read_text())
for name, pin in source['files'].items():
    assert h(b / 'branded' / name) == pin, name
    if name != 'src/version.h':
        assert h(b / 'original' / name) == pin, name
assert 'PASS 27 production-ROM integration scenarios' in (b / 'production-tests.txt').read_text()
checks = {}
for engine in ('jit', 'interp'):
    receipt = json.loads((b / ('checks-' + engine) / 'receipt.json').read_text())
    assert receipt['passed'] and receipt['banner_present']
    assert receipt['rom_sha256'] == identity['rom_sha256']
    assert receipt['menu_sha256'] == h(b / 'test.bin')
    checks[engine] = receipt
base = root / 'build/uart0-repair/console8-ab-replay-20261015'
manifest = json.loads((base / 'manifest.json').read_text())
for name, pin in manifest['files'].items():
    assert h(base / name) == pin['sha256'], name
out = b / 'console8-branded'
assert not out.exists()
shutil.copytree(base, out)
for name in ('manifest.json', 'SHA256SUMS'):
    (out / name).unlink()
shutil.copyfile(b / 'branded/MOS.bin', out / 'mos-candidate.bin')
shutil.copyfile(b / 'branded/MOS.map', out / 'mos-candidate.map')
shutil.copyfile(b / 'test.bin', out / 'test.bin')
shutil.copyfile(root / 'experiments/uart0-repair/ab-quickstart.txt', out / 'readme.txt')
firmware = (root / 'build/uart0-suite/short-text-20261015/firmware.txt').read_text()
assert 'CRC239097B7' in firmware and '7E66FD09' in firmware
firmware = firmware.replace('CRC239097B7', 'CRC44BC5C07').replace('7E66FD09', 'AD9C0F96')
(out / 'firmware.txt').write_text(firmware)
sources = ['build/uart0-branding/branded-source.tar', 'build/uart0-branding/branded-source.json',
           'build/uart0-branding/identity.json', 'build/uart0-branding/production-tests.txt',
           'build/uart0-branding/original-build.log', 'build/uart0-branding/branded-build.log',
           'build/uart0-branding/branded/tools.sha256', 'build/uart0-branding/branded/MOS.map',
           'build/uart0-branding/branded/symbols.txt', 'build/uart0-branding/menu-identity.h',
           'experiments/uart0-branding', 'experiments/uart0-suite/src',
           'experiments/uart0-suite/tests/menu_build.sh', 'experiments/uart0-repair/ab-quickstart.txt']
subprocess.run(['tar', '-czf', str(out / 'branded-mos-sources.tar.gz'), *sources], cwd=root, check=True)
(out / 'branding-checks.json').write_text(json.dumps(dict(identity=identity, checks=checks,
    source_only_change='version subtitle; same API1.1 sender',
    menu_change='accept banner-only rebuild ROM CRC alongside retained originals',
    physical_qualification=False, card_deployed=False,
    prior_interpreter_smoke_failure_retained='build/uart0-branding/checks-interp-integration-failed',
    prior_interpreter_failure_cause_established=False), indent=2) + '\n')
manifest.update(MOS_file_sha256=identity['rom_sha256'], branded_MOS=identity,
                branding_regression_passed=True, human_review_passed=False,
                expected_card_predecessor_manifest_sha256='a16101e21189c0e88467a6cd95ad636c308daab1af85cad516af10ba9de94b83',
                hardware_test_authorization='Author requested visible custom MOS branding on 2026-10-15; card deployment waits until Author reports card available')
manifest['files'] = {p.name: dict(bytes=p.stat().st_size, sha256=h(p)) for p in sorted(out.iterdir())}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
(out / 'SHA256SUMS').write_text(''.join(h(p) + '  ' + p.name + '\n' for p in sorted(out.iterdir()) if p.name != 'SHA256SUMS'))
allowed = {'test.bin', 'mos-candidate.bin', 'mos-candidate.map', 'readme.txt', 'firmware.txt'}
for name, pin in json.loads((base / 'manifest.json').read_text())['files'].items():
    if name not in allowed:
        assert h(out / name) == pin['sha256'], name
subprocess.run(['sha256sum', '--check', '--status', 'SHA256SUMS'], cwd=out, check=True)
print(out)
