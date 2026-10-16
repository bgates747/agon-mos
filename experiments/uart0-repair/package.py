"""Gate and package the receiver repair and matched manual Console8 tests."""
import hashlib,json,shutil,subprocess,zlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];b=root/'build/uart0-repair'
base=root/'build/uart0-race/checkpoint-fix-20261014/console8-checkpoint-fixed'
out=b/'console8-receiver-repair'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((base/'manifest.json').read_text())
for n,pin in old['files'].items():assert digest(base/n)==pin['sha256'],n
names=['checks-'+v+'-'+e+'-native' for v in ('before','fixed') for e in ('jit','interp')]
names+=['checks-before-jit-menu','checks-fixed-jit-menu','checks-fixed-interp-menu',
        'checks-candidate-jit-campaign','checks-candidate-interp-campaign',
        'checks-fixed-jit-native-badcrc','checks-fixed-jit-native-noend',
        'checks-fixed-jit-native-wrong-variant','checks-original-jit-native',
        'checks-fixed-jit-campaign-wrong-candidate']
checks={n:json.loads((b/n/'receipt.json').read_text()) for n in names}
assert all(c['passed'] and c['actual_MOS_FatFS'] and c['hostfs_disabled'] for c in checks.values())
menu=digest(b/'test.bin');native=digest(b/'native/repair.bin')
firmware={v:b/v/'.pio/build/esp32dev/firmware.bin' for v in ('before','fixed','candidate')}
for name,c in checks.items():
    assert c['native_sha256']==native
    if c['case']!='native':assert c['menu_sha256']==menu,name
    if c['variant']!='original':assert c['firmware_sha256']==digest(firmware[c['variant']]),name
    if c['control']:assert c['control_rejected'],name
    elif c['variant']=='original':assert c['result']['stage']==3 and not c['result']['completed']
    elif c['case']=='campaign':assert c['result']['campaign_passed'] and c['result']['state']['completed']==6
    else:assert c['result']['regression_passed'] and c['result']['receiver_fixed']==(c['variant']=='fixed')
audit=json.loads((b/'audit.json').read_text());assert audit['source_and_link_audit_passed']
assert len(audit['invalid_evidence_controls_rejected'])==4
assert not audit['variants']['fixed']['rescue_function_linked'] and not audit['variants']['candidate']['rescue_function_linked']
for v,p in firmware.items():assert audit['variants'][v]['firmware_sha256']==digest(p)
result=dict(receiver_fix_implemented=True,software_qualification_passed=True,
    matched_before_after_passed=True,repaired_without_rescue=True,
    candidate_normal_command_compatibility_passed=True,fixture_checks_passed=True,menu_integration_passed=True,
    physical_repair_verified=False,human_review_passed=False,release_qualified=False,
    upstream_or_installed_SDK_modified=False,physical_firmware_writes=False,
    menu_sha256=menu,native_sha256=native,checks=checks,audit=audit,
    physical_before_evidence='experiments/uart0-race/physical-results.json',
    fixed_driver_sha256=audit['fixed_driver_sha256'])
(b/'results.json').write_text(json.dumps(result,indent=2)+'\n')
assert not out.exists();shutil.copytree(base,out)
for n in ('manifest.json','SHA256SUMS'):(out/n).unlink()
shutil.copyfile(b/'test.bin',out/'test.bin');shutil.copyfile(b/'native/repair.bin',out/'repair.bin')
images={'before':'vdp-race-before.bin','fixed':'vdp-race-fixed.bin','candidate':'vdp-rx-fixed.bin'}
for v,n in images.items():shutil.copyfile(firmware[v],out/n)
shutil.copyfile(root/'experiments/uart0-repair/readme.txt',out/'readme.txt')
shutil.copyfile(root/'experiments/uart0-repair/CREDITS.txt',out/'RX-FIX-CREDITS.txt')
shutil.copyfile(b/'results.json',out/'rx-fix-checks.json');shutil.copyfile(b/'audit.json',out/'rx-fix-audit.json')
shutil.copyfile(root/'experiments/uart0-race/physical-results.json',out/'rx-before-physical.json')
names=['vdp-race-before.bin','vdp-race-fixed.bin','vdp-rx-fixed.bin','vdp-2.16.0.bin','mos-candidate.bin','flash.bin']
lines=['MANUAL CONSOLE8 RECEIVER REPAIR COMPARISON',
       'Keep installed experimental MOS unchanged; menu ROM CRC239097B7.',
       '9/6 baseline -> reboot -> 8/5 test; 9/5 repaired -> reboot -> 8/6 test.',
       '9/7 candidate -> reboot -> 8/7 campaign; 9/4 stock restore -> reboot.',
       'Require no updater error and the correct banner; return0 alone proves nothing.',
       'No automatic flash, reset or root /MOS.bin replacement. Read readme.txt.','']
for n in names:lines.append(f'{n}: bytes={(out/n).stat().st_size} CRC32={zlib.crc32((out/n).read_bytes()):08X} SHA256={digest(out/n)}')
(out/'firmware.txt').write_text('\n'.join(lines)+'\n')
# The existing race-sources archive contains the complete original private VDP
# export/libraries. This companion adds the repair and exact changed sources,
# rather than storing three duplicate upstream source trees on the card.
sourcefiles=['experiments/uart0-repair','experiments/uart0-suite/src','experiments/uart0-suite/Makefile',
 'experiments/uart0-suite/entry.asm','experiments/uart0-suite/entry.linkcmd','experiments/uart0-suite/tests/menu_build.sh',
 'build/uart0-repair/original-uart.c','build/uart0-repair/fixed-uart.c','build/uart0-repair/uart-rx-full-lock.patch',
 'build/uart0-repair/canonical_setup.py','build/uart0-repair/native','build/uart0-repair/identity.h']
for v in images:
    sourcefiles.append(f'build/uart0-repair/{v}-source.json')
    sourcefiles.append(f'build/uart0-repair/{v}/platformio.ini')
    sourcefiles += [str(p.relative_to(root)) for p in (b/v/'video').glob('uart0*')]
    sourcefiles += [f'build/uart0-repair/{v}/video/{n}' for n in ('vdu_sys.h','vdu_stream_processor.h','version.h')]
subprocess.run(['tar','-czf',str(out/'rx-fix-sources.tar.gz'),*sourcefiles],cwd=root,check=True)
manifest={k:v for k,v in old.items() if k!='files'}
manifest.update(receiver_sync_repair=True,subexperiment='uart0-repair',firmware_changed=True,
    input_only_update=False,software_qualification_passed=True,physical_repair_verified=False,
    hardware_diagnostic_status='MATCHED_REPAIR_COMPARISON_PREPARED_PHYSICAL_PENDING',
    hardware_test_authorization='Author instructed fix the receiver synchronization defect after Console8 R0010 reproduced it; prepare and stage matched manual Console8 tests on the returned card',
    receiver_firmware_files=images,fixed_driver_sha256=audit['fixed_driver_sha256'],
    files={p.name:dict(bytes=p.stat().st_size,sha256=digest(p)) for p in sorted(out.iterdir())})
for n,pin in old['files'].items():
    if n not in ('test.bin','readme.txt','firmware.txt'):assert digest(out/n)==pin['sha256'],n
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(out/'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in sorted(out.iterdir()) if p.name!='SHA256SUMS'))
print(out,flush=True)
