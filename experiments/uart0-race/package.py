"""Prepare authorized investigative firmware/files; never flash or write SD."""
import hashlib,json,shutil,subprocess,sys,zlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];b=root/'build/uart0-race';out=Path(sys.argv[1]).resolve()
assert not out.exists()
read=lambda p:json.loads(p.read_text())
checks={e:read(b/f'checks-{e}/receipt.json') for e in ('jit','interp')}
menus={e:read(b/f'checks-{e}-menu/receipt.json') for e in ('jit','interp')}
controls={c:read(b/f'checks-jit-{c}/receipt.json') for c in ('badcrc','noend','nohello')}
audit=read(b/'audit.json');interactive=read(b/'checks-interactive/receipt.json')
assert all(r['protocol_integrity_passed'] and r['result']['diagnostic_evidence_valid'] for r in [*checks.values(),*menus.values()])
assert all(r['control_rejected'] for r in controls.values()) and interactive['interactive_checks_passed']
assert audit['driver_override_linked'] and len(audit['invalid_evidence_controls_rejected'])==3
base=root/'build/uart0-recovery/console8-recovery-20261014';previous=read(base/'manifest.json')
for n,v in previous['files'].items():assert hashlib.sha256((base/n).read_bytes()).hexdigest()==v['sha256']
shutil.copytree(base,out)
for n in ('manifest.json','SHA256SUMS'):(out/n).unlink()
shutil.copyfile(b/'test.bin',out/'test.bin');shutil.copyfile(b/'race.bin',out/'race.bin')
shutil.copyfile(b/'firmware/.pio/build/esp32dev/firmware.bin',out/'vdp-race-diag.bin')
shutil.copyfile(b/'source.json',out/'race-source.json')
shutil.copyfile(b/'ESP-IDF-LICENSE',out/'ESP-IDF-LICENSE')
shutil.copyfile(root/'experiments/uart0-race/CREDITS.txt',out/'RACE-CREDITS.txt')
shutil.copyfile(root/'experiments/uart0-race/readme.txt',out/'readme.txt')
subprocess.run(['tar','--exclude=*/.pio','-czf',str(out/'race-sources.tar.gz'),
 'experiments/uart0-race','build/uart0-race/firmware','build/uart0-race/uart-idf-4.4.6.c',
 'build/uart0-race/ESP-IDF-LICENSE','build/uart0-race/source.json'],cwd=root,check=True)
(out/'suite.cfg').write_text('board=Heber Agon Console8\nmos=mos-candidate.bin\nvdp=vdp-race-diag.bin\nvdp_label=UART0 recovery diagnostic REQUIRED for menu 8/4\nvdp_flash=1\nvdp_restore=vdp-2.16.0.bin\nphysical_receiver=1\n')
identities='\n'.join(f'{name}: bytes={(out/name).stat().st_size} file_CRC32={zlib.crc32((out/name).read_bytes()):08X} SHA256={hashlib.sha256((out/name).read_bytes()).hexdigest()}' for name in ('vdp-race-diag.bin','vdp-2.16.0.bin','mos-candidate.bin','flash.bin'))
(out/'firmware.txt').write_text('HW-002 MANUAL CONSOLE8 FIRMWARE\nKeep installed old experimental MOS ROM CRC239097B7.\n9 then 2 installs vdp-race-diag.bin; reboot and require subtitle UART0 recovery diagnostic.\n9 then 4 restores official stock vdp-2.16.0.bin; reboot and require normal banner.\nUtility code 0 is not update verification; require no updater errors and the correct reboot banner.\nNo root /MOS.bin replacement or automatic flashing. See readme.txt.\n\n'+identities+'\n')
for e,r in menus.items():(out/f'race-menu-{e}.json').write_text(json.dumps(r,indent=2)+'\n')
(out/'race-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
(out/'race-interactive.json').write_text(json.dumps(interactive,indent=2)+'\n')
native=hashlib.sha256((out/'race.bin').read_bytes()).hexdigest();menu=hashlib.sha256((out/'test.bin').read_bytes()).hexdigest()
vdphash=hashlib.sha256((out/'vdp-race-diag.bin').read_bytes()).hexdigest()
for r in [*checks.values(),*menus.values(),*controls.values()]:
 pins=r['runtime_identities'];assert any(x==native+'  sdcard/uart0/race.bin' for x in pins)
 assert any(x==vdphash+'  esp32-firmware.bin' for x in pins)
for r in menus.values():assert any(x==menu+'  sdcard/uart0/test.bin' for x in r['runtime_identities'])
assert interactive['menu_sha256']==menu and interactive['native_sha256']==native and interactive['VDP_sha256']==vdphash
manifest=dict(suite=True,experiment='uart0-race',receiver_recovery_diagnostic=True,
 fixture_checks_passed=True,menu_integration_passed=True,automated_qualification_passed=False,
 human_review_passed=False,physical_qualification=False,known_receiver_race_cleared=False,
 exploratory_hardware=True,hardware_test_authorization='Author assigned this agent VDP firmware diagnostics and instructed write HW-002, commit/push, then execute preparation on 2026-10-14',
 deployment_path='/test/mos-uart0',target='Heber Agon Console8',firmware_changed=True,firmware_flashing_performed=False,
 vdp=dict(version='2.16.0',stock_release=False,diagnostic_file='vdp-race-diag.bin',stock_restore='vdp-2.16.0.bin'),
 MOS_file_sha256=hashlib.sha256((out/'mos-candidate.bin').read_bytes()).hexdigest(),
 physical_race_reproduced=False,natural_stock_failure_reproduced=False,
 files={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(out.iterdir())})
assert manifest['MOS_file_sha256']=='e7fc0732fba1ba6f94a30cc4bdab7e740c51a2b066cc35259f2abfc101fa848a'
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(out/'SHA256SUMS').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in sorted(out.iterdir()) if p.name!='SHA256SUMS'))
print('Prepared diagnostic bundle',out)
