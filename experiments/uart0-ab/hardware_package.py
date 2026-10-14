"""Build an explicitly exploratory Console8 bundle, without changing the SD."""
import hashlib,json,shutil,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
out=Path(sys.argv[1]).resolve();assert not out.exists()
base=root/'build/uart0-margin/console8-receiver-candidate-20261013'
old=json.loads((base/'manifest.json').read_text())
for n,entry in old['files'].items():
    assert hashlib.sha256((base/n).read_bytes()).hexdigest()==entry['sha256'],n
checks={e:json.loads((root/f'build/uart0-ab/hardware-check-{e}/receipt.json').read_text()) for e in ('jit','interp')}
menu=root/'build/uart0-suite/test.bin';native=root/'build/uart0-ab/hardware-native/test.bin'
for r in checks.values():
    assert r['menu_integration_passed'] and not r['known_receiver_race_cleared']
    assert r['menu_sha256']==hashlib.sha256(menu.read_bytes()).hexdigest()
    assert r['native_sha256']==hashlib.sha256(native.read_bytes()).hexdigest()
shutil.copytree(base,out)
for n in ('manifest.json','SHA256SUMS'):(out/n).unlink()
shutil.copyfile(menu,out/'test.bin');shutil.copyfile(native,out/'ab.bin')
shutil.copyfile(root/'experiments/uart0-ab/hardware-readme.txt',out/'readme.txt')
(out/'suite.cfg').write_text('board=Heber Agon Console8\nmos=mos-candidate.bin\nvdp=vdp-cts-diag.bin\nvdp_label=stock 2.16.0 for A/B (confirm normal boot banner)\nvdp_flash=1\nvdp_restore=vdp-2.16.0.bin\nphysical_receiver=1\n')
shutil.copyfile(root/'docs/uart0-ab-stall.md',out/'ab-stall.md')
shutil.copyfile(root/'experiments/uart0-ab/stall-results.json',out/'ab-stall.json')
for engine,r in checks.items():(out/f'ab-check-{engine}.json').write_text(json.dumps(r,indent=2)+'\n')
entries={f.name:dict(bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(out.iterdir())}
manifest=dict(suite=True,experiment='uart0-ab',exploratory_hardware=True,menu_integration_passed=True,
    automated_qualification_passed=False,human_review_passed=False,physical_qualification=False,
    known_receiver_race_cleared=False,deployment_path='/test/mos-uart0',target='Heber Agon Console8',
    hardware_test_authorization='Author requested Console8 hardware test on mounted Oryx SD on 2026-10-14 despite known Flexe receiver race',
    report_version=1,results='Sequential Axxxx.dat / Xxxxx.dat, Rxxxx.log and existing runs.log',
    firmware_changed=False,files=entries)
manifest['vdp']=dict(version='2.16.0',stock_release=True,exact_release_binary_emulator_qualified=False,
    optional_diagnostic_file='vdp-cts-diag.bin',stock_restore='vdp-2.16.0.bin')
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
names=[*entries,'manifest.json']
(out/'SHA256SUMS').write_text(''.join(f'{hashlib.sha256((out/n).read_bytes()).hexdigest()}  {n}\n' for n in sorted(names)))
print('Prepared exploratory hardware comparison',out)
