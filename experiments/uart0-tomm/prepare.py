"""Freeze app-only comparison; do not change or rebuild maintained MOS."""
import hashlib,json,shutil,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
out=(root/sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False)
f=out/'fixture';(f/'src').mkdir(parents=True)
src=root/'experiments/uart0-tomm'
for p in (src/'src').glob('*'):shutil.copyfile(p,f/'src'/p.name)
shutil.copyfile(src/'Makefile',f/'Makefile')
for n in ('platform.c','platform.h','bridge.src','keys.h'):
 shutil.copyfile(root/'experiments/uart0-balls/src'/n,f/'src'/n)
base=root/'build/uart0-completion/run005'
for n in ('packets.h',):shutil.copyfile(base/'fixture/src'/n,f/'src'/n)
shutil.copyfile(base/'fixture/checks.bin',f/'checks.bin')
for n in ('MOS.bin','MOS.map'):shutil.copyfile(base/n,out/n)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert h(out/'MOS.bin')=='cb1d0f4e066395533a2f07c7454246fa3a1ed46134bf155b883bb8c6e8353128'
sources={str(p.relative_to(f)):h(p) for p in sorted(f.rglob('*')) if p.is_file()}
ident=hashlib.sha256(json.dumps(sources,sort_keys=True).encode()).hexdigest()[:16]
(f/'src/identity.h').write_text('#define TM_BUILD "'+ident+'"\n')
(out/'identity.json').write_text(json.dumps(dict(build=ident,source=sources,original=h(src/'original/async_vdu.asm'),MOS=h(out/'MOS.bin'),physical=False),indent=2)+'\n')
print(ident)
