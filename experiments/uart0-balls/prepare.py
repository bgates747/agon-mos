"""Freeze an original AgonDev demo build against the accepted experimental MOS."""
import hashlib,json,shutil,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
out=(root/sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=True)
src=root/'experiments/uart0-balls';fixture=out/'fixture'
assert not fixture.exists()
shutil.copytree(src/'src',fixture/'src');shutil.copyfile(src/'Makefile',fixture/'Makefile')
mos=root/'build/uart0-completion/run005'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(mos/'MOS.bin')=='cb1d0f4e066395533a2f07c7454246fa3a1ed46134bf155b883bb8c6e8353128'
for name in ('MOS.bin','MOS.map'):shutil.copyfile(mos/name,out/name)
files={str(p.relative_to(fixture)):sha(p) for p in sorted(fixture.rglob('*')) if p.is_file() and p.name!='identity.h'}
build=hashlib.sha256(json.dumps(files,sort_keys=True).encode()+bytes.fromhex(sha(out/'MOS.bin'))).hexdigest()[:16]
(fixture/'src/identity.h').write_text('#define BD_BUILD "'+build+'"\n')
(out/'identity.json').write_text(json.dumps(dict(build=build,source=files,MOS_sha256=sha(out/'MOS.bin'),physical_qualification=False),indent=2)+'\n')
print(build)
