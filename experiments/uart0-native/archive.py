"""Archive the complete native port, private diagnostic build and raw attempts."""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

root=Path(__file__).resolve().parents[2]
home=root.parent;native=home/'worktrees/uart-native-001/uart'
build=root/'build/uart0-native'
source=build/'maintained-source.tar'
assert not source.exists()
subprocess.run(['tar','--exclude=.git','--exclude=.venv','--exclude=.build',
                '--exclude=.emulator','--exclude=.local','--exclude=__pycache__',
                '-cf',str(source),'-C',str(native),'.'],check=True)
for args,name in [(['status','--short'],'native-status.txt'),
                  (['diff','--binary'],'native-tracked.patch'),
                  (['rev-parse','HEAD'],'native-head.txt')]:
    (build/name).write_bytes(subprocess.check_output(['git','-C',str(native),*args]))
toolchain=home/'worktrees/uart-native-001/toolchain'
manifest={str(p.relative_to(toolchain)):hashlib.sha256(p.read_bytes()).hexdigest()
          for p in sorted(toolchain.rglob('*')) if p.is_file()}
(build/'toolchain-files.json').write_text(json.dumps(manifest,indent=2)+'\n')
paths=['agon-mos/experiments/uart0-native','agon-mos/build/uart0-native',
       'agon-mos/build/uart0-branding/canonical_setup.py',
       'agon-mos/build/uart0-branding/flexe_profile.py',
       'agon-mos/build/uart0-batching/native','agon-mos/build/uart0-batching/runner',
       'agon-mos/build/uart0-async/ez80-model',
       'worktrees/uart-native-001/uart/.build',
       'worktrees/uart-native-001/uart/.emulator/uart0-review1',
       'worktrees/uart-native-001/stock/.build/stock-002',
       'worktrees/uart-native-001/dependencies','worktrees/uart-native-001/toolchain',
       'agon-mos/TODO.md','agon-mos/HANDOFF.md','agon-mos/docs/devlog-2026-10-16.md',
       'agon-mos/docs/uart0-native-tranche.md']
archive=root/'build/uart0-native-evidence-20261016.tar.gz'
assert not archive.exists()
subprocess.run(['tar','--exclude=.git','--exclude=.venv','--exclude=__pycache__',
                '-czf',str(archive),'-C',str(home),*paths],check=True)
count=0;total=0
with tarfile.open(archive,'r|gz') as tar:
    for member in tar:
        count+=1
        if member.isfile():
            with tar.extractfile(member) as f:
                while chunk:=f.read(1024*1024):total+=len(chunk)
digest=hashlib.file_digest(archive.open('rb'),'sha256').hexdigest()
receipt=dict(archive=str(archive),bytes=archive.stat().st_size,sha256=digest,
             every_regular_member_read=True,members=count,uncompressed_regular_bytes=total,
             native_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
             human_review_passed=False,hardware_qualified=False)
(root/'experiments/uart0-native/archive.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
