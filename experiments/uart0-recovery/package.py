"""Prepare a hardware-first investigative bundle; never write the SD here."""
import hashlib,json,shutil,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];build=root/'build/uart0-recovery'
out=Path(sys.argv[1]).resolve();assert not out.exists()
base=root/'build/uart0-ab/console8-comparison-20261014'
old=json.loads((base/'manifest.json').read_text())
for name,entry in old['files'].items():assert hashlib.sha256((base/name).read_bytes()).hexdigest()==entry['sha256'],name
checks={e:json.loads((build/f'checks-{e}/receipt.json').read_text()) for e in ('jit','interp')}
controls={c:json.loads((build/f'checks-jit-{c}/receipt.json').read_text()) for c in ('corrupt','noreply')}
interactive=json.loads((build/'checks-interactive/receipt.json').read_text())
assert interactive['interactive_checks_passed'] and interactive['short_and_extended_passed'] and interactive['orphan_preserved']
for r in checks.values():
    assert r['fixture_checks_passed'] and r['result']['campaign_passed'] and not r['known_receiver_race_cleared']
    assert r['native_sha256']==hashlib.sha256((build/'recovery.bin').read_bytes()).hexdigest()
    assert r['menu_sha256']==hashlib.sha256((build/'test.bin').read_bytes()).hexdigest()
assert all(r['control_rejected'] for r in controls.values())
for r in controls.values():
    assert r['native_sha256']==hashlib.sha256((build/'recovery.bin').read_bytes()).hexdigest()
    assert r['menu_sha256']==hashlib.sha256((build/'test.bin').read_bytes()).hexdigest()
assert interactive['native_sha256']==hashlib.sha256((build/'recovery.bin').read_bytes()).hexdigest()
assert interactive['menu_sha256']==hashlib.sha256((build/'test.bin').read_bytes()).hexdigest()
shutil.copytree(base,out)
for name in ('manifest.json','SHA256SUMS'):(out/name).unlink()
shutil.copyfile(build/'test.bin',out/'test.bin');shutil.copyfile(build/'recovery.bin',out/'recovery.bin')
shutil.copyfile(root/'experiments/uart0-recovery/readme.txt',out/'readme.txt')
(out/'suite.cfg').write_text('board=Heber Agon Console8\nmos=mos-candidate.bin\nvdp=vdp-cts-diag.bin\nvdp_label=stock 2.16.0 REQUIRED for recovery; confirm normal boot banner\nvdp_flash=1\nvdp_restore=vdp-2.16.0.bin\nphysical_receiver=1\n')
for e,r in checks.items():(out/f'recovery-{e}.json').write_text(json.dumps(r,indent=2)+'\n')
for c,r in controls.items():(out/f'recovery-control-{c}.json').write_text(json.dumps(r,indent=2)+'\n')
(out/'recovery-interactive.json').write_text(json.dumps(interactive,indent=2)+'\n')
(out/'recovery-coverage.json').write_text((build/'expected.json').read_text())
assert hashlib.sha256((out/'mos-candidate.bin').read_bytes()).hexdigest()=='e7fc0732fba1ba6f94a30cc4bdab7e740c51a2b066cc35259f2abfc101fa848a'
files={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(out.iterdir())}
manifest=dict(suite=True,experiment='uart0-recovery',fixture_checks_passed=True,menu_integration_passed=True,
 automated_qualification_passed=False,human_review_passed=False,physical_qualification=False,known_receiver_race_cleared=False,
 exploratory_hardware=True,hardware_test_authorization='Author selected MOS-first unchanged-VDP Console8 investigation and instructed write plan, commit/push, then execute preparation on 2026-10-14',
 deployment_path='/test/mos-uart0',firmware_changed=False,required_VDP='Official stock 2.16.0, operator confirmed',
 vdp=old['vdp'],target='Heber Agon Console8',report_version=1,
 required_MOS_file_sha256='e7fc0732fba1ba6f94a30cc4bdab7e740c51a2b066cc35259f2abfc101fa848a',
 installed_ROM128K_CRC32='239097B7',physical_race_ruled_out=False,receiver_race_attributed=False,files=files)
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(out/'SHA256SUMS').write_text(''.join(f'{hashlib.sha256((out/n).read_bytes()).hexdigest()}  {n}\n' for n in sorted([*files,'manifest.json'])))
print('Prepared hardware-first investigative package',out)
