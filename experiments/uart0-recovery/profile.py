"""Own frozen profile, accepted ABI1.1 MOS and unmodified Golem VDP snapshot."""
import hashlib,json,shutil,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];build=root/'build/uart0-recovery'
source=root/'.emulator/uart0-ab-auto';p=root/'.emulator/uart0-recovery'
mode=sys.argv[1] if len(sys.argv)>1 else 'short';assert mode in ('short','extended','manual')
for d in Path('/proc').glob('[0-9]*'):
    try:
        if p.exists() and (d/'exe').resolve()==(p/'runtime/flexe-agon-emulator.bin').resolve():raise RuntimeError('Recovery profile active')
    except (FileNotFoundError,PermissionError):pass
# Verify the historical runtime before using any copy; do not repin owner builds.
for line in (source/'.runtime.sha256').read_text().splitlines():
    digest,name=line.split('  ',1);assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest,name
if not p.exists():shutil.copytree(source,p,symlinks=True,ignore=shutil.ignore_patterns('last-run','sdcard'))
for name in ('flexe-agon-emulator.bin','flexe-vdp.so','esp32-firmware.bin','esp32-firmware.elf','mos_platform.bin','mos_platform.map'):
    target=p/name
    if target.exists() or target.is_symlink():target.unlink()
    target.symlink_to('runtime/'+name)
assert hashlib.sha256((p/'mos_platform.bin').read_bytes()).hexdigest()=='e7fc0732fba1ba6f94a30cc4bdab7e740c51a2b066cc35259f2abfc101fa848a'
app=p/'sdcard/uart0';app.mkdir(parents=True,exist_ok=True)
reports=[*app.glob('*.dat'),*app.glob('*.log')]
if reports:
    history=build/'profile-history';history.mkdir(exist_ok=True)
    n=1
    while (history/f'{n:03d}').exists():n+=1
    dest=history/f'{n:03d}';dest.mkdir()
    for f in reports:shutil.copyfile(f,dest/f.name);f.unlink()
base=root/'build/uart0-ab/console8-comparison-20261014'
manifest=json.loads((base/'manifest.json').read_text())
for name,entry in manifest['files'].items():
    assert hashlib.sha256((base/name).read_bytes()).hexdigest()==entry['sha256'],name
    shutil.copyfile(base/name,app/name)
shutil.copyfile(build/'test.bin',app/'test.bin');shutil.copyfile(build/'recovery.bin',app/'recovery.bin')
shutil.copyfile(build/'checks.bin',app/'checks.bin')
(app/'suite.cfg').write_text('board=Oryx receiver-recovery fixture qualification\nvdp_label=Frozen Golem stock-command snapshot; not official release binary\nvdp_flash=0\nphysical_receiver=0\n')
commands=b'cd /uart0\r\nload test.bin\r\n'
commands+=b'run\r\n' if mode=='manual' else (b'run . rxe\r\n' if mode=='extended' else b'run . rx\r\n')
commands+=b'ECHO UART0 RECOVERY MENU RETURN\r\n'
(p/'sdcard/autoexec.txt').write_bytes(commands)
files=['flexe-agon-emulator.bin','flexe-vdp.so','esp32-firmware.bin','esp32-firmware.elf','mos_platform.bin','mos_platform.map','fab-agon-emulator','flexe-agon-emulator','sdcard/autoexec.txt']
files += [str(f.relative_to(p)) for f in app.iterdir() if f.is_file() and f.suffix not in ('.dat','.log')]
(p/'.runtime.sha256').write_text(''.join(f'{hashlib.sha256((p/n).read_bytes()).hexdigest()}  {n}\n' for n in files))
print('Prepared stopped recovery profile',p)
