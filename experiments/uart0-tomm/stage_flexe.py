"""Oryx-only stopped staging. Never launches an emulator."""
import hashlib,importlib.util,json,shutil,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];b=(root/sys.argv[1]).resolve()
base=root/'.emulator/uart0-completion-jit-final';common=b/'runtime';common.mkdir()
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources={'flexe-agon-emulator.bin':root/'build/uart0-balls/runtime-maintained/flexe-agon-emulator.bin','flexe-vdp.so':root/'build/uart0-balls/runtime-maintained/flexe-vdp.so','mos_platform.bin':b/'MOS.bin','mos_platform.map':b/'MOS.map','esp32-firmware.bin':base/'esp32-firmware.bin','esp32-firmware.elf':base/'esp32-firmware.elf'}
for n,p in sources.items():shutil.copyfile(p,common/n)
(common/'flexe-agon-emulator.bin').chmod(0o755)
assert h(common/'flexe-agon-emulator.bin')=='7e7d0e1bc89af72bde7ffbd6c06446aaefda4d1803f89eb1faf3167307ee1e01'
assert h(common/'flexe-vdp.so')=='0866265bd6f3d73ad572f31dc1bb954f308ed9a5d857efa9414d37e1ade13374'
spec=importlib.util.spec_from_file_location('factory',root.parent/'agon-dev-env/scripts/setup_emulator.py');factory=importlib.util.module_from_spec(spec);spec.loader.exec_module(factory)
profiles=[]
for engine in ('jit','interp'):
 for mode in range(3):
  p=b/f'profile-{engine}-{mode}';p.mkdir();(p/'sdcard').mkdir()
  for n in sources:(p/n).symlink_to('../runtime/'+n)
  for n in ('flexe-agon-emulator','.mos-release','.mos-release.sha256','.bespoke-vdp-profile'):shutil.copyfile(base/n,p/n)
  card=p/'card.img'
  with card.open('xb') as f:f.truncate(32*1024*1024)
  subprocess.run(['mkfs.fat','-F','16',str(card)],check=True,stdout=subprocess.DEVNULL)
  subprocess.run(['mmd','-i',str(card),'::/uart0'],check=True)
  def put(src,dst):subprocess.run(['mcopy','-i',str(card),str(src),'::/'+dst],check=True)
  put(b/'fixture/bin/compare.bin','uart0/test.bin');put(b/'fixture/checks.bin','uart0/checks.bin')
  a=p/'autoexec.txt';a.write_bytes(f'CD /uart0\r\nLOAD test.bin\r\nRUN . {mode}\r\nDIR\r\nECHO TM001 CLI RETURN\r\n'.encode());put(a,'autoexec.txt')
  (p/'sdcard.img').symlink_to('card.img')
  factory.name_flexe_profile(p)
  names=[*sources,'flexe-agon-emulator'];(p/'.runtime.sha256').write_text(''.join(h(p/n)+'  '+n+'\n' for n in names))
  subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=p,check=True)
  subprocess.run(['sha256sum','--check','--status','.mos-release.sha256'],cwd=p,check=True)
  subprocess.run(['bash','-n','flexe-agon-emulator'],cwd=p,check=True)
  profiles.append(dict(path=str(p),engine=engine,mode=mode,stopped=True))
(b/'profiles.json').write_text(json.dumps(dict(profiles=profiles,runtime={n:h(common/n) for n in sources}),indent=2)+'\n')
