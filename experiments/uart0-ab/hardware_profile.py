"""Prepare a separate headless menu8 profile; preserve forensic/human profiles."""
import hashlib
from pathlib import Path
import shutil
import sys

root=Path(__file__).resolve().parents[2]
source=root/'.emulator/uart0-ab-auto'
p=root/'.emulator/uart0-ab-hardware-auto'
for d in Path('/proc').glob('[0-9]*'):
    try:
        if (d/'exe').resolve()==(p/'runtime/flexe-agon-emulator.bin').resolve():
            raise RuntimeError('Hardware menu profile is running')
    except (FileNotFoundError,PermissionError):pass
if not p.exists():
    shutil.copytree(source,p,symlinks=True,ignore=shutil.ignore_patterns('last-run','sdcard'))
app=p/'sdcard/uart0'
app.mkdir(parents=True,exist_ok=True)
base=root/'build/uart0-margin/console8-receiver-candidate-20261013'
for f in base.iterdir():
    if f.is_file():shutil.copyfile(f,app/f.name)
for f in app.glob('*.dat'):f.unlink()
for f in [*app.glob('R????.log'),app/'runs.log']:
    if f.exists():f.unlink()
shutil.copyfile(root/'build/uart0-suite/test.bin',app/'test.bin')
shutil.copyfile(root/'build/uart0-ab/hardware-native/test.bin',app/'ab.bin')
(app/'suite.cfg').write_text('board=Oryx off-device A/B menu check\nvdp_label=Frozen Golem snapshot; not physical stock qualification\nvdp_flash=0\nphysical_receiver=0\n')
repeats=int(sys.argv[1]) if len(sys.argv)>1 else 1
assert repeats in (1,2)
(p/'sdcard/autoexec.txt').write_bytes(b'cd /uart0\r\n'+b'load test.bin\r\nrun . 8\r\n'*repeats+b'ECHO UART0 AB MENU RETURN\r\n')
names=[line.split('  ',1)[1] for line in (source/'.runtime.sha256').read_text().splitlines()]
names += ['sdcard/uart0/ab.bin','sdcard/uart0/suite.cfg']
(p/'.runtime.sha256').write_text(''.join(f'{hashlib.sha256((p/n).read_bytes()).hexdigest()}  {n}\n' for n in names))
print('Prepared',p)
