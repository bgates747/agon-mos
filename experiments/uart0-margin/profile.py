"""Dedicated diagnostic firmware protocol profile; never a physical margin proof."""
import hashlib,importlib.util,shutil,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
build=root/'build/uart0-margin'
assert sys.argv[1:] in ([],['--menu'],['--menu-auto'])
menu=bool(sys.argv[1:]);auto=sys.argv[1:]==['--menu-auto']
profile=root/('.emulator/uart0-margin-menu-auto' if auto else '.emulator/uart0-margin-menu' if menu else '.emulator/uart0-margin')
for p in Path('/proc').glob('[0-9]*'):
    try:
        if (p/'exe').resolve()==(profile/'runtime/flexe-agon-emulator.bin').resolve():raise RuntimeError('Close active margin profile before refreshing')
    except (FileNotFoundError,PermissionError):pass
spec=importlib.util.spec_from_file_location('canonical',root/'build/uart0-suite/setup_emulator.py')
canonical=importlib.util.module_from_spec(spec);spec.loader.exec_module(canonical)
canonical.link_shared_runtime(profile,root.parent/'golem/.emulator/runtime/fab-1.2.5')
runtime=profile/'runtime';runtime.mkdir(exist_ok=True)
product=root/'build/uart0-mos/runtime';esp=build/'firmware/.pio/build/esp32dev'
files={'flexe-agon-emulator.bin':product/'flexe-agon-emulator','flexe-vdp.so':product/'flexe-vdp.so',
'esp32-firmware.bin':esp/'firmware.bin','esp32-firmware.elf':esp/'firmware.elf',
'mos_platform.bin':root/'build/uart0-mos/MOS.bin','mos_platform.map':root/'build/uart0-mos/MOS.map'}
for name,source in files.items():shutil.copy2(source,runtime/name);canonical.replace_symlink(profile/name,runtime/name)
(profile/'firmware').unlink()
app=profile/'sdcard/uart0';app.mkdir(exist_ok=True)
shutil.copyfile(build/'margin.bin',app/'margin.bin')
(profile/'sdcard/autoexec.txt').write_bytes(b'cd /uart0\r\nload margin.bin &80000\r\nrun &80000\r\nECHO UART0 MARGIN RETURN\r\n')
extra=[]
if menu:
    suite=root/'build/uart0-suite'
    for name in ('test.bin','checks.bin','margin.bin','flash.bin','mos-candidate.bin','vdp-2.16.0.bin'):
        shutil.copyfile(suite/name,app/name);extra.append('sdcard/uart0/'+name)
    for path,name in (('bench/bench.bin','bench.bin'),('stress/stress.bin','stress.bin'),('api/app.bin','app.bin'),('api/short.bin','short.bin')):
        shutil.copyfile(suite/path,app/name);extra.append('sdcard/uart0/'+name)
    shutil.copyfile(esp/'firmware.bin',app/'vdp-cts-diag.bin');extra.append('sdcard/uart0/vdp-cts-diag.bin')
    cfg=(root/'experiments/uart0-suite/suite.cfg').read_text()
    cfg=cfg.replace('board=Heber Agon Console8','board=Oryx Flexe diagnostic review').replace('vdp=vdp-2.16.0.bin','vdp=vdp-cts-diag.bin').replace('vdp_label=stock 2.16.0 (confirm installed version)','vdp_label=UART0 CTS diagnostic; emulator metrics unqualified').replace('vdp_flash=1','vdp_flash=0').replace('physical_receiver=1','physical_receiver=0')
    (app/'suite.cfg').write_text(cfg);extra.append('sdcard/uart0/suite.cfg')
    if (root/'experiments/uart0-margin/readme.txt').exists():
        shutil.copyfile(root/'experiments/uart0-margin/readme.txt',app/'readme.txt');extra.append('sdcard/uart0/readme.txt')
    commands=b'run . auto\r\nrun . 7\r\nECHO UART0 MARGIN MENU RETURN\r\n' if auto else b'run\r\nECHO UART0 MARGIN MENU RETURN\r\n'
    (profile/'sdcard/autoexec.txt').write_bytes(b'cd /uart0\r\nload test.bin\r\n'+commands)
(profile/'.bespoke-vdp-profile').write_text('flexe-vdp.so\n')
canonical.write_profile_launcher(profile,strict_bespoke=True)
launcher=profile/'fab-agon-emulator'
s=launcher.read_text().replace('fab-agon-emulator.bin','flexe-agon-emulator.bin')
s=s.replace('\nvdp_name=', '''
export AGON_FLEXE_FIRMWARE="$profile_dir/esp32-firmware.bin"
export AGON_FLEXE_ELF="$profile_dir/esp32-firmware.elf"
export AGON_FLEXE_ENGINE="${AGON_FLEXE_ENGINE:-jit}"
export AGON_FLEXE_ARTIFACTS="$profile_dir/last-run"
export MOS_UART_STATS="$profile_dir/last-run/uart.json"
mkdir -p "$AGON_FLEXE_ARTIFACTS"
vdp_name=''',1)
primary=profile/'flexe-agon-emulator';primary.write_text(s);primary.chmod(0o755)
launcher.unlink()
(profile/'fab-agon-emulator.bin').unlink()
(profile/'.mos-release').write_text('UART0 development MOS; native ZDS II\n')
(profile/'.mos-release.sha256').write_text(''.join(f'{hashlib.sha256((profile/n).read_bytes()).hexdigest()}  {n}\n' for n in ('mos_platform.bin','mos_platform.map')))
pins=list(dict.fromkeys([*files,'flexe-agon-emulator','sdcard/autoexec.txt','sdcard/uart0/margin.bin',*extra]))
(profile/'.runtime.sha256').write_text(''.join(f'{hashlib.sha256((profile/n).read_bytes()).hexdigest()}  {n}\n' for n in pins))
print('Prepared stopped diagnostic protocol profile',profile)
