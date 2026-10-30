"""Prepare a stopped, isolated Oryx review using the qualified native runtime."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
from validate import validate

root=Path(__file__).resolve().parents[2]
native=Path.home()/'Agon/mystuff/worktrees/uart-native-001/uart'
build=root/'build/uart0-native'
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--attempt',required=True)
a=p.parse_args();assert a.attempt.isalnum()
qualified=build/'flexe-jit-fixed2'
validate(qualified,root/'build/uart0-batching/native')
source=native/'.emulator/uart0-jit-fixed2'
assert not (source/'sdcard.img').exists(), 'Source campaign must be stopped'
out=build/('human-'+a.attempt);out.mkdir(exist_ok=False)
profile=native/'.emulator'/('uart0-'+a.attempt)
shutil.copytree(source,profile,symlinks=True,
                ignore=shutil.ignore_patterns('last-run','sdcard.img','.runtime.sha256'))
final=native/'.build/uart-010-final/bin'
for suffix in ('bin','map'):shutil.copyfile(final/('MOS.'+suffix),profile/'runtime'/('mos_platform.'+suffix))
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(final/'MOS.bin')=='5543d6acaa64bebd3006cb034a8dda9b61cfe92c82cbbffe2c391a9392f0f4c9'
(profile/'.mos-release.sha256').write_text(''.join(sha(profile/n)+'  '+n+'\n' for n in ('mos_platform.bin','mos_platform.map')))
card=out/'card.img';shutil.copyfile(qualified/'card.img',card)
# All old reports already live in the immutable campaign evidence. This is a
# new private virtual card, never the physical Console8 card.
subprocess.run(['mdel','-i',str(card),'::/uart0/*.dat'],check=True)
startup=out/'autoexec.txt'
startup.write_bytes(b'CD /uart0\r\nLOAD stress16.bin &80000\r\nRUN &80000\r\nECHO NATIVE UART REVIEW COMPLETE\r\n')
readme=out/'readme.txt'
readme.write_text('Native experimental UART MOS review.\r\n'
 'Automatic16-byte-mode stress: four pause cases,32 replies each,8192 final bytes compared per case.\r\n'
 'Allow about two minutes; repeated progress lines are expected.\r\n'
 'Expect UART0 STRESS FIXTURE PASS then NATIVE UART REVIEW COMPLETE and the MOS prompt.\r\n'
 'Check typed help/dir work normally, then close the window and report pass/failure.\r\n'
 'One fresh review card; evidence/history stays in the project. Do not flash physical hardware.\r\n')
for path,name in ((startup,'autoexec.txt'),(readme,'uart0/readme.txt')):
    subprocess.run(['mcopy','-o','-i',str(card),str(path),'::/'+name],check=True)
(profile/'sdcard.img').symlink_to(card)
factory_path=root/'build/uart0-branding/canonical_setup.py'
spec=importlib.util.spec_from_file_location('canonical',factory_path)
factory=importlib.util.module_from_spec(spec);spec.loader.exec_module(factory)
factory.name_flexe_profile(profile)
assert not (profile/'fab-agon-emulator').exists() and not (profile/'fab-agon-emulator.bin').exists()
launcher=profile/'flexe-agon-emulator'
assert launcher.is_file() and not launcher.is_symlink()
names=['flexe-agon-emulator','flexe-agon-emulator.bin','flexe-vdp.so','mos_platform.bin',
       'mos_platform.map','esp32-firmware.bin','esp32-firmware.elf']
(profile/'.runtime.sha256').write_text(''.join(sha(profile/n)+'  '+n+'\n' for n in names))
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=profile,check=True)
subprocess.run(['bash','-n','flexe-agon-emulator'],cwd=profile,check=True)
result=dict(prepared=True,stopped=True,profile=str(profile),source_campaign=str(qualified),
            firmware_build='uart-010-final',ROM_sha256=sha(final/'MOS.bin'),
            VDP_sha256=sha(profile/'esp32-firmware.bin'),initial_card_sha256=sha(card),
            runtime_inputs={name:sha(profile/name) for name in names},
            human_review_passed=False,hardware_qualified=False)
(out/'prepared.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
