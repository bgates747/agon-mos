"""Archive the uniquely identified Console8 return; never write its SD card."""
import hashlib, importlib.util, json, re, shutil, subprocess
from pathlib import Path
from analyze import analyze

root = Path(__file__).resolve().parents[2]
build = root / 'build/uart0-recovery'
spec = importlib.util.spec_from_file_location('suite_deploy', root / 'experiments/uart0-suite/deploy.py')
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)
devices = json.loads(subprocess.check_output(
    ['lsblk', '--json', '--list', '-o', 'PATH,UUID,MOUNTPOINT,RM'], text=True))['blockdevices']
cards = [d for d in devices if (d.get('uuid') or '').upper() == '8658-1C23']
assert len(cards) == 1 and cards[0]['rm'] and cards[0]['mountpoint'], 'Console8 card missing or ambiguous'
mount = Path(cards[0]['mountpoint'])
identity = deploy.selected_mount(mount, '8658-1C23')
source = mount / 'test/mos-uart0'
assert source.is_dir() and not source.is_symlink() and not source.parent.is_symlink()
number = 1
while (build / f'physical-return-{number:03d}').exists():
    number += 1
archive = build / f'physical-return-{number:03d}'
archive.mkdir()
snapshot = archive / 'sd-fixture'
snapshot.mkdir()
hashes = {}
for path in sorted(source.iterdir()):
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    (snapshot / path.name).write_bytes(data)
    assert data == (snapshot / path.name).read_bytes() == path.read_bytes(), 'File changed during capture'
    hashes[path.name] = hashlib.sha256(data).hexdigest()
assert set(hashes) == {p.name for p in source.iterdir()}, 'Directory changed during capture'
deploy.selected_mount(mount, '8658-1C23')
receipt = json.loads((build / 'deployment.json').read_text())
assert hashes['manifest.json'] == receipt['package_manifest_sha256']
manifest = json.loads((snapshot / 'manifest.json').read_text())
assert manifest['experiment'] == 'uart0-recovery'
for name, entry in manifest['files'].items():
    assert hashes[name] == entry['sha256'], 'Deployed fixture changed: ' + name
for name in receipt['preserved_operator_and_numbered_results']:
    if name != 'runs.log':
        assert hashes[name] == receipt['old_file_hashes'][name], 'Earlier report changed: ' + name
old_journal = (Path(receipt['workspace_backup']) / 'runs.log').read_bytes()
assert (snapshot / 'runs.log').read_bytes().startswith(old_journal), 'Earlier journal changed'
root_mos = hashlib.sha256((mount / 'MOS.bin').read_bytes()).hexdigest()
assert root_mos == receipt['root_MOS_preserved_sha256']
(archive / 'capture.json').write_text(json.dumps(dict(mount=identity, files=hashes,
    root_MOS_sha256=root_mos, SD_writes_performed=False), indent=2) + '\n')

runs = []
index = (snapshot / 'runs.log').read_text()
for log in sorted(snapshot.glob('R*.log')):
    text = log.read_text()
    if 'RECOVERY_START' not in text:
        continue
    n = log.stem[1:]
    data = (snapshot / f'Y{n}.dat').read_bytes()
    result = analyze(data)
    assert result['campaign_passed']
    assert data == (snapshot / f'Z{n}.dat').read_bytes(), 'Final checkpoint differs'
    assert not (snapshot / f'C{n}.dat').exists(), 'Failure report present'
    cases = result['state']['total_cases']
    test = 10 if cases == 6 else 11
    assert text.count('RECOVERY case=') == cases
    assert f'TEST {test} PASS\nEND run={n} PASS\n' in text
    assert text in index, 'Detailed report missing from running journal'
    assert 'MOS_ROM128K_CRC32=239097B7 API=1.1' in text
    assert f'cases={cases} VDP=operator-confirmed-stock' in text
    for row in result['records']:
        expected = (f"RECOVERY case={row['case']} mode={row['mode']} kind={row['kind']} "
                    f"ticks={row['ticks']} wire={row['wire_bytes']} final_verified=8192 "
                    f"replies={row['replies']} overlap_replies={row['replies_while_busy']} rx=00")
        assert expected in text, 'Binary/text case mismatch'
    runs.append(dict(run=n, test=test, entry_RX=re.search(r'entry_RX=(\w+)', text)[1], **result))
assert sorted(r['state']['total_cases'] for r in runs) == [6, 24], 'Expected one short and one extended return'
summary = dict(scope='Console8 unchanged-stock-VDP workload completed; rare receiver race remains unexcluded',
    hardware_runs_passed=True, runs=runs, total_cases=sum(len(r['records']) for r in runs),
    final_buffer_bytes_checked=sum(r['final_buffer_bytes_checked'] for r in runs),
    workload_wire_bytes=sum(c['wire_bytes'] for r in runs for c in r['records']),
    case_RX_errors=0, async_duplex_replies_while_busy=sum(c['replies_while_busy'] for r in runs for c in r['records']),
    installed_MOS_ROM128K_CRC32='239097B7', VDP_identity='Stock 2.16.0 operator label; not independently read back',
    physical_race_reproduced=False, physical_race_ruled_out=False, receiver_repair_verified=False,
    new_batching_MOS_tested=False, exact_CPU_cycles_measured=False, external_elapsed_time_recorded=False,
    fixture_menu_sha256=hashes['test.bin'], native_sha256=hashes['recovery.bin'],
    source_archive=str(archive.relative_to(root)), SD_writes_performed=False)
(archive / 'analysis.json').write_text(json.dumps(summary, indent=2) + '\n')
(root / 'experiments/uart0-recovery/physical-results.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({k:v for k,v in summary.items() if k != 'runs'}, indent=2))
