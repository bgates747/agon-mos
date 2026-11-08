"""Install the prepared RX-005 appliance on the identity-checked Console8 card.
Run on Oryx with the project deployment directory as the sole argument.
Prior archive and every replaced file must still match before any card write.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

out = Path(sys.argv[1]).resolve()
root = Path('/run/media/smith/AGONC8')
sha = lambda data: hashlib.sha256(data).hexdigest()
old = json.loads((out / 'predeployment.json').read_text())
prepared = json.loads((out / 'prepared.json').read_text())
volumes = json.loads(subprocess.check_output(
    ['lsblk', '--json', '-o', 'PATH,LABEL,UUID,MOUNTPOINTS'], text=True))
def devices(rows):
    for row in rows:
        yield row
        yield from devices(row.get('children', []))
assert any(d.get('label') == 'AGONC8' and d.get('uuid') == '8658-1C23'
           and str(root) in (d.get('mountpoints') or [])
           for d in devices(volumes['blockdevices'])), 'Wrong/missing card'
assert sha((out / 'predeployment.tar.gz').read_bytes()) == old['archive_sha256']
assert sha((out / 'appliance.tar.gz').read_bytes()) == prepared['archive_sha256']
expected_dirs = set(old['directories'])
actual_dirs = {str(p.relative_to(root)) for p in (root / 'test').iterdir()
               if p.name == 'mos-uart0' or p.name.startswith('mos-uart0-')}
assert actual_dirs == expected_dirs, 'UART directory set changed since archive'
actual = {'autoexec.txt'}
for name in expected_dirs:
    assert name.startswith('test/mos-uart0') and '..' not in name
    actual.update(str(p.relative_to(root)) for p in (root / name).rglob('*') if p.is_file())
assert actual == set(old['files']), 'Files changed since archive'
for name, item in old['files'].items():
    data = (root / name).read_bytes()
    assert len(data) == item['bytes'] and sha(data) == item['sha256'], name
with tarfile.open(out / 'appliance.tar.gz') as archive:
    blobs = {}
    for member in archive.getmembers():
        assert member.isfile() and not member.issym() and not member.islnk()
        assert member.name == 'autoexec.txt' or (
            member.name.startswith('appliance/') and len(Path(member.name).parts) == 2)
        assert member.name not in blobs
        blobs[member.name] = archive.extractfile(member).read()
assert sha(blobs['autoexec.txt']) == prepared['new_boot_script_sha256']
assert blobs['autoexec.txt'] == b'CD /test/mos-uart0\r\ntest\r\n'
sums = blobs['appliance/SHA256SUMS'].decode().splitlines()
assert set(blobs) == {'autoexec.txt', 'appliance/SHA256SUMS'} | {
    'appliance/' + line.split('  ', 1)[1] for line in sums}
for line in sums:
    digest, name = line.split('  ', 1)
    assert sha(blobs['appliance/' + name]) == digest, name
staging = root / 'test/.rx005-new'
assert not staging.exists()
staging.mkdir()
for name, data in blobs.items():
    if not name.startswith('appliance/'):
        continue
    with (staging / Path(name).name).open('wb') as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
# These exact old directories were completely archived and checked above.
for name in sorted(expected_dirs):
    shutil.rmtree(root / name)
staging.rename(root / 'test/mos-uart0')
boot_tmp = root / '.autoexec-rx005-new'
assert not boot_tmp.exists()
with boot_tmp.open('wb') as handle:
    handle.write(blobs['autoexec.txt'])
    handle.flush()
    os.fsync(handle.fileno())
boot_tmp.replace(root / 'autoexec.txt')
os.sync()
for name, data in blobs.items():
    target = root / name if name == 'autoexec.txt' else root / 'test/mos-uart0' / Path(name).name
    assert target.read_bytes() == data, str(target)
assert {p.name for p in (root / 'test/mos-uart0').iterdir()} == {
    Path(name).name for name in blobs if name.startswith('appliance/')}
assert not any(p.name.startswith('mos-uart0-') for p in (root / 'test').iterdir())
receipt = dict(schema='RX005-console8-deployment-1', volume='AGONC8', uuid='8658-1C23',
               target='/test/mos-uart0', boot='CD /test/mos-uart0; test',
               all_readback_exact=True, old_archive_sha256=old['archive_sha256'],
               next_report=old['next_report'], files={name: sha(data) for name, data in blobs.items()},
               physical_execution=False, firmware_flashing=False)
(out / 'deployed.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
