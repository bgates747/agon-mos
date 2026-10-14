"""Select only the Console8 card, then invoke the existing guarded deployer."""
import hashlib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];build=root/'build/uart0-recovery';package=Path(sys.argv[1]).resolve()
assert sys.argv[2:] in ([],['--deploy'])
deploy=sys.argv[2:]==['--deploy']
# The deployer independently repeats uniqueness, removability and mount checks.
rows=json.loads(subprocess.check_output(['lsblk','--json','--list','-o','PATH,UUID,MOUNTPOINT,RM'],text=True))['blockdevices']
match=[r for r in rows if (r.get('uuid') or '').upper()=='8658-1C23'];assert len(match)==1 and match[0]['rm'] and match[0]['mountpoint'],'Console8 card unavailable/ambiguous'
mount=Path(match[0]['mountpoint']);target=mount/'test/mos-uart0'
manifest=target/'manifest.json';old=json.loads(manifest.read_text())
assert old['deployment_path']=='/test/mos-uart0'
assert hashlib.sha256((target/'test.bin').read_bytes()).hexdigest()==old['files']['test.bin']['sha256'],'Unrecognized test.bin collision'
root_mos=mount/'MOS.bin';before=hashlib.sha256(root_mos.read_bytes()).hexdigest() if root_mos.exists() else None
# All input strings are structured argv; no shell interpolation of mount paths.
command=[str(root/'.venv/bin/python'),'-B',str(root/'experiments/uart0-suite/deploy.py'),str(package),
 '--mount',str(mount),'--uuid','8658-1C23','--backup',str(root/'build/uart0-suite/before-recovery-20261014'),
 '--receipt',str(build/'deployment.json'),'--previous-manifest-sha256',hashlib.sha256(manifest.read_bytes()).hexdigest(),
 '--exploratory-receiver-recovery']
if not deploy:command.append('--dry-run')
subprocess.run(command,check=True)
if deploy:
    after=hashlib.sha256(root_mos.read_bytes()).hexdigest() if root_mos.exists() else None
    assert before==after,'Root MOS changed'
    receipt=json.loads((build/'deployment.json').read_text());receipt['root_MOS_preserved_sha256']=after
    (build/'deployment.json').write_text(json.dumps(receipt,indent=2)+'\n')
