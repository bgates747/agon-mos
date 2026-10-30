"""Compare actual native core bytes and explicit relocation records to the frozen oracle."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--directory',type=Path,required=True)
p.add_argument('--toolchain',type=Path,required=True)
p.add_argument('--rom',type=Path,required=True)
a=p.parse_args();directory=a.directory;tool=a.toolchain/'bin'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(directory/'frozen-source.tar')=='38321531d35faff356b065daab1b4ac64dea9a4acb4e3d1e0b72177937dacc9f'
relocations={};raws={};objects={}
for name in ('frozen','native'):
    obj=directory/(name+'-uart0.o');raw=directory/(name+'-STARTUP.bin')
    objects[name]=sha(obj);copy=directory/(name+'-copy.o')
    subprocess.run([str(tool/'ez80-none-elf-objcopy'),'--dump-section',
                    '.STARTUP='+str(raw),str(obj),str(copy)],check=True)
    copy.unlink();assert sha(obj)==objects[name]
    output=subprocess.check_output([str(tool/'ez80-none-elf-objdump'),'-r',str(obj)],text=True)
    (directory/(name+'-relocations.txt')).write_text(output)
    relocations[name]=[line for line in output.splitlines() if re.match(r'^[0-9a-fA-F]+\s+r_',line)]
    raws[name]=raw.read_bytes()
assert raws['native']==raws['frozen'] and len(raws['native'])==2497
assert relocations['native']==relocations['frozen'] and len(relocations['native'])==300
receipt=dict(passed=True,bytes=2497,section_sha256=sha(directory/'native-STARTUP.bin'),
             explicit_relocations_identical=True,relocations=300,heuristic_masking=False,
             final_ROM_sha256=sha(a.rom),frozen_source_sha256=sha(directory/'frozen-source.tar'),objects=objects)
(directory/'comparison.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
