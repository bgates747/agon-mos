"""Prepare the menu-only repair over the verified diagnostic bundle, off-card."""
import hashlib, json, shutil, subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[3]
b=root/'build/uart0-ui'
base=root/'build/uart0-race/console8-diagnostic-20261014'
out=b/'console8-inputfix-20261014'
old=json.loads((base/'manifest.json').read_text())
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,pin in old['files'].items():
    assert digest(base/name)==pin['sha256'],name
checks={name:json.loads((b/name/'receipt.json').read_text())
        for name in ('after-jit-02','after-interp','packets-jit','packets-interp')}
assert all(c['passed'] and c['prior_reports_preserved'] for c in checks.values())
menu=digest(b/'test.bin')
assert all(checks[n]['menu_sha256']==menu for n in ('after-jit-02','after-interp'))
assert all(c['VDP_sha256']==old['files']['vdp-race-diag.bin']['sha256'] for c in checks.values())
assert not out.exists()
shutil.copytree(base,out)
for name in ('manifest.json','SHA256SUMS'):(out/name).unlink()
shutil.copyfile(b/'test.bin',out/'test.bin')
shutil.copyfile(root/'experiments/uart0-race/readme.txt',out/'readme.txt')
(out/'firmware.txt').write_text('MENU INPUT REPAIR: no new firmware flash required.\nHardware diagnostic R0009 hung; do not repeat 8/4 while investigated.\n'+(out/'firmware.txt').read_text())
result=dict(menu_input_checks_passed=True,physical_menu_confirmation=False,
    physical_missed_key_cause_reproduced=False,
    hardware_diagnostic_status='HUNG_R0009_FIRST_CASE_NO_COMPLETED_RECORD',
    firmware_and_native_images_changed=False,menu_sha256=menu,checks=checks,
    before_SDL_probe=json.loads((b/'before-fast/receipt.json').read_text()),
    source_sha256={n:digest(root/n) for n in ('experiments/uart0-suite/src/main.c','experiments/uart0-suite/src/uart.src')})
(b/'results.json').write_text(json.dumps(result,indent=2)+'\n')
shutil.copyfile(b/'results.json',out/'menu-input-checks.json')
for n,c in checks.items():(out/f'menu-input-{n}.json').write_text(json.dumps(c,indent=2)+'\n')
subprocess.run(['tar','-czf',str(out/'menu-input-sources.tar.gz'),
 'experiments/uart0-suite/src','experiments/uart0-suite/tests','experiments/uart0-suite/Makefile',
 'experiments/uart0-suite/entry.asm','experiments/uart0-suite/entry.linkcmd','build/uart0-ui/identity.h'],cwd=root,check=True)
manifest={k:v for k,v in old.items() if k!='files'}
manifest.update(input_only_update=True,firmware_changed=False,physical_qualification=False,
    hardware_diagnostic_status=result['hardware_diagnostic_status'],physical_menu_confirmation=False,
    hardware_test_authorization='Author requested submenu keypress repair and returned the Console8 card for refresh on 2026-10-14; no repeat of the hung receiver diagnostic is requested by this package',
    files={f.name:dict(bytes=f.stat().st_size,sha256=digest(f)) for f in sorted(out.iterdir())})
for name,pin in old['files'].items():
    if name not in ('test.bin','readme.txt','firmware.txt'):
        assert digest(out/name)==pin['sha256'],name
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(out/'SHA256SUMS').write_text(''.join(f'{digest(f)}  {f.name}\n' for f in sorted(out.iterdir()) if f.name!='SHA256SUMS'))
print(out)
