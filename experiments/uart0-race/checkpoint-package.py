"""Gate the repaired receiver fixture on real FatFS regressions, off-card."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from analyze import analyze
root=Path(__file__).resolve().parents[2]
b=root/'build/uart0-race/checkpoint-fix-20261014'
base=root/'build/uart0-ui/console8-inputfix-20261014'
out=b/'console8-checkpoint-fixed'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((base/'manifest.json').read_text())
for n,pin in old['files'].items():assert digest(base/n)==pin['sha256'],n
names=('fat-before-jit','fat-after-jit-02','fat-after-interp','fat-menu-jit',
       'fat-control-sdwrite-02','fat-control-badcrc','fat-control-noend','fat-control-nohello')
checks={n:json.loads((b/n/'receipt.json').read_text()) for n in names}
assert all(c['passed'] and c['actual_MOS_FatFS'] and c['hostfs_disabled'] for c in checks.values())
assert checks['fat-before-jit']['old_hang_reproduced'] and not checks['fat-before-jit']['returned_to_MOS']
native=digest(b/'race.bin')
payload=bytes(((n*157+7)%254)+1 for n in range(4096))+b'\0'
for n in ('fat-after-jit-02','fat-after-interp','fat-menu-jit'):
    c=checks[n];assert c['native_sha256']==native and c['result']['diagnostic_evidence_valid'] and c['returned_to_MOS']
    d=(b/n/'artifacts/mos-to-vdp.bin').read_bytes()
    for mode in (0,1):assert bytes([23,0,0xe6,0,mode,0])+payload in d
    assert c['runtime']['esp32-firmware.bin']==old['files']['vdp-race-diag.bin']['sha256']
assert digest(b/'fat-menu-jit/reports/test.bin')==old['files']['test.bin']['sha256']
assert checks['fat-control-sdwrite-02']['returned_to_MOS']
for n in ('fat-control-badcrc','fat-control-noend'):
    c=checks[n];assert c['result']['protocol_complete'] and not c['result']['diagnostic_evidence_valid']
assert checks['fat-control-nohello']['result']['stage']==3 and checks['fat-control-nohello']['result']['completed']==0
# Retain the first failed repair: a timestamp command became payload byte23.
contaminated=analyze((b/'fat-after-jit/reports/race.dat').read_bytes())
assert contaminated['protocol_complete'] and all(c['received']==1 and c['crc32']=='51D16A4A' for c in contaminated['cases'])
result=dict(fixture_checks_passed=True,menu_integration_passed=True,
    actual_FatFS_regression_passed=True,old_hang_reproduced=True,
    timestamp_contamination_reproduced=True,raw_payload_windows_verified_clean=True,
    native_sha256=native,menu_sha256=old['files']['test.bin']['sha256'],
    firmware_images_changed=False,physical_retry_performed=False,
    receiver_repair_verified=False,checks=checks,failed_first_repair=contaminated,
    source_sha256=digest(root/'experiments/uart0-race/host.asm'))
(b/'results.json').write_text(json.dumps(result,indent=2)+'\n')
assert not out.exists();shutil.copytree(base,out)
for n in ('manifest.json','SHA256SUMS'):(out/n).unlink()
shutil.copyfile(b/'race.bin',out/'race.bin')
shutil.copyfile(root/'experiments/uart0-race/readme.txt',out/'readme.txt')
original=root/'build/uart0-race/console8-diagnostic-20261014/firmware.txt'
(out/'firmware.txt').write_text('CHECKPOINT/MENU REPAIR: firmware unchanged; no reflash if recovery diagnostic VDP is still installed.\nUse menu8/4 for the repaired two-case test; afterward menu9/4 restores stock VDP.\n'+original.read_text())
shutil.copyfile(b/'results.json',out/'checkpoint-fix-checks.json')
subprocess.run(['tar','-czf',str(out/'checkpoint-fix-sources.tar.gz'),
 'experiments/uart0-race/host.asm','experiments/uart0-race/fat-regression.py',
 'experiments/uart0-race/checkpoint-package.py','experiments/uart0-race/analyze.py',
 'experiments/uart0-race/build.sh','experiments/uart0-race/packets.rb',
 'docs/uart0-checkpoint-failure.md','build/uart0-race/checkpoint-fix-20261014/host.linkcmd',
 'build/uart0-race/checkpoint-fix-20261014/cases.inc','build/uart0-race/checkpoint-fix-20261014/host.map',
 'build/uart0-race/checkpoint-fix-20261014/host.lst'],cwd=root,check=True)
manifest={k:v for k,v in old.items() if k!='files'}
manifest.update(input_only_update=False,native_checkpoint_fix=True,firmware_changed=False,
    hardware_diagnostic_status='RETRY_READY_FIXTURE_CHECKPOINT_ERRORS_REPAIRED',
    actual_FatFS_regression_passed=True,
    hardware_test_authorization='Author requests a substantive receiver hardware test with the menu repair included, and has returned the Console8 card for staging on 2026-10-14',
    files={f.name:dict(bytes=f.stat().st_size,sha256=digest(f)) for f in sorted(out.iterdir())})
for n,pin in old['files'].items():
    if n not in ('race.bin','readme.txt','firmware.txt'):assert digest(out/n)==pin['sha256'],n
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(out/'SHA256SUMS').write_text(''.join(f'{digest(f)}  {f.name}\n' for f in sorted(out.iterdir()) if f.name!='SHA256SUMS'))
print(out)
