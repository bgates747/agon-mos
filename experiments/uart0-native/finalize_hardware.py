"""Seal the checked native package with source companions and exact evidence."""
import hashlib,json,shutil,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2];b=root/'build/uart0-native';out=b/'console8-native'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(out/'mos-candidate.bin') != '5543d6acaa64bebd3006cb034a8dda9b61cfe92c82cbbffe2c391a9392f0f4c9', 'Cannot reseal withdrawn native MOS: N-007 baud-rate boot failure'
checks={engine:json.loads((b/('hardware-menu-'+engine)/'receipt.json').read_text()) for engine in ('jit','interp')}
for r in checks.values():
 assert r['passed'] and r['menu_sha256']==sha(out/'test.bin') and r['stress_sha256']==sha(out/'stress.bin')
 assert r['VDP_sha256']==sha(out/'vdp-rx-fixed.bin')
stress=json.loads((out/'stress.json').read_text());stress.update(reserved_padding=255,native_public_ABI='1.2',CTS_batch=16)
(out/'stress.json').write_text(json.dumps(stress,indent=2)+'\n')
shutil.copyfile(root/'experiments/uart0-stress/analyze.rb',out/'stress-read.rb')
shutil.copyfile(root/'experiments/uart0-native/inspect_hardware.py',out/'native-read.py')
subprocess.run(['tar','-czf',str(out/'native-mos-sources.tar.gz'),'-C',str(b),'maintained-source.tar'],check=True)
subprocess.run(['tar','-czf',str(out/'native-test-sources.tar.gz'),
 'experiments/uart0-native','experiments/uart0-suite/src','experiments/uart0-suite/entry.asm',
 'experiments/uart0-suite/entry.linkcmd','experiments/uart0-stress/analyze.rb','build/uart0-ui/identity.h'],cwd=root,check=True)
(out/'native-checks.json').write_text(json.dumps(dict(both_engines=checks,native_child_human_review_passed=True,
 native_menu_human_review_pending=True,hardware_qualified=False,firmware_flashing_performed=False),indent=2)+'\n')
(out/'README.md').write_text('# Native Console8 UART package\n\nSee readme.txt for the manual run and firmware.txt for exact firmware identities.\nThe new native MOS is required; this is not a branding-only update.\nThe main fixture stays test.bin, option3 selects the reviewed native batch16 test,\nand the existing journal assigns new sequential run numbers.\nOld reports and running-log numbering are preserved. No physical firmware has been flashed by the agent.\n')
manifest=json.loads((out/'manifest.json').read_text())
manifest.update(automated_qualification_passed=True,menu_integration_passed=True,native_menu_checks=checks,
 source_companions=['native-mos-sources.tar.gz','native-test-sources.tar.gz'],native_child_human_review_passed=True)
manifest['files']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(out.iterdir()) if p.name not in ('manifest.json','SHA256SUMS')}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(out/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(out.iterdir()) if p.name!='SHA256SUMS'))
subprocess.run(['sha256sum','--check','--status','SHA256SUMS'],cwd=out,check=True)
print('Sealed checked native package:',out)
