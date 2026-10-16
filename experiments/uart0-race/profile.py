"""Isolated frozen frontend/MOS with this project's compiled diagnostic VDP."""
import hashlib,json,shutil,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];b=root/'build/uart0-race'
source=root/'.emulator/uart0-margin';p=root/'.emulator/uart0-race'
mode=sys.argv[1] if len(sys.argv)>1 else 'native';assert mode in ('native','menu-auto','manual')
for d in Path('/proc').glob('[0-9]*'):
    try:
        if p.exists() and (d/'exe').resolve()==(p/'runtime/flexe-agon-emulator.bin').resolve():raise RuntimeError('Race profile active')
    except (FileNotFoundError,PermissionError):pass
for line in (source/'.runtime.sha256').read_text().splitlines():
    digest,name=line.split('  ',1);assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest,name
if not p.exists():shutil.copytree(source,p,symlinks=True,ignore=shutil.ignore_patterns('sdcard','last-run'))
runtime=p/'runtime';firmware=b/'firmware/.pio/build/esp32dev'
for name in ('flexe-agon-emulator.bin','flexe-vdp.so','mos_platform.bin','mos_platform.map'):
    assert hashlib.sha256((runtime/name).read_bytes()).digest()==hashlib.sha256((source/'runtime'/name).read_bytes()).digest()
for name,sourcefile in [('esp32-firmware.bin',firmware/'firmware.bin'),('esp32-firmware.elf',firmware/'firmware.elf')]:shutil.copyfile(sourcefile,runtime/name)
for name in ('flexe-agon-emulator.bin','flexe-vdp.so','mos_platform.bin','mos_platform.map','esp32-firmware.bin','esp32-firmware.elf'):
    target=p/name
    if target.exists() or target.is_symlink():target.unlink()
    target.symlink_to('runtime/'+name)
app=p/'sdcard/uart0';app.mkdir(parents=True,exist_ok=True)
reports=[*app.glob('*.dat'),*app.glob('*.log')]
if reports:
    history=b/'profile-history';history.mkdir(exist_ok=True);n=1
    while (history/f'{n:03d}').exists():n+=1
    saved=history/f'{n:03d}';saved.mkdir()
    for f in reports:shutil.copyfile(f,saved/f.name);f.unlink()
shutil.copyfile(b/'race.bin',app/'race.bin')
extra=[]
if mode!='native':
    base=root/'build/uart0-recovery/console8-recovery-20261014';m=json.loads((base/'manifest.json').read_text())
    for name,entry in m['files'].items():
        assert hashlib.sha256((base/name).read_bytes()).hexdigest()==entry['sha256']
        shutil.copyfile(base/name,app/name);extra.append('sdcard/uart0/'+name)
    shutil.copyfile(b/'test.bin',app/'test.bin')
    (app/'suite.cfg').write_text('board=Oryx compiled receiver-race diagnostic\nvdp_label=UART0 recovery diagnostic; physical evidence pending\nvdp_flash=0\nphysical_receiver=0\n')
    run=b'run . race\r\n' if mode=='menu-auto' else b'run\r\n'
    commands=b'cd /uart0\r\nload test.bin\r\n'+run+b'ECHO UART0 RACE RETURN\r\n'
else:commands=b'cd /uart0\r\nload race.bin &80000\r\nrun &80000\r\nECHO UART0 RACE RETURN\r\n'
(p/'sdcard/autoexec.txt').write_bytes(commands)
names=['flexe-agon-emulator.bin','flexe-vdp.so','mos_platform.bin','mos_platform.map','esp32-firmware.bin','esp32-firmware.elf','fab-agon-emulator','flexe-agon-emulator','sdcard/autoexec.txt','sdcard/uart0/race.bin']
(p/'.runtime.sha256').write_text(''.join(f'{hashlib.sha256((p/n).read_bytes()).hexdigest()}  {n}\n' for n in dict.fromkeys(names+extra)))
print('Prepared stopped diagnostic profile',p)
