"""Oryx only: generate stopped private RX005 profiles; never launch."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,shutil,subprocess
p=argparse.ArgumentParser(description=__doc__)
for key in ('out','build','firmware','elf','setup-api','flexe-api'):
 p.add_argument('--'+key,type=Path,required=True)
p.add_argument('--firmware-sha256',required=True);p.add_argument('--elf-sha256',required=True)
a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
api=load('setup',a.setup_api);flexe=load('flexe',a.flexe_api)
proof=json.loads((a.build/'result.json').read_text())
assert h(a.build/'mos/bin/mos.bin')==proof['mos_sha256']
assert h(a.build/'mos/bin/mos.map')==proof['mos_map_sha256']
assert h(a.build/'fixture/bin/test.bin')==proof['fixture_sha256']
assert h(a.firmware)==a.firmware_sha256 and h(a.elf)==a.elf_sha256,'VDP owner artifact mismatch'
native=Path('/home/smith/Agon/mystuff/flexe-agon-emulator/build/fx224/host-r03/results/artifacts')
pins={'flexe-agon-emulator':'bad83f5455ab8d03436e8b7be68960110b318ef636dc60613e5215eb2dc37dda','flexe-vdp.so':'d77a7305b5c180381e49a4922ffd5a8ea9f824fee29110d5a955f337a1c96f0d'}
runtime=out/'runtime';runtime.mkdir()
for name,digest in pins.items():
 assert h(native/name)==digest,name
 target=runtime/('flexe-agon-emulator.bin' if name=='flexe-agon-emulator' else name)
 shutil.copy2(native/name,target)
shutil.copy2(a.firmware,runtime/'esp32-firmware.bin');shutil.copy2(a.elf,runtime/'esp32-firmware.elf')
rows=[]
for engine in ('jit','interp'):
 profile=out/engine;profile.mkdir();(profile/'sdcard').mkdir();(profile/'last-run').mkdir()
 for name in ('flexe-agon-emulator.bin','flexe-vdp.so','esp32-firmware.bin','esp32-firmware.elf'):
  (profile/name).symlink_to('../runtime/'+name)
 shutil.copyfile(a.build/'mos/bin/mos.bin',profile/'mos_platform.bin')
 shutil.copyfile(a.build/'mos/bin/mos.map',profile/'mos_platform.map')
 (profile/'.bespoke-vdp-profile').write_text('flexe-vdp.so\n')
 api.write_mos_identity(profile);api.write_profile_launcher(profile,strict_bespoke=True)
 launcher=profile/'fab-agon-emulator';script=launcher.read_text()
 script=script.replace('sdl_lib="${HOME}/.local/lib"','sdl_lib="/usr/lib/x86_64-linux-gnu"')
 script=script.replace('export LD_LIBRARY_PATH="${sdl_lib}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"','export LD_LIBRARY_PATH="${sdl_lib}"')
 script=script.replace('set -euo pipefail','set -euo pipefail\n'+f'export AGON_FLEXE_ENGINE={engine}\nexport AGON_FLEXE_FIRMWARE="{profile}/esp32-firmware.bin"\nexport AGON_FLEXE_ELF="{profile}/esp32-firmware.elf"\nexport AGON_FLEXE_ARTIFACTS="{profile}/last-run"')
 # Eirene uses the real FAT driver; an empty hostfs directory alone does not
 # mount the prepared image. Keep the immutable selected image explicit.
 script=script.replace('        -z "$@"','        --sdcard-img "${profile_dir}/card.img" '+chr(92)+'\n        -z "$@"')
 assert '--sdcard-img "${profile_dir}/card.img"' in script
 script=script.replace('FSIM runtime identity mismatch','RX005 runtime identity mismatch').replace('FSIM review profile','RX005 trial profile')
 launcher.write_text(script)
 (profile/'.mos-release').write_text('RX005 private trial '+proof['mos_crc32']+'; no physical qualification\n')
 (profile/'.mos-release.sha256').write_text(''.join(h(profile/n)+'  '+n+'\n' for n in ('mos_platform.bin','mos_platform.map')))
 with (profile/'card.img').open('xb') as f:f.truncate(32*1024*1024)
 subprocess.run(['mkfs.fat','-F','16',str(profile/'card.img')],check=True,stdout=subprocess.DEVNULL)
 subprocess.run(['mmd','-i',str(profile/'card.img'),'::/rx005'],check=True)
 subprocess.run(['mcopy','-i',str(profile/'card.img'),str(a.build/'fixture/bin/test.bin'),'::/rx005/test.bin'],check=True)
 (profile/'autoexec.txt').write_bytes(b'CD /rx005\r\ntest\r\nECHO RX005 CLI RETURN\r\n')
 subprocess.run(['mcopy','-i',str(profile/'card.img'),str(profile/'autoexec.txt'),'::/autoexec.txt'],check=True)
 (profile/'sdcard.img').symlink_to('card.img')
 flexe.name_flexe_profile(profile);flexe.verify_profile_executables(profile/'flexe-agon-emulator',profile/'flexe-agon-emulator.bin')
 names=('flexe-agon-emulator','flexe-agon-emulator.bin','flexe-vdp.so','esp32-firmware.bin','esp32-firmware.elf','mos_platform.bin','mos_platform.map')
 (profile/'.runtime.sha256').write_text(''.join(h(profile/n)+'  '+n+'\n' for n in names))
 subprocess.run(['bash','-n',str(profile/'flexe-agon-emulator')],check=True)
 rows.append({'path':str(profile),'engine':engine,'stopped':True,'initial_card_sha256':h(profile/'card.img')})
result={'schema':'RX005-stopped-profiles-1','build':proof,'firmware_sha256':h(a.firmware),'elf_sha256':h(a.elf),'profiles':rows}
(out/'profiles.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
